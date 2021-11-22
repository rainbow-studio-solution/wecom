odoo.define("wecom_widget.FieldTextMarkDown", function (require) {
    'use strict';

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _lt = core._lt;
    var _t = core._t;
    var QWeb = core.qweb;
    var TranslatableFieldMixin = basic_fields.TranslatableFieldMixin;
    var FieldHtml = require('web_editor.field.html');
    // var FieldWeComMarkDown = basic_fields.DebouncedField.extend(TranslatableFieldMixin, {
    var FieldWeComMarkDown = FieldHtml.extend({
        // template: "WeComMarkdown",
        className: "oe_form_field oe_form_field_html markdown-body",
        supportedFieldTypes: ['text', 'html'],
        tagName: 'div',
        jsLibs: [

        ],
        cssLibs: [
            '/wecom_widget/static/lib/markdown/github-markdown.css',
        ],

        // _prepareInput: function ($input) {
        //     console.log("_prepareInput");
        //     var self = this;
        //     this.$input = this.$el.find('textarea');
        //     return $.when($input, this._super.apply(this, arguments));
        // },
        // _renderReadonly: function () {
        //     console.log("_renderReadonly", this.value);
        //     this._prepareInput(this.$el);
        // },
        // _renderEdit: function () {
        //     console.log("_renderEdit", this.value);
        //     this._prepareInput(this.$el);
        // },
        // _setValue: function () {
        //     console.log("_setValue", this.value);
        //     var $input = this.$el.find('textarea');
        //     return this._super($input.val());
        // },
        // _getValue: function () {
        //     console.log("_getValue", this.value);
        //     return this.value;
        // },
    })

    field_registry.add('wecom_markdown', FieldWeComMarkDown);

    return FieldWeComMarkDown;
});