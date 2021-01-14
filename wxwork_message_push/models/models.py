# -*- coding: utf-8 -*-


from lxml.builder import E

from odoo import api, models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = "base"

    # def _message_get_default_recipients(self):
    #     """
    #     用于查找要在记录集上发送邮件的默认收件人的通用实现。 此方法是可用于所有模型的通用实现，因为我们可以在不继承自mail.thread的模型上通过邮件模板发送电子邮件。

    #     在特定模型上重写此方法以实现特定于模型的行为。 还可以考虑从mail.thread继承。
    #     """
    #     res = {}
    #     for record in self:
    #         recipient_ids, email_to, email_cc = [], False, False
    #         if "partner_id" in record and record.partner_id:
    #             recipient_ids.append(record.partner_id.id)
    #         elif "email_normalized" in record and record.email_normalized:
    #             email_to = record.email_normalized
    #         elif "email_from" in record and record.email_from:
    #             email_to = record.email_from
    #         elif "partner_email" in record and record.partner_email:
    #             email_to = record.partner_email
    #         elif "email" in record and record.email:
    #             email_to = record.email
    #         res[record.id] = {
    #             "partner_ids": recipient_ids,
    #             "email_to": email_to,
    #             "email_cc": email_cc,
    #         }
    #     return super(BaseModel, self)._message_get_default_recipients()
