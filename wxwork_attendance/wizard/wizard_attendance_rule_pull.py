# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

from ...wxwork_api.wx_qy_api.CorpApi import CorpApi, CORP_API_TYPE, ApiException
from ...wxwork_api.wx_qy_api.ErrorCode import Errcode
import datetime
import time
import json


class WizardAttendanceRulePull(models.TransientModel):
    _name = "wizard.attendance.rule.pull"
    _description = "企业微信打卡规则拉取向导"

    department_id = fields.Many2one(
        "hr.department", string="Department", help="部门为空，获取企业所有打卡规则",
    )
    current_date = fields.Datetime(
        string="Please select a date",
        default=fields.Datetime.now,
        required=True,
        help="规则的日期当天0点的Unix时间戳",
    )
    status = fields.Boolean(string="Status", readonly=True)

    def get_employees_by_department(self, department_obj):
        """
        根据企微部门ID，通过API获取需要拉取打卡记录企业微信成员列表
        :param department_id:部门对象
        :return:企业微信成员UserID列表
        """
        if department_obj.wxwork_department_id:
            wxwork_department_id = department_obj.wxwork_department_id
        else:
            wxwork_department_id = 1
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["USER_LIST"],
                {"department_id": str(wxwork_department_id), "fetch_child": "1",},
            )
            userlist = []
            for obj in response["userlist"]:
                userlist.append(obj["userid"])
            if len(userlist) > 100:
                batch_list = []
                for i in range(0, int(len(userlist)) + 1, 100):
                    tmp_list1 = json.dumps(userlist[i : i + 100])
                    batch_list.append(tmp_list1)
                userlist = batch_list
                return userlist, True
            else:
                return json.dumps(userlist), False
        except ApiException as e:
            raise UserError(
                "错误：%s %s\n\n详细信息：%s"
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )

    def action_pull_attendance_rule(self):
        pull_list, batch = self.get_employees_by_department(self.department_id)
