from odoo import api, models, fields
from odoo.exceptions import UserError

import datetime
import time
import json

from ...wxwork_api1.ErrCode import Errcode
from ...wxwork_api.wx_qy_api.CorpApi import CorpApi, CORP_API_TYPE, ApiException


class ResConfigSettings(models.TransientModel):
    _name = "wizard.wxwork.attendance.rule.pull"
    _description = "企业微信打卡规则拉取向导"
    _order = "start_time"

    department_id = fields.Many2one(
        "hr.department",
        string="部门",
    )
    current_date = fields.Datetime(
        string="请选择日期",
        default=fields.Datetime.now,
        required=True,
        help="规则的日期当天0点的Unix时间戳",
    )
    # TODO:获取任务是否开启
    status = fields.Boolean(string="后台拉取任务状态")

    def action_pull_attendance(self):
        pull_list, batch = self.get_employees_by_department(self.department_id)

        if batch:
            for i in range(0, int(len(pull_list))):
                self.get_checkin_option(pull_list[i])
        else:
            self.get_checkin_option(pull_list)

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
                    env = self.sudo().env["hr.attendance.rule.wxwrok"]
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

    def create_wxwork_attendance(self, attendance, checkinoption):
        # print(json.dumps(checkinoption["group"]["checkindate"]))
        t = datetime.datetime.strptime(
            self.current_date.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S"
        )
        try:
            attendance.create(
                {
                    "name": self.sudo()
                    .env["hr.employee"]
                    .search([("wxwork_id", "=", checkinoption["userid"])], limit=1)
                    .name,
                    "pull_time": t,
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

    def get_employee_id(self, wxwork_id):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env["hr.employee"]
            employee = env.search([("wxwork_id", "=", wxwork_id)], limit=1)
            return employee.id

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
                {
                    "department_id": str(wxwork_department_id),
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
            raise UserError(
                "错误：%s %s\n\n详细信息：%s"
                % (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg)
            )
