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
        events: _.extend({
            'mouseover .user_simple': '_onShowUserCard',
            'mouseout .user_simple': '_onHideUserCard',
        }, AbstractField.prototype.events),
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.template_content = params.data[state]; // 字段值
            this.control_type = this.nodeOptions.type; // 控件类型:user,department
            this.show_type = this.nodeOptions.show; // 显示类型：simple，details
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
        _renderWecomUsersDisplaySimple: async function () {
            var self = this;
            let contacts = this.template_content;
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
                let control_key = {};

                if (this.control_type === 'user') {
                    template_name = "WecomUsers";
                    model_name = "wecom.user";
                    fields = ["name", "alias", "userid", "mobile", "department_complete_name", "thumb_avatar", "gender", "position"];
                    domain_key = "userid";
                    domain_key = "userid";
                    control_key = "users";
                }
                if (this.control_type === 'department') {
                    template_name = "WecomDepartments";
                    model_name = "wecom.department";
                    domain_key = "userid";
                    control_key = "departments";
                }
                if (this.show_type === 'simple') {
                    template_name = template_name + "Simple";
                }
                if (this.show_type === 'details') {
                    template_name = template_name + "Details";
                }

                const current_selected_company_id = session.user_context.allowed_company_ids[0];

                self._rpc({
                    model: model_name,
                    method: 'search_read',
                    fields: fields,
                    domain: [
                        ['company_id', '=', current_selected_company_id],
                        [domain_key, 'in', contacts]
                    ],
                }).then(function (rows) {
                    // console.log(typeof (rows), rows);
                    let $control = $(QWeb.render(template_name, {
                        rows: rows,
                    }));
                    $control.appendTo(self.$el);
                })
            }
        },
        _onShowUserCard: function (ev) {
            let badge = ev.currentTarget;
            let card = $(badge).next().clone(); // 克隆card,并去掉o_hidden样式
            $(badge).data("content", card.html()); // 将card的html内容存储到data-content中
            $(badge).popover({
                template: '<div class="popover wecom_contacts_popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header text-center"></h3><div class="popover-body"></div></div>',
            });
            $(badge).popover('show');
        },
        _onHideUserCard: function (ev) {
            let badge = ev.currentTarget;
            $(badge).popover('hide');
        }
    });

    fieldRegistry.add('wecom_contact_display', WecomContactDisplay);

    return {
        WecomContactDisplay: WecomContactDisplay,
    };
});