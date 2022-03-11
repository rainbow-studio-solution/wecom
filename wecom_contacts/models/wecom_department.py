# -*- coding: utf-8 -*-


from odoo import _, api, fields, models


class WeComDepartment(models.Model):
    _name = "wecom.department"
    _description = "Wecom department"
    _order = "order"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    name = fields.Char(string="Name", copy=False)
    name_en = fields.Char(string="English Name", copy=False)
    department_id = fields.Integer(string="Department ID", copy=False)
    department_leader = fields.Char(string="Department Leader", copy=False)
    # department_leader_ids = fields.One2many("wecom.users","user_id",string="Department Leaders", copy=False)
    parent_id = fields.Many2one(
        "wecom.department",
        "Parent department",
        index=True,
        readonly=False,
    )
    child_ids = fields.One2many(
        "wecom.department", "parent_id", string="Child Departments"
    )
    order = fields.Integer(default=0, string="Order value")
