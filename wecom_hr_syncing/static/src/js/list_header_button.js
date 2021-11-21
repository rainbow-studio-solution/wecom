odoo.define('wecom_hr_syncing.list_sync', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;

    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wecom_sync_tags', this._sync_wecom_tags.bind(this));
            }
        },
        _onSelectionChanged: function (ev) {
            this._super.apply(this, arguments);
            this.$('.o_list_wecom_sync_tags').toggle(!this.selectedRecords.length);
        },
        _sync_wecom_tags: function () {
            var self = this;
            self._rpc({
                model: 'ir.ui.view',
                method: 'search_read',
                domain: [
                    ['name', '=', 'wizard.wecom.tag']
                ],
                fields: ['name', 'model', 'type'],
                limit: 1,
            }).then(function (views) {
                var view = views[0];
                self.do_action({
                    type: 'ir.actions.act_window',
                    name: _t('Sync tag'),
                    res_model: view.model,
                    views: [
                        [view.id, view.type]
                    ],
                    view_mode: 'form',
                    view_type: 'form',
                    target: 'new',
                    context: {}
                });
            })
        }
    });
});