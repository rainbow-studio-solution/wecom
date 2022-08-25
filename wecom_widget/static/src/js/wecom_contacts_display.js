// *-------------------------------------------------------
// * 企业微信通讯录展示组件
// * 注意视图中必须含有 <field name="company_id" />
// *-------------------------------------------------------
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
            'mouseover .contacts_simple': '_onShowUserCard',
            'mouseout .contacts_simple': '_onHideUserCard',
            'mouseover .contacts_details': '_onShowUserCard',
            'mouseout .contacts_details': '_onHideUserCard',
        }, AbstractField.prototype.events),
        className: "d-flex flex-row",
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.state = state; // 字段名称
            this.params = params;
            this.data = params.data;
            this.template_content = params.data[state]; // 字段值
            this.control_type = this.nodeOptions.type; // 控件类型:user,department
            this.show_type = this.nodeOptions.show; // 显示类型：simple，details

            this.current_company_id = this.data["company_id"].res_id;
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
                    self._renderWecomContactDisplay();
                }
            }
        },
        _prepareInput: function ($el) {
            return this.$el;
        },
        _renderWecomContactDisplay: async function () {
            var self = this;
            let contacts = this.template_content;
            let new_contacts = [];
            _.forEach(contacts, function (contact) {
                // 处理Tag的userlist
                if ($.isPlainObject(contact)) {
                    if (self.hasKey("userid", contact)) {
                        new_contacts.push(contact["userid"]);
                    }
                    if (self.hasKey("name", contact)) {
                        delete contact["name"];
                    }
                }
            })
            if (new_contacts.length > 0) {
                contacts = new_contacts;
            }

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
                    control_key = "users";
                }
                if (this.control_type === 'department') {
                    template_name = "WecomDepartments";
                    model_name = "wecom.department";
                    fields = ["name", "name_en", "department_id", "complete_name"];
                    domain_key = "department_id";
                    control_key = "departments";
                }
                if (this.show_type === 'simple') {
                    template_name = template_name + "Simple";
                }
                if (this.show_type === 'details') {
                    template_name = template_name + "Details";
                }
                if (this.current_company_id) {
                    self._rpc({
                        model: model_name,
                        method: 'search_read',
                        fields: fields,
                        domain: [
                            ['company_id', '=', self.current_company_id],
                            [domain_key, 'in', contacts]
                        ],
                    }).then(function (rows) {
                        let $control = $(QWeb.render(template_name, {
                            rows: rows,
                        }));
                        $control.appendTo(self.$el);
                    })
                }
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
        },
        hasKey(key, obj) {
            if (obj.hasOwnProperty(key)) {
                return true;
            } else {
                return false;
            }
        }
    });

    fieldRegistry.add('wecom_contact_display', WecomContactDisplay);

    return {
        WecomContactDisplay: WecomContactDisplay,
    };
});