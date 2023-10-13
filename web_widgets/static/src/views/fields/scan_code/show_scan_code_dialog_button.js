/** @odoo-module **/

import { browser } from '@web/core/browser/browser';
import { _lt, _t } from '@web/core/l10n/translation';
import { Tooltip } from '@web/core/tooltip/tooltip';
import { ScanCodeDialog } from './scan_code_dialog';
import { useService } from '@web/core/utils/hooks';

import { Component, useRef } from '@odoo/owl';

export class ShowScanCodeDialogButton extends Component {
	setup() {
		this.button = useRef('button');
		this.notificationService = useService('notification');
		this.popover = useService('popover');
		this.dialogService = useService('dialog');
		this.isWecomBrowser = this.is_wecom_browser();

		console.log(this.props);
	}
	is_wecom_browser() {
		var ua = navigator.userAgent.toLowerCase();
		let isWx = ua.match(/MicroMessenger/i) == 'micromessenger';
		if (!isWx) {
			return false;
		} else {
			let isWxWork = ua.match(/WxWork/i) == 'wxwork';
			if (isWxWork) {
				return true;
			} else {
				return false;
			}
		}
	}
	showTooltip() {
		const closeTooltip = this.popover.add(this.button.el, Tooltip, {
			tooltip: this.props.successText
		});
		browser.setTimeout(() => {
			closeTooltip();
		}, 800);
	}

	async onClick() {
		let self = this;
		if (!browser.navigator.mediaDevices || !browser.navigator.mediaDevices.enumerateDevices) {
			return this.notificationService.add(_t('The current browser environment does not support enumerateDevices()! Unable to load camera.'), {
				// className: payload.className,
				sticky: false,
				title: _t('Error!'),
				type: 'warning'
			});
		} else {
			return new Promise((resolve) => {
				this.dialogService.add(
					ScanCodeDialog,
					{
						title: self.props.fieldNameText,
						body: self.props.content,
						confirm: async () => {
							// await this.orm.call("hr.expense", "action_approve_duplicates", [record.resId]);
							// resolve(true);
						}
					},
					{
						onClose: resolve.bind(null, false)
					}
				);
			});
		}

		// if (!this.isWecomBrowser) {
		// 	this.notificationService.add(
		// 		_t("Non WeCom application built-in browser!"),
		// 		{
		// 		// className: payload.className,
		// 		sticky: false,
		// 		title: _t("Error!"),
		// 		type: "warning",
		// 	});
		// }
		// let write;
		// // any kind of content can be copied into the clipboard using
		// // the appropriate native methods
		// if (typeof this.props.content === 'string' || this.props.content instanceof String) {
		// 	write = (value) => browser.navigator.clipboard.writeText(value);
		// } else {
		// 	write = (value) => browser.navigator.clipboard.write(value);
		// }
		// try {
		// 	await write(this.props.content);
		// } catch (error) {
		// 	return browser.console.warn(error);
		// }
		// this.showTooltip();
	}
}
ShowScanCodeDialogButton.template = 'web.ShowScanCodeDialogButton';
ShowScanCodeDialogButton.props = {
	fieldNameText: { type: String, optional: true },
	content: { type: [String, Object], optional: true },
};
