# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 University of Tuebingen, CERN.
# Copyright (C) 2015 University of Tuebingen.
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

"""B2Share Schemas module Command Line Interface."""

from __future__ import absolute_import

import click
import json
from jsonschema import validate
import os

from flask_cli import with_appcontext

from invenio_db import db

from .errors import RootSchemaAlreadyExistsError
from .helpers import load_root_schemas
from .validate import restricted_metaschema
from .api import BlockSchema

from b2share.modules.communities.api import Community, CommunityDoesNotExistError
from b2share.modules.communities.cli import communities
from b2share.modules.communities.helpers import get_community_by_name_or_id


@click.group()
def schemas():
    """Schemas management commands."""


@schemas.command()
@with_appcontext
@click.option('-v', '--verbose', is_flag=True, default=False)
def init(verbose):
    """CLI command loading Root Schema files in the database."""
    try:
        load_root_schemas(cli=True, verbose=verbose)
    except RootSchemaAlreadyExistsError as e:
        raise click.ClickException(str(e))

            
@schemas.command()
@with_appcontext
@click.option('-v','--verbose', is_flag=True, default=False)
@click.argument('community')
@click.argument('name')
def block_schema_add(verbose, community, name):
    """Adds a block schema to the database. Community is the ID or NAME of the maintaining community for this block schema. Name is the name as displayed in block_schema_list command."""
    if verbose:
        click.secho("Creating block schema with name %s to be maintained by community %s" % (name, community))
    comm = get_community_by_name_or_id(community)
    if not comm:
        raise click.BadParameter("There is no community by this name or ID: %s" % community)
    if len(name)>255:
        raise click.BadParameter("NAME parameter is longer than the 255 character maximum")
    block_schema = BlockSchema.create_block_schema(comm.id, name)
    db.session.commit()
    if verbose:
        click.secho("Created block schema with name %s and id %s" % (name, block_schema.id))

@schemas.command()
@with_appcontext
@click.option('-c','--community', help='show only block schemas filtered by maintaining community id or name')
def block_schema_list(community):
    """Lists all block schemas for this b2share instance (filtered for a community)."""
    comm = get_community_by_name_or_id(community)
    community_id = None
    if comm:
        community_id = comm.id
    try:
        block_schemas = BlockSchema.get_all_block_schemas(community_id=community_id)
    except BlockSchemaDoesNotExistError:
         raise click.ClickException("No block schemas found, community parameter was: %s" % community)
    click.secho("BLOCK SCHEMA ID\t\t\t\tNAME\t\tMAINTAINER\tDEPRECATED\t#VERSIONS")
    for bs in block_schemas:
        bs_comm = Community.get(id=bs.community)
        click.secho("%s\t%s\t%s\t\t%s\t\t%d" % (bs.id,bs.name[0:15], bs_comm.name[0:15], bs.deprecated, len(bs.versions)  ))
        