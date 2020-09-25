odoo.define('rainbow_community_theme.view_dialogs', function (require) {
    "use strict";

    var config = require('web.config');
    if (!config.device.isMobile) {
        return;
    }

    var core = require('web.core');
    var view_dialogs = require('web.view_dialogs');

    var _t = core._t;

    view_dialogs.FormViewDialog.include({
        /**
         * @override
         */
        init(parent, options) {
            options.headerButtons = options.headerButtons || [];
            this._super.apply(this, arguments);
        },
        /**
         * Set the "Remove" button to the dialog's header buttons set
         *
         * @override
         */
        _setRemoveButtonOption(options, btnClasses) {
            options.headerButtons.push({
                text: _t("Remove"),
                classes: `btn-secondary ${btnClasses}`,
                click: async () => {
                    await this._remove();
                    this.close();
                },
            });
        },
    });

    view_dialogs.SelectCreateDialog.include({
        init: function () {
            this._super.apply(this, arguments);
            this.on_clear = this.options.on_clear || (function () {});
            this.viewType = 'kanban';
        },
        /**
         * @override
         */
        _prepareButtons: function () {
            this._super.apply(this, arguments);
            if (this.options.disable_multiple_selection) {
                if (this.options.selectionMode) {
                    this.headerButtons.push({
                        text: _t("Clear"),
                        classes: 'btn-secondary o_clear_button',
                        close: true,
                        click: function () {
                            this.on_clear();
                        },
                    });
                }
            } else {
                this.__buttons = this.__buttons.filter(button => !button.classes.split(' ').includes('o_select_button'));
            }
        },
    });

});