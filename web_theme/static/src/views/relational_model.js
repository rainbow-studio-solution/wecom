/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { DynamicList, DynamicRecordList, DynamicGroupList } from '@web/views/relational_model';

patch(DynamicRecordList.prototype, 'web_theme.DynamicRecordList', {
	setup() {
		this._super(...arguments);
		this.theme = session.theme;
		if (this.theme['list_rows_limit']) {
			this.limit = this.theme['list_rows_limit'];
		}
	}
});
