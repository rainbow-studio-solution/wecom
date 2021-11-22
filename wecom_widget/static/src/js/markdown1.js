odoo.define('web_widget_markdown', function (require) {
    "use strict";

    var fieldRegistry = require('web.field_registry');
    var basicFields = require('web.basic_fields');


    var markdownField = basicFields.DebouncedField.extend(basicFields.TranslatableFieldMixin, {
        supportedFieldTypes: ['text'],
        template: 'FieldMarkdown',
        jsLibs: [
            '/wecom_widget/static/lib/simplemde-markdown-editor/simplemde.min.js',
        ],
        cssLibs: [
            '/wecom_widget/static/lib/simplemde-markdown-editor/simplemde.min.css',
        ],
        events: {},

        /**
         * @constructor
         */
        init: function () {
            this._super.apply(this, arguments);
            this.simplemde = {}
        },

        /**
         * When the the widget render, check view mode, if edit we
         * instanciate our SimpleMDE
         * 
         * @override
         */
        start: function () {
            if (this.mode === 'edit') {
                var $textarea = this.$el.find('textarea');
                var simplemdeConfig = {
                    element: $textarea[0],
                    initialValue: this.value,
                    uniqueId: "markdown-" + this.model + this.res_id,
                }
                if (this.nodeOptions) {
                    simplemdeConfig = {
                        ...simplemdeConfig,
                        ...this.nodeOptions
                    };
                }
                this.simplemde = new SimpleMDE(simplemdeConfig);
                this.simplemde.codemirror.on("change", this._doDebouncedAction.bind(this));
                this.simplemde.codemirror.on("blur", this._doAction.bind(this));
                if (this.field.translate) {
                    this.$el = this.$el.add(this._renderTranslateButton());
                    this.$el.addClass('o_field_translate');
                }
            }
            return this._super();
        },

        /**
         * return the SimpleMDE value
         *
         * @private
         */
        _getValue: function () {
            return this.simplemde.value();
        },

        _formatValue: function (value) {
            return this._super.apply(this, arguments) || '';
        },

        _renderEdit: function () {
            this._super.apply(this, arguments);
            var newValue = this._formatValue(this.value);
            if (this.simplemde.value() !== newValue) {
                this.simplemde.value(newValue);
            }
        },

        _renderReadonly: function () {
            this.$el.html(SimpleMDE.prototype.markdown(this._formatValue(this.value)));
        },
    });

    fieldRegistry.add('markdown', markdownField);

    return {
        markdownField: markdownField,
    };
});