# -*- coding: utf-8 -*-

from ..api.CorpApi import *
# from ..api.ApiException import *

from odoo import _, api, fields, models, tools

class NoticeTemplate(models.Model):
    _name = 'wxwork.notice.template'
    _description = '企业微信通知模板'

    name = fields.Char('模板名称')
    model_id = fields.Many2one('ir.model', '应用于', help="此模板可以使用的文档类型")
    model = fields.Char('相关文件模型', related='model_id.model', index=True, store=True, readonly=True)

    from_user = fields.Char('从',help="" )
    use_default_to = fields.Boolean('默认接收者',)
    to_user = fields.Char('到用户', help="消息接收者，多个接收者用‘|’分隔，最多支持1000个。特殊情况：指定为@all，则向该企业应用的全部成员发送")
    to_party = fields.Char('到部门', help="部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数")
    to_tag = fields.Char('到标签', help="标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数")
    msgtype = fields.Selection([
        ('text', '文本消息'),
        ('image', '图片消息'),
        ('voice', '语音消息'),
        ('video', '视频消息'),
        ('file', '文件消息'),
        ('textcard', '文本卡片消息'),
        ('news', '图文消息'),
        ('mpnews', '图文消息（mpnews）'),
        ('markdown', 'markdown消息'),
        ('miniprogram_notice', '小程序通知消息'),],
        '消息类型', required=True, default='text',
        )

    safe = fields.Boolean('保密消息', default=False)

    title = fields.Char('标题',size=128, help="视频消息的标题，不超过128个字节，超过会自动截断")
    description = fields.Char('描述',size=512,help="描述，不超过512个字节，超过会自动截断")
    content = fields.Text('消息主体',help="最长不超过2048个字节，超过将截断")
    url = fields.Char('点击后跳转的链接', help="点击后跳转的链接")
    picurl = fields.Char('图片链接', help="图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。")
    btntxt = fields.Char('按钮文字', size=4, help="按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。")
    body= fields.Text('消息模板')

    # 用于实现占位符助手的假字段
    model_object_field = fields.Many2one('ir.model.fields', string="主字段",
                                         help="从相关文档模型中选择目标字段。如果它是关系字段，您将能够在关系的目标位置选择目标字段。")
    sub_object = fields.Many2one('ir.model', '子模型', readonly=True,
                                 help="当关系字段被选为第一个字段时，该字段显示关系所在的文档模型。")
    sub_model_object_field = fields.Many2one('ir.model.fields', '子字段',
                                             help="当关系字段被选为第一个字段时，此字段允许您选择目标文档模型（子模型）中的目标字段。")
    null_value = fields.Char('默认值', help="如果目标字段为空，则使用可选值")

    def build_expression(self, field_name, sub_field_name, null_value):
        '''
        返回占位符表达式，以便在模板字段中使用，具体取决于占位符助手中提供的值。
        :param field_name:主字段名称
        :param sub_field_name:子字段名称（M2O）
        :param null_value:如果目标值为空，则为默认值
        :return:最终占位符表达式
        '''
        expression = ''
        if field_name:
            expression = "${object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += "}"
        return expression

    # @api.multi
    def send_notice(self, send_to_all=False):
        '''
        生成一个新的企业微信通知。 模板由res_id和来自模板的模型给出的记录呈现。
        :return:
        '''
        params = self.env['ir.config_parameter'].sudo()
        corpid = params.get_param('wxwork.corpid')
        secret = params.get_param('wxwork.auth_secret')
        agentid = params.get_param('wxwork.auth_agentid')

        api = CorpApi(corpid, secret)
        # try:
        response = api.httpCall(
            CORP_API_TYPE['MESSAGE_SEND'],
            {
                # "touser": "ZhuShengBen",
                # "toparty": "PartyID1 | PartyID2",
                # "totag": "TagID1 | TagID2",
                # "agentid": 1000002,
                # 'msgtype' : 'text',
                # 'climsgid' : 'climsgidclimsgid_%f' % (random.random()),
                # 'text' : {
                #     'content':'方法论',
                # },
                # 'safe' : 0,
            }
        )
        # except ApiException as e:
        #     print e.errCode, e.errMsg


    # @api.multi
    def generate_notice(self):
        '''
        根据res_ids给出的记录，根据给定模型从模板生成企业微信通知
        :return:
        '''

    # @api.multi
    def generate_notice_template(self):
        '''
        生成企业微信消息模板
        :return:
        '''