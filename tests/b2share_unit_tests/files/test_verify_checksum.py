# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test Invenio integration with submission tests."""
from mock import patch
from six import BytesIO
from six.moves.urllib.request import urlopen
from invenio_db import db
from invenio_files_rest.models import Bucket, ObjectVersion
from invenio_files_rest.storage.base import FileStorage
from invenio_files_rest.tasks import verify_checksum

from b2share_unit_tests.helpers import create_deposit, create_user, \
    generate_record_data, url_for_file
from b2share.modules.files.tasks import schedule_all_files_for_checksum, \
    schedule_failed_checksum_files


def test_verify_checksum(app, tmp_location):
    """Test that verify_checksum sets last_check=False
       if the checksum is different and last_check=None
       if it failed to calculate the checksum, e.g. an exception was raised."""
    with app.app_context():
        b1 = Bucket.create(tmp_location)
        objects = []
        for i in range(10):
            objects.append(
                ObjectVersion.create(b1, str(i), stream=BytesIO(b'test')))
        db.session.commit()

        for obj in objects:
            verify_checksum.apply([str(obj.file_id)])
            assert obj.file.last_check

        # assert that mismatches in md5 checksums are caught
        corrupted_file = objects[0].file
        with open(corrupted_file.uri, 'w') as file_writer:
            file_writer.write('modified content')

        verify_checksum.apply([str(corrupted_file.id)])
        assert corrupted_file.last_check is False

        # assert that when exceptions occur last_check=None
        failed_file = objects[1].file
        with patch.object(FileStorage,
                          'checksum') \
                as mock_check:
            mock_check.side_effect = KeyError()
            verify_checksum.apply_async(args=[str(failed_file.id)],
                                        kwargs={'throws': False})
            assert failed_file.last_check is None


def test_verify_checksum_in_deposit(app, test_communities,
                                    login_user, test_users):
    """Test uploading and reading deposit files."""
    with app.app_context():
        creator = create_user('creator')
        uploaded_files = {
            'myfile1.dat': b'contents1',
            'myfile2.dat': b'contents2',
            'replaced.dat': b'old_content',
        }
        test_record_data = generate_record_data()
        deposit = create_deposit(test_record_data, creator, uploaded_files)
        uploaded_file_name = 'additional.dat'
        uploaded_file_content = b'additional content'
        headers = [('Accept', '*/*')]
        with app.test_client() as client:
            login_user(creator, client)

            # try uploading a new file
            file_url = url_for_file(deposit.files.bucket.id,
                                    uploaded_file_name)
            client.put(
                file_url,
                input_stream=BytesIO(uploaded_file_content),
                headers=headers
            )
            uploaded_files[uploaded_file_name] = uploaded_file_content

            # get file content by its uri
            file_instance = deposit.files['replaced.dat'].obj.file
            file_reader = urlopen('file://' + file_instance.uri)
            content = file_reader.read()
            assert content == b'old_content'

            # first make it writeable
            file_instance.writable = True
            file_instance.set_contents(BytesIO(b'test'))
            db.session.add(file_instance)
            db.session.commit()

            # changing the contents this way should be okay
            # as the checksum is updated after writing
            verify_checksum.apply([str(file_instance.id)])
            assert file_instance.last_check

            # directly changing the contents at the uri though
            # will cause verify_checksum to change the last_check to
            # False as the checksum will be different now
            with open(file_instance.uri, 'w') as file_writer:
                file_writer.write('modified content')

            verify_checksum.apply([str(file_instance.id)])
            assert not file_instance.last_check


def test_scheduling(app, test_communities, login_user):
    """Test that scheduling files happens properly."""
    with app.app_context():
        b1 = Bucket.create()
        objects = []
        for i in range(10):
            objects.append(
                ObjectVersion.create(b1, str(i), stream=BytesIO(b'test')))
        db.session.commit()

        # corrupt 1 file
        corrupted_file = objects[0].file
        with open(corrupted_file.uri, 'w') as file_writer:
            file_writer.write('modified content')

        # schedule all files
        schedule_all_files_for_checksum()

        # assert that all will be checked
        assert not corrupted_file.last_check
        for o in objects[1:]:
            assert o.file.last_check

        # make 1 file fail
        failed_file = objects[1].file
        failed_file.last_check = None

        # schedule all failed
        schedule_failed_checksum_files()
        # assert that 1 wiil run again
        assert failed_file.last_check
        assert not corrupted_file.last_check
