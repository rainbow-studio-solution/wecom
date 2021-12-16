from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )

    # 通讯录
    contacts_app_id = fields.Many2one(
        related="company_id.contacts_app_id", readonly=False
    )

    contacts_secret = fields.Char(related="contacts_app_id.secret", readonly=False)

    contacts_access_token = fields.Char(related="contacts_app_id.access_token")

    contacts_app_config_ids = fields.One2many(
        # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
        related="contacts_app_id.app_config_ids",
        # domain="[('company_id', '=', company_id),('app_id', '=', contacts_app_id)]",
        readonly=False,
    )

    contacts_app_callback_service_ids = fields.One2many(
        related="contacts_app_id.app_callback_service_ids", readonly=False
    )

    # contacts_auto_sync_hr_enabled = fields.Boolean(
    #     # related="company_id.contacts_auto_sync_hr_enabled", readonly=False
    #     related="contacts_app_id.access_token",
    #     app_config_parameter="wecom.resources_path",
    # )

    # contacts_sync_hr_department_id = fields.Integer(
    #     related="company_id.contacts_sync_hr_department_id", readonly=False
    # )

    # contacts_edit_enabled = fields.Boolean(
    #     related="company_id.contacts_edit_enabled", readonly=False
    # )

    # contacts_sync_user_enabled = fields.Boolean(
    #     related="company_id.contacts_sync_user_enabled", readonly=False
    # )

    # contacts_use_system_default_avatar = fields.Boolean(
    #     related="company_id.contacts_use_system_default_avatar", readonly=False
    # )
    # contacts_update_avatar_every_time_sync = fields.Boolean(
    #     related="company_id.contacts_update_avatar_every_time_sync", readonly=False
    # )

    # @api.onchange("contacts_use_system_default_avatar")
    # def _onchange_contacts_use_system_default_avatar(self):
    #     if self.contacts_use_system_default_avatar:
    #         self.contacts_update_avatar_every_time_sync = False

    # # JS API
    # corp_jsapi_ticket = fields.Char(
    #     "Enterprise JS API Ticket",
    #     related="company_id.corp_jsapi_ticket",
    #     readonly=True,
    # )

    # agent_jsapi_ticket = fields.Char(
    #     "Application JS API Ticket",
    #     related="company_id.agent_jsapi_ticket",
    #     readonly=True,
    # )

    # jsapi_debug = fields.Boolean(
    #     "JS API Debug mode", config_parameter="wecom.jsapi_debug", default=False,
    # )

    # js_api_list = fields.Char(
    #     "JS API Inertface List", related="company_id.js_api_list", readonly=False,
    # )

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     ir_config = self.env["ir.config_parameter"].sudo()

    #     debug_enabled = (
    #         True if ir_config.get_param("wecom.debug_enabled") == "True" else False
    #     )

    #     res.update(debug_enabled=debug_enabled,)
    #     return res

    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     ir_config = self.env["ir.config_parameter"].sudo()
    #     ir_config.set_param("wecom.debug_enabled", self.debug_enabled or "False")

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_parameters()

    def generate_service(self):
        """
        生成服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_service()
