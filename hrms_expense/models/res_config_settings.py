# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    module_hrms_payroll_expense = fields.Boolean(
        string="Reimburse Expenses in Payslip"
    )  # 工资单上的报销,报销工资单中的费用

    module_hrms_expense_extract = fields.Boolean(
        string="Send bills to OCR to generate expenses"
    ) #费用数字化（OCR）,使用OCR和人工智能将收据数字化
