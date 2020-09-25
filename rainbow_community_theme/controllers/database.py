# -*- coding: utf-8 -*-

import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import tempfile
import time

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_decode, iri_to_uri
from lxml import etree
import unicodedata

import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo.tools.safe_eval import safe_eval
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security

_logger = logging.getLogger(__name__)

path = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', 'template'))
loader = jinja2.FileSystemLoader(path)

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

CONTENT_MAXAGE = http.STATIC_CACHE_LONG  # menus, translations, static qweb

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

COMMENT_PATTERN = r'Modified by [\s\w\-.]+ from [\s\w\-.]+'

# ----------------------------------------------------------
# Odoo Web helpers
# ----------------------------------------------------------

db_list = http.db_list

db_monodb = http.db_monodb


class Database(http.Controller):
    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = odoo.tools.config['list_db']
        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        d['pattern'] = DBNAME_PATTERN
        # databases list
        d['databases'] = []
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = odoo.service.db.list_db_incompatible(
                d['databases'])
        except odoo.exceptions.AccessDenied:
            monodb = db_monodb()
            if monodb:
                d['databases'] = [monodb]
        return env.get_template("db_manager.html").render(d)

    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        request._cr = None
        return self._render_template(manage=False)

    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        request._cr = None
        return self._render_template()

    @http.route('/web/database/create',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def create(self, master_pwd, name, lang, password, **post):
        try:
            if not re.match(DBNAME_PATTERN, name):
                raise Exception(
                    _('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'
                      ))
            # country code could be = "False" which is actually True in python
            country_code = post.get('country_code') or False
            dispatch_rpc('db', 'create_database', [
                master_pwd, name,
                bool(post.get('demo')), lang, password, post['login'],
                country_code, post['phone']
            ])
            request.session.authenticate(name, post['login'], password)
            return http.local_redirect('/web/')
        except Exception as e:
            error = "Database creation error: %s" % (str(e) or repr(e))
        return self._render_template(error=error)

    @http.route('/web/database/duplicate',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def duplicate(self, master_pwd, name, new_name):
        try:
            if not re.match(DBNAME_PATTERN, new_name):
                raise Exception(
                    _('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'
                      ))
            dispatch_rpc('db', 'duplicate_database',
                         [master_pwd, name, new_name])
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database duplication error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)

    @http.route('/web/database/drop',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def drop(self, master_pwd, name):
        try:
            dispatch_rpc('db', 'drop', [master_pwd, name])
            request._cr = None  # dropping a database leads to an unusable cursor
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database deletion error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)

    @http.route('/web/database/backup',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def backup(self, master_pwd, name, backup_format='zip'):
        try:
            odoo.service.db.check_super(master_pwd)
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s.%s" % (name, ts, backup_format)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', content_disposition(filename)),
            ]
            dump_stream = odoo.service.db.dump_db(name, None, backup_format)
            response = werkzeug.wrappers.Response(dump_stream,
                                                  headers=headers,
                                                  direct_passthrough=True)
            return response
        except Exception as e:
            _logger.exception('Database.backup')
            error = "Database backup error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)

    @http.route('/web/database/restore',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def restore(self, master_pwd, backup_file, name, copy=False):
        try:
            data_file = None
            db.check_super(master_pwd)
            with tempfile.NamedTemporaryFile(delete=False) as data_file:
                backup_file.save(data_file)
            db.restore_db(name, data_file.name, str2bool(copy))
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database restore error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)
        finally:
            if data_file:
                os.unlink(data_file.name)

    @http.route('/web/database/change_password',
                type='http',
                auth="none",
                methods=['POST'],
                csrf=False)
    def change_password(self, master_pwd, master_pwd_new):
        try:
            dispatch_rpc('db', 'change_admin_password',
                         [master_pwd, master_pwd_new])
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Master password update error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)

    @http.route('/web/database/list', type='json', auth='none')
    def list(self):
        """
        Used by Mobile application for listing database
        :return: List of databases
        :rtype: list
        """
        return http.db_list()
