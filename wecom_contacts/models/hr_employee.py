# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    # ----------------------------------------------------------------------------------
    # 开发人员注意：hr模块中
    # hr.employee.work_email = res.users.email 
    # hr.employee.private_email = res.partner.email 
    # ----------------------------------------------------------------------------------
    # base 模块中
    # res.user.email = res.partner.email 
    # res.user.private_email = res.partner.email 
    # ------------------------------------------
    # hr.employee.create() 方法中 创建hr.employee.work_email时会将 res.users.email更新到hr.employee.work_email
    # res.users.write() 方法中 更新res.users.email时会将 res.users.email更新到hr.employee.work_email
    # ------------------------------------------
    # 故重写了 将  related='address_home_id.email'去掉，并添加 store 属性
    # ----------------------------------------------------------------------------------
    private_email = fields.Char( string="Private Email", groups="hr.group_hr_user",store=True,)