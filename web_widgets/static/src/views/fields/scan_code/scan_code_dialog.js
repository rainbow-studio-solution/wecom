/** @odoo-module */

// ------------------------------------------------------------------------------------------
// 参考
// web\static\src\webclient\barcode\barcode_scanner.js
// https://developer.mozilla.org/zh-CN/docs/Web/API/MediaDevices/getUserMedia
// https://developer.mozilla.org/zh-CN/docs/Web/API/MediaDevices/enumerateDevices
// ------------------------------------------------------------------------------------------

import { browser } from '@web/core/browser/browser';
import { Dialog } from '@web/core/dialog/dialog';
import { _lt, _t } from '@web/core/l10n/translation';
import { useService,useChildRef } from '@web/core/utils/hooks';

import { Component, onMounted, onRendered  } from '@odoo/owl';

export class ScanCodeDialog extends Component {
	setup() {
		this.env.dialogData.close = () => this._cancel();
		this.notificationService = useService('notification');
		this.modalRef = useChildRef();
		this.isConfirmedOrCancelled = false; // ensures we do not confirm and/or cancel twice
		this.isWecomBrowser = this.is_wecom_browser();
		// const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter()

		console.log('dialog', this.props);
		onMounted(async () => {
			// const constraints = {
			// 	video: { facingMode: this.props.facingMode },
			// 	audio: false
			// };

			browser.navigator.mediaDevices
				.enumerateDevices()
				.then(function (devices) {
					devices.forEach(function (device) {
						console.log(device.kind + ': ' + device.label + ' id = ' + device.deviceId);
					});
				})
				.catch(function (err) {
					console.log(err.name + ': ' + err.message);
				});

			try {
				// this.stream = await browser.navigator.mediaDevices.getUserMedia(constraints);
				// console.log(this.stream )
				browser.navigator.mediaDevices.ondevicechange = (event) => {
					console.log(event);
				};
			} catch (err) {
				const errors = {
					NotFoundError: _t('No device can be found.'),
					NotAllowedError: _t('Odoo needs your authorization first.')
				};
				const errorMessage = _t('Could not start scanning. ') + (errors[err.name] || err.message);
				console.log(err);
				// this.onError(new Error(errorMessage));
				return;
			}

			await this.initCameraSelect();
		});
		onRendered(() => {
			this.onRendered();
		});
	}
	onRendered() {
		// 在渲染组件之前，会用来初始化一些数据等
		// navigator.mediaDevices.ondevicechange = event => {
		// 	console.log(event)
		// 	// self.updateDeviceList();
		// }
	}
	async initCameraSelect() {}
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
	async _cancel() {
		if (this.isConfirmedOrCancelled) {
			return;
		}
		this.isConfirmedOrCancelled = true;
		this.disableButtons();
		if (this.props.cancel) {
			try {
				await this.props.cancel();
			} catch (e) {
				this.props.close();
				throw e;
			}
		}
		this.props.close();
	}
	async _confirm() {
		if (this.isConfirmedOrCancelled) {
			return;
		}
		this.isConfirmedOrCancelled = true;
		this.disableButtons();
		if (this.props.confirm) {
			try {
				await this.props.confirm();
			} catch (e) {
				this.props.close();
				throw e;
			}
		}
		this.props.close();
	}
	disableButtons() {
		if (!this.modalRef.el) {
			return; // safety belt for stable versions
		}
		for (const button of [...this.modalRef.el.querySelectorAll('.modal-footer button')]) {
			button.disabled = true;
		}
	}
}
ScanCodeDialog.template = 'web.ScanCodeDialog';
ScanCodeDialog.components = { Dialog };
ScanCodeDialog.props = {
	fullscreen: { type: Boolean, optional: true },
	close: Function,
	title: {
		validate: (m) => {
			return typeof m === 'string' || (typeof m === 'object' && typeof m.toString === 'function');
		},
		optional: true
	},
	body: String,
	confirm: { type: Function, optional: true },
	confirmLabel: { type: String, optional: true },
	cancel: { type: Function, optional: true },
	cancelLabel: { type: String, optional: true }
};
ScanCodeDialog.defaultProps = {
	contentClass: 'o_scan_code_dialog',
	bodyClass: '',
	fullscreen: true,
	confirmLabel: _lt('Ok'),
	cancelLabel: _lt('Cancel'),
	title: _lt('Scan Code')
};
