odoo.define('wecom_widget.wecom_message_widget', function (require) {
    "use strict";

    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var FieldTextEmojis = require('mail.field_text_emojis');

    var _t = core._t;
    /**
     * wecom_message_widget是一个小部件，用于显示文本区域（正文）和字符数量的文本。 每次用户更改身体时都会计算此文本。
     * 页面中必须有 <field name="msgtype" />  
     */
    var WeComMessageWidget = FieldTextEmojis.extend({
        className: 'o_field_text',
        enableEmojis: false,
        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            // this.set_message_type();
            this.nbrChar = 0;

            // this.nbrSMS = 0;
            // this.encoding = 'GSM7';
            this.enableEmojis = false;
            // this.msgtype = this.get_message_type(this.nodeOptions.msgtype_field);
        },
        start: function () {
            this._super.apply(this, arguments);
            if (this.mode === 'edit') {
                console.log(this.$input);
            }
        },
        /**
         * @override
         *"This will add the emoji dropdown to a target field (controlled by the "enableEmojis" attribute)
         */
        on_attach_callback: function () {
            if (this.enableEmojis) {
                this._super.apply(this, arguments);
            }
        },

        //--------------------------------------------------------------------------
        // Private:覆盖小部件 
        //--------------------------------------------------------------------------
        get_message_type: function (type) {
            var result = [];
            switch (type) {
                case "text":
                    result = [_t("Text message"), _t("The maximum length is 256 characters.")];
                    break;
                case "image":
                    result = [_t("Picture message"), ""];
                    break;
                case "voice":
                    result = [_t("Voice message"), ""];
                    break;
                case "video":
                    result = [_t("Video message"), _t("Title, no more than 16 characters, will be automatically truncated if it exceeds; Description, no more than 64 characters, will be automatically truncated if it exceeds.")];
                    break;
                case "file":
                    result = [_t("File message"), ""];
                    break;
                case "textcard":
                    result = [_t("Text card message"), _t("Title, cannot exceed 16 characters, it will be automatically truncated if it exceeds;Description, cannot exceed 64 characters, it will be automatically truncated if it exceeds;URL link, cannot exceed 256 characters, please make sure to include the protocol header (http/https).")];
                    break;
                case "news":
                    result = [_t("Graphic message"), _t("Title, cannot exceed 16 characters, it will be automatically truncated if it exceeds;Description, cannot exceed 64 characters, it will be automatically truncated if it exceeds;URL link, no more than 256 characters, please make sure to include the protocol header (http/https); picture link, support JPG, PNG format, better effect is 1068*455 for large images and 150*150 for small images. ")];
                    break;
                case "mpnews":
                    result = [_t("Graphic message(mpnews)"), _t("Title, cannot exceed 16 characters, it will be automatically truncated if it exceeds;Author, cannot exceed 8 characters;                    Content, supports html tags, cannot exceed 83250 characters;Description, cannot exceed 512 bytes, it will be automatically truncated if it exceeds;")];
                    break;
                case "markdown":
                    result = [_t("Markdown message"), _t("The maximum length cannot exceed 256 characters and must be utf8 encoding. ")];
                    break;
                case "miniprogram":
                    result = [_t("Mini Program Notification Message"), ""];
                    break;
                case "taskcard":
                    result = [_t("Task card message"), _t("Title, cannot exceed 16 characters, it will be automatically truncated if it exceeds;Description, cannot exceed 64 characters, it will be automatically truncated if it exceeds;Link, the maximum length is 256 characters, please make sure to include the protocol header (http/https). ")];
                    break;
                default:
                    result = [_t("Unknown type"), ""];
            }
            return result;
        },
        /**
         * @private
         * @override
         */
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);

            this.set_message_type();
            this._compute();
            $('.o_message_container').remove();
            var $message_container = $('<div class="o_message_container"/>');
            $message_container.append(this._renderMessageInfo());
            // $message_container.append(this._renderIAPButton());
            this.$el = this.$el.add($message_container);

            return def;
        },

        //--------------------------------------------------------------------------
        // Private: SMS
        //--------------------------------------------------------------------------

        /**
         * Compute the number of characters and sms
         * @private
         */
        _compute: function () {
            var content = this._getValue();
            // this.encoding = this._extractEncoding(content);
            this.nbrChar = content.length;
            this.nbrChar += (content.match(/\n/g) || []).length;
            // this.nbrSMS = this._countMessage(this.nbrChar, this.encoding);

        },
        set_message_type: function () {
            var self = this;
            // console.log(this);
            // setTimeout(function () {
            //     // console.log(this.$input.parents("o_form_view"));
            //     // console.log(this.$input.parent());
            //     console.log(this.$input);
            // }, 3000);

            // console.log(self.$el[0].parents("o_form_view"));
            // console.log(this.record);
            this.msgtype = this.get_message_type(this.record['data']['msgtype'])[0];
            this.description = this.get_message_type(this.record['data']['msgtype'])[1];
        },
        /**
         * Count the number of SMS of the content
         * @private
         * @returns {integer} Number of SMS
         */
        // _countMessage: function () {
        //     if (this.nbrChar === 0) {
        //         return 0;
        //     }
        //     if (this.encoding === 'UNICODE') {
        //         if (this.nbrChar <= 70) {
        //             return 1;
        //         }
        //         return Math.ceil(this.nbrChar / 67);
        //     }
        //     if (this.nbrChar <= 160) {
        //         return 1;
        //     }
        //     return Math.ceil(this.nbrChar / 153);
        // },

        /**
         * Extract the encoding depending on the characters in the content
         * @private
         * @param {String} content Content of the SMS
         * @returns {String} Encoding of the content (GSM7 or UNICODE)
         */
        _extractEncoding: function (content) {
            if (String(content).match(RegExp("^[@£$¥èéùìòÇ\\nØø\\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\\\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà]*$"))) {
                return 'GSM7';
            }
            return 'UNICODE';
        },

        /**
         * Render the IAP button to redirect to IAP pricing
         * @private
         */
        _renderIAPButton: function () {
            return $('<a>', {
                'href': 'https://iap-services.odoo.com/iap/sms/pricing',
                'target': '_blank',
                'title': _t('SMS Pricing'),
                'aria-label': _t('SMS Pricing'),
                'class': 'fa fa-lg fa-info-circle',
            });
        },

        /**
         * Render the number of characters, sms and the encoding.
         * @private
         */
        _renderMessageInfo: function () {
            // var string = _.str.sprintf(_t('Message type: %s, %s characters, fits in %s SMS (%s) '), this.msgtype, this.nbrChar, this.nbrSMS, this.encoding);
            var string = _.str.sprintf(_t('Message type: %s, %s characters, %s'), this.msgtype, this.nbrChar, this.description);
            var $span = $('<span>', {
                'class': 'text-muted o_message_count',
            });
            $span.text(string);
            return $span;
        },

        /**
         * Update widget SMS information with re-computed info about length, ...
         * @private
         */
        _updateMessageInfo: function () {
            this._compute();
            // var string = _.str.sprintf(_t('%s characters, fits in %s SMS (%s) '), this.nbrChar, this.nbrSMS, this.encoding);
            var string = _.str.sprintf(_t('Message type: %s, %s characters, %s'), this.msgtype, this.nbrChar, this.description);
            this.$('.o_message_count').text(string);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         * 失去焦点
         */
        _onBlur: function () {
            var content = this._getValue();
            if (!content.trim().length && content.length > 0) {
                this.do_warn(_t("Your Message must include at least one non-whitespace character"));
                this.$input.val(content.trim());
                this._updateMessageInfo();
            }
        },

        /**
         * @override
         * @private
         */
        _onChange: function () {
            this._super.apply(this, arguments);
            this._updateMessageInfo();
        },

        /**
         * @override
         * @private
         */
        _onInput: function () {
            this._super.apply(this, arguments);
            this._updateMessageInfo();
        },
    });

    fieldRegistry.add('wecom_message_widget', WeComMessageWidget);

    return WeComMessageWidget;
});