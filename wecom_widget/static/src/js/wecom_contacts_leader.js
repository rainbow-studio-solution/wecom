// *-------------------------------------------------------
// * 企业微信通讯录 部门负责人 展示组件
// * 注意视图中必须含有 <field name="company_id" /> <field name="department" />
// *-------------------------------------------------------
odoo.define('wecom.wecom_contacts_leader', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var session = require('web.session');
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;

    var WecomContactLeader = AbstractField.extend({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.is_leader = params.data[state]; // 字段值
            this.current_company_id = this.data["company_id"].res_id;
            this.department = this.data["department"]; //部门列表字符串
            // console.log(this.department)
            // console.log(this.is_leader)
        },
        _renderEdit: function () {
            this._prepareInput(this.$el);
        },
        _renderReadonly: function () {
            var self = this;

            if (jQuery.isEmptyObject(JSON.parse(self.is_leader)) || self.is_leader == "") {
                return;
            } else if (jQuery.isEmptyObject(JSON.parse(self.department)) || self.department == "") {
                return;
            } else {
                self.is_leader = JSON.parse(self.is_leader);
                self.department = JSON.parse(self.department);
                if (self.is_leader.length > 0 && self.department.length > 0) {
                    self._renderWecomContactLeader();
                }
            }
        },
        _prepareInput: function ($el) {
            return this.$el;
        },
        _renderWecomContactLeader: async function () {
            var self = this;
            let departments = this.department;
            let is_leaders = this.is_leader;
            let new_departments = [];

            //遍历部门列表，获取部门名称
        },
        hasKey(key, obj) {
            if (obj.hasOwnProperty(key)) {
                return true;
            } else {
                return false;
            }
        }
    });

    fieldRegistry.add('wecom_contacts_leader', WecomContactLeader);

    return {
        WecomContactLeader: WecomContactLeader,
    };
});