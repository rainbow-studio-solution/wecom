//----------------------------------------
// Wxwork One2many help widgets
//----------------------------------------
odoo.define('wxwork.one2many_help_fields', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var RelationalFields = require('web.relational_fields');
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    var field_utils = require('web.field_utils');


    var FieldOne2ManyHlep = RelationalFields.FieldOne2Many.extend({
        description: _lt("One2manyHelp"),
        className: 'o_field_one2many_help',
        supportedFieldTypes: ['one2many_help'],
        // attrs:
        // - help: 帮助字段
        // - widget: "one2many_help"
        // value：
        // - data:数据
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.options = options;
            this.widget = this.attrs.widget;
        },
        // _getRenderer: function () {
        //     if (this.attrs.widget === "one2many_help") {
        //         this.help_field = this.attrs.help;
        //         console.log("data", this.value.data);
        //         // console.log("ListRenderer", ListRenderer);
        //         // // return false;
        //         return ListRenderer;
        //     }
        //     return this._super.apply(this, arguments);
        // },
    });



    ListRenderer.include({
        _renderHeader: function (isGrouped) {
            console.log("ListRenderer", this);
        },
    });
    fieldRegistry.add('one2many_help', FieldOne2ManyHlep);
    return {
        FieldOne2ManyHlep: FieldOne2ManyHlep,
    };

});