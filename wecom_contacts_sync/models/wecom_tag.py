# -*- coding: utf-8 -*-

import logging
import json
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
import xmltodict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class WecomTag(models.Model):
    _name = "wecom.tag"
    _description = "Wecom tag"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )

    name = fields.Char(string="Name", readonly=True, compute="_compute_name")  # 标签名称
    tagid = fields.Integer(string="Tag ID", readonly=True, default="0",)  # 标签id
    tagname = fields.Char(string="Tag name", readonly=True, default="")  # 标签名称
    userlist = fields.Text(
        string="User list", readonly=True, default="[]"
    )  # 标签中包含的成员列表
    partylist = fields.Text(
        string="Party list", readonly=True, default="[]"
    )  # 标签中包含的部门id列表

    # odoo 字段
    user_ids = fields.Many2many(
        "wecom.user",
        "wecom_user_tag_rel",
        "wecom_tag_id",
        "wecom_user_id",
        string="Members",
    )

    def _compute_name(self):
        for tag in self:
            tag.name = tag.tagname

    # ------------------------------------------------------------
    # 企微标签下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_tags(self):
        """
        下载标签列表
        """
        start_time = time.time()
        company = self.env.context.get("company_id")
        if type(company) == int:
            company = self.env["res.company"].browse(company)
        tasks = []

        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("TAG_GET_LIST")
            )

        except ApiException as ex:
            end_time = time.time()
            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=False
            )
            tasks = [
                {
                    "name": "download_tag_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(ex),
                }
            ]
        except Exception as e:
            end_time = time.time()

            tasks = [
                {
                    "name": "download_tag_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": str(e),
                }
            ]
        else:
            wecom_tags = response["taglist"]  # 列表类型数据

            # 下载标签
            for wecom_tag in wecom_tags:
                download_tag_result = self.download_tag(company, wecom_tag)
                if download_tag_result:
                    for r in download_tag_result:
                        tasks.append(r)  # 加入 下载标签失败结果
            end_time = time.time()
            task = {
                "name": "download_tag_data",
                "state": True,
                "time": end_time - start_time,
                "msg": _("Tag list downloaded successfully."),
            }
            tasks.append(task)
        finally:
            return tasks  # 返回结果

    def download_tag(self, company, wecom_tag):
        """
        下载标签
        """
        tag = self.sudo().search(
            [("tagid", "=", wecom_tag["tagid"]), ("company_id", "=", company.id),],
            limit=1,
        )
        result = {}
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )

            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_GET_MEMBER"
                ),
                {"tagid": str(wecom_tag["tagid"])},
            )
            response["userlist"] = [user["userid"] for user in response["userlist"]]
            wecom_tag.update(
                {
                    "userlist": self.env["wecom.tools"].check_dictionary_keywords(
                        response, "userlist"
                    ),
                    "partylist": self.env["wecom.tools"].check_dictionary_keywords(
                        response, "partylist"
                    ),
                }
            )

        except ApiException as ex:
            result = _(
                "Wecom API acquisition company[%s]'s tag [id:%s] member failed, error details: %s"
            ) % (company.name, wecom_tag["tagid"], str(ex))
            _logger.warning(result)
        except Exception as e:
            result = _(
                "Wecom API acquisition company[%s]'s tag [id:%s] member failed, error details: %s"
            ) % (company.name, wecom_tag["tagid"], str(e))
            _logger.warning(result)
        else:
            for key in wecom_tag.keys():
                if type(wecom_tag[key]) in (list, dict) and wecom_tag[key]:
                    json_str = json.dumps(
                        wecom_tag[key],
                        sort_keys=False,
                        indent=2,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    wecom_tag[key] = json_str
            if not tag:
                result = self.create_tag(company, tag, wecom_tag)
            else:
                result = self.update_tag(company, tag, wecom_tag)
        finally:
            return result

    def create_tag(self, company, tag, wecom_tag):
        """
        创建标签
        """
        try:
            tag.create(
                {
                    "tagname": wecom_tag["tagname"],
                    "tagid": wecom_tag["tagid"],
                    "userlist": wecom_tag["userlist"],
                    "partylist": wecom_tag["partylist"],
                    "company_id": company.id,
                }
            )
        except Exception as e:
            result = _("Error creating company [%s]'s tag [%s], error reason: %s") % (
                company.name,
                wecom_tag["tagname"],
                repr(e),
            )

            _logger.warning(result)
            return {
                "name": "add_tag",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def update_tag(self, company, tag, wecom_tag):
        """
        更新标签
        """
        try:
            tag.write(
                {
                    "tagname": wecom_tag["tagname"],
                    "userlist": wecom_tag["userlist"],
                    "partylist": wecom_tag["partylist"],
                }
            )
        except Exception as e:
            result = _("Error update company [%s]'s tag [%s], error reason: %s") % (
                company.name,
                wecom_tag["tagname"],
                repr(e),
            )

            _logger.warning(result)
            return {
                "name": "update_tag",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def download_single_tag(self):
        """
        下载单个标签
        """
        company = self.company_id
        params = {}
        message = ""
        try:
            wxapi = self.env["wecom.service_api"].InitServiceApi(
                company.corpid, company.contacts_app_id.secret
            )
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_GET_MEMBER"
                ),
                {"tagid": str(self.tagid)},
            )

            response["userlist"] = [user["userid"] for user in response["userlist"]]
            for key in response.keys():
                if type(response[key]) in (list, dict) and response[key]:
                    json_str = json.dumps(
                        response[key],
                        sort_keys=False,
                        indent=2,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    response[key] = json_str
            self.write(
                {
                    "tagname": response["tagname"],
                    "userlist":response["userlist"],
                    "partylist": response["partylist"],
                }
            )
        except ApiException as ex:
            message = _("Tag [id:%s, name:%s] failed to download,Reason: %s") % (
                self.tagid,
                self.tagname,
                str(ex),
            )
            _logger.warning(message)
            params = {
                "title": _("Download failed!"),
                "message": message,
                "sticky": True,  # 延时关闭
                "className": "bg-danger",
                "type": "danger",
            }
        except Exception as e:
            message = _("Tag [id:%s, name:%s] failed to download,Reason: %s") % (
                self.tagid,
                self.tagname,
                str(e),
            )
            _logger.warning(message)
            params = {
                "title": _("Download failed!"),
                "message": message,
                "sticky": True,  # 延时关闭
                "className": "bg-danger",
                "type": "danger",
            }
        else:
            message = _("Tag [id:%s, name:%s] downloaded successfully") % (
                self.tagid,
                self.tagname,
            )
            params = {
                "title": _("Download Success!"),
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
            return action  # 返回结果

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_tag(self, cmd):
        """
        通讯录事件更新标签
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        tag_dict = xmltodict.parse(xml_tree)["xml"]
 
        tags = self.sudo().search([("company_id", "=", company_id.id)])
        callback_tag = tags.search(
            [("tagid", "=", tag_dict["TagId"])] , limit=1,
        )

        update_dict = {}

        for key, value in tag_dict.items():
            if key.lower() in self._fields.keys():
                update_dict.update({
                    key.lower(): value
                })
            else:
                if key=="AddUserItems":
                    # 标签中新增的成员userid列表，用逗号分隔
                    update_dict.update({
                        "add_users": value
                    })
                if key=="DelUserItems":
                    # 标签中删除的成员userid列表，用逗号分隔
                    update_dict.update({
                        "del_users": value
                    })
                if key=="AddPartyItems":
                    # 标签中新增的部门id列表，用逗号分隔
                    update_dict.update({
                        "add_departments": value
                    })
                if key=="DelPartyItems":
                    # 标签中删除的部门id列表，用逗号分隔
                    update_dict.update({
                        "del_departments": value
                    })
        

        if callback_tag:
            userlist = json.loads(callback_tag.userlist)
            partylist = json.loads(callback_tag.partylist)


            if "add_users" in update_dict:
                # 需要增加的成员
                userids = update_dict["add_users"].split(",")
                add_users_set = self.env["wecomapi.tools.data"].difference_data_set(set(userids),set(userlist))
                add_users = list(add_users_set)

                for userid in add_users:
                    userlist.append(userid)

                del update_dict["add_users"]
            
            if "del_users" in update_dict:
                # 需要删除的成员
                userids = update_dict["del_users"].split(",")
                del_users_set = self.env["wecomapi.tools.data"].intersection_data_set(set(userlist),set(userids))
                del_users = list(del_users_set)

                for user in del_users:
                    if user in userlist:
                        userlist.remove(user)

                del update_dict["del_users"]    
  
            if "add_departments" in update_dict:
                # 需要增加的部门
                department_ids = update_dict["add_departments"].split(",")
                add_departments_set = self.env["wecomapi.tools.data"].difference_data_set(set(department_ids),set(partylist))
                add_departments = list(add_departments_set)
                for department_id in add_departments:
                    partylist.append(department_id)
                
                del update_dict["add_departments"]   

            if "del_departments" in update_dict:
                # 需要删除的部门
                department_ids = update_dict["del_departments"].split(",")
                del_departments_set = self.env["wecomapi.tools.data"].intersection_data_set(set(department_ids),set(partylist))
                del_departments = list(del_departments_set)

                for department in del_departments:
                    if department in partylist:
                        partylist.remove(department)
                
                del update_dict["del_departments"]  

            update_dict.update({
                "userlist": json.dumps(
                    userlist,
                    sort_keys=False,
                    indent=2,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ),
                "partylist": json.dumps(
                    partylist,
                    sort_keys=False,
                    indent=2,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ),
            })

            del update_dict["tagid"]
            callback_tag.write(update_dict)