/** @odoo-module **/

// 参考 PdfViewerField  addons\web\static\src\views\fields\pdf_viewer\

import { _lt } from '@web/core/l10n/translation';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { url } from '@web/core/utils/urls';
import { standardFieldProps } from '@web/views/fields/standard_field_props';
import { FileUploader } from '@web/views/fields/file_handler';

import { Component, onWillUpdateProps, useState } from '@odoo/owl';

export class OfficeViewerField extends Component {
	setup() {
		this.notification = useService('notification');
		this.orm = useService('orm');
		this.state = useState({
			filePath: this.props.record.data[this.props.filePathField] || '',
			moduleName: this.props.moduleName || '',
			storagePath: this.props.storagePath || '',
			isValid: true,
			objectUrl: ''
		});
		// ! props.value 为 office文档的路径
		// ! props.record.resModel 为 当前表单的模型

		// console.log('props', this.props);
		// console.log('state', this.state);
		onWillUpdateProps((nextProps) => {
			// console.log('nextProps', nextProps);
			if (nextProps.readonly) {
			    this.state.filePath = nextProps.record.data[nextProps.filePathField] || "";
			    this.state.objectUrl = "";
			}
		});
	}

	get filePath() {
		return this.state.filePath || this.props.value || '';
	}

	get url() {
		if (!this.state.isValid || !this.props.value) {
			return null;
		}
		const objectUrl = _.str.sprintf(
			'https://view.officeapps.live.com/op/view.aspx?src=%s%s',
			window.location.protocol + '//' + window.location.host,
			this.props.value
		);
		const fileUrl = this.state.objectUrl || objectUrl;
		this.state.filePath = this.props.value;
		this.state.objectUrl = objectUrl;
		return fileUrl;
	}

	update({ data, name }) {
		// console.log(name, data);
		this.state.fileName = name || '';
		const { fileNameField, record } = this.props;
		const changes = { [this.props.name]: data || false };
		if (fileNameField in record.fields && record.data[fileNameField] !== name) {
			changes[fileNameField] = name || false;
		}
		return this.props.record.update(changes);
	}

	onFileRemove() {
		this.state.isValid = true;
		this.state.filePath = '';
		this.update({});
	}

	async onFileUploaded({ data, name, objectUrl }) {
		let self = this;
		const result = await this.orm.call('ir.module.module', 'upload_office_documents', [
			name,
			self.props.moduleName,
			self.props.storagePath,
			data
		]);

		if (result['state']) {
			name = result['file_name'];
			data = result['web_path'];
			objectUrl = result['web_path'];
			this.state.isValid = true;
			this.state.objectUrl = objectUrl;
			// console.log('完成上传', this.state);
			this.notification.add(
				result['msg'],
				{
					title: this.env._t("Successfully uploaded the file!"),
					type: "success",
					sticky: false,
				});
			this.update({ data, name });
		} else {
			this.notification.add(result['msg'], {
				title: this.env._t("Failed to upload file!"),
				type: "warning",
				sticky: false,
			});
		}
	}
	onLoadFailed() {
		this.state.isValid = false;
		this.notification.add(this.env._t('Could not display the selected Microsoft Office Documents'), {
			type: 'danger'
		});
	}
}
OfficeViewerField.template = 'web.OfficeViewerField';
OfficeViewerField.components = {
	FileUploader
};
OfficeViewerField.props = {
	...standardFieldProps,
	filePathField: { type: String, optional: true },
	previewImage: { type: String, optional: true },
	moduleName: { type: String, optional: true },
	storagePath: { type: String, optional: true },
	accept: { type: String, optional: true },
	height: { type: Number, optional: true }
};
OfficeViewerField.displayName = _lt('Microsoft Office Documents Viewer');
OfficeViewerField.supportedTypes = ['char'];
OfficeViewerField.extractProps = ({ attrs }) => {
	// console.log('accept', attrs.accept);
	return {
		filePathField: attrs.filePath,
		previewImage: attrs.options.preview_image,
		moduleName: attrs.module_name,
		storagePath: attrs.storage_path,
		accept: attrs.accept,
		height: Number(attrs.height)
	};
};

registry.category('fields').add('office_viewer', OfficeViewerField);
