# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def send(self, auto_commit=False, raise_exception=False):
        """
        立即发送选定的电子邮件，而忽略它们的当前状态（除非已被重新发送，否则不应传递已发送的电子邮件）。
成功发送的电子邮件被标记为“已发送”，而失败发送的电子邮件被标记为“例外”，并且相应的错误邮件将输出到服务器日志中。
        :param bool auto_commit：发送每封邮件后是否强制提交邮件状态（仅用于调度程序处理）；
                 在正常发送绝对不能为True（默认值：False） 
        :param bool raise_exception：如果电子邮件发送过程失败，是否引发异常 
        :return: True
        """
        # print(self)

        return super(MailMail, self).send(auto_commit=False, raise_exception=False)
