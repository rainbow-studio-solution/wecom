odoo.define('wecom_contacts_sync.sync_contacts', function (require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    // 企微通讯录-成员同步
    function renderWecomUserSyncButton() {
        const current_company_id = session.user_context.allowed_company_ids[0]; //当前公司id
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_sync_contacts_user', function () {
                self._rpc({
                    model: 'wecom.user',
                    method: 'download_wecom_users',
                    // args: ["", current_selected_company_id],
                    context: {
                        'company_id': current_company_id
                    },
                }).then(function (data) {
                    var params = {};
                    let result = data[0];

                    if (result["state"]) {
                        params = {
                            type: 'success',
                            title: _t("Sync succeeded!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                            buttons: [{
                                text: _t("Refresh"),
                                click: () => {
                                    window.location.reload(true);
                                },
                                primary: true
                            }],
                        }
                    } else {
                        params = {
                            type: 'danger',
                            title: _t("Sync failed!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                        }
                    }

                    self.displayNotification(params);
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
            var $buttonSync = this.$el.find('.o_button_sync_contacts_user');
            if (this.getSelectedIds().length === 0) {
                $buttonSync.removeClass('d-none');
            } else {
                $buttonSync.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderWecomUserSyncButton.apply(this, arguments);
        }
    })

    var WecomUserSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: WecomUserSyncRequestListController,
        }),
    });

    viewRegistry.add('wecom_user_tree_sync', WecomUserSyncRequestListView);

    // 企微通讯录-部门同步
    function renderWecomDepartmentSyncButton() {
        const current_company_id = session.user_context.allowed_company_ids[0]; //当前公司id
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_sync_contacts_department', function () {
                self._rpc({
                    model: 'wecom.department',
                    method: 'download_wecom_deps',
                    // args: ["", current_selected_company_id],
                    context: {
                        'company_id': current_company_id
                    },
                }).then(function (data) {
                    var params = {};
                    let result = data[0];

                    if (result["state"]) {
                        params = {
                            type: 'success',
                            title: _t("Sync succeeded!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                            buttons: [{
                                text: _t("Refresh"),
                                click: () => {
                                    window.location.reload(true);
                                },
                                primary: true
                            }],
                        }
                    } else {
                        params = {
                            type: 'danger',
                            title: _t("Sync failed!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                        }
                    }

                    self.displayNotification(params);
                })
            });
        }
    }

    var WecomDepartmentSyncRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('wecom_base.group_wecom_settings_manager')
                .then(function (is_wecom_settings_manager) {
                    if (is_wecom_settings_manager) {
                        self.buttons_template = 'WecomDepartmentSyncRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonSync = this.$el.find('.o_button_sync_contacts_department');
            if (this.getSelectedIds().length === 0) {
                $buttonSync.removeClass('d-none');
            } else {
                $buttonSync.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderWecomDepartmentSyncButton.apply(this, arguments);
        }
    })

    var WecomDepartmentSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: WecomDepartmentSyncRequestListController,
        }),
    });

    viewRegistry.add('wecom_department_tree_sync', WecomDepartmentSyncRequestListView);

    // 企微通讯录-标签同步
    function renderWecomTagSyncButton() {
        const current_company_id = session.user_context.allowed_company_ids[0]; //当前公司id
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_sync_contacts_tag', function () {
                self._rpc({
                    model: 'wecom.tag',
                    method: 'download_wecom_tags',
                    // args: ["", current_selected_company_id],
                    context: {
                        'company_id': current_company_id
                    },
                }).then(function (data) {
                    var params = {};
                    let result = data[0];

                    if (result["state"]) {
                        params = {
                            type: 'success',
                            title: _t("Sync succeeded!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                            buttons: [{
                                text: _t("Refresh"),
                                click: () => {
                                    window.location.reload(true);
                                },
                                primary: true
                            }],
                        }
                    } else {
                        params = {
                            type: 'danger',
                            title: _t("Sync failed!"),
                            message: _.str.sprintf(_t('%s It takes %s seconds'), result["msg"], result["time"].toFixed(2)),
                            sticky: true,
                        }
                    }

                    self.displayNotification(params);
                })
            });
        }
    }

    var WecomTagSyncRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('wecom_base.group_wecom_settings_manager')
                .then(function (is_wecom_settings_manager) {
                    if (is_wecom_settings_manager) {
                        self.buttons_template = 'WecomTagSyncRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonSync = this.$el.find('.o_button_sync_contacts_tag');
            if (this.getSelectedIds().length === 0) {
                $buttonSync.removeClass('d-none');
            } else {
                $buttonSync.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderWecomTagSyncButton.apply(this, arguments);
        }
    })

    var WecomTagSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: WecomTagSyncRequestListController,
        }),
    });

    viewRegistry.add('wecom_tag_tree_sync', WecomTagSyncRequestListView);
});