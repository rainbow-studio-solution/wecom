odoo.define('hrms.sync_contacts_deps', function (require) {
    "use strict";
    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    // 企微部门
    function renderSyncDepartmentButton() {
        if (this.$buttons) {
            var self = this;
            const current_company_id = session.user_context.allowed_company_ids[0]; //当前公司id
            this.$buttons.on('click', '.o_button_sync_deps', function () {
                return self._rpc({
                    model: 'hr.department',
                    method: 'sync_wecom_deps',
                    // args: [],
                    context: {
                        'company_id': current_company_id
                    },
                }).then(function (results) {
                    $.each(results, function (index, result) {
                        if (result["state"]) {
                            self.displayNotification({
                                type: 'success',
                                title: _t("Sync succeeded!"),
                                message: result["msg"],
                                sticky: true,
                                buttons: [{
                                    text: _t("Refresh"),
                                    click: () => {
                                        window.location.reload(true);
                                    },
                                    primary: true
                                }],
                            });
                        } else {
                            self.displayNotification({
                                type: 'danger',
                                title: _t("Sync failed!"),
                                message: result["msg"],
                                sticky: true,
                            });
                        }
                    });
                })
            });
        }
    }

    var HrDepartmentRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('hr.group_hr_user')
                .then(function (is_hr_user) {
                    if (is_hr_user) {
                        self.buttons_template = 'HrDepartmentSyncRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonDownload = this.$el.find('.o_button_download_deps');
            if (this.getSelectedIds().length === 0) {
                $buttonDownload.removeClass('d-none');
            } else {
                $buttonDownload.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderSyncDepartmentButton.apply(this, arguments);
        }
    })

    var HrDepartmentSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: HrDepartmentRequestListController,
        }),
    });

    viewRegistry.add('hrms_department_tree_sync', HrDepartmentSyncRequestListView);


    var HrDepartmentRequestKanbanController = KanbanController.extend({
        willStart: function () {
            var self = this;

            const current_company_id = session.user_context.allowed_company_ids[0];
            const allowed_companies = session.user_companies.allowed_companies;
            let show_download_button = false;
            var ready = this.getSession().user_has_group('hr.group_hr_user')
                .then(function (is_hr_user) {
                    _.forEach(allowed_companies, function (company) {
                        if (company["id"] == current_company_id) {
                            show_download_button = company["is_wecom_organization"];
                        }
                    })

                    if (is_hr_user && show_download_button) {
                        self.buttons_template = 'HrDepartmentSyncRequestKanbanView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderSyncDepartmentButton.apply(this, arguments);
        }
    });


    var HrDepartmentSyncRequestKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: HrDepartmentRequestKanbanController,
        }),
    });
    viewRegistry.add('hrms_department_kanban_sync', HrDepartmentSyncRequestKanbanView);
});