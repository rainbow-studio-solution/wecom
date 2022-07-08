# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, Warning
from odoo.modules.module import get_module_resource, get_resource_path

import logging
import time
import io
import requests
import json
import base64
import logging
import platform
from PIL import Image

_logger = logging.getLogger(__name__)


class WecomMsgauditTool(models.AbstractModel):
    _name = "wecom.msgaudit.tools"
    _description = "WeCom Session Content Archive Tools"

    # --------------------------------------------------
    # 格式话消息
    # msg_record：消息记录
    # msg_str：消息字符串
    # 注意参数 msg_record，msg_str 不能同时为空
    # --------------------------------------------------

    def format_text_message(
        self, msg_record=False, msg_str=None, is_mixed_message=False
    ):
        """
        格式化文本消息
        """
        content_dic = {}
        if msg_record:
            content_dic = eval(msg_record.text)
        else:
            content_dic = eval(msg_str)

        if is_mixed_message:
            content = (
                """
            <div class="card mt-1" style="width: 54rem;"><div class="card-body"><p class="card-text">%s</p></div></div>
            """
                % content_dic["content"]
            )
        else:
            content = "<p class='text-wrap'>%s</p>" % content_dic["content"]

        return {
            "formatted": True,
            "content": content,
        }

    def format_image_message(
        self,
        msg_record=False,
        msg_str=None,
        mixed_message=False,
        media_file_seq=0,
        is_mixed_message=False,
    ):
        """
        格式化图片消息
        """
        content = ""
        get_param = self.env["ir.config_parameter"].sudo().get_param
        content_dic = {}
        company = self.env.user.company_id
        formatted = False
        if msg_record:
            company = msg_record.company_id
            content_dic = eval(msg_record.image)
            msgid = msg_record.msgid
            msgtime = msg_record.msgtime
        elif mixed_message:
            company = mixed_message.company_id
            msgid = "%s_%s" % (mixed_message.msgid, media_file_seq)
            msgtime = mixed_message.msgtime
            content_dic = eval(msg_str)
        else:
            content_dic = eval(msg_str)

        corpid = company.corpid
        secret = company.msgaudit_app_id.secret
        private_keys = company.msgaudit_app_id.private_keys
        key_list = []
        for key in private_keys:
            key_dic = {
                "publickey_ver": key.publickey_ver,
                "private_key": key.private_key,
            }
            key_list.append(key_dic)

        try:
            mediadata_url = get_param("wecom.msgaudit.msgaudit_sdk_url") + get_param(
                "wecom.msgaudit.msgaudit_mediadata_url"
            )
            proxy = True if get_param("wecom.msgaudit_sdk_proxy") == "True" else False

            headers = {"content-type": "application/json"}
            original_file_size = content_dic["filesize"]  # 图片原始大小
            target_file_size = (
                int(get_param("wecom.msgaudit.chatdata_img_max_size")) * 1024
            )  # 图片最大大小，超过此大小，进行压缩

            body = {
                "seq": 0,
                "sdkfileid": content_dic["sdkfileid"],
                "corpid": corpid,
                "secret": secret,
                "private_keys": key_list,
                "target_file_size": target_file_size,
                "original_file_size": original_file_size,
                "msgtype": "image",
            }
            if proxy:
                body.update(
                    {"proxy": mediadata_url, "paswd": "odoo:odoo",}
                )
            response = requests.get(
                mediadata_url, data=json.dumps(body), headers=headers, timeout=None
            )
            res = response.json()

            if res["code"] == 0:
                mediadata = res["data"]
                image = "data:image/png;base64,%s" % mediadata
                use_physical_path_storage = (
                    get_param("wecom.msgaudit.use_physical_path_storage") == "True"
                )
                check_image_result = self.check_media_file_or_store(
                    mediadata,
                    store=use_physical_path_storage,
                    msgtype="image",
                    msgid=msgid,
                    msgtime=msgtime,
                )  # 校验图片和存储图片

                if check_image_result["image"]["verify"]:
                    formatted = True
                else:
                    formatted = False

                if use_physical_path_storage and check_image_result["image"]["verify"]:
                    image = "/wecom_msgaudit/static/media%s/%s" % (
                        check_image_result["image"]["path"],
                        check_image_result["image"]["file"],
                    )  # 使用存储路径的图片

                if is_mixed_message:
                    content = """
<div class="card mt-1" style="width: 54rem;">
    <img src="%s" class="card-img-top" data-toggle="modal" data-target="#modal_%s" title="%s"/>
</div>
<div class="modal fade" id="modal_%s" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h4 class="modal-title">%s</h4>
                <button type="button" data-dismiss="modal" aria-label="Close" tabindex="-1" class="close">×</button>    
            </div>
            <div class="modal-body">
                <img src="%s" class="img-fluid w-100 h-auto"/>
            </div>
        </div>
    </div>
</div>""" % (
                        image,
                        msgid,
                        _("Click to view"),
                        msgid,
                        msgid,
                        image,
                    )
                else:
                    content = "<img src='%s' class='img-fluid w-100'>" % image
            elif res["code"] == 10010:
                formatted = True
                content = "<span class='card-text bg-warning text-white'>%s</span>" % _(
                    "The current message record has exceeded 3 days and cannot be formatted."
                )
                if is_mixed_message:
                    content = "<p class='card bg-warning text-white'>%s</p>" % _(
                        "The current message record has exceeded 3 days and cannot be formatted."
                    )
            else:
                _logger.warning(
                    _(
                        "Request error, error code:%s, error description:%s, suggestion:%s"
                    )
                    % (res["code"], res["description"], res["suggestion"])
                )

        except Exception as e:
            formatted = False
            _logger.exception("Format picture exception: %s" % e)
            if "code" in str(e):
                raise UserError(
                    _(
                        "Request error, error code:%s, error description:%s, suggestion:%s"
                    )
                    % (res["code"], res["description"], res["suggestion"])
                )
            elif "HTTPConnectionPool" in str(e):
                raise UserError(_("API interface not started!"))
            else:
                raise UserError(_("Unknown error:%s") % e)
        finally:
            return {
                "formatted": formatted,
                "content": content,
            }

    def format_link_message(
        self, msg_record=False, msg_str=None, is_mixed_message=False
    ):
        """
        格式化链接消息
        """
        content_dic = {}
        if msg_record:
            content_dic = eval(msg_record.link)
        else:
            content_dic = eval(msg_str)
        content = """
        <div class="card mt-1" %s>
            <div class="row no-gutters">
                <div class="col-md-4">
                    <img src="%s" alt="%s">
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <h5 class="card-title">%s</h5>
                        <p class="card-text">%s</p>
                        <p class="card-text"><small class="text-muted">
                            <a href="%s" target="_blank">%s</a>
                        </small></p>
                    </div>
                </div>
            </div>
        </div>
        """ % (
            "style='width: 54rem;'" if is_mixed_message else "",
            content_dic["image_url"],
            content_dic["title"],
            content_dic["title"],
            content_dic["description"],
            content_dic["link_url"],
            _("Open link"),
        )

        return {
            "formatted": True,
            "content": content,
        }

    def format_mixed_message(self, msg_record=False, msg_str=None):
        """
        格式化混合消息
        """
        content_dic = {}
        if msg_record:
            content_dic = eval(msg_record.mixed)
            company = msg_record.company_id
        else:
            content_dic = eval(msg_str)
        content = ""
        for index, item in enumerate(content_dic["item"]):
            item_format = getattr(self, "format_%s_message" % item["type"])
            item_content = item_format(
                msg_record=False, msg_str=item["content"], is_mixed_message=True
            )

            if item["type"] == "image":
                item_content = item_format(
                    msg_record=False,
                    msg_str=item["content"],
                    mixed_message=msg_record,
                    media_file_seq=index,
                    is_mixed_message=True,
                )
            if item_content["formatted"]:
                content += item_content["content"]
        return {
            "formatted": True,
            "content": content,
        }

    # --------------------------------------------------
    # 其他工具
    # --------------------------------------------------
    def check_media_file_or_store(
        self, data_image, store=False, msgid=None, msgtype=None, msgtime=None
    ):
        """
        校验媒体文件，根据给定的条件存储媒体文件

        data_image: data:image/png;base64,...................
        msgid: 消息id
        msgtype: 消息类型
        msgtime: UTC时间
        store: 是否存储到物理路径
        path: 存储到物理路径的路径
        """
        result = {msgtype: {}}
        if store:
            media_sub_path = "/%s/%s" % (msgtype, msgtime.strftime("%Y%m%d"),)
            media_path = get_module_resource("wecom_msgaudit", "static", "media",)
            media_full_path = self.env["wecomapi.tools.file"].path_is_exists(
                media_path, media_sub_path
            )

        try:
            if msgtype == "image":
                # 检查文件是否能正常打开
                image = Image.open(io.BytesIO(base64.b64decode(data_image)))
                image.verify()  # 检查文件完整性
                image.close()
                result[msgtype].update(
                    {"verify": True,}
                )
                if store:
                    media_file_name = "%s.png" % msgid
                    media_file_full_path = "%s%s" % (media_full_path, media_file_name)
                    with open(media_file_full_path, "wb") as f:
                        f.write(base64.b64decode(data_image))
                        result[msgtype].update(
                            {"path": media_sub_path, "file": media_file_name,}
                        )
                else:
                    result[msgtype].update({"file": data_image})

        except Exception as e:
            _logger.warning("Exception: %s" % e)
            result[msgtype].update(
                {"verify": False,}
            )
        finally:
            return result

    def verify_img(sefl, img_str):
        """
        校验图片
        路径存储 img_str: /wecom_msgaudit/static/media/image/20220708/16307707961615879262_1657257256215.png
        base64 img_str:data:image/png;base64,..................
        """
        if img_str[0] == "/":
            img_str = img_str[1:]  # 去掉第一个 /

            resource_path = [r for r in img_str.split("/")]
            module_name = resource_path[0]

            resource_path = img_str.replace(module_name, "")[1:]  # 去掉第一个 /
            img_path = get_module_resource(module_name, resource_path)
            try:
                image = Image.open(img_path)  # 检查文件是否能正常打开
                image.verify()  # 检查文件完整性
                image.close()
            except:
                return False
            else:
                return True
        else:
            try:
                image_data = img_str.split(",")[-1]
                image = Image.open(
                    io.BytesIO(base64.b64decode(image_data))
                )  # 检查文件是否能正常打开
                image.verify()  # 检查文件完整性
                image.close()
            except:
                return False
            else:
                return True
