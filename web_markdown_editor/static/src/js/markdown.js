odoo.define("web_markdown_editor.FieldTextMarkDown", function (require) {
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
            '/web_markdown_editor/static/src/js/marked.js',
            // '/web_markdown_editor/static/src/js/dropzone.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/js/bootstrap-markdown.js',
            //语言包
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ar.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.cs_CZ.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.da_DK.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.de.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.es.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fa.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fr.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.hu.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.it.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ja.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KP.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KR.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nb_NO.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nl.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pl.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pt_BR.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ru.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sl.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sv.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.tr.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.uk.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_CN.js',
            // '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_TW.js',
        ],
        cssLibs: [
            '/web_markdown_editor/static/lib/bootstrap-markdown/css/bootstrap-markdown.min.css',
            '/web_markdown_editor/static/lib/glyphicons/glyphicon.css',
        ],

        _getValue: function () {
            return this.$markdown.getContent();
        },
        _prepareInput: function () {
            var $input = this._super.apply(this, arguments);
            // console.log($input.find("span"))
            // var translate_span = $input[1].detach();
            var translate_span = $input[1].find("span");
            console.log(translate_span);
            _.defer(function ($elm) {
                // $input[1].detach();
                $input.removeClass(this.className);
                $input.wrap(
                    _.str.sprintf("<div class='%s'></div>", this.className));
                $elm.markdown(this._getMarkdownOptions());
                this.$markdown = $elm.data("markdown");
                this.$markdown.setContent(this.value || "");
            }.bind(this), $input);
            // $input.after(translate_span);
            $input.after(translate_span);
            return $input;
        },
        _renderEdit: function () {
            // Keep a reference to the input so $el can become something else
            // without losing track of the actual input.
            // console.log(this.$el);
            // var translate_span = this.$el[1];
            // this.$el.after(translate_span);
            // this.$el[1].remove();
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
            markdownOpts.additionalButtons = [
                [{
                    name: 'oTranslate',
                    data: [{
                        name: 'cmdTranslate',
                        title: _t('Translate'),
                        icon: "glyphicon glyphicon-globe",
                        callback: self._markdownTranslate,
                    }],
                }],
            ];
            // if (this.res_id) {
            //     var self = this;
            //     if (_t.database.multi_lang && this.field.translate) {
            //         markdownOpts.additionalButtons = [
            //             [{
            //                 name: 'oTranslate',
            //                 data: [{
            //                     name: 'cmdTranslate',
            //                     title: _t('Translate'),
            //                     icon: "glyphicon glyphicon-globe",
            //                     callback: self._markdownTranslate,
            //                 }],
            //             }],
            //         ];
            //     }
            // }
            return markdownOpts;
        },

        _markdownTranslate: function () {
            this._onTranslate();
        },

    });


    field_registry.add('markdown', FieldTextMarkDown);
    return FieldTextMarkDown;
});