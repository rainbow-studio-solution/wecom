# -*- coding: utf-8 -*-

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
    agentid = fields.Integer('企业应用ID',required=True, help="企业应用的id，整型。企业内部开发，可在应用的设置页面查看")
    safe = fields.Boolean('保密消息', default=False)

    title = fields.Char('标题',size=128, help="视频消息的标题，不超过128个字节，超过会自动截断")
    description = fields.Char('描述',size=512,help="描述，不超过512个字节，超过会自动截断")
    content = fields.Text('消息主体',help="最长不超过2048个字节，超过将截断")
    url = fields.Char('点击后跳转的链接', help="点击后跳转的链接")
    picurl = fields.Char('图片链接', help="图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。")
    btntxt = fields.Char('按钮文字', size=4, help="按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。")
    body= fields.Text('消息模板')
