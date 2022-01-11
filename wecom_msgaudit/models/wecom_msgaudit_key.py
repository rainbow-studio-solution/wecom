# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError, Warning
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class WeComMsgAuditKey(models.Model):
    _name = "wecom.msgaudit.key"
    _description = "Wecom Session content archive key"
    _order = "publickey_ver"

    name = fields.Char(string="Name", compute="_compute_name")
    app_id = fields.Many2one(
        "wecom.apps",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wecom.apps"].id,
        # domain="[('company_id', '=', company_id)]",
        required=True,
    )
    private_key = fields.Text(string="Private key")
    public_key = fields.Text(string="Public key")
    publickey_ver = fields.Integer(
        string="Public key version", default=1, required=True,
    )

    _sql_constraints = [
        (
            "app_id_ver_uniq",
            "unique (app_id,publickey_ver)",
            _("Key version must be unique !"),
        )
    ]

    @api.depends("app_id", "publickey_ver")
    def _compute_name(self):
        for record in self:
            if record.app_id and record.publickey_ver:
                record.name = "%s/V%s %s" % (
                    record.app_id.name,
                    str(record.publickey_ver),
                    _("Key"),
                )
            elif record.app_id and not record.publickey_ver:
                record.name = "%s/%s" % (record.app_id.name, _("Key"),)
            elif not record.app_id and record.publickey_ver:
                record.name = "V%s %s" % (str(record.publickey_ver), _("Key"),)
            else:
                record.name = ""

    def generate_key(self):
        """
        生成公钥和私钥
        """
        # 获取一个伪随机数生成器
        random_generator = Random.new().read
        # 获取一个rsa算法对应的密钥对生成器实例
        rsa = RSA.generate(1024, random_generator)
        # 生成私钥
        private_pem = rsa.exportKey()
        # 生成公钥
        public_pem = rsa.publickey().exportKey()

        self.private_key = private_pem
        self.public_key = public_pem
        # key = RSA.importKey(self.private_key).exportKey()
        # print(key)
