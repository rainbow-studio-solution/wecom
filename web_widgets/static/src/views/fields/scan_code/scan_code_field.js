/** @odoo-module **/

import { _lt } from '@web/core/l10n/translation';
import { registry } from '@web/core/registry';

import { ScanCodeCopyButton } from './scan_code_copy_button';
import { ShowScanCodeDialogButton } from './show_scan_code_dialog_button';
import { UrlField } from '@web/views/fields/url/url_field';
import { CharField } from '@web/views/fields/char/char_field';
import { TextField } from '@web/views/fields/text/text_field';
import { standardFieldProps } from '@web/views/fields/standard_field_props';

import { Component } from '@odoo/owl';

class ScanCodeField extends Component {
	setup() {
		let self = this;
		this.copyText = this.env._t('Copy');
		this.successText = this.env._t('Copied');

		this.fieldNameText = '';
		_.each(this.props.record.fields, function (field) {
			if (field.name === self.props.name) {
				self.fieldNameText = field.string;
			}
		});

	}
	get copyButtonClassName() {
		return `o_btn_${this.props.type}_copy`;
	}
}
ScanCodeField.template = 'web.ScanCodeField';
ScanCodeField.props = {
	...standardFieldProps
};

export class ScanCodeButtonField extends ScanCodeField {
	get copyButtonClassName() {
		const classNames = [super.copyButtonClassName];
		classNames.push('rounded-2');
		return classNames.join(' ');
	}
}
ScanCodeButtonField.template = 'web.ScanCodeButtonField';
ScanCodeButtonField.components = { ShowScanCodeDialogButton };
ScanCodeButtonField.displayName = _lt('Copy to Clipboard');

registry.category('fields').add('ScanCodeButton', ScanCodeButtonField);

// ---------------------------------------------------------------
// char
// ---------------------------------------------------------------
export class ScanCodeCharField extends ScanCodeField {}
ScanCodeCharField.components = { Field: CharField, ShowScanCodeDialogButton, ScanCodeCopyButton };
ScanCodeCharField.displayName = _lt('Copy Text to Clipboard');
ScanCodeCharField.supportedTypes = ['char'];

registry.category('fields').add('ScanCodeChar', ScanCodeCharField);

// ---------------------------------------------------------------
// text
// ---------------------------------------------------------------
export class ScanCodeTextField extends ScanCodeField {}
ScanCodeTextField.components = { Field: TextField, ShowScanCodeDialogButton, ScanCodeCopyButton };
ScanCodeTextField.displayName = _lt('Copy Multiline Text to Clipboard');
ScanCodeTextField.supportedTypes = ['text'];

registry.category('fields').add('ScanCodeText', ScanCodeTextField);

// ---------------------------------------------------------------
// url
// ---------------------------------------------------------------
export class ScanCodeURLField extends ScanCodeField {}
ScanCodeURLField.components = { Field: UrlField, ShowScanCodeDialogButton, ScanCodeCopyButton };
ScanCodeURLField.displayName = _lt('Copy URL to Clipboard');
ScanCodeURLField.supportedTypes = ['char'];

registry.category('fields').add('ScanCodeURL', ScanCodeURLField);
