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
    _name = "wizard.attendance.rule.pull"
    _description = "Enterprise WeChat,Wizard pull attendance rules"

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

    def create_wxwork_attendance(self, attendance, checkinoption):
        # print(json.dumps(checkinoption["group"]["checkindate"]))

        t = datetime.datetime.strptime(
            self.current_date.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S"
        )
        try:
            attendance.create(
                {
                    "grouptype": t,
                    "wxwork_id": checkinoption["userid"],
                    "groupid": checkinoption["group"]["groupid"],
                    "groupname": checkinoption["group"]["groupname"],
                    "grouptype": checkinoption["group"]["grouptype"],
                    "checkindate_json": json.dumps(
                        checkinoption["group"]["checkindate"]
                    ),
                    "spe_workdays_json": checkinoption["group"]["spe_workdays"],
                    "spe_offdays_json": checkinoption["group"]["spe_offdays"],
                    "sync_holidays": checkinoption["group"]["sync_holidays"],
                    "need_photo": checkinoption["group"]["need_photo"],
                    "wifimac_infos": checkinoption["group"]["wifimac_infos"],
                    "note_can_use_local_pic": checkinoption["group"][
                        "note_can_use_local_pic"
                    ],
                    "allow_checkin_offworkday": checkinoption["group"][
                        "allow_checkin_offworkday"
                    ],
                    "allow_apply_offworkday": checkinoption["group"][
                        "allow_apply_offworkday"
                    ],
                    "loc_infos": checkinoption["group"]["loc_infos"],
                }
            )
        except BaseException as e:
            print("拉取记录失败:%s - %s" % (checkinoption["userid"], repr(e)))

    def get_checkin_option(self, pull_list):
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.attendance_secret")

        wxapi = CorpApi(corpid, secret)
        t = datetime.datetime.strptime(
            self.current_date.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S"
        )
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE["GET_CHECKIN_OPTION"],
                {
                    "datetime": str(time.mktime(t.timetuple())),
                    "useridlist": json.loads(pull_list),
                },
            )
            # print(str(time.mktime(t.timetuple())))
            # print(response["info"])
            for checkinoption in response["info"]:
                with api.Environment.manage():
                    new_cr = self.pool.cursor()
                    self = self.with_env(self.env(cr=new_cr))
                    env = self.sudo().env["hr.attendance.wxwrok.rule"]
                    records = env.search(
                        [
                            ("wxwork_id", "=", checkinoption["userid"]),
                            ("pull_time", "=", t),
                        ],
                        limit=1,
                    )
                    try:
                        if len(records) > 0:
                            pass
                        else:
                            self.create_wxwork_attendance(records, checkinoption)
                    except Exception as e:
                        print(repr(e))

                    new_cr.commit()
                    new_cr.close()

        except ApiException as e:
            raise UserError(
                "错误：%s %s\n\n详细信息：%s"
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )

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
        contacts_sync_hr_department_id = params.get_param(
            "wxwork.contacts_sync_hr_department_id"
        )

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
        params = self.env["ir.config_parameter"].sudo()
        corpid = params.get_param("wxwork.corpid")
        secret = params.get_param("wxwork.contacts_secret")
        debug = params.get_param("wxwork.debug_enabled")
        contacts_sync_hr_department_id = params.get_param(
            "wxwork.contacts_sync_hr_department_id"
        )

        wxapi = CorpApi(corpid, secret)
        if not self.department_id:
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
        # else:
        #     pull_list, batch = self.get_employees_by_department(self.department_id)

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
                    # "grouptype": res["grouptype"],#TODO
                    "checkindate": res["checkindate"],
                    "spe_workdays": res["spe_workdays"],
                    # "spe_offdays": json.dumps(res["spe_offdays"]),#TODO
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
                    # "type": res["type"],#TODO
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
                    # "grouptype": res["grouptype"],#TODO
                    "checkindate": res["checkindate"],
                    "spe_workdays": res["spe_workdays"],
                    # "spe_offdays": json.dumps(res["spe_offdays"]),#TODO
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
                    # "type": res["type"],#TODO
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
