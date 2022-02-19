odoo.define('wecom_contacts.download_tags', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');

    var viewRegistry = require('web.view_registry');

    // 企微标签
    function renderDownloadContactButton() {
        if (this.$buttons) {
            var self = this;
            this.$buttons.on('click', '.o_button_download_contact_tags', function () {
                return self._rpc({
                    model: 'res.partner.category',
                    method: 'download_wecom_contact_tags',
                    args: [],
                }).then(function (results) {
                    $.each(results, function (index, result) {
                        if (result["state"]) {
                            self.displayNotification({
                                type: 'success',
                                title: _t("Download succeeded!"),
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
                                title: _t("Download failed!"),
                                message: result["msg"],
                                sticky: true,
                            });
                        }
                    });
                })
            });
        }
    }

    var ResPartnerCategoryRequestListController = ListController.extend({
        willStart: function () {
            var self = this;
            var ready = this.getSession().user_has_group('base.group_partner_manager')
                .then(function (is_partner_manager) {
                    if (is_partner_manager) {
                        self.buttons_template = 'ResPartnerCategoryDownloadRequestListView.buttons';
                    }
                });
            return Promise.all([this._super.apply(this, arguments), ready]);
        },
        _onSelectionChanged: function (ev) {
            this._super(ev);
            var $buttonDownload = this.$el.find('.o_button_download_contact_tags');
            if (this.getSelectedIds().length === 0) {
                $buttonDownload.removeClass('d-none');
            } else {
                $buttonDownload.addClass('d-none');
            }
        },
        renderButtons: function () {
            this._super.apply(this, arguments);
            renderDownloadContactButton.apply(this, arguments);
        }
    })

    var ResPartnerCategoryDownloadRequestListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ResPartnerCategoryRequestListController,
        }),
    });



    viewRegistry.add('res_partner_category_tree_download', ResPartnerCategoryDownloadRequestListView);

});