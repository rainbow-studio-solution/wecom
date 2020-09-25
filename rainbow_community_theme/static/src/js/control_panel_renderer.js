odoo.define('rainbow_community_theme.ControlPanelRenderer', function (require) {
    "use strict";

    var config = require('web.config');
    var ControlPanelRenderer = require('web.ControlPanelRenderer');

    ControlPanelRenderer.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _renderBreadcrumbsItem: function (bc, index, length) {
            var $bc = this._super.apply(this, arguments);

            var isLast = (index === length - 1);
            var isBeforeLast = (index === length - 2);

            $bc.toggleClass('d-none d-md-inline-block', !isLast && !isBeforeLast)
                .toggleClass('o_back_button', isBeforeLast)
                .toggleClass('btn btn-secondary', isBeforeLast && config.device.isMobile);

            return $bc;
        },
    });


});