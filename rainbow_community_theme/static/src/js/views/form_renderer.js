odoo.define('rainbow_community_theme.MobileFormRenderer', function (require) {
    "use strict";

    var config = require('web.config');

    if (!config.device.isMobile) {
        return;
    }

    /**
     * This file defines the MobileFormRenderer, an extension of the FormRenderer
     * implementing some tweaks to improve the UX in mobile.
     * In mobile, this renderer is used instead of the classical FormRenderer.
     */

    var core = require('web.core');
    var FormRenderer = require('web.FormRenderer');

    var qweb = core.qweb;

    FormRenderer.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * In mobile, buttons/widget tag displayed in the statusbar are folded in a dropdown.
         *
         * @override
         * @private
         */
        _renderHeaderButtons: function (node) {
            var $headerButtons = $();
            var self = this;
            var buttons = [];
            _.each(node.children, function (child) {
                if (child.tag === 'button') {
                    buttons.push(self._renderHeaderButton(child));
                }
                if (child.tag === 'widget') {
                    buttons.push(self._renderTagWidget(child));
                }
            });

            if (buttons.length) {
                $headerButtons = $(qweb.render('StatusbarButtons'));
                var $dropdownMenu = $headerButtons.find('.dropdown-menu');
                _.each(buttons, function ($button) {
                    $dropdownMenu.append($button.addClass('dropdown-item'));
                });
                this._toggleStatusbarButtons($headerButtons);
            }

            return $headerButtons;
        },

        /**
         * Hide action dropdown button if no visible dropdown item button
         *
         * @private
         */
        _toggleStatusbarButtons: function ($headerButtons) {
            var $visibleButtons = $headerButtons.find('.dropdown-menu button:not(.o_invisible_modifier)');

            // We need to remove also the button that match these CSS selector:
            // .o_form_view.o_form_editable .oe_read_only {
            //     display: none !important;
            // }
            // At this time the widget is not appended and so the selector is not enable yet.
            $visibleButtons = $visibleButtons.filter((index, element) => {
                return !(this.mode === 'edit' && element.matches('.oe_read_only'));
            });

            $headerButtons.toggleClass('o_invisible_modifier', !$visibleButtons.length);
        },

        /**
         * Update visibility of action dropdown button.
         * Useful when invisible modifiers are on dropdown item buttons.
         *
         * @override
         * @private
         */
        _updateAllModifiers: function () {
            var def = this._super.apply(this, arguments);
            this._toggleStatusbarButtons(this.$('.o_statusbar_buttons'));
            return def;
        },
    });


});