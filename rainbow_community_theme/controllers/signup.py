# -*- coding: utf-8 -*-

import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class AuthSignupHome(Home):
    @http.route('/web/signup',
                type='http',
                auth='public',
                website=True,
                sitemap=False)
    def rainbow_web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    User = request.env['res.users']
                    user_sudo = User.sudo().search(
                        User._get_login_domain(qcontext.get('login')),
                        order=User._get_login_order(),
                        limit=1)
                    template = request.env.ref(
                        'auth_signup.mail_template_user_signup_account_created',
                        raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode(
                                {'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([
                    ("login", "=", qcontext.get("login"))
                ]):
                    qcontext["error"] = _(
                        "Another user is already registered using this email address."
                    )
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        module = request.env['ir.module.module']
        module_check = module.sudo().check_module_installed('website')
        if module_check:
            response = request.render('auth_signup.signup', qcontext)
        else:
            response = request.render('rainbow_community_theme.signup_layout',
                                      qcontext)

        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/reset_password',
                type='http',
                auth='public',
                website=True,
                sitemap=False)
    def rainbow_web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get(
                'reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login,
                        request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _(
                        "An email has been sent with credentials to reset your password"
                    )
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        module = request.env['ir.module.module']
        module_check = module.sudo().check_module_installed('website')
        if module_check:
            response = request.render('auth_signup.reset_password', qcontext)
        else:
            response = request.render(
                'rainbow_community_theme.reset_password_layout', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response