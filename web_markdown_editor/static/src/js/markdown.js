odoo.define("web_markdown_editor.FieldTextMarkDown", function (require) {
    'use strict';

    var basic_fields = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
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
            '/web_markdown_editor/static/src/js/dropzone.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/js/bootstrap-markdown.js',
            //语言包
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ar.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.cs_CZ.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.da_DK.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.de.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.es.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fa.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fr.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.hu.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.it.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ja.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KP.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KR.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nb_NO.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nl.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pl.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pt_BR.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ru.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sl.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sv.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.tr.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.uk.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_CN.js',
            '/web_markdown_editor/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_TW.js',
        ],
        cssLibs: [
            '/web_markdown_editor/static/lib/bootstrap-markdown/css/bootstrap-markdown.min.css',
            '/web_markdown_editor/static/lib/glyphicons//glyphicon.css',
        ],
        _getValue: function () {
            return this.$markdown.getContent();
        },
        _prepareInput: function () {
            var $input = this._super.apply(this, arguments);
            // console.log(this.className);
            _.defer(function ($elm) {
                $input.removeClass(this.className);
                $input.wrap(
                    _.str.sprintf("<div class='%s'></div>", this.className));
                $elm.markdown(this._getMarkdownOptions());
                this.$markdown = $elm.data("markdown");
                this.$markdown.setContent(this.value || "");
            }.bind(this), $input);
            return $input;
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

            // Only can create attachments on non-virtual records
            if (this.res_id) {
                var self = this;
                markdownOpts.dropZoneOptions = {
                    paramName: 'ufile',
                    url: '/web/binary/upload_attachment',
                    acceptedFiles: 'image/*',
                    width: 'o_form_field_markdown',
                    params: {
                        csrf_token: core.csrf_token,
                        session_id: this.getSession().override_session,
                        callback: '',
                        model: this.model,
                        id: this.res_id,
                    },
                    success: function () {
                        self._markdownDropZoneUploadSuccess(this);
                    },
                    error: function () {
                        self._markdownDropZoneUploadError(this);
                    },
                    init: function () {
                        self._markdownDropZoneInit(this);
                    },
                };
                if (_t.database.multi_lang && this.field.translate) {
                    markdownOpts.additionalButtons = [
                        [{
                            name: 'oTranslate',
                            data: [{
                                name: 'cmdTranslate',
                                title: _t('Translate'),
                                icon: {
                                    glyph: 'glyphicon glyphicon-globe'
                                },
                                callback: this._markdownTranslate,
                            }],
                        }],
                    ];
                }
                // if (_t.database.multi_lang && this.field.translate) {
                //     var lang = this.getSession().user_context.lang.split('_')[0].toUpperCase();
                //     markdownOpts.additionalButtons = [
                //         [{
                //             name: 'oTranslate',
                //             data: [{
                //                 name: 'cmdTranslate',
                //                 toggle: true,
                //                 title: _t('Translate:') + lang,
                //                 icon: {
                //                     glyph: 'glyphicon glyphicon-globe'
                //                 },
                //                 // callback: this._markdownTranslate,
                //             }],
                //         }],
                //     ];
                // }
            }

            return markdownOpts;
        },

        _getAttachmentId: function (response) {
            var matchElms = response.match(/"id":\s?(\d+)/);
            if (matchElms && matchElms.length) {
                return matchElms[1];
            }
            return null;
        },

        _markdownDropZoneInit: function (markdown) {
            var self = this;
            var caretPos = 0;
            var $textarea = null;
            markdown.on('drop', function (e) {
                $textarea = $(e.target);
                caretPos = $textarea.prop('selectionStart');
            });
            markdown.on('success', function (file, response) {
                var text = $textarea.val();
                var attachment_id = self._getAttachmentId(response);
                if (attachment_id) {
                    var ftext = text.substring(0, caretPos) + '\n![' +
                        _t('description') +
                        '](/web/image/' + attachment_id + ')\n' +
                        text.substring(caretPos);
                    $textarea.val(ftext);
                } else {
                    self.do_warn(
                        _t('Error'),
                        _t("Can't create the attachment."));
                }
            });
            markdown.on('error', function (file, error) {
                console.warn(error);
            });
        },

        _markdownDropZoneUploadSuccess: function () {
            this.isDirty = true;
            this._doDebouncedAction();
            this.$markdown.$editor.find(".dz-error-mark:last")
                .css("display", "none");
        },

        _markdownDropZoneUploadError: function () {
            this.$markdown.$editor.find(".dz-success-mark:last")
                .css("display", "none");
        },

        _markdownTranslate: function () {
            this._onTranslate();
        },

    });


    field_registry.add('markdown', FieldTextMarkDown);
    return FieldTextMarkDown;
});