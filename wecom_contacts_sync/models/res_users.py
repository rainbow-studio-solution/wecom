# -*- coding: utf-8 -*-

import logging
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
from lxml import etree
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)



class User(models.Model):
    _inherit = ["res.users"]

    # employee_id = fields.Many2one(
    #     "hr.employee",
    #     string="Company employee",
    #     compute="_compute_company_employee",
    #     search="_search_company_employee",
    #     store=True,
    # )  # 变更用户类型时，需要绑定用户，避免出现“创建员工”的按钮，故 store=True

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
    # 故重写了 将  private_email = address_home_id.email 修改为 private_email=employee_id.private_email
    # 故重写了 SELF_WRITEABLE_FIELDS
    # ----------------------------------------------------------------------------------

    # private_email = fields.Char(related='employee_id.private_email', string="Private Email")

    # wecom_userid = fields.Char(string="WeCom User Id", related="wecom_user.userid",)
    # wecom_openid = fields.Char(string="WeCom Open Userid", related="wecom_user.open_userid",)
    # qr_code = fields.Char(
    #     string="Personal QR code",
    #     readonly=True,related="wecom_user.qr_code"
    # )
    # is_wecom_user = fields.Boolean(
    #     string="WeCom User", readonly=True, default=False,
    # )

    def _get_or_create_user_by_wecom_userid(self, object, send_mail, send_message):
        """
        通过企微用户id获取odoo用户
        """
        login = tools.ustr(object.wecom_userid)
        self.env.cr.execute(
            "SELECT id, active FROM res_users WHERE lower(login)=%s", (login,)
        )
        res = self.env.cr.fetchone()
        if res:
            if res[1]:
                return res[0]
        else:
            group_portal_id = self.env["ir.model.data"]._xmlid_to_res_id(
                "base.group_portal"
            )  # 门户用户组
            SudoUser = self.sudo()
            values = {
                "name": object.name,
                "login": login,
                "notification_type": "inbox",
                "groups_id": [(6, 0, [group_portal_id])],
                "share": False,
                "active": object.active,
                "image_1920": object.image_1920,
                "password": self.env["wecom.tools"].random_passwd(8),
                "company_ids": [(6, 0, [object.company_id.id])],
                "company_id": object.company_id.id,
                "employee_ids": [(6, 0, [object.id])],
                "employee_id": object.id,
                "lang": self.env.lang,
                "company_id": object.company_id.id,
                # 以下为企业微信字段
                "wecom_user": object.wecom_user.id,
                "wecom_userid": object.wecom_userid.lower(),
                "wecom_openid": object.wecom_openid,
                "is_wecom_user": object.is_wecom_user,
                "qr_code": object.qr_code,
            }            

            """
            MailThread功能可以通过上下文键进行一定程度的控制:

            -'mail_create_nosubscribe':在create或message_post上,不要订阅记录线程的uid
            -'mail_create_nolog'：在创建时，不要记录自动的“<Document>“创建”消息
            -'mail_notrack'：在创建和写入时，不要执行值跟踪创建消息
            -'tracking_disable'：在创建和写入时，不执行邮件线程功能（自动订阅、跟踪、发布等）
            -'mail_notify_force_send': 如果要发送的电子邮件通知少于50封,直接发送,而不是使用队列;默认情况下为True
            """
            user = SudoUser.with_context(
                    mail_create_nosubscribe=True,
                    mail_create_nolog=True,
                    mail_notrack=True,
                    tracking_disable=True,
                    send_mail=send_mail,
                    send_message=send_message,
                ).create(values)
            print(user.partner_id)
            # 关联公司
            user.partner_id.write({
                "company_id": object.company_id.id,
                "parent_id": object.company_id.partner_id.id,
            })
            return user.id
            # return SudoUser.with_context(send_mail=send_mail).create(values).id

    @api.model_create_multi
    def create(self, vals_list):
        """
        重写以自动邀请用户注册
        send_mail: true 表示发送邀请邮件, false 表示不发送邀请邮件
        批量创建用户时，建议 send_mail=False
        """
        users = super(User, self).create(vals_list)

        if not self.env.context.get("no_reset_password") and self.env.context.get(
            "send_mail"
        ):
            users_with_email = users.filtered("email")
            if users_with_email:
                try:
                    users_with_email.with_context(
                        create_user=True
                    ).action_reset_password()
                except MailDeliveryException:
                    users_with_email.partner_id.with_context(
                        create_user=True
                    ).signup_cancel()

        return users

# ------------------------------------------------------------
# 变更用户类型向导
# ------------------------------------------------------------
class ChangeTypeWizard(models.TransientModel):
    _name = "change.type.wizard"
    _description = "Wizard to change user type(WeCom)"

    def _default_user_ids(self):
        user_ids = (
            self._context.get("active_model") == "res.users"
            and self._context.get("active_ids")
            or []
        )
        return [
            (
                0,
                0,
                {"user_id": user.id, "user_login": user.login, "user_name": user.name,},
            )
            for user in self.env["res.users"].browse(user_ids)
        ]

    user_ids = fields.One2many(
        "change.type.user", "wizard_id", string="Users", default=_default_user_ids
    )

    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped("user_ids.user_id"):
            return {"type": "ir.actions.client", "tag": "reload"}
        return {"type": "ir.actions.act_window_close"}


class ChangeTypeUser(models.TransientModel):
    _name = "change.type.user"
    _description = "User, Change Type Wizard"

    wizard_id = fields.Many2one(
        "change.type.wizard", string="Wizard", required=True, ondelete="cascade"
    )

    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="cascade"
    )
    user_login = fields.Char(string="Login account", readonly=True,)
    user_name = fields.Char(string="Login name", readonly=True)
    # 用户类型参见res_group
    new_type = fields.Selection(
        [("1", _("Internal User")), ("9", _("Portal User")), ("10", _("Public User")),],
        string="User Type",
        default="1",
    )

    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError(
                    _(
                        "Before clicking the 'Change User Type' button, you must modify the new user type"
                    )
                )
            if (
                # 排除初始系统自带的用户
                line.user_id.id == 1
                or line.user_id.id == 2
                or line.user_id.id == 3
                or line.user_id.id == 4
                or line.user_id.id == 5
            ):
                pass
            else:
                if line.new_type == "1":
                    try:
                        line.user_id.employee_id = (
                            self.env["hr.employee"].search(
                                [
                                    ("id", "in", line.user_id.employee_ids.ids),
                                    ("company_id", "=", line.user_id.company_id.id),
                                ],
                                limit=1,
                            ),
                        )
                    except Exception as e:
                        print("用户 %s 类型变更错误,错误:%s" % (line.user_id.name, repr(e)))

                line.user_id.write({"groups_id": [(6, 0, line.new_type)]})
        self.write({"new_type": False})
