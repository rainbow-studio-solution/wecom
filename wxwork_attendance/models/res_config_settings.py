# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import time
import json
import platform
import logging

_logger = logging.getLogger(__name__)

from ...wxwork_api.ErrCode import Errcode
from ...wxwork_api.wx_qy_api.CorpApi import CorpApi, CORP_API_TYPE, ApiException


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_secret = fields.Char(
        "打卡凭证密钥", config_parameter="wxwork.attendance_secret"
    )
    attendance_access_token = fields.Char(
        "打卡token",
        config_parameter="wxwork.attendance_access_token",
        readonly=True,
    )

    def get_attendance_access_token(self):
        if self.corpid == False:
            raise UserError(_("请正确填写企业ID."))
        elif self.contacts_secret == False:
            raise UserError(_("请正确填写打卡凭证密钥."))
        else:
            wxapi = CorpApi(self.corpid, self.attendance_secret)
            self.env["ir.config_parameter"].sudo().set_param(
                "wxwork.attendance_access_token", wxapi.getAccessToken()
            )

    def cron_pull_attendance_data(self):
        """
        拉取3天内的考勤记录任务-全体人员
        :return:
        """
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=3)
        # print(start_time,end_time)
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wxwork.debug_enabled")
        if debug:
            _logger.error("开始拉取考勤记录")
        pull_list, batch = self.get_all_employees(debug)
        if batch:
            if debug:
                _logger.error("当前员工人数超过100人，正在拆分列表，分批拉取")
            for i in range(0, int(len(pull_list))):
                self.get_checkin_data(pull_list[i], i, start_time, end_time, debug)
        else:
            if debug:
                _logger.error("当前员工人数不足100人，正在拉取")
            self.get_checkin_data(pull_list, start_time, end_time, debug)

    def get_checkin_data(self, pull_list, i, start_time, end_time, debug):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.attendance_secret")
        if debug:
            if i is None:
                _logger.error("打开API成功")
            else:
                _logger.error("第 %s 批次 打开API成功" % i)
        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_CHECKIN_DATA"],
                {
                    "opencheckindatatype": 3,
                    "starttime": str(time.mktime(start_time.timetuple())),
                    "endtime": str(time.mktime(end_time.timetuple())),
                    "useridlist": json.loads(pull_list),
                },
            )
            if debug:
                if i is None:
                    _logger.error("API获取考勤记录成功，正在更新数据")
                else:
                    _logger.error("第 %s 批次 API获取考勤记录成功，正在更新数据" % i)
            for checkindata in response["checkindata"]:
                with api.Environment.manage():
                    new_cr = self.pool.cursor()
                    self = self.with_env(self.env(cr=new_cr))
                    env = self.sudo().env["hr.attendance.data.wxwrok"]
                    records = env.search(
                        [
                            ("wxwork_id", "=", checkindata["userid"]),
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
                    try:
                        if len(records) > 0:
                            pass
                        else:
                            self.create_wxwork_attendance(records, checkindata, debug)
                    except Exception as e:
                        print(repr(e))

                    new_cr.commit()
                    new_cr.close()
            if debug:
                if i is None:
                    _logger.error("更新打卡数据成功")
                else:
                    _logger.error("第 %s 批次 更新打卡数据成功" % i)

        except ApiException as e:
            if debug:
                if i is None:
                    _logger.error(
                        "拉取失败，错误：%s %s\n\n详细信息：%s"
                        % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                    )
                else:
                    _logger.error(
                        "第 %s 批次 拉取失败，错误：%s %s\n\n详细信息：%s"
                        % (i, str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                    )

    def create_wxwork_attendance(self, attendance, checkindata, debug):
        try:
            attendance.create(
                {
                    "name": self.sudo()
                    .env["hr.employee"]
                    .search([("wxwork_id", "=", checkindata["userid"])], limit=1)
                    .name,
                    "wxwork_id": checkindata["userid"],
                    "groupname": checkindata["groupname"],
                    "checkin_type": checkindata["checkin_type"],
                    "checkin_time": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(checkindata["checkin_time"])
                    ),
                    "exception_type": checkindata["exception_type"],
                    "location_title": checkindata["location_title"],
                    "location_detail": checkindata["location_detail"],
                    "wifiname": checkindata["wifiname"],
                    "notes": checkindata["notes"],
                    "wifimac": checkindata["wifimac"],
                    "mediaids": checkindata["mediaids"],
                    "lat": checkindata["lat"],
                    "lng": checkindata["lng"],
                }
            )
        except BaseException as e:
            if debug:
                _logger.error("更新打卡数据失败:%s - %s" % (checkindata["userid"], repr(e)))

    def get_all_employees(self, debug):
        """
        通过API获取企业微信成员列表
        :param department_id:部门对象
        :return:企业微信成员UserID列表
        """

        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")

        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["USER_LIST"],
                {
                    "department_id": "1",
                    "fetch_child": "1",
                },
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
            if debug:
                _logger.error(
                    "错误：%s %s\n\n详细信息：%s"
                    % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
                )
