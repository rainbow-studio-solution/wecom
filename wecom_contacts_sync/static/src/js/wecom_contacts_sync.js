odoo.define('wecom_contacts_sync.sync_contacts', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    // 企微通讯录同步
    function renderWecomSyncButton() {
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_sync_contacts', function () {
                self.do_action({
                    // context: {},
                    name: _t("Use the wizard to sync contacts"),
                    type: "ir.actions.act_window",
                    res_id: false,
                    // res_id: "1245",
                    res_model: "wecom.contacts.sync.wizard",
                    target: "new",
                    view_mode: "form",
                    view_type: "form",
                    search_view_id: [false],
                    views: [
                        [false, "form"]
                    ]
                })
            });
        }
    }

    var WecomUserSyncRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('wecom_base.group_wecom_settings_manager')
                .then(function (is_wecom_settings_manager) {
                    if (is_wecom_settings_manager) {
                        self.buttons_template = 'WecomUserSyncRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonSync = this.$el.find('.o_button_sync_contacts');
            if (this.getSelectedIds().length === 0) {
                $buttonSync.removeClass('d-none');
            } else {
                $buttonSync.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderWecomSyncButton.apply(this, arguments);
        }
    })

    var WecomUserSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: WecomUserSyncRequestListController,
        }),
    });

    viewRegistry.add('wecom_user_tree_sync', WecomUserSyncRequestListView);
});