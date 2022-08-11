//----------------------------------------
// 企业微信通讯录展示组件
//----------------------------------------
odoo.define('wecom.wecom_contacts_display', function (require) {
    "use strict";
    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var session = require('web.session');
    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');
    var QWeb = core.qweb;

    var WecomContactDisplay = AbstractField.extend({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.template_content = params.data[state]; // 字段值
            this.control_type = self.nodeOptions.type; // 控件类型:user,department
            this.show_type = self.nodeOptions.show; // 显示类型：simple，details
        },
        _renderEdit: function () {
            this._prepareInput(this.$el);
        },
        _renderReadonly: function () {
            var self = this;

            if (jQuery.isEmptyObject(JSON.parse(self.template_content)) || self.template_content == "") {
                return;
            } else {
                self.template_content = JSON.parse(self.template_content);
                if (this.template_content.length > 0) {
                    self._renderWecomUsersDisplaySimple();
                }
            }
        },
        _prepareInput: function ($el) {
            return this.$el;
        },
        _renderWecomUsersDisplaySimple: function () {
            var self = this;
            let rows = this.template_content;
            if (this.control_type == null || this.control_type == "") {
                return;
            } else if (this.show_type == null || this.show_type == "") {
                return;
            } else {
                let template_name = "";
                let model_name = "";
                let data_dic = {};
                let fields = [];
                let domain_key = "";

                if (this.control_type === 'user') {
                    template_name = "WecomUsers";
                    model_name = "wecom.user";
                    fields = ["name", "alias", "userid", "mobile", "main_department", "thumb_avatar", "gender"];
                    domain_key = "userid";
                    data_dic = {
                        users: rows
                    }
                }
                if (this.control_type === 'department') {
                    template_name = "WecomDepartments";
                    model_name = "wecom.department";
                    domain_key = "userid";
                    data_dic = {
                        departments: rows
                    }
                }
                if (this.show_type === 'simple') {
                    template_name = template_name + "Simple";
                    data_dic = {
                        departments: rows
                    }
                }
                if (this.show_type === 'details') {
                    template_name = template_name + "Details";
                    data_dic = {
                        departments: rows
                    }
                }
                const current_selected_company_id = session.user_context.allowed_company_ids[0];
                _.forEach(rows, function (row) {
                    self._rpc({
                        model: model_name,
                        method: 'search_read',
                        fields: fields,
                        domain: [
                            ['company_id', '=', current_selected_company_id],
                            [domain_key, '=', row]
                        ],
                    }).then(function (data) {
                        console.log(data);
                    });
                });

                let $control = $(QWeb.render(template_name, data_dic));
                $control.appendTo(this.$el);
            }
        }
    });

    fieldRegistry.add('wecom_contact_display', WecomContactDisplay);

    return {
        WecomContactDisplay: WecomContactDisplay,
    };
});