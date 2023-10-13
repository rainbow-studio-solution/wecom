/** @odoo-module **/

import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { ListRenderer } from '@web/views/list/list_renderer';
import { ListController } from '@web/views/list/list_controller';
import { Widget } from '@web/views/widgets/widget';
import { WecomContactsDisplayField } from './fields/contacts_display';

const { Component, useState, useRef, useEnv, onWillStart, onMounted, onRendered, onWillUnmount } = owl;

/**
 * ^注意事项：
 * ^1. type合法值只能为 userName （用户名称）， departmentName （部门名称）
 * ^2. openid合法值为用户的openid或者部门的id
 * ^3. 如果type为userName，openid为用户的userid，那么会显示用户的名称
 * ^4. 如果type为departmentName，openid为部门的departmentid，那么会显示部门的名称
 * ^5. 每 20ms 最多绑定 1000 个 open-data 元素，超出的部分将被忽略
 **/
export class WecomContactsDisplayListController extends ListController {
	setup() {
		super.setup();
		this.modelName = this.props.resModel || '';
		// console.log(this.modelName);
	}
}
// WecomContactsDisplayListController.template = "wecom_widget.WecomContactsDisplayListView";

export class WecomContactsDisplayListRenderer extends ListRenderer {
	setup() {
		super.setup();

		this.orm = useService('orm');
		this.rpc = useService('rpc');

		let modelName = this.props.list.resModel || '';
		let postData = [];

		// 生成请求数据 postData
		_.forEach(this.props.list.records, function (record) {
			let data = record.data;
			let obj = {
				company_id: data.company_id[0],
				modelName: modelName
			};
			postData.push(obj);
		});

		this.postData = uniqueFunc(postData, 'company_id'); //去重

		function uniqueFunc(arr, uniId) {
			const res = new Map();
			return arr.filter((item) => !res.has(item[uniId]) && res.set(item[uniId], 1));
		}

		onWillStart(() => {
			this.onWillStart();
		});
		onMounted(() => {
			// this.onMounted();
		});
	}
	async onWillStart() {
		try {
			if (/MicroMessenger/i.test(navigator.userAgent)) {
				// 企微环境
				await this.configParams();
			} else {
				//非企微环境
			}

			// await agentConfig(agentConfigParams)
			await this.agentConfigParams();
			// WWOpenData.bindAll(document.querySelectorAll('ww-open-data'))
		} catch (error) {
			console.error(error);
		}
	}
	onMounted() {
		// 在渲染组件之后，
		let allWWOpenDataEl = document.getElementsByTagName('ww-open-data');
		// console.log(allWWOpenDataEl);
	}

	onPatched() {
		// 在发生改变时执行， 此方法在元素根据新状态重新渲染之前进行调用。
	}
	//-----------------------------------------------
	// Handlers
	//-----------------------------------------------
	async configParams(config) {}

	async agentConfigParams(config) {
		this.orm.call('wecom.client_api', 'geContactsDisplayAgentConfig', [this.postData]).then((result) => {
			if (result.code === 0) {
				let config = result.configs[0];
				wx.agentConfig({
					corpid: config.corpid, // 必填，企业微信的corpid，必须与当前登录的企业一致
					agentid: config.agentid, // 必填，企业微信的应用id （e.g. 1000247）
					timestamp: config.timestamp, // 必填，生成签名的时间戳
					nonceStr: config.nonceStr, // 必填，生成签名的随机串
					signature: config.signature, // 必填，签名，见附录-JS-SDK使用权限签名算法
					jsApiList: config.jsApiList, //必填，传入需要使用的接口名称，不要传入不需要使用的接口名称，减少权限，减少出错
					success: function (res) {
						console.log(res, '请求微信成功');
						WWOpenData.bindAll(document.querySelectorAll('ww-open-data'));
					},
					fail: function (res) {
						console.log('查看错误信息' + res);
						if (res.errMsg.indexOf('function not exist') > -1) {
							alert('版本过低请升级');
						}
					}
				});
			}
		});
	}
	getColumns(record) {
		const columns = super.getColumns(record);

		const sectionColumns = columns.filter((col) => col.widget === 'wecom_contacts_display_component');
		// console.log(sectionColumns);

		return columns;
	}
	getSectionColumns(columns) {
		const sectionColumns = columns.filter((col) => col.widget === 'wecom_contacts_display_component');
		// console.log(sectionColumns);
		return sectionColumns;
	}
}
WecomContactsDisplayListRenderer.recordRowTemplate = 'wecom_widget.WecomContactsDisplayListRenderer.RecordRow';
WecomContactsDisplayListRenderer.components = {
	...ListRenderer.components
	// Field: WecomContactsDisplayField,
};

registry.category('views').add('wecom_contacts_display_component_list', {
	...listView,
	Controller: WecomContactsDisplayListController,
	Renderer: WecomContactsDisplayListRenderer
});
