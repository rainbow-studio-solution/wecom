# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(Http, self).session_info()
        user = request.env.user
        if self.env.user.has_group('base.group_user'):
            allowed_companies = session_info["user_companies"]["allowed_companies"]
            
            allowed_companies = {
                comp.id: {
                    'id': comp.id,
                    'name': comp.name,
                    'is_wecom_organization': comp.is_wecom_organization,
                    'sequence': comp.sequence,
                } for comp in user.company_ids
            }
            session_info["user_companies"]["allowed_companies"] = allowed_companies
            
        return session_info