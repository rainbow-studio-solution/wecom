odoo.define("web.AdvancedDialog", function (require) {
    'use strict';


    var core = require('web.core');
    var Dialog = require('web.Dialog');


    function AdvancedDialog(parent, action) {
        var dialog = new Dialog(this, action.params);
        dialog.open();
    }
    core.action_registry.add("dialog", AdvancedDialog);

});