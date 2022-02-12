odoo.define('wecom_hrm.download_tags', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    function renderDownloadTagsButton() {
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_download_tags', function () {
                console.log('download tags');
                return self._rpc({
                    model: 'hr.employee.category',
                    method: 'download_wecom_tags',
                    args: [],
                }).then(function (result) {
                    console.log(typeof (result), result);
                    if (result) {
                        self.displayNotification({
                            type: 'success',
                            title: _t("Download succeeded!"),
                            message: _t("Tag list downloaded successfully."),
                            sticky: true,
                            buttons: [{
                                text: _t("Refresh"),
                                click: () => {
                                    window.location.reload(true);
                                },
                                primary: true
                            }],
                        });
                    }
                })

            });
        }
    }

    var EmployeeCategoryRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('hr.group_hr_manager')
                .then(function (is_sale_manager) {
                    if (is_sale_manager) {
                        self.buttons_template = 'EmployeeCategoryMiningRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderDownloadTagsButton.apply(this, arguments);
        }
    })

    var EmployeeCategoryMiningRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: EmployeeCategoryRequestListController,
        }),
    });

    viewRegistry.add('hr_employee_category_mining_request_tree', EmployeeCategoryMiningRequestListView);

    // ListController.include({
    //     renderButtons: function ($node) {
    //         this._super.apply(this, arguments);
    //         if (this.$buttons) {
    //             this.$buttons.on('click', '.o_list_wecom_download_tags', this._download_wecom_tags.bind(this));
    //         }
    //     },
    //     _onSelectionChanged: function (ev) {
    //         this._super.apply(this, arguments);
    //         this.$('.o_list_wecom_download_tags').toggle(!this.selectedRecords.length);
    //     },
    //     _download_wecom_tags: function () {
    //         var self = this;
    //         self._rpc({
    //             model: 'hr.employee.category',
    //             method: 'download_wecom_tags',
    //             // domain: [
    //             //     ['name', '=', 'wizard.wecom.tag']
    //             // ],
    //             args: [],
    //         })
    //         //     .then(function (result) {

    //         //     self.do_action({
    //         //         type: 'ir.actions.act_window',
    //         //         name: _t('Sync tag'),
    //         //         res_model: view.model,
    //         //         views: [
    //         //             [view.id, view.type]
    //         //         ],
    //         //         view_mode: 'form',
    //         //         view_type: 'form',
    //         //         target: 'new',
    //         //         context: {}
    //         //     });
    //         // })
    //     }
    // });
});