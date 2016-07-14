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

from .errors import RootSchemaAlreadyExistsError
from .helpers import load_root_schemas
from .validate import restricted_metaschema

from b2share.modules.communities.api import Community, CommunityDoesNotExistError
from b2share.modules.communities.cli import communities



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


@communities.command()
@with_appcontext
@click.option('-v','--verbose', is_flag=True, default=False)
@click.argument('community')
#help='path to the metadata-schema file to add for this community', help='id or name of the community to add the metadata-schema for')
@click.argument('schema_file')
def add_schema(verbose,community,schema_file):
    """Adds a new version of a metadata schema for a community"""
    try:
        fetched_community = Community.get(id=community)
    except:
        try:
            fetched_community = Community.get(name=community)
        except CommunityDoesNotExistError:
            raise click.BadParameter("No community exists by the name or ID %s" % community)
    if not(os.path.isfile(schema_file)):
        raise click.ClickException("schema_file argument should point to a file")
    with open(schema_file,'r') as f:
        community_schema = f.read().replace('\n','')
    try:
        community_schema_dict = json.loads(community_schema)
    except json.JSONDecodeError as e:
        raise click.ClickException("%s is not a valid JSON file" % schema_file)
    block_schemas = community_schema_dict['block_schemas']
    for key in block_schemas.keys():
        if verbose:
            click.echo(" checking block schema %s for community_schema file %s" % (key, schema_file))
        versions = block_schemas[key]['versions']
        if verbose:
            click.echo("Versions: %d" % len(versions))
        try:
            validate(versions[0],restricted_metaschema)
        except JSONDecodeError as e:
            #raise click.ClickException(str(e))
            click.echo('testing')