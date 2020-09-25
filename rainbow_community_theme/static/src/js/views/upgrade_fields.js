odoo.define('rainbow_community_theme.upgrade_widgets', function (require) {
    "use strict";

    /**
     * This module adds two field widgets in the view registry: 'upgrade_boolean'
     * and 'upgrade_radio'. In community, those widgets implement a specific
     * behavior to upgrade to enterprise. This behavior is overriden in enterprise
     * by the default FieldBoolean and FieldRadio behaviors.
     */

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var relational_fields = require('web.relational_fields');

    var UpgradeBoolean = basic_fields.FieldBoolean.extend({
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Compatibility with community, where a function 'renderWithLabel' is
         * defined to correctly position the 'Enterprise' label indicating that the
         * feature is enterprise only. Without this, it crashes when opening
         * Settings views in enterprise.
         */
        renderWithLabel: function () {},
    });

    var UpgradeRadio = relational_fields.FieldRadio.extend({
        // We don't require this widget to be displayed in studio sidebar in
        // non-debug mode hence just extended it from its original widget, so that
        // description comes from parent and hasOwnProperty based condition fails
    });



    field_registry
        .add('upgrade_boolean', UpgradeBoolean)
        .add('upgrade_radio', UpgradeRadio);

});