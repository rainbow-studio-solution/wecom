/** @odoo-module **/

import { View } from '@web/views/view';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';

patch(View.prototype, 'web_theme.View', {
	setup() {
		this._super();
		// console.log(this);
	}
});
