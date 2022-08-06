//---------------------------------------------------------------------------
// 企业微信打卡规则- WiFi打卡信息 渲染小部件
//---------------------------------------------------------------------------

odoo.define('wecom_attendance.loc_infos', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;

    var WecomAttendanceLocInfos = AbstractField.extend({
        className: 'wecom_attendance_view',
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.template_content = params.data["loc_infos"]
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

            _.forEach(rows, function (row) {
                for (var key in row) {
                    if (key == 'lat' || key == 'lng') {
                        row[key] = self.transformLatAndLng(row[key]);
                    }
                }

            });
            let $control = $(QWeb.render('WecomAttendance.Location', {
                rows: rows,
            }));
            $control.appendTo(this.$el);
        },
        transformLatAndLng: function (value) {
            // 位置打卡地点纬度和精度，是实际纬度和维度的1000000倍，与腾讯地图一致采用GCJ-02坐标系统标准
            return value / 1000000;
        },
    });
    fieldRegistry.add('wecom_attendance_loc_infos', WecomAttendanceLocInfos);

    return {
        WecomAttendanceLocInfos: WecomAttendanceLocInfos,
    };
});