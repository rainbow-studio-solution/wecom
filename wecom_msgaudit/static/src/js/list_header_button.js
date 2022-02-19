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
            }
        },
        _onSelectionChanged: function (ev) {
            this._super.apply(this, arguments);
            this.$('.o_list_wecom_download_chatdata').toggle(!this.selectedRecords.length);
        },
        _download_wecom_chatdata: function () {
            var self = this;
            self._rpc({
                model: 'wecom.chatdata',
                method: 'download_chatdatas',
                args: [""],
                // route: '/wecom/get_chatdata',
            }).then(function (result) {
                if (typeof (result) == 'boolean') {
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
                } else {
                    if (result.indexOf("HTTPConnectionPool") != -1 || result.indexOf("404") != -1) {
                        self.displayNotification({
                            type: 'warning',
                            title: _t("Error!"),
                            message: _t("API interface not started!"),
                            sticky: true,
                        });
                    }
                }
            })
        },
    });
});