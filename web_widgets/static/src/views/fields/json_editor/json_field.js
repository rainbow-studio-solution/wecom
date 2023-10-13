/** @odoo-module **/

import { loadCSS, loadJS } from '@web/core/assets';
import { _lt } from '@web/core/l10n/translation';
import { registry } from '@web/core/registry';
import { useBus, useService } from '@web/core/utils/hooks';
import { formatText } from '@web/views/fields/formatters';
import { standardFieldProps } from '@web/views/fields/standard_field_props';

import { Component, onWillStart, onWillUpdateProps, useEffect, useRef, useState } from '@odoo/owl';

export class JsonField extends Component {
	setup() {
		this.jsonEditor = null;
		this.editorRef = useRef('editor');
		// this.cookies = useService("cookie");

		// this.state = useState({
		// 	isJSON: true,
		// 	json: this.props.value
		// });
		// console.log(this.props);

		onWillStart(async () => {
			await loadJS('/web_widgets/static/libs/jsoneditor/dist/jsoneditor.js');
			await loadCSS('/web_widgets/static/libs/jsoneditor/dist/jsoneditor.css');
			const jsLibs = [
				// "/web_widgets/static/lib/ace/mode-python.js",
				// "/web/static/lib/ace/mode-xml.js",
				// "/web/static/lib/ace/mode-qweb.js",
			];
			const proms = jsLibs.map((url) => loadJS(url));
			return Promise.all(proms);
		});

		useEffect(
			() => {
				this.setupJsonEditor();
				// this.updateJsonEditor(this.props);
				return () => this.destroyJsonEditor();
			},
			() => [this.editorRef.el]
		);
	}

	setupJsonEditor() {
		const self = this;
		this.jsonEditor = this.editorRef.el;
		let mode = 'code';
		let modes = [];

		// if (this.props.readonly) {
		// 	modes = ['text', 'code'];
		// } else {
		// 	modes = ['code', 'form', 'text', 'tree', 'view', 'preview']; // allowed modes
		// }
		if (this.props.mode === '') {
			mode = 'code';
		} else {
			mode = this.props.mode;
		}
		if (this.props.modes.length > 0) {
			modes = this.props.modes;
		 }
		else {
			modes = ['code', 'form', 'text', 'tree', 'view', 'preview']; // allowed modes
		}

		this.options = {
			mode: mode,
			modes: modes,
			// onError: function (err) {
			// 	console.error(err.toString());
			// },
			// onChange: function () {
			// 	console.log('onChange');
			// },
			// onChangeJSON: function (json) {
			// 	console.log('onChangeJSON', json);
			// },
			// onChangeText: function (text) {
			// 	console.log('onChangeText', formatText(text));
			// },
			// onValidationError: function (err) {
			// 	console.error('onValidationError', err);
			// 	self.state.isJSON = false;
			// },
			onEditable: function (node) {
				if (self.props.readonly) {
					// In modes code and text, node is empty: no path, field, or value
					// returning false makes the text area read-only
					return false;
				} else {
					return true;
				}
			},
			onValidate: function (json) {
				if (!self.props.readonly) {
					self.props.update(json);
				}
			}
		};

		this.jsonEditor = new JSONEditor(this.jsonEditor, this.options, this.props.value || {});
	}

	destroyJsonEditor() {
		if (this.jsonEditor) {
			this.jsonEditor.destroy();
		}
	}
}
JsonField.template = 'web.JsonField';
JsonField.props = {
	...standardFieldProps,
	mode: { type: String, optional: true },
	modes: { type: Array, optional: true },
};
JsonField.defaultProps = {
	mode: 'code',
	modes: ["code", "form", "text", "tree", "view", "preview"],
};
JsonField.displayName = _lt('Json Editor');
JsonField.supportedTypes = ['json'];
JsonField.extractProps = ({ attrs }) => {
	return {
		mode: attrs.options.mode,
		modes: attrs.options.modes,
	};
};

registry.category('fields').add('json_editor', JsonField);
