# -*- coding: utf-8 -*-

import os
import base64
import platform
import json
import requests
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, Warning

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode
from odoo.addons.wxwork_api.tools.wx_tools import WxTools
from requests_toolbelt import MultipartEncoder


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
    img_file_filename = fields.Char()

    voice_file = fields.Binary(string="Voice file", help="格式支持amr，文件大小应在 5B ~ 2MB 之间")
    voice_file_filename = fields.Char()

    video_file = fields.Binary(
        string="Video file", help="不超过10M, 文件格式:  mp4,文件大小应在 5B ~ 10MB 之间"
    )
    video_file_filename = fields.Char()

    file_file = fields.Binary(string="Ordinary file", help="文件大小不超过20M")
    file_file_filename = fields.Char()

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
            file_extension = os.path.splitext(self.img_file_filename)[1]
            if file_extension not in [".jpg", ".png"]:
                raise ValidationError(_("Allowed file formats are jpg or png"))
            file_size = int(len(self.img_file) * 3 / 4)  # 以字节为单位计算file_size
            if file_size >> 2 * 1024 * 1024 < 5:
                raise ValidationError(_("Picture file size must be between 5B and 2MB"))

    @api.onchange("voice_file")
    def _onchange_voice_file(self):
        if self.voice_file:
            file_extension = os.path.splitext(self.voice_file_filename)[1]
            if file_extension not in [".arm"]:
                raise ValidationError(_("Allowed file formats are arm"))
            file_size = int(len(self.voice_file) * 3 / 4)  # 以字节为单位计算file_size
            if file_size >> 2 * 1024 * 1024 < 5:
                raise ValidationError(_("Voice file size must be between 5B and 2MB"))

    @api.onchange("video_file")
    def _onchange_video_file(self):
        if self.video_file:
            file_extension = os.path.splitext(self.video_file_filename)[1]
            if file_extension not in [".mp4"]:
                raise ValidationError(_("Allowed file formats are mp4"))
            file_size = int(len(self.video_file) * 3 / 4)  # 以字节为单位计算file_size
            if file_size >> 10 * 1024 * 1024 < 5:
                raise ValidationError(_("Video file size must be between 5B and 2MB"))

    @api.onchange("file_file")
    def _onchange_file_file(self):
        if self.file_file:
            file_size = int(len(self.file_file) * 3 / 4)  # 以字节为单位计算file_size
            if file_size >> 20 * 1024 * 1024 < 5:
                raise ValidationError(
                    _("Ordinary file size must be between 5B and 2MB")
                )

    def upload_media(self):
        if self.img_file or self.voice_file or self.video_file or self.file_file:
            sys_params = self.env["ir.config_parameter"].sudo()
            corpid = sys_params.get_param("wxwork.corpid")
            secret = sys_params.get_param("wxwork.material_secret")
            wxapi = CorpApi(corpid, secret)
            img_file_extension = os.path.splitext(self.img_file_filename)[1]
            file_path = self._check_file_path(
                self.img_file, "material", self.img_file_filename
            )
            print(file_path)
            if self.temporary:
                # 上传临时素材
                pass
            else:
                """
                上传图片得到图片URL，该URL永久有效
                返回的图片URL，仅能用于图文消息正文中的图片展示，或者给客户发送欢迎语等；若用于非企业微信环境下的页面，图片将被屏蔽。
                每个企业每天最多可上传100张图片
                """

                try:
                    # access_token = wxapi.getAccessToken()
                    # url = (
                    #     "https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg?access_token=%s"
                    #     % (access_token)
                    # )
                    files = {"media": open(file_path, "rb")}
                    # response = requests.post(url=url, files=files)
                    # res = json.loads(response.text)
                    # print(res)
                    # if res["errcode"] == 0:
                    #     self.img_url = res["url"]
                    response = wxapi.httpPostFile(
                        CORP_API_TYPE["MEDIA_UPLOADIMG"], files,
                    )

                    if response["errcode"] == 0:
                        self.img_url = response["url"]
                except ApiException as e:
                    raise Warning(
                        _(
                            "Upload error! \nError code: %s, \nError description:%s, \nError details:%s"
                        )
                        % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                    )
        else:
            raise UserError(_("Please upload files!"))

    @api.model
    def create(self, vals):
        material = super(WxWorkMaterial, self).create(vals)
        return material

    def write(self, vals):
        res = super(WxWorkMaterial, self).write(vals)
        return res

    @api.model
    def _check_file_path(self, file, subpath, filename):
        sys_params = self.env["ir.config_parameter"].sudo()
        path = sys_params.get_param("wxwork.img_path")
        file_path = self.env["wxwork.tools"].path_is_exists(path, subpath)
        full_path = file_path + filename

        if not os.path.exists(full_path):
            try:
                with open(full_path, "wb") as fp:
                    fp.write(base64.b64decode(file))
                    fp.close()
                    # return full_path
            except IOError:
                raise UserError(_("file_write writing %s!"), full_path)

        if platform.system() == "Windows":
            full_path = full_path.replace("/", "\\")

        return full_path

    # def unlink(self):
    #     resources = self.mapped('resource_id')
    #     super(WxWorkMaterial, self).unlink()
    #     return resources.unlink()

