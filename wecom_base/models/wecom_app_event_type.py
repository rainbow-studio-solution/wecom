# -*- coding: utf-8 -*-

import logging
import base64
from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from lxml import etree
from lxml import etree as ET
from odoo.http import Response
# from lxml_to_dict import lxml_to_dict
# from xmltodict import lxml_to_dict
import xmltodict, json

_logger = logging.getLogger(__name__)


class WeComAppEventType(models.Model):

    _name = "wecom.app.event_type"
    _description = "Wecom Application Event"
    _order = "id"

    DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: Odoo function to compare floats based on specific precisions
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - UserError: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""

    name = fields.Char(string="Name", translate=True, copy=False, required=True,)
    model_ids = fields.Many2many("ir.model", string="Related Model",)
    msg_type = fields.Char(
        string="Message Type", copy=False, required=True, default="event"
    )
    event = fields.Char(string="Event Code", copy=False, required=True,)
    change_type = fields.Char(string="Change Type", copy=False)
    code = fields.Char(string="Python Code", default="",)
    command = fields.Char(string="Command", copy=False)

    def handle_event(self):
        """
        处理事件
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        event_str = etree.fromstring(xml_tree).find("Event").text
        changetype_str = etree.fromstring(xml_tree).find("ChangeType").text

        _logger.info(
            _(
                "Received the callback notification of enterprise wechat, event [%s], change type [%s]."
            )
            % (event_str, changetype_str,)
        )
        event = (
            self.env["wecom.app.event_type"]
            .sudo()
            .search([("event", "=", event_str), ("change_type", "=", changetype_str),])
        )
        if not event:
            _logger.warning(
                _(
                    "Cannot find [%s] change type for executing company [%s], ignoring it."
                )
                % (event.name, company_id.name,)
            )
            return

        if event.code:
            # ^ 正确响应企业微信本次的POST请求，企业微信将不会再次发送请求
            # ^ ·企业微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共重试三次
            # ^ ·当接收成功后，http头部返回200表示接收ok，其他错误码企业微信后台会一律当做失败并发起重试
            try:
                event.with_context(
                    xml_tree=xml_tree, company_id=company_id
                ).sudo().run()
            except Exception as e:
                _logger.warning(
                    _(
                        "Unable to execute [%s] change type for company [%s], ignoring it. reason: %s"
                    )
                    % (event.name, company_id.name, str(e))
                )
                return Response("success", status=200)
            else:
                return Response("success", status=200)

    def run(self):
        """
        执行事件
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        func_name = self.code.split("model.")[1]
        cmd = self.command

        for m in self.model_ids:
            model_obj = self.env.get(m.model)
            if hasattr(model_obj, func_name):
                # 存在函数
                func = getattr(model_obj.with_context(xml_tree=xml_tree, company_id=company_id), func_name)
                func(cmd)
                _logger.info(
                    _("Method [%s] to execute model [%s]") % (func_name, model_obj,)
                )
            else:
                _logger.warning(
                    _("Function [%s] does not exist in model [%s]") % (func_name, model_obj,)
                )
