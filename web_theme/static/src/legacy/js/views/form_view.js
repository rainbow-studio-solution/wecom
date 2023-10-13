odoo.define('web_mobile.FormView', function (require) {
"use strict";

var config = require('web.config');
var FormView = require('web.FormView');
var QuickCreateFormView = require('web.QuickCreateFormView');

/**
 * We don't want to see the keyboard after the opening of a form view.
 * The keyboard takes a lot of space and the user doesn't have a global view
 * on the form.
 * Plus, some relational fields are overrided (Many2One for example) and the
 * user have to click on it to set a value. On this kind of field, the autofocus
 * doesn't make sense because you can't directly type on it.
 * So, we have to disable the autofocus in mobile.
 */
FormView.include({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);

        if (config.device.isMobile) {
            this.controllerParams.disableAutofocus = true;
        }
    },
});

QuickCreateFormView.include({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.controllerParams.disableAutofocus = false;
    },
});

});
