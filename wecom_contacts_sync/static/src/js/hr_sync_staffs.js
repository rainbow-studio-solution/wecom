odoo.define('hrms.sync_contacts_staffs', function (require) {
    "use strict";

    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var KanbanRenderer = require('web.KanbanRenderer');
    var KanbanRecord = require('web.KanbanRecord');
    var viewRegistry = require('web.view_registry');
    const ChatMixin = require('hr.chat_mixin');

    const EmployeeArchiveMixin = {
        _getArchiveAction: function (id) {
            return {
                type: 'ir.actions.act_window',
                name: _t('Employee Termination'),
                res_model: 'hr.departure.wizard',
                views: [
                    [false, 'form']
                ],
                view_mode: 'form',
                target: 'new',
                context: {
                    'active_id': id,
                    'toggle_active': true,
                }
            }
        }
    };

    // 企微员工
    function renderSyncEmployeeButton() {
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_sync_staffs', function () {
                return self._rpc({
                    model: 'hr.employee',
                    method: 'sync_wecom_user',
                    args: [],
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
    var HrEmployeeRequestListController = ListController.extend({
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
                        self.buttons_template = 'HrEmployeeSyncRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonDownload = this.$el.find('.o_button_sync_staffs');
            if (this.getSelectedIds().length === 0) {
                $buttonDownload.removeClass('d-none');
            } else {
                $buttonDownload.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderSyncEmployeeButton.apply(this, arguments);
        }
    })

    var HrEmployeeSyncRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: HrEmployeeRequestListController,
        }),
    });

    var HrEmployeeRequestKanbanController = KanbanController.extend({
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
                        self.buttons_template = 'HrEmployeeSyncRequestKanbanView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderSyncEmployeeButton.apply(this, arguments);
        }
    });

    var EmployeeKanbanRecord = KanbanRecord.extend(ChatMixin);

    var EmployeeKanbanRenderer = KanbanRenderer.extend({
        config: Object.assign({}, KanbanRenderer.prototype.config, {
            KanbanRecord: EmployeeKanbanRecord,
        }),
    });

    var HrEmployeeSyncRequestKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: HrEmployeeRequestKanbanController,
            Renderer: EmployeeKanbanRenderer
        }),
    });


    viewRegistry.add('hrms_employee_tree_sync', HrEmployeeSyncRequestListView);
    viewRegistry.add('hrms_employee_kanban_sync', HrEmployeeSyncRequestKanbanView);
});