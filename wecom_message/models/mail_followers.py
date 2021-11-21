# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Followers(models.Model):
    _inherit = ["mail.followers"]

    def _get_recipient_data(
        self, records, message_type, subtype_id, pids=None, cids=None
    ):
        if message_type == "wxwork":
            if pids is None:
                sms_pids = records._wecom_message_get_partner_fields().ids
            else:
                sms_pids = pids
            res = super(Followers, self)._get_recipient_data(
                records, message_type, subtype_id, pids=pids, cids=cids
            )
            new_res = []
            for pid, cid, pactive, pshare, ctype, notif, groups in res:
                if pid and pid in sms_pids:
                    notif = "wxwork"
                new_res.append((pid, cid, pactive, pshare, ctype, notif, groups))
            return new_res
        else:
            return super(Followers, self)._get_recipient_data(
                records, message_type, subtype_id, pids=pids, cids=cids
            )
