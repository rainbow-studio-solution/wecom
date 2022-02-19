# -*- coding: utf-8 -*-

import logging
import base64
import time
from lxml import etree
from odoo import api, fields, models, _
from lxml_to_dict import lxml_to_dict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class PartnerCategory(models.Model):
    _inherit = "res.partner.category"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
        readonly=True,
    )

    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    tagid = fields.Integer(
        string="WeCom Tag ID",
        readonly=True,
        default=0,
        help="Tag ID, non negative integer. When this parameter is specified, the new tag will generate the corresponding tag ID. if it is not specified, it will be automatically increased by the current maximum ID.",
    )
    is_wecom_tag = fields.Boolean(
        string="WeCom Tag",
        default=False,
    )

    @api.depends("is_wecom_tag")
    def _compute_display_name(self):
        tag = _("WeCom Tag")
        for rec in self:
            if rec.is_wecom_tag:
                rec.display_name = "%s:%s" % (tag, rec.name)
            else:
                rec.display_name = rec.name

    @api.model
    def download_wecom_contact_tags(self):
        """
        下载企微标签列表 res.partner.category
        """
        start_time = time.time()
        company = self.env.context.get("company_id")

        tasks = []
        if not company:
            company = self.env.company
        if company.is_wecom_organization:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
                )
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call(
                        "TAG_GET_LIST"
                    )
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
                tags = response["taglist"]
                for tag in tags:
                    category = self.search(
                        [
                            ("tagid", "=", tag["tagid"]),
                            ("company_id", "=", company.id),
                        ],
                        limit=1,
                    )

                    if not category:
                        category.create(
                            {
                                "name": tag["tagname"],
                                "tagid": tag["tagid"],
                                "is_wecom_tag": True,
                            }
                        )
                    else:
                        category.write(
                            {
                                "name": tag["tagname"],
                                "is_wecom_tag": True,
                            }
                        )
                    result = self.download_wecom_tag_member(
                        category, wxapi, tag["tagid"], company
                    )
                    if result:
                        tasks.append(
                            {
                                "name": "download_tag_members",
                                "state": False,
                                "time": 0,
                                "msg": _(
                                    "Failed to download tag [%s] member of company [%s]!"
                                )
                                % (tag["tagname"], company.name),
                            }
                        )
            finally:
                end_time = time.time()
                task = {
                    "name": "download_tag_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Tag list downloaded successfully."),
                }
                tasks.append(task)
        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_tag_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure or switch the company."
                    ),
                }
            ]
        return tasks

    def download_wecom_tag_member(self, category, wxapi, tagid, company):
        """
        下载企微标签成员
        """
        res = {}
        try:
            response = wxapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call(
                    "TAG_GET_MEMBER"
                ),
                {"tagid": str(tagid)},
            )
        except ApiException as ex:
            self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=False
            )
            res = {
                "name": "download_tag_members",
                "state": False,
                "time": 0,
                "msg": repr(e),
            }
        except Exception as e:
            res = {
                "name": "download_tag_members",
                "state": False,
                "time": 0,
                "msg": repr(e),
            }
        else:
            partner_ids = []
            for user in response["userlist"]:
                partner = (
                    self.env["res.partner"]
                    .sudo()
                    .search(
                        [
                            ("wecom_userid", "=", user["userid"].lower()),
                            ("company_id", "=", company.id),
                            ("is_wecom_user", "=", True),
                            "|",
                            ("active", "=", True),
                            ("active", "=", False),
                        ],
                        limit=1,
                    )
                )
                if partner:
                    partner_ids.append(partner.id)
            if len(partner_ids) > 0:
                category.write({"partner_ids": [(6, 0, partner_ids)]})

        finally:
            return res  # 返回失败的结果
