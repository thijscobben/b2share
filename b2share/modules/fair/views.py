# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2015, 2016, University of Tuebingen, CERN.
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

"""EUDAT B2ACCESS Fair REST API."""

import json
from flask import Blueprint
from invenio_rest import ContentNegotiatedMethodView

from invenio_records_rest.serializers.jsonld import JSONLDSerializer


blueprint = Blueprint(
    'fdp',
    __name__,
)


class FairDataPoint(ContentNegotiatedMethodView):
    view_name = 'fair_data_point'

    def __init__(self, **kwargs):
        """Constructor."""
        super(FairDataPoint, self).__init__(
            serializers={
                'application/ld-json': JSONLDSerializer,
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'PATCH': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, path):
        pass

    def patch(self):
        pass


class CatalogMetadata(ContentNegotiatedMethodView):
    view_name = 'fair_data_point'

    def __init__(self, **kwargs):
        """Constructor."""
        super(FairDataPoint, self).__init__(
            serializers={
                'application/ld-json': JSONLDSerializer,
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, path):
        pass

    def post(self):
        pass


class DatasetMetadata(ContentNegotiatedMethodView):
    view_name = 'fair_data_point'

    def __init__(self, **kwargs):
        """Constructor."""
        super(FairDataPoint, self).__init__(
            serializers={
                'application/ld-json': JSONLDSerializer,
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, path):
        pass

    def post(self):
        pass


class DistributionMetadata(ContentNegotiatedMethodView):
    view_name = 'fair_data_point'

    def __init__(self, **kwargs):
        """Constructor."""
        super(FairDataPoint, self).__init__(
            serializers={
                'application/ld-json': JSONLDSerializer,
            },
            default_method_media_type={
                'GET': 'application/ld-json',
                'POST': 'application/ld-json',
            },
            default_media_type='application/ld-json',
            **kwargs
        )

    def get(self, path):
        pass

    def post(self):
        pass


blueprint.add_url_rule('/fdp/',
                       view_func=FairDataPoint.as_view(
                           FairDataPoint.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>',
                       view_func=CatalogMetadata.as_view(
                           CatalogMetadata.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>/<dataset_id>',
                       view_func=DatasetMetadata.as_view(
                           DatasetMetadata.view_name))
blueprint.add_url_rule('/fdp/<catalog_id>/<dataset_id>/<distribution_id>',
                       view_func=DistributionMetadata.as_view(
                           DistributionMetadata.view_name))
