# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""WebMessage Forms"""

from string import strip
from datetime import datetime

from flask import url_for
from invenio.sqlalchemyutils import db
from invenio.websession_model import User, Usergroup
from invenio.webmessage_model import MsgMESSAGE, UserMsgMESSAGE
from invenio.webinterface_handler_flask_utils import _
from invenio.bibknowledge import get_kb_mappings
from flask.ext.wtf import Form
from invenio.wtforms_utils import InvenioBaseForm, FilterForm, \
                    DateTimePickerWidget, FilterTextField, AutocompleteField, \
                    MultiWidget, RowWidget
from wtforms import DateTimeField, BooleanField, TextField, TextAreaField, \
                    PasswordField, HiddenField, validators
from wtforms import FormField, SelectField
from wtforms import Form as WTFormDefault
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class JournalForm(WTFormDefault):
    name = QuerySelectField('',
            get_pk=lambda i: i['key'],
            get_label=lambda i: i['value'],
            query_factory=lambda: [{'key':'', 'value':_('Any journal')}] + get_kb_mappings('EJOURNALS'))
    vol = TextField(_('Vol'))
    page = TextField(_('Pg'))

class EasySearchForm(InvenioBaseForm):
    """Defines form for easy seach popup."""
    author = AutocompleteField(_('Author'), data_provide="typeahead-url",
        data_source=lambda: url_for('search.list', field='exactauthor'))
    title = TextField(_('Title'))
    rn = AutocompleteField(_('Report number'), data_provide="typeahead-url",
        data_source=lambda: url_for('search.list', field='reportnumber'))
    aff = AutocompleteField(_('Affiliation'), data_provide="typeahead-url",
        data_source=lambda: url_for('search.list', field='affiliation'))
    cn = AutocompleteField(_('Collaboration'), data_provide="typeahead-url",
        data_source=lambda: url_for('search.list', field='collaboration'))
    k = AutocompleteField(_('Keywords'), data_provide="typeahead-url",
        data_source=lambda: url_for('search.list', field='keyword'))
    journal = FormField(JournalForm, widget=RowWidget())


