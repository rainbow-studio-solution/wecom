# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import config, ormcache, mute_logger

FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class WeComAppConfig(models.Model):
    _name = "wecom.app_config"
    _description = "Wecom Application Configuration"
    _table = "wecom_app_config"
    # _rec_name = "key"
    _order = "id"

    app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wecom.apps"].id,
        # domain="[('company_id', '=', company_id)]",
        required=True,
    )
    name = fields.Char(string="Name", translate=True, required=True, copy=True)
    key = fields.Char(required=True,)
    ttype = fields.Selection(
        selection=FIELD_TYPES, string="Field Type", required=True, copy=True
    )
    value = fields.Text(required=True)
    description = fields.Html(string="Description", translate=True, copy=True)

    _sql_constraints = [
        (
            "app_id_key_uniq",
            "unique (app_id,key)",
            _("The key of each application must be unique !"),
        )
    ]

    @api.model
    def get_param(self, app_id, key, default=False):
        """检索给定key的value

        :param string key: 要检索的参数值的键。
        :param string default: 如果缺少参数，则为默认值。
        :return: 参数的值， 如果不存在，则为 ``default``.
        :rtype: string
        """
        return self._get_param(app_id, key) or default

    def _get_param(self, app_id, key):
        params = self.search_read(
            [("app_id", "=", app_id), ("key", "=", key)],
            fields=["ttype", "value"],
            limit=1,
        )

        value = params[0]["value"]
        ttype = params[0]["ttype"]
        if ttype == "boolean":
            boolean_value = str(value).lower()
            if boolean_value in ["true", "yes", "t", "1"]:
                return True
            elif boolean_value in ["false", "no", "f", "0"]:
                return False
            else:
                return False
        return value if params else None

    @api.model
    def set_param(self, app_id, key, value):
        """设置参数的值。

        :param string key: 要设置的参数值的键。
        :param string value: 要设置的值。
        :return: 参数的上一个值，如果不存在，则为False。
        :rtype: string
        """
        param = self.search([("app_id", "=", app_id), ("key", "=", key)])
        if param:
            old = param.value
            if value is not False and value is not None:
                if str(value) != old:
                    param.write({"value": value})
            else:
                param.unlink()
            return old
        else:
            if value is not False and value is not None:
                self.create({"app_id": app_id, "key": key, "value": value})
            return False

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super(WeComAppConfig, self).create(vals_list)

    def write(self, vals):
        self.clear_caches()
        return super(WeComAppConfig, self).write(vals)

    def unlink(self):
        self.clear_caches()
        return super(WeComAppConfig, self).unlink()
