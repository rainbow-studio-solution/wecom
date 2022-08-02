# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import UserError


class HrMenusWizard(models.TransientModel):
    _name = "hr.menus.wizard"

    # hr_menus_ids = fields.Many2many(
    #     "ir.ui.menu",
    #     string="HR Related Menus",
    #     compute_sudo=True,
    #     compute="_compute_hr_menus",
    # )
    hr_menus_domain = fields.Char(
        default="['&','&','&',('parent_id','=',False),('web_icon', 'ilike', 'hr'),('name', 'not like', 'HRMS'),'|',('active','=',True),('active','=',False)]"
    )
    hr_menus_ids = fields.Many2many(
        "ir.ui.menu",
        string="HR Related Menus",
        store=True,
        # readonly=False,
        # default=lambda self: self.env["ir.ui.menu"].search(
        #     [
        #         "&",
        #         "&",
        #         "&",
        #         ("parent_id", "=", False),
        #         ("web_icon", "ilike", "hr"),
        #         ("name", "not like", "HRMS"),
        #         "|",
        #         ("active", "=", True),
        #         ("active", "=", False),
        #     ]
        # ),
        # compute_sudo=True,
        # compute="_compute_hr_menus"，
        # domain="['&','&','&',('parent_id','=',False),('web_icon', 'ilike', 'hr'),('name', 'not like', 'HRMS'),'|',('active','=',True),('active','=',False)]",
    )
    # compute_sudo=True,domain="['&amp;','&amp;','&amp;',('parent_id','=',False),('web_icon', 'ilike', 'hr'),('name', 'not like', 'HRMS'),'|',('active','=',True),('active','=',False)]",

    def _compute_hr_menus(self):
        for res in self:
            hr_menus_ids = self.env["ir.ui.menu"].search(
                [
                    "&",
                    "&",
                    "&",
                    ("parent_id", "=", False),
                    ("web_icon", "ilike", "hr"),
                    ("name", "not like", "HRMS"),
                    "|",
                    ("active", "=", True),
                    ("active", "=", False),
                ]
            )
            print(hr_menus_ids)
            res.hr_menus_ids = hr_menus_ids