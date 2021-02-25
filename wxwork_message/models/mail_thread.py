# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields
from odoo.addons.phone_validation.tools import phone_validation
from odoo.tools import html2plaintext, plaintext2html

from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
from odoo.exceptions import MissingError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """ 
    邮件线程模型被任何需要作为讨论主题的模型所继承，消息可以附加在讨论主题上。
    公共方法的前缀是``message```以避免与将从此类继承的模型的方法发生名称冲突。

  
    ``mail.thread``定义用于处理和显示通信历史记录的字段。
    ``mail.thread``还管理继承类的跟随者。所有功能和预期行为都由管理 mail.thread. 
    Widgets是为7.0及以下版本的Odoo设计的。

    实现任何方法都不需要继承类，因为默认实现适用于任何模型。
    但是，在处理传入电子邮件时，通常至少重写``message_new``和``message_update``方法（调用``super``），以便在创建和更新线程时添加特定于模型的行为。

    选项:
        - _mail_flat_thread: 
            如果设置为True，则所有没有parent_id的邮件将自动附加到发布在源上的第一条邮件。
            如果设置为False，则使用线程显示Chatter，并且不会自动设置parent_id。

    MailThread特性可以通过上下文键进行某种程度的控制 :

     - ``mail_create_nosubscribe``: 在创建或消息发布时，不要向记录线程订阅uid
     - ``mail_create_nolog``: 在创建时，不要记录自动的'<Document>created'消息
     - ``mail_notrack``: 在创建和写入时，不要执行值跟踪创建消息
     - ``tracking_disable``: 在创建和写入时，不执行邮件线程功能（自动订阅、跟踪、发布…）
     - ``mail_notify_force_send``: 如果要发送的电子邮件通知少于50个，请直接发送，而不是使用队列；默认情况下为True
    """

    _inherit = "mail.thread"

    # ------------------------------------------------------
    # 增加、查询、修改、删除
    # CRUD
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 模型/CRUD助手
    # MODELS / CRUD HELPERS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 包装和工具
    # WRAPPERS AND TOOLS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 追踪/记录
    # TRACKING / LOG
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 邮件网关
    # MAIL GATEWAY
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 收件人管理工具
    # RECIPIENTS MANAGEMENT TOOLS
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 消息发布API
    # MESSAGE POST API
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 消息发布工具
    # MESSAGE POST TOOLS
    # ------------------------------------------------------

    def _message_compute_author(
        self, author_id=None, email_from=None, raise_exception=True
    ):
        """ 
        计算消息的作者信息的工具方法。目的是确保发送电子邮件时，作者/当前用户/电子邮件地址之间的最大一致性。
        """
        if author_id is None:
            if email_from:
                author = self._mail_find_partner_from_emails([email_from])[0]
            else:
                author = self.env.user.partner_id
                email_from = author.email_formatted
            author_id = author.id

        if email_from is None:
            if author_id:
                author = self.env["res.partner"].browse(author_id)
                email_from = author.email_formatted

        # 没有作者电子邮件的超级用户模式->可能是公共用户；无论如何，我们不想崩溃
        if not email_from and not self.env.su and raise_exception:
            raise exceptions.UserError(
                _("Unable to log message, please configure the sender's email address.")
            )

        return author_id, email_from

    # ------------------------------------------------------
    # 通知API
    # NOTIFICATION API
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 关注者API
    # FOLLOWERS API
    # ------------------------------------------------------

    # ------------------------------------------------------
    # 控制器
    # CONTROLLERS
    # ------------------------------------------------------
