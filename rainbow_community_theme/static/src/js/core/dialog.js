odoo.define("rainbow_community_theme.Dialog", function(require) {
    "use strict";

    const config = require("web.config");
    if (!config.device.isMobile) {
        return;
    }

    const Dialog = require("web.Dialog");

    Dialog.include({
        /**
         * @override
         *
         * @param {Widget} parent
         * @param {Array} options.headerButtons
         */
        init(parent, { headerButtons }) {
            this._super.apply(this, arguments);
            this.headerButtons = headerButtons || [];
        },

        /**
         * Renders the header as a "Top App Bar" layout :
         * - navigation icon: right arrow that closes the dialog;
         * - title: same as on desktop;
         * - action buttons: optional actions related to the current screen.
         * Only applied for fullscreen dialog.
         *
         * @override
         */
        async willStart() {
            const prom = await this._super.apply(this, arguments);
            if (this.renderHeader && this.fullscreen) {
                const $modalHeader = this.$modal.find(".modal-header");
                $modalHeader.find("button.close").remove();
                const $navigationBtn = $("<button>", {
                    class: "btn fa fa-arrow-left",
                    "data-dismiss": "modal",
                    "aria-label": "close",
                });
                $modalHeader.prepend($navigationBtn);
                const $btnContainer = $("<div>");
                this._setButtonsTo($btnContainer, this.headerButtons);
                $modalHeader.append($btnContainer);
            }
            return prom;
        },
    });
});
