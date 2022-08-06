//---------------------------------------------------------------------------
// 企业微信打卡规则- WiFi打卡信息 渲染小部件
//---------------------------------------------------------------------------

odoo.define('wecom_attendance.wifimac', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;

    var WecomAttendanceWifimac = AbstractField.extend({
        className: 'wecom_attendance_view',
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.template_content = params.data["wifimac_infos"]
        },
        _renderEdit: function () {
            this._prepareInput(this.$el);
        },
        _renderReadonly: function () {
            var self = this;
            this.$el.removeClass("o_field_widget");

            if (jQuery.isEmptyObject(JSON.parse(this.template_content)) || this.template_content == "") {
                return;
            } else {
                this.template_content = JSON.parse(this.template_content);
                if (this.template_content.length > 0) {
                    self._renderWifimac();
                }
            }
        },
        _prepareInput: function ($el) {
            return this.$el;
        },
        _renderWifimac: function () {
            var self = this;
            let rows = this.template_content;

            let $control = $(QWeb.render('WecomAttendance.Wifimac', {
                rows: rows,
            }));
            $control.appendTo(this.$el);
        },
        changeSecondsToHours: function (seconds) {
            // 将秒转化成 HH:mm 格式
            const time = moment.duration(seconds, 'seconds');
            const hours = time.hours();
            const minutes = time.minutes();
            return moment({
                h: hours,
                m: minutes
            }).format('HH:mm');
        },
    });
    fieldRegistry.add('wecom_attendance_wifimac', WecomAttendanceWifimac);

    return {
        WecomAttendanceWifimac: WecomAttendanceWifimac,
    };
});