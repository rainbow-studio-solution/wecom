# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError

from ...wxwork_api.wx_qy_api.CorpApi import CorpApi, CORP_API_TYPE, ApiException
from ...wxwork_api.wx_qy_api.ErrorCode import Errcode
import datetime
import time
import json
import binascii


class WizardAttendanceRulePull(models.TransientModel):
    _name = "wizard.attendance.data.pull"
    _description = "Enterprise WeChat,Wizard pull attendance rules"

    department_id = fields.Many2one("hr.department", string="Department",)
    opencheckindatatype = fields.Selection(
        ([("1", "Clock in/Clock out"), ("2", "Go out"), ("3", "All")]),
        string="Clock type",
        help="打卡类型。1：上下班打卡；2：外出打卡；3：全部打卡",
    )
    start_time = fields.Datetime(
        string="Starting time", required=True, compute="_compute_start_time"
    )
    end_time = fields.Datetime(
        string="End Time", default=fields.Datetime.now, required=True
    )
    delta = fields.Selection(
        ([("1", "1 day"), ("7", "7 day"), ("15", "15 day"), ("30", "30 day")]),
        string="Days",
        default="1",
    )
    status = fields.Boolean(
        string="Automatically pull the task status of attendance",
        readonly=True,
        default=lambda self: self._default_status(),
    )

    def _default_status(self):
        cron = self.env.ref("wxwork_attendance.ir_cron_auto_pull_attendance_data")
        return cron.active

    @api.depends("end_time", "delta")
    def _compute_start_time(self):
        self.start_time = self.end_time - datetime.timedelta(int(self.delta))

    def action_pull_attendance_data(self):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")
        contacts_sync_hr_department_id = params.get_param(
            "wxwork.contacts_sync_hr_department_id"
        )

        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(CORP_API_TYPE["GET_CORP_CHECKIN_OPTION"],)
            # print(json.dumps(response))
            for res in response["group"]:
                self.pull_attendance_rule(res, debug)
        except ApiException as e:
            raise UserError(
                "错误：%s %s\n\n详细信息：%s"
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )

    def pull_attendance_rule(self, res, debug):
        rule = (
            self.env["hr.attendance.wxwrok.rule"]
            .sudo()
            .search([("groupid", "=", res["groupid"])], limit=1,)
        )
        try:
            if not rule:
                self.create_rule(rule, res, debug)
            else:
                self.update_rule(rule, res, debug)
        except Exception as e:
            if debug:
                print(
                    _("Failed to pull attendance rules:%s, error: %s")
                    % (res["groupname"], repr(e))
                )

    def create_rule(self, rule, res, debug):
        # print(res["groupname"])
        # str(value).encode('ascii')
        try:
            rule.create(
                {
                    "name": res["groupname"],
                    "groupid": res["groupid"],
                    "grouptype": str(res["grouptype"]),
                    "checkindate": res["checkindate"],
                    "spe_workdays": res["spe_workdays"],
                    "spe_offdays": res["spe_offdays"],
                    "sync_holidays": self.check_type(res, "sync_holidays"),
                    "groupname": res["groupname"],
                    "need_photo": res["need_photo"],
                    "wifimac_infos": res["wifimac_infos"],
                    "note_can_use_local_pic": res["note_can_use_local_pic"],
                    "allow_checkin_offworkday": self.check_type(
                        res, "allow_checkin_offworkday"
                    ),
                    "allow_apply_offworkday": self.check_type(
                        res, "allow_apply_offworkday"
                    ),
                    "loc_infos": res["loc_infos"],
                    "range": res["range"],
                    "create_time": datetime.datetime.fromtimestamp(res["create_time"]),
                    "white_users": res["white_users"],
                    "type": str(res["type"]),
                    "reporterinfo": res["reporterinfo"],
                    "ot_info": self.check_type(res, "ot_info"),
                    "allow_apply_bk_cnt": res["allow_apply_bk_cnt"],
                    "option_out_range": res["option_out_range"],
                    "use_face_detect": self.check_type(res, "use_face_detect"),
                    "allow_apply_bk_day_limit": self.check_type(
                        res, "allow_apply_bk_day_limit"
                    ),
                    "update_userid": self.check_type(res, "update_userid"),
                    "schedulelist": res["schedulelist"],
                    "offwork_interval_time": self.check_type(
                        res, "offwork_interval_time"
                    ),
                }
            )
        except Exception as e:
            if debug:
                print(
                    _("Create attendance rules error: %s") % (res["groupname"], repr(e))
                )

    def update_rule(self, rule, res, debug):
        # print(self.check_json_data(res["spe_offdays"]))
        try:
            rule.write(
                {
                    "name": res["groupname"],
                    "grouptype": str(res["grouptype"]),
                    "checkindate": res["checkindate"],
                    "spe_workdays": res["spe_workdays"],
                    "spe_offdays": res["spe_offdays"],
                    "sync_holidays": self.check_type(res, "sync_holidays"),
                    "groupname": res["groupname"],
                    "need_photo": res["need_photo"],
                    "wifimac_infos": res["wifimac_infos"],
                    "note_can_use_local_pic": res["note_can_use_local_pic"],
                    "allow_checkin_offworkday": self.check_type(
                        res, "allow_checkin_offworkday"
                    ),
                    "allow_apply_offworkday": self.check_type(
                        res, "allow_apply_offworkday"
                    ),
                    "loc_infos": res["loc_infos"],
                    "range": res["range"],
                    "create_time": datetime.datetime.fromtimestamp(res["create_time"]),
                    "white_users": res["white_users"],
                    "type": str(res["type"]),
                    "reporterinfo": res["reporterinfo"],
                    "ot_info": self.check_type(res, "ot_info"),
                    "allow_apply_bk_cnt": res["allow_apply_bk_cnt"],
                    "option_out_range": res["option_out_range"],
                    "use_face_detect": self.check_type(res, "use_face_detect"),
                    "allow_apply_bk_day_limit": self.check_type(
                        res, "allow_apply_bk_day_limit"
                    ),
                    "update_userid": self.check_type(res, "update_userid"),
                    "schedulelist": res["schedulelist"],
                    "offwork_interval_time": self.check_type(
                        res, "offwork_interval_time"
                    ),
                }
            )
        except Exception as e:
            if debug:
                print(
                    _("Update attendance rules error: %s") % (res["groupname"], repr(e))
                )

    def check_json_data(self, list):
        if not list:
            return None
        else:
            json.dumps(list)

    def check_type(self, res, key):
        """
        由于考勤规则三个类型的字典不一样
        故需要检查班次类型
        """
        if key in res.keys():
            return res[key]
        else:
            return None
