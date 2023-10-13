/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, onWillUnmount, onPatched, useRef, useEffect, useState } from '@odoo/owl';
import { SettingsPage } from '@web/webclient/settings_form_view/settings/settings_page';

patch(SettingsPage.prototype, 'web_theme.SettingsPage', {
	setup() {
		this._super();
		this.offset = 300;
		this.theme = session.theme;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];
		this.settingsRef = useRef('settings');

		onMounted(() => {
			// settings
			this.settingsRef.el.addEventListener('scroll', this.onScrollSettingsEl);
		});
	},
	onScrollSettingsEl() {
		const offset = 300;
		// console.log('settingsEl', this,this.parentElement);

		const scrollTopButton = this.parentElement.querySelector('.o_scroll_top');
		if (this.scrollTop > offset) {
			scrollTopButton.classList.remove('o_hidden');
		} else {
			scrollTopButton.classList.add('o_hidden');
		}
	},
	onClickScrollToTop(ev) {
		let scrollTopButton = ev.target;
		if (scrollTopButton.tagName == 'span') {
			scrollTopButton = scrollTopButton.parentNode;
		} else if (scrollTopButton.tagName == 'svg') {
			scrollTopButton = scrollTopButton.parentNode.parentNode;
		} else if (scrollTopButton.tagName == 'path') {
			scrollTopButton = scrollTopButton.parentNode.parentNode.parentNode;
		} else if (scrollTopButton.tagName == 'rect') {
			scrollTopButton = scrollTopButton.parentNode.parentNode.parentNode;
		}

		const scrollingEl = scrollTopButton.parentElement.querySelector('.settings');

		const duration = 500; //时间
		$(scrollingEl).animate(
			{
				scrollTop: 0
			},
			duration
		);
		return false;
	}
});
