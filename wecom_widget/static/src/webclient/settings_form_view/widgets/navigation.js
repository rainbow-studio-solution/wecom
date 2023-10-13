/** @odoo-module */

import { registry } from '@web/core/registry';
import { _t } from '@web/core/l10n/translation';
import { unique } from '@web/core/utils/arrays';
import { useService } from '@web/core/utils/hooks';

const { Component, useState, onWillStart } = owl;

class WecomResConfigNavigation extends Component {
	setup() {}
	_jumpAnchor(ev) {
		ev.preventDefault(); //阻止默认行为
		let button = ev.target;
		if (button.tagName != 'A') {
			button = button.parentNode;
		}
		let anchor = button.href.split('#')[1];
		let settingsEl = document.querySelector('.settings');
		let wecomSettingsEl = document.querySelector('.app_settings_block');
		let anchorEl = document.getElementById(anchor);
		if (anchorEl) {
			if (wecomSettingsEl.clientHeight > settingsEl.clientHeight) {
				// settingsEl.scrollTo({
				//     top: anchorEl.offsetTop,
				//     behavior: 'smooth'
				// })
				$(settingsEl).animate(
					{
						// scrollTop: anchorEl.offsetTop,
						scrollTop: anchorEl.offsetTop
					},
					1000
				);
			}
		}
	}
}
WecomResConfigNavigation.template = 'wecom_widget.res_config_wecom_navigation_menu';
registry.category('view_widgets').add('res_config_wecom_navigation_menu', WecomResConfigNavigation);
