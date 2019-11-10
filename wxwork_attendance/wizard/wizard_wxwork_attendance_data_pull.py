from odoo import api, models, fields
from odoo.exceptions import UserError
# from wxworkapi.CorpApi import CorpApi, CORP_API_TYPE
import datetime
import time
import json
import platform

from ...wxwork_api.ErrCode import Errcode
from ...wxwork_api.CorpApi import CorpApi, CORP_API_TYPE,  ApiException


class ResConfigSettings(models.TransientModel):
    _name = 'wizard.wxwork.attendance.data.pull'
    _description = '企业微信打卡数据拉取向导'
    _order = 'start_time'


    department_id = fields.Many2one('hr.department', string="部门",)
    checkin_type = fields.Selection(
        ([('1', '上下班打卡'), ('2', '外出打卡'), ('3', '全部打卡')]),
        string='打卡类型')
    start_time = fields.Datetime(string="开始时间", required=True, compute='_compute_start_time')
    end_time = fields.Datetime(string="结束时间", default=fields.Datetime.now, required=True)
    delta = fields.Selection(
        ([('1', '1 天'), ('7', '7 天'), ('15', '15天'), ('30', '30天')]),
        string='天数',default="1")
    # TODO:获取任务是否开启
    status = fields.Boolean(string="后台拉取任务状态")

    @api.depends('end_time','delta')
    def _compute_start_time(self):
        self.start_time = self.end_time - datetime.timedelta(int(self.delta))

    def action_pull_attendance(self):
        pull_list,batch = self.get_employees_by_department(self.department_id)
        if batch:
            for i in range(0, int(len(pull_list))):
                self.get_checkin_data(pull_list[i])
        else:
            self.get_checkin_data(pull_list)


    def get_checkin_data(self,pull_list):
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.attendance_secret')

        if self.checkin_type:
            checkin_type = self.checkin_type
        else:
            checkin_type = 3

        wxapi = CorpApi(corpid, secret)

        try:
            response = wxapi.httpCall(
                CORP_API_TYPE['GET_CHECKIN_DATA'],
                {
                    "opencheckindatatype": str(checkin_type),
                    "starttime": str(time.mktime(self.start_time.timetuple())),
                    "endtime": str(time.mktime(self.end_time.timetuple())),
                    "useridlist": json.loads(pull_list),
                    # "useridlist": pull_list,
                }
            )
            for checkindata in response["checkindata"]:
                with api.Environment.manage():
                    new_cr = self.pool.cursor()
                    self = self.with_env(self.env(cr=new_cr))
                    env = self.sudo().env['hr.attendance.data.wxwrok']
                    records = env.search([
                        ('wxwork_id', '=', checkindata['userid']),
                        ('checkin_time', '=', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(checkindata['checkin_time']))),
                        ],
                        limit=1)
                    try:
                        if len(records) > 0:
                            pass
                        else:
                            self.create_wxwork_attendance(records,checkindata)
                    except Exception as e:
                        print(repr(e))

                    new_cr.commit()
                    new_cr.close()

        except ApiException as e:
            raise UserError(
                '错误：%s %s\n\n详细信息：%s' %
                (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg))

    def create_wxwork_attendance(self, attendance, checkindata):
        try:
            attendance.create({
                'name': self.sudo().env['hr.employee'].search([('wxwork_id', '=', checkindata['userid'])],limit=1).name,
                'wxwork_id': checkindata['userid'],
                'groupname': checkindata['groupname'],
                'checkin_type': checkindata['checkin_type'],
                'checkin_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(checkindata['checkin_time'])),
                'exception_type': checkindata['exception_type'],
                'location_title': checkindata['location_title'],
                'location_detail': checkindata['location_detail'],
                'wifiname': checkindata['wifiname'],
                'notes': checkindata['notes'],
                'wifimac': checkindata['wifimac'],
                'mediaids': checkindata['mediaids'],
                'lat': checkindata['lat'],
                'lng': checkindata['lng'],
            })
        except BaseException as e:
            print('拉取记录失败:%s - %s' % (checkindata['userid'], repr(e)))


    def get_employee_id(self,wxwork_id):
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            env = self.sudo().env['hr.employee']
            employee = env.search([ ('wxwork_id', '=', wxwork_id)],  limit=1)
            return employee.id

    def get_employees_by_department(self,department_obj):
        '''
        根据企微部门ID，通过API获取需要拉取打卡记录企业微信成员列表
        :param department_id:部门对象
        :return:企业微信成员UserID列表
        '''
        if department_obj.wxwork_department_id:
            wxwork_department_id = department_obj.wxwork_department_id
        else:
            wxwork_department_id = 1
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.contacts_secret')

        wxapi = CorpApi(corpid, secret)
        try:
            response = wxapi.httpCall(
                CORP_API_TYPE['USER_LIST'],
                {
                    'department_id': str(wxwork_department_id),
                    'fetch_child': '1',
                }
            )
            userlist = []
            for obj in response['userlist']:
                userlist.append(obj['userid'])
            if len(userlist) > 100:
                batch_list = []
                for i in range(0, int(len(userlist)) + 1, 100):
                    tmp_list1 = json.dumps(userlist[i:i + 100])
                    batch_list.append(tmp_list1)
                userlist = batch_list
                return userlist,True
            else:
                return json.dumps(userlist),False
        except ApiException as e:
            raise UserError(
                '错误：%s %s\n\n详细信息：%s' %
                (str(e.errCode), Errcode.getErrcode(e.errCode), e.errMsg))
