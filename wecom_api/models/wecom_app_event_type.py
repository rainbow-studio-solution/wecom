# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.tools.safe_eval import safe_eval, test_python_expr
from lxml import etree

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
    code = fields.Text(
        string="Python Code",
        groups="base.group_system",
        default="",
        help="Write Python code that the action will execute. Some variables are available for use; help about python expression is given in the help tab.",
    )

    @api.constrains("code")
    def _check_python_code(self):
        for action in self.sudo().filtered("code"):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def handle_event(self):
        """
        处理事件
        """
        xml_tree = self.env.context.get("xml_tree")
        company = self.env.context.get("company")

        event = xml_tree.find("Event").text
        change_type = xml_tree.find("ChangeType").text

        event = (
            self.env["wecom.app.event_type"]
            .sudo()
            .search([("event", "=", event), ("change_type", "=", change_type)])
        )
        if not event:
            _logger.warning(
                _(
                    "Cannot find [%s] change type for executing company [%s], ignoring it."
                )
                % (event.name, company.name,)
            )
            return

        if event.code:
            try:
                event.with_context(xml_tree=xml_tree, company=company).sudo().run()
            except Exception as e:
                _logger.warning(
                    _(
                        "Unable to execute [%s] change type for company [%s], ignoring it."
                    )
                    % (event.name, company.name,)
                )

    def run(self):
        """
        执行事件
        """
        xml_tree = self.env.context.get("xml_tree")
        company = self.env.context.get("company")
        func_name = self.code.split("model.")[1]

        for model in self.model_ids:
            model_obj = self.env.get(model.model)
            print(model_obj, type(model_obj))
            func_obj = getattr(self.env[model.model], "wecom_event_change_contact_user")
            eval(func_obj)("123")
            # model_obj.with_context(xml_tree=xml_tree, company=company).func_obj()
            # self.env[model.model].sudo().eval(func)
            # self.env[model.model].sudo().with_context(
            #     xml_tree=xml_tree, company=company
            # ).eval(func)

        #     self.env[model.model].sudo().with_context(
        #         xml_tree=xml_tree, company=company
        #     ).function
