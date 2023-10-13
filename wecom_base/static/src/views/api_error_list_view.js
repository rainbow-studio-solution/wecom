/** @odoo-module */

import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';

import { listView } from '@web/views/list/list_view';
import { ListController } from '@web/views/list/list_controller';
import { _t } from 'web.core';

export class WecomApiErrorListController extends ListController {
	setup() {
		super.setup();
		this.orm = useService('orm');
		this.action = useService('action');
	}
	async onClickGetApiErrorCode() {
		const result = await this.orm.call('wecom.service_api_error', 'get_api_error_eode', []);
		if (result['state']) {
			this.action.doAction({
				type: 'ir.actions.client',
				tag: 'display_notification',
				params: {
					type: 'success',
					title: _t('Get successfully!'),
					message: result['msg'],
					sticky: false,
					next: {
						type: 'ir.actions.client',
						tag: 'reload'
					}
					// buttons: [{
					//     text: _t("Refresh"),
					//     click: () => {
					//         window.location.reload(true);
					//     },
					//     primary: true
					// }],
				}
			});
		} else {
			this.action.doAction({
				type: 'ir.actions.client',
				tag: 'display_notification',
				params: {
					type: 'danger',
					title: _t('Get failed!'),
					message: result['msg'],
					sticky: true
				}
			});
		}
	}
}

export const WecomApiErrorListView = {
	...listView,
	Controller: WecomApiErrorListController,
	buttonTemplate: 'WecomApiErrorCodeListView.buttons'
};
registry.category('views').add('wecom_api_error_list', WecomApiErrorListView);
