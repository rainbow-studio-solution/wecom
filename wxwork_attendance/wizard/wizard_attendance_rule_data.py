# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


from odoo.addons.wxwork_api.api.corp_api import CorpApi, CORP_API_TYPE
from odoo.addons.wxwork_api.api.abstract_api import ApiException
from odoo.addons.wxwork_api.api.error_code import Errcode

import datetime
import time
import json
import binascii
import logging

_logger = logging.getLogger(__name__)


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
        string="Starting date", required=True, compute="_compute_start_time"
    )
    end_time = fields.Datetime(
        string="End date", required=True, default=datetime.date.today(),
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
        """
        拉取考勤数据
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        contacts_sync_hr_department_id = params.get_param(
            "wxwork.contacts_sync_hr_department_id"
        )
        if not self.department_id:
            department_id = contacts_sync_hr_department_id
        else:
            department_id = self.department_id.wxwork_department_id

        pull_list, batch = self.get_employees_by_department(department_id, params)

        if batch:
            # 需要分批次拉取
            if debug:
                _logger.info(
                    _(
                        "The number of people has exceeded 100 and is processed in batches."
                    )
                )
            for i in range(0, int(len(pull_list))):
                self.get_checkin_data(pull_list[i], params)
        else:
            # 不需要分批次拉取
            if debug:
                _logger.info(
                    _(
                        "The quantity does not exceed 100, and batch processing is not required."
                    )
                )
            self.get_checkin_data(pull_list, params)

    def get_employees_by_department(self, department_id, params):
        """
        根据企微部门ID，通过API获取需要拉取打卡记录企业微信成员列表
        :param department_id:部门对象
        :return:企业微信成员UserID列表
        """
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")

        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["USER_LIST"],
                {"department_id": str(department_id), "fetch_child": "1",},
            )
            userlist = []
            for obj in response["userlist"]:
                userlist.append(obj["userid"])

            # 用户列表不超过100个。若用户超过100个，需要分批获取
            if len(userlist) > 100:
                # 用户列表超过100
                batch_list = []
                for i in range(0, int(len(userlist)) + 1, 100):
                    tmp_list1 = json.dumps(userlist[i : i + 100])
                    batch_list.append(tmp_list1)
                userlist = batch_list
                return userlist, True
            else:
                # 用户列表没有超过100
                return json.dumps(userlist), False
        except ApiException as e:
            if debug:
                _logger.debug(
                    _(
                        "Failed to get the enterprise WeChat user list，error code: %s,Error description: %s,Error Details:%s"
                        % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                    )
                )
            raise UserError(
                _("error: %s %s\n\ndetails: %s")
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )

    def get_checkin_data(self, pull_list, params):
        """
        获取打卡记录数据
        """
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.attendance_secret")
        debug = params.get_param("wxwork.debug_enabled")

        if not self.opencheckindatatype:
            opencheckindatatype = 3
        else:
            opencheckindatatype = self.opencheckindatatype
        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_CHECKIN_DATA"],
                {
                    "opencheckindatatype": str(opencheckindatatype),
                    "starttime": str(time.mktime(self.start_time.timetuple())),
                    "endtime": str(time.mktime(self.end_time.timetuple())),
                    "useridlist": json.loads(pull_list),
                },
            )

            for checkindata in response["checkindata"]:
                record = (
                    self.env["hr.attendance.wxwrok.data"]
                    .sudo()
                    .search(
                        [
                            ("userid", "=", checkindata["userid"]),
                            (
                                "checkin_time",
                                "=",
                                time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(checkindata["checkin_time"]),
                                ),
                            ),
                        ],
                        limit=1,
                    )
                )
                try:
                    if not record:
                        if debug:
                            _logger.debug(
                                _("Create %s attendance records")
                                % checkindata["userid"]
                            )
                        self.create_attendance_data(record, checkindata, debug)
                except Exception as e:
                    print(_("Failed to create attendance record, reason: %s") % repr(e))
        except ApiException as e:
            if debug:
                _logger.debug(
                    _(
                        "Failed to pull Enterprise WeChat attendance record data.，error code: %s,Error description: %s,Error Details:%s"
                        % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                    )
                )
            raise UserError(
                _("error: %s %s\n\ndetails: %s")
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )

    def create_attendance_data(self, record, checkindata, debug):
        try:
            record.create(
                {
                    "name": self.sudo()
                    .env["hr.employee"]
                    .search([("wxwork_id", "=", checkindata["userid"])], limit=1)
                    .name,
                    "userid": checkindata["userid"],
                    "groupname": checkindata["groupname"],
                    "checkin_type": checkindata["checkin_type"],
                    "exception_type": checkindata["exception_type"],
                    "checkin_time": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(checkindata["checkin_time"])
                    ),
                    "location_title": checkindata["location_title"],
                    "location_detail": checkindata["location_detail"],
                    "wifiname": checkindata["wifiname"],
                    "notes": checkindata["notes"],
                    "wifimac": checkindata["wifimac"],
                    "mediaids": checkindata["mediaids"],
                    "lat": checkindata["lat"],
                    "lng": checkindata["lng"],
                    "deviceid": checkindata["deviceid"],
                    "sch_checkin_time": self.timestamp_to_time(
                        self.check_key(checkindata, "sch_checkin_time")
                    ),
                    "groupid": checkindata["groupid"],
                    "schedule_id": self.check_key(checkindata, "schedule_id"),
                    "timeline_id": self.check_key(checkindata, "timeline_id"),
                }
            )
        except BaseException as e:
            if debug:
                print(
                    _("Failed to create %s attendance record, reason: %s")
                    % (checkindata["userid"], repr(e))
                )

    def check_key(self, res, key):
        """
        检查json数据中是否存在key
        """
        if key in res.keys():
            return res[key]
        else:
            return None

    def timestamp_to_time(self, timestamp):
        if not timestamp:
            return None
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp),)

