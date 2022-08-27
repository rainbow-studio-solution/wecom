# -*- coding: utf-8 -*-


import logging
from lxml import etree
from odoo import api, fields, models, _, Command, tools

_logger = logging.getLogger(__name__)

WECOM_USER_MAPPING_ODOO_EMPLOYEE = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称;
    "Department": "department_ids",  # 成员部门列表，仅返回该应用有查看权限的部门id
    "MainDepartment": "department_id",  # 主部门
    "IsLeaderInDept": "",  # 表示所在部门是否为上级，0-否，1-是，顺序与Department字段的部门逐一对应
    "DirectLeader": "",  # 直属上级
    "Mobile": "mobile_phone",  # 手机号码
    "Position": "job_title",  # 职位信息
    "Gender": "gender",  # 企微性别：0表示未定义，1表示男性，2表示女性；odoo性别：male为男性，female为女性，other为其他
    "Email": "work_email",  # 邮箱;
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Avatar": "avatar",  # 头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可。
    "Alias": "alias",  # 成员别名
    "Telephone": "work_phone",  # 座机;
    "Address": "work_location",  # 地址;
    "ExtAttr": {
        "Type": "",  # 扩展属性类型: 0-本文 1-网页
        "Text": "",  # 文本属性类型，扩展属性类型为0时填写
        "Value": "",  # 文本属性内容
        "Web": "",  # 网页类型属性，扩展属性类型为1时填写
        "Title": "",  # 网页的展示标题
        "Url": "",  # 网页的url
    },  # 扩展属性;
}


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    _order = "wecom_user_order"

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

    wecom_user_info = fields.Text(string="WeCom user info", readonly=True, default="{}")
    wecom_userid = fields.Char(string="WeCom User Id", related="wecom_user.userid",)
    wecom_openid = fields.Char(string="WeCom Open Userid", related="wecom_user.open_userid",)
    alias = fields.Char(string="Alias", readonly=True,)
    english_name = fields.Char(string="English Name", readonly=True,)

    department_ids = fields.Many2many(
        "hr.department", string="Multiple departments", readonly=True,
    )
    use_system_avatar = fields.Boolean(readonly=True, default=True)
    avatar = fields.Char(string="Avatar")

    qr_code = fields.Char(
        string="Personal QR code",
        help="Personal QR code, Scan can be added as external contact",
        readonly=True,
    )
    wecom_user_order = fields.Char("WeCom user sort", default="0", readonly=True,)
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
                employee.get_wecom_openid()

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
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
            print("1",company)
        else:
            company = self.env.company
            print("2",company)
        
        # if not company:
        #     company = self.env.company
        

        return {}