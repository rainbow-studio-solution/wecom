/** @odoo-module **/

import { loadCSS, loadJS } from '@web/core/assets';
import { _lt } from '@web/core/l10n/translation';
import { registry } from '@web/core/registry';
import { useOwnedDialogs, useService } from '@web/core/utils/hooks';
import { standardFieldProps } from '@web/views/fields/standard_field_props';
import { TranslationButton } from '@web/views/fields/translation_button';

// import Editor from '@toast-ui/editor';

import { Component, onWillStart, onWillUpdateProps,onPatched , useEffect, useRef, useEnv } from '@odoo/owl';

export class MarkdownField extends Component {
	setup() {
		// const userService = useService("user");
		this.markdownEditor = null;
		this.editorRef = useRef('editor');
		this.lang = this.env.model.root.context.lang;
		
		onWillStart(async () => {
			let jsLibs = [];
			let cssLibs = [];

			//  Editor
			await loadCSS('/web_widgets/static/libs/tui.editor/toastui-editor.css');
			await loadJS('/web_widgets/static/libs/tui.editor/toastui-editor-all.js');
			if (this.props.userPlugin) {
				// Chart
				// cssLibs.push('/web_widgets/static/libs/tui.editor/plugin/chart/toastui-chart.min.css');
				// jsLibs.push('/web_widgets/static/libs/tui.editor/plugin/chart/toastui-chart.js');

				// Code Highlight
				cssLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/code-syntax-highlight/code-syntax-highlight.min.css'
				);
				cssLibs.push('/web_widgets/static/libs/tui.editor/plugin/code-syntax-highlight/prism.min.css');

				// Color Picker
				cssLibs.push('/web_widgets/static/libs/tui.editor/plugin/color-syntax/tui-color-picker.min.css');
				cssLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/color-syntax/toastui-editor-plugin-color-syntax.min.css'
				);
				jsLibs.push('/web_widgets/static/libs/tui.editor/plugin/color-syntax/tui-color-picker.min.js');

				// Merged Table
				cssLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/table-merged-cell/toastui-editor-plugin-table-merged-cell.min.css'
				);

				// uml

				// Editor's Plugin
				// jsLibs.push('/web_widgets/static/libs/tui.editor/plugin/chart/toastui-editor-plugin-chart.min.js');
				jsLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/code-syntax-highlight/toastui-editor-plugin-code-syntax-highlight-all.min.js'
				);
				jsLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/color-syntax/toastui-editor-plugin-color-syntax.min.js'
				);
				jsLibs.push(
					'/web_widgets/static/libs/tui.editor/plugin/table-merged-cell/toastui-editor-plugin-table-merged-cell.min.js'
				);
				jsLibs.push('/web_widgets/static/libs/tui.editor/plugin/uml/toastui-editor-plugin-uml.min.js');
			}
			if (this.lang !== 'en_US') {
				jsLibs.push('/web_widgets/static/libs/tui.editor/i18n/' + this.lang + '.js');
			}

			const proms = cssLibs.map((url) => loadCSS(url));
			proms.push(...jsLibs.map((url) => loadJS(url)));

			return Promise.all(proms);
		});
		// onWillUpdateProps(this.updateMarkdownEditor);
		useEffect(
			() => {
				this.setupMarkdownEditor();
				// this.updateMarkdownEditor(this.props);
				return () => this.destroyMarkdownEditor();
			},
			() => [this.editorRef.el]
		);

		onPatched(() => {
			// console.log('onPatched', this.props.value,);
			if (this.markdownEditor && this.props.value!=="") {
				this.markdownEditor.setMarkdown(this.props.value);
			}
        });
	}

	setupMarkdownEditor() {
		const self = this;
		this.markdownEditor = this.editorRef.el;
		// const { Editor } = toastui.Editor;
		const Editor = toastui.Editor;
		// const { Editor } = toastui;
		let markdownContent = "";
		if (this.props.value) {
			markdownContent = this.props.value;
		}
		let options = {
			viewer: true,
			el: self.editorRef.el,
			initialEditType: 'markdown',
			initialValue:  markdownContent,
			hideModeSwitch: true,
			placeholder: _lt('Please enter text.'),
			useCommandShortcut: true, // 使用命令快捷方式
			usageStatistics: false, // 使用情况统计
			language: self.lang,
			events: {
				change: () => {
					self.updateMarkdownEditor();
				}
			}
		};

		if (this.props.height !== '') {
			options.height = this.props.height;
		} else {
			options.height = '500px';
		}

		if (this.props.theme === 'dark') {
			options.theme = 'dark';
		}

		if (this.props.previewStyle === 'tab') {
			options.previewStyle = 'tab';
		} else {
			options.previewStyle = 'vertical';
		}

		if (this.props.userPlugin) {
			const { codeSyntaxHighlight, colorSyntax, tableMergedCell, uml } = Editor.plugin;
			// const { chart, codeSyntaxHighlight } = Editor.plugin;

			const chartOptions = {
				minWidth: 100,
				maxWidth: 600,
				minHeight: 100,
				maxHeight: 300
			};
			// options.plugins = [[chart, chartOptions]];
			options.plugins = [
				// [chart, chartOptions],
				[codeSyntaxHighlight, { highlighter: Prism }, colorSyntax, tableMergedCell, uml]
			];
		}
		if (this.props.readonly) {
			this.markdownEditor = Editor.factory(options);
		} else {
			this.markdownEditor = new Editor(options);
			if (this.props.isTranslatable) {
				// 判断是否需要翻译
				let translateButton = this.editorRef.el.parentElement.querySelector('span.o_field_translate');
				translateButton.innerHTML = '<i class="fa fa-language fa-lg"/>';

				function createTranslateButton() {
					const button = document.createElement('button');
					button.appendChild(translateButton);
					button.className = 'translate toastui-editor-toolbar-icons last d-flex align-items-center';
					button.style.backgroundImage = 'none';
					button.style.margin = '2px';
					button.style.padding = '2px';
					return button;
				}
				let toolbarItems = this.markdownEditor.options.toolbarItems;
				toolbarItems.push([
					{
						el: createTranslateButton(),
						tooltip: _lt('Translate'),
						command: 'translate'
					}
				]);
				options.toolbarItems = toolbarItems;
				self.destroyMarkdownEditor();
				this.markdownEditor = new Editor(options);
			}
		}
	}

	updateMarkdownEditor() {
		// if (this.markdownEditor.getMarkdown() !== value) {
		// 	return this.props.update(value);
		// }
		this.props.update(this.markdownEditor.getMarkdown());
	}

	destroyMarkdownEditor() {
		if (this.markdownEditor) {
			this.markdownEditor.destroy();
		}
	}
}
MarkdownField.template = 'web.MarkdownField';
MarkdownField.components = {
	TranslationButton
};
MarkdownField.props = {
	...standardFieldProps,
	isTranslatable: { type: Boolean, optional: true },
	height: { type: String, optional: true },
	theme: { type: String, optional: true },
	previewStyle: { type: String, optional: true },
	userPlugin: { type: Boolean, optional: true },
	plugins: { type: Array, optional: true }
};
MarkdownField.defaultProps = {
	height: '500px',
	theme: '',
	previewStyle: 'vertical',
	userPlugin: false
};
MarkdownField.displayName = _lt('Markdown Editor');
MarkdownField.supportedTypes = ['text'];
MarkdownField.extractProps = ({ attrs, field }) => {
	return {
		isTranslatable: field.translate,
		height: attrs.options.height,
		theme: attrs.options.theme,
		previewStyle: attrs.options.previewStyle,
		userPlugin: attrs.options.userPlugin
	};
};

registry.category('fields').add('markdown_editor', MarkdownField);
