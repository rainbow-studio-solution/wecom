odoo.define('web.WecomApiDialog', function (require) {
    "use strict";
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    function WecomApiDialog(parent, action) {
        var dialog = new Dialog(this, action.params);
        dialog.open();
    }
    core.action_registry.add("wecom_api_dialog", WecomApiDialog);
});