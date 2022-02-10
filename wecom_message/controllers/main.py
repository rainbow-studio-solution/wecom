# -*- coding: utf-8 -*-

import base64
import io
import functools
import werkzeug.utils
import odoo
from odoo import api, http, models, fields, SUPERUSER_ID, _
from odoo.modules import get_module_path, get_resource_path
from odoo.http import request
from odoo.addons.web.controllers.main import db_monodb, Binary
from odoo.tools.mimetypes import guess_mimetype


class WxworkBinary(Binary):
    """[summary]
    获取方块Logo
    Args:
        Binary ([type]): [description]
    """

    # @http.route(
    #     [
    #         "/web/binary/wecom_message_logo",
    #         "/wecom_message_logo",
    #         "/wecom_message_logo.png",
    #     ],
    #     type="http",
    #     auth="none",
    #     cors="*",
    # )
    @http.route(
        [
            "/web/binary/wecom_message_logo",
            "/wecom_message_logo",
            "/wecom_message_logo.png",
        ],
        type="http",
        auth="none",
        cors="*",
    )
    def company_wecom_message_web_logo(self, **kw):

        response = (
            request.env["res.company"]
            .sudo()
            .browse(int(kw["company"]))
            .message_app_id.square_logo_url
        )
        return werkzeug.utils.redirect(response)

