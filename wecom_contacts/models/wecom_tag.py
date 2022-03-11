# -*- coding: utf-8 -*-


from odoo import _, api, fields, models


class WeComTag(models.Model):
    _name = "wecom.tag"
    _description = "Wecom tag"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    name = fields.Char(string="Name", copy=False)
    tag_name = fields.Char(string="Tag name", copy=False)
    tag_id = fields.Integer(string="Tag ID", copy=False)
    userlist = fields.Char(string="User lsit", default=[], copy=False)
    # user_ids = fields.One2many("wecom.users","user_id",string="Users", copy=False)
    partylist = fields.Char(string="Party lsit", default=[], copy=False)
    # department_ids = fields.One2many("wecom.department","department_id",string="Departments", copy=False)
