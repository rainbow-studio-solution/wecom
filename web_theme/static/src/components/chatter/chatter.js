/** @odoo-module **/

import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, onWillUnmount, onPatched, useExternalListener, useRef, useEffect, useState } from '@odoo/owl';
import { Chatter } from '@mail/components/chatter/chatter';

patch(Chatter.prototype, 'web_theme.Chatter', {
	setup() {
		this._super();

		this.theme = session.theme;
		this.offset = 300;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];
		this.chatter_position = this.theme['form_chatter_position'];

		const scrollPanel = useRef('scrollPanel');

		onMounted(() => {
			const scrollEl = scrollPanel.el;
			const resizeObserver = new ResizeObserver((entries) => {
				const scrollEl = entries[0].target;
				if (scrollEl.scrollHeight > scrollEl.clientHeight && this.chatter_position === 1) {
					scrollEl.addEventListener('scroll', this.onScrollEl);
				}
			});
			if (scrollPanel.el != null) {
				resizeObserver.observe(scrollPanel.el);
			}
		});
	},
	onScrollEl() {
		const offset = 300;
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

		const rootEl = this.__owl__.refs.root;
		let scrollingEl = rootEl.querySelector('.o_Chatter_scrollPanel');

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
