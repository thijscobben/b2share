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

"""Celery background tasks."""

from celery import shared_task
from flask import current_app
from invenio_files_rest.models import FileInstance
from invenio_files_rest.tasks import schedule_checksum_verification


def failed_checksum_files_query():
    return FileInstance.query.filter_by(last_check=None)


@shared_task()
def schedule_all_files_for_checksum():
    current_app.config['FILES_REST_CHECKSUM_VERIFICATION_FILES_QUERY'] = \
        'invenio_files_rest.tasks.default_checksum_verification_files_query'
    schedule_checksum_verification.apply_async(kwargs={'batch_interval':
                                                       {'minutes': 10},
                                                       'max_count': 0,
                                                       'max_size': 0})


@shared_task()
def schedule_failed_checksum_files():
    current_app.config['FILES_REST_CHECKSUM_VERIFICATION_FILES_QUERY'] = \
        'b2share.modules.records.tasks.failed_checksum_files_query'
    schedule_checksum_verification.apply_async(kwargs={'batch_interval':
                                                       {'minutes': 10},
                                                       'max_count': 0,
                                                       'max_size': 0})
