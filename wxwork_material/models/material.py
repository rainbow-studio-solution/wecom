# -*- coding: utf-8 -*-

import os
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode


class WxWorkMaterial(models.Model):
    "Template for sending Enterprise WeChat message"
    _name = "wxwork.material"
    # _inherit = ["wxwork.message.render.mixin"]
    _description = "Enterprise WeChat material"
    _order = "name"

    name = fields.Char("Name", required=True,)
    type = fields.Selection(
        [
            ("image", "Picture"),
            ("voice", "Voice"),
            ("video", "Video"),
            ("file", "Ordinary file"),
        ],
        string="Media file type",
        required=True,
        default="image",
    )
    temporary = fields.Boolean(string="Temporary material", default=False)
    img_url = fields.Char(string="Picture URL", readonly=True, help="上传后得到的图片URL。永久有效")
    media_id = fields.Char(string="", readonly=True, help="媒体文件上传后获取的唯一标识，3天内有效")
    created_at = fields.Date(
        string="Media file upload timestamp", readonly=True, help="媒体文件上传时间戳"
    )

    img_file = fields.Image(string="Picture file", help="图片文件大小应在 5B ~ 2MB 之间")
    img_filename = fields.Char()

    voice_file = fields.Binary(
        string="Voice", help="格式支持mp3、wma、wav、amr，文件大小不超过5M，语音时长不超过1分钟"
    )
    voice_filename = fields.Char()

    video_file = fields.Binary(
        string="Video", help="不超过20M, 文件格式: rm, rmvb, wmv, avi, mpg, mpeg, mp4"
    )
    video_filename = fields.Char()

    file_file = fields.Binary(string="Ordinary file")
    file_filename = fields.Char()

    @api.onchange("type")
    def _onchange_type(self):
        # addons\adyen_platforms\models\adyen_account.py
        if self.type != "image":
            self.temporary = True
        else:
            self.temporary = False

    @api.onchange("img_file")
    def _onchange_img_file(self):
        if self.img_file:
            file_size = int(len(self.img_file) * 3 / 4)  # 以字节为单位计算file_size
            print(self.img_file, file_size)

    def upload_media(self):
        if self.img_file or self.voice_file or self.video_file or self.file_file:
            pass
        else:
            raise UserError(_("Please upload files!"))

    @api.model
    def create(self, vals):
        material = super(WxWorkMaterial, self).create(vals)
        return material

    def write(self, vals):
        # print("保存1", self.img_file.file_size)
        res = super(WxWorkMaterial, self).write(vals)
        if vals.get("type") and vals.get("type") == "image" and vals.get("img_file"):
            print("保存1")
            self._check_img_file_requirements(
                vals.get("img_file"), vals.get("img_filename")
            )
        return res

    @api.model
    def _check_img_file_requirements(self, content, filename):
        file_extension = os.path.splitext(filename)[1]
        file_size = int(len(content) * 3 / 4)  # 以字节为单位计算file_size
        if file_extension not in [".jpg", ".png"]:
            raise ValidationError(_("Allowed file formats are jpg or png"))
        print(file_size)

    # def unlink(self):
    #     resources = self.mapped('resource_id')
    #     super(WxWorkMaterial, self).unlink()
    #     return resources.unlink()
