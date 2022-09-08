# -*- coding: utf-8 -*-

import time
import logging
from lxml import etree
from odoo import api, fields, models, _, Command, tools

_logger = logging.getLogger(__name__)

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    # _order = "wecom_user_order"

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
    # private_email = fields.Char(string="Private Email", groups="hr.group_hr_user",store=True,)
    
    is_wecom_organization = fields.Boolean(
        related="company_id.is_wecom_organization", readonly=False
    )
    wecom_user = fields.Many2one('wecom.user',required=True)
    wecom_userid = fields.Char(string="WeCom User Id", related="wecom_user.userid",)
    wecom_openid = fields.Char(string="WeCom Open Userid", related="wecom_user.open_userid",)
    alias = fields.Char(string="Alias", readonly=True, related="wecom_user.alias")
    english_name = fields.Char(string="English Name", readonly=True,related="wecom_user.english_name")

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )
    use_system_avatar = fields.Boolean(readonly=True, default=True)
    avatar = fields.Char(string="Avatar",related="wecom_user.avatar")

    qr_code = fields.Char(
        string="Personal QR code",
        readonly=True,related="wecom_user.qr_code"
    )
    # wecom_user_order = fields.Char("WeCom user sort", default="0", readonly=True,)
    is_wecom_user = fields.Boolean(
        string="WeCom employees", readonly=True, default=False,
    )

    def unbind_wecom_member(self):
        """
        解除绑定企业微信成员
        """
        self.write(
            {"is_wecom_user": False, "wecom_userid": None, "qr_code": None,}
        )
        if self.user_id:
            # 关联了User
            self.user_id.write(
                {"is_wecom_user": False, "wecom_userid": None, "qr_code": None,}
            )

    # ------------------------------------------------------------
    # 从员工生成用户
    # ------------------------------------------------------------
    def create_user_from_employee(self):
        """
        从员工生成用户
        :return:
        """
        send_mail = self.env.context.get("send_mail")
        send_message = self.env.context.get("send_message")
        if send_mail is None:
            send_mail = True
        if send_message is None:
            send_message = True

        for employee in self:
            params = {}
            if employee.wecom_openid is False:
                employee.wecom_user.get_open_userid()

            try:
                res_user_id = self.env["res.users"]._get_or_create_user_by_wecom_userid(
                    employee, send_mail, send_message
                )
            except Exception as e:
                message = _(
                    "Failed to copy employee [%s] as system user, reason:%s"
                ) % (employee.name, repr(e),)
                _logger.warning(message)
                params = {
                    "title": _("Fail"),
                    "message": message,
                    "sticky": True,  # 延时关闭
                    "className": "bg-danger",
                    "type": "danger",
                }
            else:
                message = _("Successfully copied employee [%s] as system user") % (
                    employee.name
                )
                params = {
                    "title": _("Success"),
                    "message": message,
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                    "type": "success",
                    "next": {"type": "ir.actions.client", "tag": "reload",},  # 刷新窗体
                }
            finally:
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": params,
                }
                return action

    
    # ------------------------------------------------------------
    # 从 模型 wecom.user 同步员工
    # ------------------------------------------------------------
    @api.model
    def sync_wecom_user(self):
        """
        同步企微成员
        """
        start_time = time.time()
        tasks = {}
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company

        wecom_users = self.env['wecom.user'].search([('company_id','=',company.id)])
        try:
            for wecom_user in wecom_users:
                # 从企业微信同步员工
                employee = self.search([('wecom_userid','=',wecom_user.userid)])
                if not employee:
                    employee = self.search([('wecom_openid','=',wecom_user.open_userid)])

                if not employee:
                    employee = self.sudo().create({
                        'company_id':company.id,
                        'name':wecom_user.name,
                        'work_phone':None, # 避免使用公司的电话
                        'wecom_user':wecom_user.id,
                        'is_wecom_user':True,
                    })
                else:
                    employee.sudo().write({
                        'name':wecom_user.name,
                    })
        except Exception as e:
            end_time = time.time()
            tasks = {
                "state": False,
                "time": end_time - start_time,
                "msg": str(e),
            }
        else:
            end_time = time.time()
            tasks = {
                "state": True,
                "time": end_time - start_time,
                "msg": _("Successfully synchronized wecom employees"),
            }
        finally:
            return tasks
