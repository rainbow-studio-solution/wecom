# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class MassMailing(models.Model):
    _name = "wxwork.message.sending"
    _description = "Enterprise WeChat message sending"

    subject = fields.Char(
        "Subject", help="Subject of your Mailing", required=True, translate=True
    )

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

    use_templates = fields.Boolean("Use templates", translate=True)
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

    markdown_content = fields.Text("Content", help="markdown内容，最长不超过2048个字节，必须是utf8编码")

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

