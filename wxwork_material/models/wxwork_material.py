# -*- coding: utf-8 -*-

import os
import base64
import platform
import subprocess
import logging
import time
from pydub import AudioSegment
from datetime import datetime, timedelta
import pytz

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError, Warning

from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode
from requests_toolbelt.multipart.encoder import MultipartEncoder


_logger = logging.getLogger(__name__)

extensions_and_size = {
    "image": {"extensions": [".jpg", ".png"], "size": [5, 2 * 1024 * 1024]},
    "voice": {"extensions": [".amr"], "size": [5, 2 * 1024 * 1024], "duration": 60},
    "video": {"extensions": [".mp4"], "size": [5, 10 * 1024 * 1024]},
    "file": {"extensions": [], "size": [5, 20 * 1024 * 1024]},
}


class WxWorkMaterial(models.Model):
    "Template for sending Enterprise WeChat message"
    _name = "wxwork.material"
    _description = "Enterprise WeChat material"
    _order = "company_id,name"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wxwork_organization', '=', True)]",
        copy=False,
        store=True,
    )
    name = fields.Char("Name", required=True, translate=True,)
    media_type = fields.Selection(
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
    img_url = fields.Char(
        string="Picture URL",
        readonly=True,
        help="The URL of the picture obtained after uploading. Permanently valid.",
        copy=False,
    )
    media_id = fields.Char(
        string="Media file identification",
        readonly=True,
        help="The unique identification obtained after uploading the media file is valid for 3 days",
        copy=False,
    )
    created_at = fields.Datetime(
        string="Upload time",
        readonly=True,
        help="Media file upload timestamp (Beijing time)",
        copy=False,
    )

    media_file = fields.Binary(
        string="Media files",
        help="Picture file size should be between 5B and 2MB;"
        "The voice file format supports AMR, and the file size should be between 5B and 2MB"
        "The video file shall not exceed 10m, the file format: MP4, and the file size shall be between 5B and 10MB"
        "Normal file size shall not exceed 20m",
        required=True,
    )
    media_filename = fields.Char()

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name, company_id)",
            "The material name of each company must be unique !",
        ),
    ]

    @api.onchange("media_type")
    def _onchange_media_type(self):

        if self.media_type != "image":
            self.temporary = True
        else:
            self.temporary = False

    @api.onchange("media_file")
    def _onchange_media_file(self):
        if self.media_file:
            self._check_file_size_and_extension(
                self.media_type, self.media_file, self.media_filename
            )

    def upload_media(self):
        if self.img_url:
            # 存在 上传后得到的永久有效图片URL。
            raise UserError(
                _(
                    "Already uploaded, please do not upload again! You can create a new record to upload the file."
                )
            )
        if self.created_at:
            # 存在 媒体文件上传时间戳(北京时间)
            created_time = self.created_at

            overdue = self.env["wxwork.tools"].cheeck_overdue(created_time, 3)
            if overdue:
                pass
            else:
                raise UserError(
                    _(
                        "The temporary material has not expired, please do not upload it repeatedly."
                    )
                )

        if self.media_file:
            # 存在媒体文件
            sys_params = self.env["ir.config_parameter"].sudo()
            if self.company_id:
                corpid = self.company_id.corpid
                # agentid = self.company_id.material_agentid
                secret = self.company_id.material_secret

                wxapi = CorpApi(corpid, secret)

                file_path = self._check_file_path(
                    self.media_file, "material", self.media_filename
                )

                if self.temporary:
                    """
                    素材上传得到media_id，该media_id仅三天内有效
                    media_id在同一企业内应用之间可以共享
                    """
                    try:
                        multipart_encoder = MultipartEncoder(
                            fields={
                                self.media_filename: (
                                    "file",
                                    open(file_path, "rb"),
                                    "text/plain",
                                )
                            },
                        )
                        headers = {"Content-Type": multipart_encoder.content_type}
                        response = wxapi.httpPostFile(
                            CORP_API_TYPE["MEDIA_UPLOAD"],
                            {"type": self.media_type},
                            multipart_encoder,
                            headers,
                        )

                        if response["errcode"] == 0:
                            self.media_id = response["media_id"]
                            timeStamp = int(response["created_at"])
                            timeArray = time.localtime(timeStamp)
                            self.created_at = time.strftime(
                                "%Y-%m-%d %H:%M:%S", timeArray
                            )
                    except ApiException as e:
                        raise Warning(
                            _(
                                "Failed to upload picture! \nError code: %s, \nError description:%s, \nError details:%s"
                            )
                            % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                        )
                else:
                    """
                    上传图片得到图片URL，该URL永久有效
                    返回的图片URL，仅能用于图文消息正文中的图片展示，或者给客户发送欢迎语等；若用于非企业微信环境下的页面，图片将被屏蔽。
                    每个企业每天最多可上传100张图片
                    """
                    try:
                        # files = {"media": open(file_path, "rb")}
                        multipart_encoder = MultipartEncoder(
                            fields={
                                self.media_filename: (
                                    "file",
                                    open(file_path, "rb"),
                                    "text/plain",
                                )
                            },
                        )
                        headers = {"Content-Type": multipart_encoder.content_type}
                        response = wxapi.httpPostFile(
                            CORP_API_TYPE["MEDIA_UPLOADIMG"],
                            {},
                            multipart_encoder,
                            headers,
                        )

                        if response["errcode"] == 0:
                            self.img_url = response["url"]
                            self.created_at = fields.Datetime.now()
                    except ApiException as e:
                        raise Warning(
                            _(
                                "Failed to upload picture! \nError code: %s, \nError description:%s, \nError details:%s"
                            )
                            % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                        )
            else:
                raise UserError(_("Please upload files!"))

            return self

    @api.model
    def create(self, vals):
        if vals.get("media_type") and vals.get("media_file"):
            # 检查文件的大小和格式，语音文件检查时长
            self._check_file_size_and_extension(
                vals.get("media_type"),
                vals.get("media_file"),
                vals.get("media_filename"),
            )
            # 检查文件路径
            self._check_file_path(
                vals.get("media_file"), "material", vals.get("media_filename")
            )
        material = super(WxWorkMaterial, self).create(vals)
        return material

    def write(self, vals):
        # if vals.get("media_id") or vals.get("img_url"):
        #     raise UserError(
        #         _(
        #             "Already uploaded, please do not upload again! You can create a new record to upload the file."
        #         )
        #     )
        res = super(WxWorkMaterial, self).write(vals)

        if vals.get("media_type") and vals.get("media_file"):
            # 检查文件的大小和格式，语音文件检查时长
            self._check_file_size_and_extension(
                vals.get("media_type"),
                vals.get("media_file"),
                vals.get("media_filename"),
            )
            # 检查文件路径
            self._check_file_path(
                vals.get("media_file"), "material", vals.get("media_filename")
            )
        return res

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if default:
            if not default.get("company_id"):
                pass
        return super(WxWorkMaterial, self).copy(default=default)

    @api.model
    def _check_material_file_expiration(self):
        """[summary]
        检查素材文件是否过期
        Args:
            material ([type]): [description]

        Returns:
            [type]: [description]
        """
        # media_id = ""
        if self.created_at:
            # 有创建日期
            created_time = self.created_at
            MAX_FAIL_TIME = 3

            # 检查是否超过3天
            overdue = self.env["wxwork.tools"].cheeck_overdue(
                created_time, MAX_FAIL_TIME
            )
            if overdue:
                # 临时素材超期，重新上传
                self.upload_media()
                # media_id = self.media_id
        else:
            # 无创建日期，执行第一次上传临时素材
            self.upload_media()
            # media_id = self.media_id
        return self.media_id

    @api.model
    def _check_file_path(self, file, subpath, filename):
        sys_params = self.env["ir.config_parameter"].sudo()
        path = sys_params.get_param("wxwork.img_path")
        if path:
            pass
        else:
            raise UserError(
                _("Enterprise WeChat storage path has not been configured yet!")
            )
        file_path = self.env["wxwork.tools"].path_is_exists(path, subpath)
        full_path = file_path + filename

        if not os.path.exists(full_path):
            try:
                with open(full_path, "wb") as fp:
                    fp.write(base64.b64decode(file))
                    fp.close()
                    # return full_path
            except IOError:
                raise UserError(_("Error saving file to path %s!"), full_path)

        if platform.system() == "Windows":
            full_path = full_path.replace("/", "\\")

        return full_path

    @api.model
    def _check_file_size_and_extension(self, filetype, file, filename):
        file_extension_list = []
        file_size_list = []
        file_extension = os.path.splitext(filename)[1]
        file_size = int(len(file) * 3 / 4)  # 以字节为单位计算file_size

        if filetype == "image":
            file_extension_list = extensions_and_size["image"]["extensions"]
            file_size_list = extensions_and_size["image"]["size"]
        if filetype == "voice":
            file_extension_list = extensions_and_size["voice"]["extensions"]
            file_size_list = extensions_and_size["voice"]["size"]
            # 语音文件先上传到本地文件夹进行时长检查
            file_path = self._check_file_path(file, "material", filename)
            duration, path = self.get_amr_duration(file_path)
            if int(duration) > 60:
                # 语音文件时长超过了60秒,删除mp3文件
                os.remove(os.path.abspath(path))
                raise ValidationError(
                    _("The duration of the voice file exceeds 60 seconds!")
                )

        if filetype == "video":
            file_extension_list = extensions_and_size["video"]["extensions"]
            file_size_list = extensions_and_size["video"]["size"]
        if filetype == "file":
            file_extension_list = extensions_and_size["file"]["extensions"]
            file_size_list = extensions_and_size["file"]["size"]
        if filetype is None:
            raise ValidationError(_("Unknown type of media file!"))

        if len(file_extension_list) > 0 and file_extension not in file_extension_list:
            raise ValidationError(
                _("Allowed file formats are %s")
                % (" or ".join(str(x) for x in file_extension_list))
            )
        # if file_size_list[0] != 0:
        if file_size > file_size_list[1] or file_size_list[1] < file_size_list[0]:
            raise ValidationError(
                _("Media file size must be between %sB and %sMB")
                % (file_size_list[0], file_size_list[1] / 1024 / 1024)
            )
        # elif file_size > file_size_list[1]:
        #     raise ValidationError(
        #         _("Media file size cannot be larger than %sMB")
        #         % (file_size_list[1] / 1024 / 1024)
        #     )

    def get_amr_duration(self, filepath):
        """
        获取.amr语音文件的时长
        """
        path = os.path.split(filepath)[0]
        filename = os.path.split(filepath)[1].split(".")[0]
        mp3_audio_filepath = os.path.join(path, filename + ".mp3")

        mp3_transformat_path = self.amr_transformat_mp3(
            os.path.abspath(filepath), mp3_audio_filepath
        )
        if os.path.exists(mp3_transformat_path):
            mp3_audio = AudioSegment.from_file(
                os.path.abspath(mp3_transformat_path), format="mp3"
            )
            return mp3_audio.duration_seconds, mp3_transformat_path

    @classmethod
    def amr_transformat_mp3(self, amr_path, mp3_path=None):
        path, name = os.path.split(amr_path)
        if name.split(".")[-1] != "amr":
            print("not a amr file")
            return 0
        if mp3_path is None or mp3_path.split(".")[-1] != "mp3":
            mp3_path = os.path.join(path, name + ".mp3")
        error = subprocess.call(["ffmpeg", "-i", amr_path, mp3_path])
        if error:
            _logger.info("[Convert Error]:Convert file-%s to mp3 failed" % amr_path)
            return 0
        return mp3_path

