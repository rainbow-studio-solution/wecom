# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class WxWorkMessage(models.Model):
    """
    参考模型 'mail.mail'
    """

    _name = "wxwork.message"
    _description = "Enterprise WeChat Outgoing message"
    _inherits = {"mail.message": "mail_message_id"}
    _order = "id desc"
    _rec_name = "subject"

    name = fields.Char("Subject", help="Subject of your Mailing", required=True,)
    to_all = fields.Boolean("To all members", readonly=True,)
    to_user = fields.Many2many(
        "hr.employee",
        string="To Employees",
        domain="[('active', '=', True), ('is_wxwork_employee', '=', True)]",
        help="Message recipients (users)",
    )
    to_party = fields.Many2many(
        "hr.department",
        string="To Departments",
        domain="[('active', '=', True), ('is_wxwork_department', '=', True)]",
        help="Message recipients (departments)",
    )
    to_tag = fields.Many2many(
        "hr.employee.category",
        # "employee_category_rel",
        # "emp_id",
        # "category_id",
        string="To Tags",
        domain="[('is_wxwork_category', '=', True)]",
        help="Message recipients (tags)",
    )

    use_templates = fields.Boolean("Test template message",)
    templates_id = fields.Many2one("mail.template", string="Message template")
    msgtype = fields.Selection(
        [
            ("text", "Text message"),
            ("image", "Picture message"),
            ("voice", "Voice messages"),
            ("video", "Video message"),
            ("file", "File message"),
            ("textcard", "Text card message"),
            ("news", "Graphic message"),
            ("mpnews", "Graphic message（mpnews）"),
            ("markdown", "Markdown message"),
            ("miniprogram", "Mini Program Notification Message"),
            ("taskcard", "Task card message"),
        ],
        string="Message type",
        required=True,
        default="markdown",
        readonly=True,
    )

    text_content = fields.Text(
        "Text message content", help="消息内容，最长不超过2048个字节，超过将截断（支持id转译）"
    )

    image_media_id = fields.Text(
        "Picture message media id", help="图片媒体文件id，可以调用上传临时素材接口获取"
    )

    voice_media_id = fields.Text("Voice message media id", help="语音文件id，可以调用上传临时素材接口获取")

    video_title = fields.Char("Video message title", help="视频消息的标题，不超过128个字节，超过会自动截断")
    video_media_id = fields.Char(
        "Video message media id", help="视频媒体文件id，可以调用上传临时素材接口获取"
    )
    video_description = fields.Html(
        "Video message description", help="视频消息的描述，不超过512个字节，超过会自动截断"
    )

    file_media_id = fields.Char("File message media id", help="文件id，可以调用上传临时素材接口获取")

    textcard_title = fields.Char(
        "Text card message title", help="标题，不超过128个字节，超过会自动截断（支持id转译）"
    )
    textcard_description = fields.Html(
        "Text card message description", help="描述，不超过512个字节，超过会自动截断（支持id转译）"
    )
    textcard_url = fields.Char(
        "Text card message url", help="点击后跳转的链接。 最长2048字节，请确保包含了协议头(http/https)"
    )
    textcard_btntxt = fields.Char(
        "Text card message btntxt", help="按钮文字。 默认为“详情”， 不超过4个文字，超过自动截断。"
    )

    news_articles_title = fields.Char(
        "Graphic message articles title", help="标题，不超过128个字节，超过会自动截断（支持id转译）"
    )
    news_articles_description = fields.Char(
        "Graphic message articles description", help="描述，不超过512个字节，超过会自动截断（支持id转译）"
    )
    news_articles_url = fields.Char(
        "Graphic message articles url", help="点击后跳转的链接。最长2048字节，请确保包含了协议头(http/https)"
    )
    news_articles_picurl = fields.Char(
        "Graphic message articles picture url",
        help="图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图 1068*455，小图150*150。",
    )

    mpnews_articles_title = fields.Char(
        "Graphic message (mpnews) articles title", help="标题，不超过128个字节，超过会自动截断（支持id转译）"
    )
    mpnews_articles_thumb_media_id = fields.Char(
        "Graphic message (mpnews) articles thumbnail",
        help="图文消息缩略图的media_id, 可以通过素材管理接口获得。此处thumb_media_id即上传接口返回的media_id",
    )
    mpnews_articles_author = fields.Char(
        "Graphic message (mpnews) articles author", help="图文消息的作者，不超过64个字节"
    )
    mpnews_articles_content_source_url = fields.Char(
        "Graphic message (mpnews) articles 'Read the original' page link",
        help="图文消息点击“阅读原文”之后的页面链接",
    )
    mpnews_articles_contentl = fields.Char(
        "Graphic message (mpnews) articles content",
        help="图文消息的内容，支持html标签，不超过666 K个字节（支持id转译）",
    )
    mpnews_articles_digest = fields.Char(
        "Graphic message (mpnews) articles digest",
        help="图文消息的描述，不超过512个字节，超过会自动截断（支持id转译）",
    )

    markdown_content = fields.Text(
        "Content", sanitize=False, help="markdown内容，最长不超过2048个字节，必须是utf8编码"
    )

    miniprogram_notice_appid = fields.Char(
        "Mini Program appid", help="小程序appid，必须是与当前小程序应用关联的小程序"
    )
    miniprogram_notice_page = fields.Char(
        "Mini Program Page", help="点击消息卡片后的小程序页面，仅限本小程序内的页面。该字段不填则消息点击后不跳转。",
    )
    miniprogram_notice_title = fields.Char(
        "Mini Program title", help="消息标题，长度限制4-12个汉字（支持id转译）",
    )
    miniprogram_notice_description = fields.Char(
        "Mini Program description", help="消息描述，长度限制4-12个汉字（支持id转译）",
    )
    miniprogram_notice_emphasis_first_item = fields.Boolean(
        "Mini Program description", help="是否放大第一个content_item",
    )
    miniprogram_notice_content_item = fields.Char(
        "Mini Program description", help="消息内容键值对，最多允许10个item",
    )

    taskcard_title = fields.Char(
        "Task card message title", help="标题，不超过128个字节，超过会自动截断（支持id转译）"
    )
    taskcard_description = fields.Html(
        "Task card message description", help="描述，不超过512个字节，超过会自动截断（支持id转译）"
    )
    taskcard_url = fields.Char(
        "Task card message url", help="点击后跳转的链接。最长2048字节，请确保包含了协议头(http/https)"
    )
    taskcard_task_id = fields.Char(
        "Task ID", help="任务id，同一个应用发送的任务卡片消息的任务id不能重复，只能由数字、字母和“_-@”组成，最长支持128字节",
    )
    taskcard_btn = fields.Char("Task card button list", help="按钮列表，按钮个数为1~2个。",)

    safe = fields.Selection(
        [
            ("0", "Shareable"),
            ("1", "Cannot share and content shows watermark"),
            ("2", "Only share within the company "),
        ],
        string="Secret message",
        required=True,
        default="1",
        readonly=True,
        help="表示是否是保密消息，0表示可对外分享，1表示不能分享且内容显示水印，2表示仅限在企业内分享，默认为0；注意仅mpnews类型的消息支持safe值为2，其他消息类型不支持",
    )

    enable_id_trans = fields.Boolean(
        string="Turn on id translation", help="表示是否开启id转译，0表示否，1表示是，默认0", default=False
    )
    enable_duplicate_check = fields.Boolean(
        string="Turn on duplicate message checking",
        help="表示是否开启重复消息检查，0表示否，1表示是，默认0",
        default=False,
    )
    duplicate_check_interval = fields.Integer(
        string="Time interval for repeated message checking",
        help="表示是否重复消息检查的时间间隔，默认1800s，最大不超过4小时",
        default="1800",
    )

    state = fields.Selection(
        [
            ("outgoing", "Outgoing"),
            ("sent", "Sent"),
            ("received", "Received"),
            ("exception", "Delivery Failed"),
            ("cancel", "Cancelled"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="outgoing",
    )

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if "notification" not in values and values.get("mail_message_id"):
                values["notification"] = True
            if values.get("use_templates") and len(values.get("to_user")) > 1:
                raise UserError(
                    _(
                        "In the test template message mode, only one user is allowed to send."
                    )
                )

        new_messages = super(WxWorkMessage, self).create(values_list)
        new_messages_w_attach = self
        for mail, values in zip(new_messages, values_list):
            if values.get("attachment_ids"):
                new_messages_w_attach += mail
        if new_messages_w_attach:
            new_messages_w_attach.mapped("attachment_ids").check(mode="read")

        return new_messages

    def write(self, vals):
        res = super(WxWorkMessage, self).write(vals)
        if vals.get("attachment_ids"):
            for mail in self:
                mail.attachment_ids.check(mode="read")
        if self.use_templates and len(self.to_user) > 1:
            raise UserError(
                _(
                    "In the test template message mode, only one user is allowed to send."
                )
            )
        return res

    # def unlink(self):
    #     # cascade-delete the parent message for all mails that are not created for a notification
    #     mail_msg_cascade_ids = [
    #         mail.mail_message_id.id for mail in self if not mail.notification
    #     ]
    #     res = super(WxWorkMessage, self).unlink()
    #     if mail_msg_cascade_ids:
    #         self.env["wxwork.message"].browse(mail_msg_cascade_ids).unlink()
    #     return res

    @api.onchange("use_templates")
    def _onchange_use_templates(self):
        if self.use_templates:
            self.to_party = None
            self.to_tag = None
            if len(self.to_user) > 1:
                raise UserError(
                    _(
                        "In the test template message mode, only one user is allowed to send."
                    )
                )
            else:
                pass
        else:
            self.markdown_content = None

    @api.onchange("templates_id")
    def _onchange_templates_id(self):
        if self.templates_id:
            mail_template_info = (
                self.env["mail.template"]
                .browse(self.templates_id.id)
                .read(["id", "body_html"])
            )
            self.markdown_content = mail_template_info[0]["body_html"]

    def send(self):
        """
        立即发送选定的消息，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的消息）。
        成功发送的消息被标记为“已发送”，而失败发送的消息被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。
        :param bool auto_commit: 发送每封消息后是否强制提交消息状态（仅用于调度程序处理）；
                                在正常传递中，绝对不能为True（默认值：False）
        :param bool raise_exception: 如果消息发送过程失败，是否引发异常
        :return: True
        """
        touser, toparty, totag = self.get_message_recipient_data()
        if self.use_templates:
            # 使用模板消息，暂时只使用MACKDOWN类型的消息模板
            template = self.markdown_content
            if template:
                pass
        else:
            # 不使用模板消息
            pass

    def get_message_recipient_data(self):
        """
        获取接收人数据：
        :returns:
            touser：成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty：部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
            totag：标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数
        """
        touser = ""
        toparty = ""
        totag = ""

        if len(self.to_user) == 1:
            touser = self.to_user.wxwork_id
        else:
            for employee in self.to_user:
                touser += employee.wxwork_id + "|"
            touser = touser[:-1]  # 移除最后一个字符

        if len(self.to_party) == 1:
            toparty = str(self.to_party.wxwork_department_id)
        else:
            for department in self.to_party:
                toparty += str(department.wxwork_department_id) + "|"
            toparty = toparty[:-1]  # 移除最后一个字符

        if len(self.to_tag) == 1:
            totag = str(self.to_tag.tagid)
        else:
            for category in self.to_tag:
                totag += str(category.tagid) + "|"
            totag = totag[:-1]  # 移除最后一个字符

        if self.to_all:
            touser = "@all"
            toparty = ""
            totag = ""
        else:
            if touser == "" and toparty == "" and totag == "":
                raise UserError(
                    _("Employee, department, and tag cannot be empty at the same time.")
                )

        return touser, toparty, totag

    def cancel(self):
        return self.write({"state": "cancel"})

