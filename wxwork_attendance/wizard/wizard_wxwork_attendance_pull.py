from odoo import api, models, fields
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _name = 'wizard.wxwork.attendance.pull'
    _description = '企业微信打卡拉取向导'
    _order = 'start_time'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
    #                               ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="部门",)
    start_time = fields.Datetime(string="开始时间", required=True)
    end_time = fields.Datetime(string="结束时间", default=fields.Datetime.now, required=True)
    status = fields.Boolean(string="状态", readonly=True)
