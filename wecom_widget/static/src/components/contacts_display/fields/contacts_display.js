/** @odoo-module **/

import { _lt } from '@web/core/l10n/translation';
import { registry } from '@web/core/registry';
import { standardFieldProps } from '@web/views/fields/standard_field_props';
import { browser } from '@web/core/browser/browser';
import { useService } from '@web/core/utils/hooks';
import { X2ManyField } from '@web/views/fields/x2many/x2many_field';

const { Component, useState, useRef, useEnv, onWillStart, onMounted, onRendered, onWillUnmount } = owl;

/**
 * ^注意事项：
 * ^1. type合法值只能为 userName （用户名称）， departmentName （部门名称）
 * ^2. openid合法值为用户的openid或者部门的id
 * ^3. 如果type为userName，openid为用户的userid，那么会显示用户的名称
 * ^4. 如果type为departmentName，openid为部门的departmentid，那么会显示部门的名称
 * ^5. 每 20ms 最多绑定 1000 个 open-data 元素，超出的部分将被忽略
 **/
export class WecomContactsDisplayField extends Component {
	setup() {
		super.setup();
		this.orm = useService('orm');
		// console.log(this.props)
		this.model = this.props.record.resModel;
		this.resId = this.props.record.resId;

		// console.log(this.model, this.resId);
		/**
		 * wx.config 参数
		 * @see https://open.work.weixin.qq.com/api/doc/90001/90144/90547
		 */
		this.configParams = {};

		/**
		 * wx.agentConfig 参数
		 * @see https://open.work.weixin.qq.com/api/doc/90001/90144/90548
		 */
		this.agentConfigParams = {};

		this.opendatas = [];
		// useInputField({ getValue: () => this.props.value || "" });
		// console.log(this.agentConfigParams);
		onWillStart(() => {
			// this.onWillStart();
		});
	}
	async onWillStart() {
		// 在渲染组件之前，会用来初始化一些数据等
		try {
			if (/MicroMessenger/i.test(navigator.userAgent)) {
				// 企微环境
				await config(this.configParams);
			} else {
				//非企微环境
			}
			// await config(this.agentConfigParams)
			await this.generateAgentConfigParams();
		} catch (error) {
			console.log(error);
		}
	}
	onMounted() {
		// 在渲染组件之后，
		console.log(this);
	}

	//-----------------------------------------------
	// Handlers
	//-----------------------------------------------
	async generateAgentConfigParams() {
		// 生成 agentConfig 参数

		const result = await this.orm.call('wecom.client_api', 'geContactsDisplayAgentConfig', [
			this.model,
			this.resId
		]);

		// this.agentConfigParams = {};
		// return {
		//     corpid: this.configParams.corpid,
		//     agentid: this.configParams.agentid,
		//     timestamp: this.configParams.timestamp,
		//     nonceStr: this.configParams.nonceStr,
		//     signature: this.configParams.signature,
		//     jsApiList: ["selectExternalContact"],
		// }
	}

	/**
	 * 调用 wx.config
	 *
	 * @see https://open.work.weixin.qq.com/api/doc/90001/90144/90547
	 */
	async config(config) {
		return new Promise((resolve, reject) => {
			console.info('wx.config', config);
			wx.config(config);
			wx.ready(resolve);
			wx.error(reject);
		}).then(
			() => {
				console.info('wx.ready');
			},
			(error) => {
				console.error('wx.error', error);
				throw error;
			}
		);
	}

	/**
	 * 调用 wx.agentConfig
	 *
	 * @see https://open.work.weixin.qq.com/api/doc/90001/90144/90548
	 */
	async agentConfig(config) {
		return new Promise((success, fail) => {
			console.info('wx.agentConfig', config);
			wx.agentConfig({
				...config,
				success,
				fail
			});
		}).then(
			(res) => {
				console.info('wx.agentConfig success', res);
				return res;
			},
			(error) => {
				console.error('wx.agentConfig fail', error);
				throw error;
			}
		);
	}
}
WecomContactsDisplayField.template = 'oec_widget.WecomContactsDisplay';
WecomContactsDisplayField.props = {
	...standardFieldProps,
	datatype: {
		type: String,
		optional: true
	}
	// openid: {
	//     type: String,
	//     optional: true
	// },
};
WecomContactsDisplayField.displayName = _lt('Wecom Contacts Display Component');
WecomContactsDisplayField.supportedTypes = ['wecom_contacts_display_component'];
WecomContactsDisplayField.extractProps = ({ attrs, field }) => {
	// console.log(attrs, field);
	return {
		datatype: attrs.type
		// openid: attrs.openid,
	};
};
registry.category('fields').add('wecom_contacts_display_component', WecomContactsDisplayField);
