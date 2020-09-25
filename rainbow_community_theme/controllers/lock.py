# -*- coding: utf-8 -*-

import werkzeug
from werkzeug.urls import url_decode, iri_to_uri

import odoo
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request

db_monodb = http.db_monodb

def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)

def ensure_db(redirect='/web/database/selector'):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db

class LockController(http.Controller):
    def _lock_redirect(self, uid, redirect=None):
        return redirect if redirect else '/web'

    @http.route('/web/lock', type='http', auth='none')
    def web_lock(self, redirect=None, **kw):
        print("lock")
        print(request.session.uid)
        ensure_db()
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        else:
            return request.render('rainbow_community_theme.lock_layout')

        # try:
        #     context = request.env['ir.http'].webclient_rendering_context()
        #     response = request.render('rainbow_community_theme.lock', qcontext=context)
        #     # response.headers['X-Frame-Options'] = 'DENY'
        #     return response
        # except AccessError:
        #     return werkzeug.utils.redirect('/web/login?error=access')