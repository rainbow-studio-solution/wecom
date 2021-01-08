odoo.define('wxwork_attendance.list_pull_button', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wxwork_attendance_rule_pull', this._pull_attendance_rule.bind(this));
            }
        },
        _pull_attendance_rule: function () {
            this.do_action({
                context: {

                },
                name: "Wizard pull attendance rules",
                type: "ir.actions.act_window",
                res_id: false,
                res_model: "wizard.attendance.rule.pull",
                target: "new",
                view_mode: "form",
                view_type: "form",
                views: [
                    [false, "form"]
                ]
            })
        }
    });
});