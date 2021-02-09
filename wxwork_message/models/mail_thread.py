# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields
from odoo.addons.phone_validation.tools import phone_validation
from odoo.tools import html2plaintext, plaintext2html

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    wxwork_message_has_error = fields.Boolean(
        "Enterprise WeChat Message Delivery error",
        compute="_compute_wxwork_message_has_error",
        search="_search_wxwork_message_has_error",
        help="如果选中，则某些邮件有传递错误。 ",
    )

    def _compute_wxwork_message_has_error(self):
        res = {}
        if self.ids:
            self._cr.execute(
                """ SELECT msg.res_id, COUNT(msg.res_id) FROM mail_message msg
                                 RIGHT JOIN mail_message_res_partner_needaction_rel rel
                                 ON rel.mail_message_id = msg.id AND rel.notification_type = 'wxwork' AND rel.notification_status in ('exception')
                                 WHERE msg.author_id = %s AND msg.model = %s AND msg.res_id in %s AND msg.message_type != 'user_notification'
                                 GROUP BY msg.res_id
                """,
                (self.env.user.partner_id.id, self._name, tuple(self.ids),),
            )
            res.update(self._cr.fetchall())

        for record in self:
            record.wxwork_message_has_error = bool(res.get(record._origin.id, 0))

    @api.model
    def _search_wxwork_message_has_error(self, operator, operand):
        return [
            "&",
            ("message_ids.has_wxwork_error", operator, operand),
            ("message_ids.author_id", "=", self.env.user.partner_id.id),
        ]

    def _wxwork_message_get_partner_fields(self):
        """ 
        发送企业微信消息时，此方法返回用于查找要链接的联系人的字段。 不需要伴侣，仅可以包含企业微信用户ID字段。 但是，在拥有合作伙伴时，它为通知管理提供了更大的灵活性。 
        """
        fields = []
        if hasattr(self, "partner_id"):
            fields.append("partner_id")
        if hasattr(self, "partner_ids"):
            fields.append("partner_ids")
        return fields

    def _wxwork_message_get_default_partners(self):
        """ 
        继承的模型可能需要重写此方法。
        :returns partners: recordset of res.partner
        """
        partners = self.env["res.partner"]
        for fname in self._wxwork_message_get_partner_fields():
            partners |= self.mapped(fname)
        return partners

    def _wxwork_message_get_userid_fields(self):
        """ 
        此方法返回用于查找记录上发送企业微信消息的用户id的字段。
        """
        return ["wxwork_id"]

    def _sms_get_recipients_info(self, force_field=False, partner_fallback=True):
        """"
        获取有关当前记录集的企业微信兄欧系收件人信息。 此方法检查数字和卫生状况以集中计算。 

        用例范例 

          * click on a field -> number is actually forced from field, find customer
            linked to record, force its number to field or fallback on customer fields;
          * contact -> find numbers from all possible phone fields on record, find
            customer, force its number to found field number or fallback on customer fields;

        :param force_field: either give a specific field to find phone number, either
            generic heuristic is used to find one based on ``_wxwork_message_get_userid_fields``;
        :param partner_fallback: if no value found in the record, check its customer
            values based on ``_wxwork_message_get_default_partners``;

        :return dict: record.id: {
            'partner': a res.partner recordset that is the customer (void or singleton)
                linked to the recipient. See ``_wxwork_message_get_default_partners``;
            'sanitized': sanitized number to use (coming from record's field or partner's
                phone fields). Set to False is number impossible to parse and format;
            'number': original number before sanitation;
            'partner_store': whether the number comes from the customer phone fields. If
                False it means number comes from the record itself, even if linked to a
                customer;
            'field_store': field in which the number has been found (generally mobile or
                phone, see ``_wxwork_message_get_userid_fields``);
        } for each record in self
        """
        result = dict.fromkeys(self.ids, False)
        tocheck_fields = (
            [force_field] if force_field else self._wxwork_message_get_userid_fields()
        )
        for record in self:
            all_numbers = [record[fname] for fname in tocheck_fields if fname in record]
            all_partners = record._wxwork_message_get_default_partners()

            valid_number = False
            for fname in [f for f in tocheck_fields if f in record]:
                valid_number = phone_validation.phone_sanitize_numbers_w_record(
                    [record[fname]], record
                )[record[fname]]["sanitized"]
                if valid_number:
                    break

            if valid_number:
                result[record.id] = {
                    "partner": all_partners[0]
                    if all_partners
                    else self.env["res.partner"],
                    "sanitized": valid_number,
                    "number": record[fname],
                    "partner_store": False,
                    "field_store": fname,
                }
            elif all_partners and partner_fallback:
                partner = self.env["res.partner"]
                for partner in all_partners:
                    for fname in self.env[
                        "res.partner"
                    ]._wxwork_message_get_userid_fields():
                        valid_number = phone_validation.phone_sanitize_numbers_w_record(
                            [partner[fname]], record
                        )[partner[fname]]["sanitized"]
                        if valid_number:
                            break

                if not valid_number:
                    fname = (
                        "mobile"
                        if partner.mobile
                        else ("phone" if partner.phone else "mobile")
                    )

                result[record.id] = {
                    "partner": partner,
                    "sanitized": valid_number if valid_number else False,
                    "number": partner[fname],
                    "partner_store": True,
                    "field_store": fname,
                }
            else:
                # 找不到任何经过清理的数字->将第一个设置值作为后备；
                # 如果没有，则将False分配给第一个可用数字字段
                value, fname = next(
                    (
                        (value, fname)
                        for value, fname in zip(all_numbers, tocheck_fields)
                        if value
                    ),
                    (False, tocheck_fields[0] if tocheck_fields else False),
                )
                result[record.id] = {
                    "partner": self.env["res.partner"],
                    "sanitized": False,
                    "number": value,
                    "partner_store": False,
                    "field_store": fname,
                }
        return result

    def _wxwork_message_schedule_mass(
        self, body="", template=False, active_domain=None, **composer_values
    ):
        """ 
        安排在记录集上发送大量企业微信消息的快捷方法。

        :param template: an optional sms.template record;
        :param active_domain: bypass self.ids and apply composer on active_domain
          instead;
        """
        composer_context = {
            "default_res_model": self._name,
            "default_composition_mode": "mass",
            "default_template_id": template.id if template else False,
            "default_body": body if body and not template else False,
        }
        if active_domain is not None:
            composer_context["default_use_active_domain"] = True
            composer_context["default_active_domain"] = repr(active_domain)
        else:
            composer_context["default_res_ids"] = self.ids

        create_vals = {
            "mass_force_send": False,
            "mass_keep_log": True,
        }
        if composer_values:
            create_vals.update(composer_values)

        composer = (
            self.env["sms.composer"]
            .with_context(**composer_context)
            .create(create_vals)
        )
        return composer._action_send_sms()

    def _message_wxwork_with_template(
        self,
        template=False,
        template_xmlid=False,
        template_fallback="",
        partner_ids=False,
        **kwargs
    ):
        """ 
        wxwork.template执行_message_wxwork的快捷方法。

        :param template: a valid sms.template record;
        :param template_xmlid: XML ID of an sms.template (if no template given);
        :param template_fallback: plaintext (jinja-enabled) in case template
          and template xml id are falsy (for example due to deleted data);
        """
        self.ensure_one()
        if not template and template_xmlid:
            template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if template:
            body = template._render_field("body", self.ids, compute_lang=True)[self.id]
        else:
            body = self.env["sms.template"]._render_template(
                template_fallback, self._name, self.ids
            )[self.id]
        return self._message_wxwork(body, partner_ids=partner_ids, **kwargs)

    def _message_wxwork(
        self,
        body,
        subtype_id=False,
        partner_ids=False,
        number_field=False,
        sms_numbers=None,
        sms_pid_to_number=None,
        **kwargs
    ):
        """ 
        使用基于企业微信的通知方法在记录上发布消息的主要方法。 

        :param body: content of SMS;
        :param subtype_id: mail.message.subtype used in mail.message associated
          to the sms notification process;
        :param partner_ids: if set is a record set of partners to notify;
        :param number_field: if set is a name of field to use on current record
          to compute a number to notify;
        :param sms_numbers: see ``_notify_record_by_wxwork``;
        :param sms_pid_to_number: see ``_notify_record_by_wxwork``;
        """
        self.ensure_one()
        sms_pid_to_number = sms_pid_to_number if sms_pid_to_number is not None else {}

        if number_field or (partner_ids is False and sms_numbers is None):
            info = self._sms_get_recipients_info(force_field=number_field)[self.id]
            info_partner_ids = info["partner"].ids if info["partner"] else False
            info_number = info["sanitized"] if info["sanitized"] else info["number"]
            if info_partner_ids and info_number:
                sms_pid_to_number[info_partner_ids[0]] = info_number
            if info_partner_ids:
                partner_ids = info_partner_ids + (partner_ids or [])
            if not info_partner_ids:
                if info_number:
                    sms_numbers = [info_number] + (sms_numbers or [])
                    # will send a falsy notification allowing to fix it through SMS wizards
                elif not sms_numbers:
                    sms_numbers = [False]

        if subtype_id is False:
            subtype_id = self.env["ir.model.data"].xmlid_to_res_id("mail.mt_note")

        return self.message_post(
            body=plaintext2html(html2plaintext(body)),
            partner_ids=partner_ids
            or [],  # TDE FIXME: temp fix otherwise crash mail_thread.py
            message_type="sms",
            subtype_id=subtype_id,
            sms_numbers=sms_numbers,
            sms_pid_to_number=sms_pid_to_number,
            **kwargs
        )

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        recipients_data = super(MailThread, self)._notify_thread(
            message, msg_vals=msg_vals, **kwargs
        )
        self._notify_record_by_wxwork(
            message, recipients_data, msg_vals=msg_vals, **kwargs
        )
        return recipients_data

    def _notify_record_by_wxwork(
        self,
        message,
        recipients_data,
        msg_vals=False,
        sms_numbers=None,
        sms_pid_to_number=None,
        check_existing=False,
        put_in_queue=False,
        **kwargs
    ):
        """ 
        通知方式：通过企业微信。 

        :param message: mail.message record to notify;
        :param recipients_data: see ``_notify_thread``;
        :param msg_vals: see ``_notify_thread``;

        :param sms_numbers: additional numbers to notify in addition to partners
          and classic recipients;
        :param pid_to_number: force a number to notify for a given partner ID
              instead of taking its mobile / phone number;
        :param check_existing: check for existing notifications to update based on
          mailed recipient, otherwise create new notifications;
        :param put_in_queue: use cron to send queued SMS instead of sending them
          directly;
        """
        sms_pid_to_number = sms_pid_to_number if sms_pid_to_number is not None else {}
        sms_numbers = sms_numbers if sms_numbers is not None else []
        sms_create_vals = []
        sms_all = self.env["sms.sms"].sudo()

        # pre-compute SMS data
        body = msg_vals["body"] if msg_vals and msg_vals.get("body") else message.body
        sms_base_vals = {
            "body": html2plaintext(body),
            "mail_message_id": message.id,
            "state": "outgoing",
        }

        # notify from computed recipients_data (followers, specific recipients)
        partners_data = [r for r in recipients_data["partners"] if r["notif"] == "sms"]
        partner_ids = [r["id"] for r in partners_data]
        if partner_ids:
            for partner in self.env["res.partner"].sudo().browse(partner_ids):
                number = (
                    sms_pid_to_number.get(partner.id) or partner.mobile or partner.phone
                )
                sanitize_res = phone_validation.phone_sanitize_numbers_w_record(
                    [number], partner
                )[number]
                number = sanitize_res["sanitized"] or number
                sms_create_vals.append(
                    dict(sms_base_vals, partner_id=partner.id, number=number)
                )

        # notify from additional numbers
        if sms_numbers:
            sanitized = phone_validation.phone_sanitize_numbers_w_record(
                sms_numbers, self
            )
            tocreate_numbers = [
                value["sanitized"] or original for original, value in sanitized.items()
            ]
            sms_create_vals += [
                dict(
                    sms_base_vals,
                    partner_id=False,
                    number=n,
                    state="outgoing" if n else "error",
                    error_code="" if n else "sms_number_missing",
                )
                for n in tocreate_numbers
            ]

        # create sms and notification
        existing_pids, existing_numbers = [], []
        if sms_create_vals:
            sms_all |= self.env["sms.sms"].sudo().create(sms_create_vals)

            if check_existing:
                existing = (
                    self.env["mail.notification"]
                    .sudo()
                    .search(
                        [
                            "|",
                            ("res_partner_id", "in", partner_ids),
                            "&",
                            ("res_partner_id", "=", False),
                            ("sms_number", "in", sms_numbers),
                            ("notification_type", "=", "sms"),
                            ("mail_message_id", "=", message.id),
                        ]
                    )
                )
                for n in existing:
                    if (
                        n.res_partner_id.id in partner_ids
                        and n.mail_message_id == message
                    ):
                        existing_pids.append(n.res_partner_id.id)
                    if (
                        not n.res_partner_id
                        and n.sms_number in sms_numbers
                        and n.mail_message_id == message
                    ):
                        existing_numbers.append(n.sms_number)

            notif_create_values = [
                {
                    "mail_message_id": message.id,
                    "res_partner_id": sms.partner_id.id,
                    "sms_number": sms.number,
                    "notification_type": "sms",
                    "sms_id": sms.id,
                    "is_read": True,  # discard Inbox notification
                    "notification_status": "ready"
                    if sms.state == "outgoing"
                    else "exception",
                    "failure_type": "" if sms.state == "outgoing" else sms.error_code,
                }
                for sms in sms_all
                if (sms.partner_id and sms.partner_id.id not in existing_pids)
                or (not sms.partner_id and sms.number not in existing_numbers)
            ]
            if notif_create_values:
                self.env["mail.notification"].sudo().create(notif_create_values)

            if existing_pids or existing_numbers:
                for sms in sms_all:
                    notif = next(
                        (
                            n
                            for n in existing
                            if (
                                n.res_partner_id.id in existing_pids
                                and n.res_partner_id.id == sms.partner_id.id
                            )
                            or (
                                not n.res_partner_id
                                and n.sms_number in existing_numbers
                                and n.sms_number == sms.number
                            )
                        ),
                        False,
                    )
                    if notif:
                        notif.write(
                            {
                                "notification_type": "sms",
                                "notification_status": "ready",
                                "sms_id": sms.id,
                                "sms_number": sms.number,
                            }
                        )

        if sms_all and not put_in_queue:
            sms_all.filtered(lambda sms: sms.state == "outgoing").send(
                auto_commit=False, raise_exception=False
            )

        return True
