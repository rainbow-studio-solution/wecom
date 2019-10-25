from odoo import api, models, fields
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _name = 'wizard.wxwork.attendance'
    _description = '企业微信打卡拉取向导'
    _order = 'start_time'

    department_id = fields.Many2one('hr.department', string="部门", related="employee_id.department_id",
                                    readonly=True)
    start_time = fields.Datetime(string="开始时间", default=fields.Datetime.now, required=True)
    end_time = fields.Datetime(string="结束时间", required=True)
    status = fields.Boolean(string="状态",readonly=True)
