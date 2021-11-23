odoo.define("wecom_widget.FieldTextMarkDown", function (require) {
	'use strict';

	var basic_fields = require('web.basic_fields');
	var field_registry = require('web.field_registry');
	var core = require('web.core');
	var Dialog = require('web.Dialog');
	var _lt = core._lt;
	var _t = core._t;
	var QWeb = core.qweb;

	var FieldTextMarkDown = basic_fields.FieldText.extend({
		description: _lt("MarkDown"),
		className: [
			basic_fields.FieldText.prototype.className,
			'o_form_field_markdown',
		].join(' '),
		jsLibs: [
			'/wecom_widget/static/lib/bootstrap-markdown/js/marked.js',
			'/wecom_widget/static/lib/bootstrap-markdown/js/bootstrap-markdown.js',
			//语言包
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ar.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.cs_CZ.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.da_DK.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.de.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.es.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fa.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.fr.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.hu.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.it.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ja.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KP.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ko_KR.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nb_NO.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.nl.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pl.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.pt_BR.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.ru.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sl.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.sv.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.tr.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.uk.js',
			'/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_CN.js',
			// '/wecom_widget/static/lib/bootstrap-markdown/locale/bootstrap-markdown.zh_TW.js',
		],
		cssLibs: [
			'/wecom_widget/static/lib/bootstrap-markdown/css/bootstrap-markdown.min.css',
			'/wecom_widget/static/src/css/markdown.css',
			// '/wecom_widget/static/src/css/dialog.css',
		],

		_getValue: function () {
			return this.$markdown.getContent();
		},
		_prepareInput: function () {
			var $input = this._super.apply(this, arguments);

			_.defer(function ($elm) {
				if ($input[1]) {
					$input[1].remove();
				}

				$input.removeClass(this.className);
				$input.wrap(
					_.str.sprintf("<div class='%s'></div>", this.className));
				$elm.markdown(this._getMarkdownOptions());
				var fullscreen = $elm.prev().find(".md-control-fullscreen");
				if (this.res_id) {
					if (_t.database.multi_lang && this.field.translate) {
						if ($input[1]) {
							$input[1].remove();
						}
						var $button = this._renderTranslateButton();
						$button.addClass("fa fa-language fa-lg");
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
			if (this.value != "") {
				this.$el.html(marked(this._formatValue(this.value)));
			}
		},
		_getMarkdownOptions: function () {
			var markdownOpts = {
				autofocus: false,
				savable: false,
				language: this.getSession().user_context.lang,
			};
			markdownOpts.additionalButtons = [
				[{
					name: 'oHelp',
					data: [{
						name: 'cmdHelp',
						title: _t('Help'),
						icon: {
							fa: 'fa fa-question-circle fa-lg'
						},
						callback: this._openHelpDialog,
					}],
				}],
			];
			return markdownOpts;
		},
		_openHelpDialog: function () {
			var code1 = "<span class='tag'>&lt;font</span><span class='pln'> </span><span class='atn'>color</span><span class='pun'>=</span><span class='atv'>'info'</span><span class='tag'>&gt;</span><span class='pln'>绿色</span><span class='tag'>&lt;/font&gt;</span>";
			var code2 = "<span class='tag'>&lt;font</span><span class='pln'> </span><span class='atn'>color</span><span class='pun'>=</span><span class='atv'>'comment'</span><span class='tag'>&gt;</span><span class='pln'>灰色</span><span class='tag'>&lt;/font&gt;</span>";
			var code3 = "<span class='tag'>&lt;font</span><span class='pln'> </span><span class='atn'>color</span><span class='pun'>=</span><span class='atv'>'warning'</span><span class='tag'>&gt;</span><span class='pln'>橙红色</span><span class='tag'>&lt;/font&gt;</span>";
			var dialog_title = _t("Markdown syntax supported by WeCom");
			var dialog = new Dialog(this, {
				size: 'large',
				title: dialog_title,
				$content: QWeb.render('wecom.markdown.syntax', {
					code1: code1,
					code2: code2,
					code3: code3,
				})
			});
			dialog.open();
		},
	});

	field_registry.add('wecom_markdown', FieldTextMarkDown);
	return FieldTextMarkDown;
});