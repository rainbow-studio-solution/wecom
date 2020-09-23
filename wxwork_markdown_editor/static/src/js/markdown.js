odoo.define("wxwork_markdown_editor.FieldTextMarkDown", function (require) {
    'use strict';

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var dom = require('web.dom');
    var _lt = core._lt;
    var _t = core._t;

    var FieldTextMarkDown = basic_fields.FieldText.extend({
        description: _lt("MarkDown"),
        className: [
            basic_fields.FieldText.prototype.className,
            'o_form_field_markdown',
        ].join(' '),
        jsLibs: [
            '/wxwork_markdown_editor/static/src/js/marked.js',
            // '/wxwork_markdown_editor/static/src/js/dropzone.js',
            '/wxwork_markdown_editor/static/lib/bootstrap-markdown/js/bootstrap-markdown.js',
            //语言包
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ar.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.cs_CZ.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.da_DK.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.de.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.es.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fa.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fr.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.hu.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.it.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ja.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KP.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KR.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nb_NO.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nl.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pl.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pt_BR.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ru.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sl.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sv.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.tr.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.uk.js',
            '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_CN.js',
            // '/wxwork_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_TW.js',
        ],
        cssLibs: [
            '/wxwork_markdown_editor/static/lib/bootstrap-markdown/css/bootstrap-markdown.min.css',
            '/wxwork_markdown_editor/static/src/css/markdown.css',
        ],

        _getValue: function () {
            return this.$markdown.getContent();
        },
        _prepareInput: function () {
            var $input = this._super.apply(this, arguments);

            _.defer(function ($elm) {
                $input[1].remove();
                $input.removeClass(this.className);
                $input.wrap(
                    _.str.sprintf("<div class='%s'></div>", this.className));
                $elm.markdown(this._getMarkdownOptions());
                if (this.res_id) {
                    if (_t.database.multi_lang && this.field.translate) {
                        var $button = this._renderTranslateButton();
                        // $button.css()
                        var fullscreen = $elm.prev().find(".md-control-fullscreen");
                        fullscreen.before($button);
                    }
                }

                this.$markdown = $elm.data("markdown");
                this.$markdown.setContent(this.value || "");
            }.bind(this), $input);
            return $input;
        },
        _renderEdit: function () {
            this._prepareInput(this.$el);
        },
        _renderReadonly: function () {
            this.$el.html(marked(this._formatValue(this.value)));
        },
        _getMarkdownOptions: function () {
            var markdownOpts = {
                autofocus: false,
                savable: false,
                language: this.getSession().user_context.lang,
            };
            return markdownOpts;
        },
    });

    field_registry.add('wxwork_markdown', FieldTextMarkDown);
    return FieldTextMarkDown;
});