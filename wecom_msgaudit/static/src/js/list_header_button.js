odoo.define('wecom_msgaudit.list_sync', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;

    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wecom_download_chatdata', this._download_wecom_chatdata.bind(this));
                this.$buttons.on('click', '.o_list_wecom_batch_update_group_chat', this._batch_update_wecom_group_chat.bind(this));
            }
        },
        _onSelectionChanged: function (ev) {
            this._super.apply(this, arguments);
            this.$('.o_list_wecom_sync_tags').toggle(!this.selectedRecords.length);
        },
        _download_wecom_chatdata: function () {
            var self = this;
            self._rpc({
                model: 'wecom.chatdata',
                method: 'download_chatdatas',
                args: [""],
            }).then(function (result) {
                console.log(result);
                if (result) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Download succeeded!"),
                        message: _t("Complete the download of chat records."),
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
                        type: 'info',
                        title: _t("Tips!"),
                        message: _t("No data to download!"),
                        sticky: false,
                    });
                }
            })
        },
        _batch_update_wecom_group_chat: function () {
            var self = this;
            self._rpc({
                model: 'wecom.chatdata',
                method: 'batch_update_group_chat',
                args: [""],
            }).then(function (result) {
                if (result) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Download succeeded!"),
                        message: _t("Complete the download of chat records."),
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
                        type: 'warning',
                        title: _t("Warning!"),
                        message: _t("Failed to batch update internal group chat information!"),
                        sticky: false,
                    });
                }
            })
        },
    });
});