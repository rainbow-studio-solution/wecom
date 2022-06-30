odoo.define('web_json_editor.ace', function (require) {
    "use strict";

    var BasicFields = require("web.basic_fields")
    var AceEditor = require("web.basic_fields.AceEditor")

    var JsonEditor = BasicFields.AceEditor.extend({
        start: function () {
            console.log(this.template);
            console.log(this.jsLibs);
            return this._super.apply(this, arguments);
        },
    })

    return {
        JsonEditor: JsonEditor
    }
});