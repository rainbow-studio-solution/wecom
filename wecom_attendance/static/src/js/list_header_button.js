odoo.define('wecom_attendance.get_checkin_rules', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var _t = core._t;

    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_get_wecom_checkin_rules', this._get_checkin_rules.bind(this));
            }
        },
        _get_checkin_rules: function () {
            var self = this;
            this.do_action({
                // context: {},
                name: "Use the wizard to get check-in rules",
                type: "ir.actions.act_window",
                res_id: false,
                res_model: "wecom.checkin.rules.wizard",
                target: "new",
                view_mode: "form",
                view_type: "form",
                views: [
                    [false, "form"]
                ]
            })
        },

    });
});