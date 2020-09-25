odoo.define('rainbow_community_theme.CalendarRenderer', function (require) {
    "use strict";

    var config = require('web.config');
    if (!config.device.isMobile) {
        return;
    }

    /**
     * This file implements some tweaks to improve the UX in mobile.
     */

    var core = require('web.core');
    var CalendarRenderer = require('web.CalendarRenderer');

    var qweb = core.qweb;

    CalendarRenderer.include({


        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Prepare the parameters for the popover.
         * Setting the popover is append to the body
         * and so no need the use of z-index
         *
         * @private
         * @override method from CalendarRenderer
         * @param {Object} eventData
         */
        _getPopoverParams: function (eventData) {
            var popoverParameters = this._super.apply(this, arguments);
            popoverParameters['container'] = 'body';
            return popoverParameters;
        },

        /**
         * Finalise the popover
         * We adding some inline css to put the popover in a "fullscreen" mode
         *
         * @private
         * @override method from CalendarRenderer
         * @param {jQueryElement} $popoverElement
         * @param {web.CalendarPopover} calendarPopover
         */
        _onPopoverShown: function ($popoverElement, calendarPopover) {
            this._super.apply(this, arguments);
            var $popover = $($popoverElement.data('bs.popover').tip);
            // Need to be executed after Bootstrap popover
            // Bootstrap set style inline and so override the scss style
            setTimeout(() => {
                $popover.toggleClass([
                    'bs-popover-left',
                    'bs-popover-right',
                ], false);
                $popover.find('.arrow').remove();
                $popover.css({
                    display: 'flex',
                    bottom: 0,
                    right: 0,
                    borderWidth: 0,
                    maxWidth: '100%',
                    transform: 'translate3d(0px, 0px, 0px)',
                });
                $popover.find('.o_cw_body').css({
                    display: 'flex',
                    flex: '1 0 auto',
                    flexDirection: 'column',
                });
                // We grow the "popover_fields_secondary" to have the buttons in the bottom of screen
                $popover.find('.o_cw_popover_fields_secondary')
                    .toggleClass('o_cw_popover_fields_secondary', false)
                    .css({
                        flexGrow: 1,
                    });
                // We prevent the use of "scroll" events to avoid bootstrap listener
                // to resize the popover
                $popover.on('touchmove', (event) => {
                    event.preventDefault();
                });
                // Firefox
                $popover.on('mousewheel', (event) => {
                    event.preventDefault();
                });
                // Chrome
                $popover.on('wheel', (event) => {
                    event.preventDefault();
                });
                // When the user click on a link the popover must be removed
                $popover.find('a.o_field_widget[href]')
                    .on('click', (event) => {
                        $('.o_cw_popover').popover('dispose');
                    })
            }, 0);
        },
        /**
         * Remove highlight classes and dispose of popovers
         *
         * @private
         */
        _unselectEvent: function () {
            this._super.apply(this, arguments);
            $('.o_cw_popover').popover('dispose');
        },
    });

});