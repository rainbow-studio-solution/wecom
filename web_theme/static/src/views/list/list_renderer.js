/** @odoo-module */

import { patch } from '@web/core/utils/patch';
import { ListRenderer } from '@web/views/list/list_renderer';
import { session } from '@web/session';
import { onMounted, onWillUnmount, onPatched, useRef, useEffect, useState } from '@odoo/owl';

patch(ListRenderer.prototype, 'web_theme.ListRenderer', {
	setup() {
		this._super(...arguments);

		this.theme = session.theme;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];
		this.list_herder_fixed = this.theme['list_herder_fixed'];

		onMounted(() => {
			const scrollEl = this.rootRef.el;
			if (this.list_herder_fixed) {
				scrollEl.dataset.herderFixed = this.list_herder_fixed;
			}
			if (scrollEl.scrollHeight > scrollEl.clientHeight) {
				scrollEl.addEventListener('scroll', this.onScrollEl);
			}
		});
	},
	onScrollEl() {
		const offset = 300;
		const scrollTopButton = this.querySelector('.o_scroll_top');

		if (this.scrollTop > 0 && this.scrollTop < offset) {
			if (this.dataset.herderFixed === 'true') {
				this.classList.add('o_list_herder_fixed');
			}
		} else if (this.scrollTop > 0 && this.scrollTop > offset) {
			scrollTopButton.classList.remove('o_hidden');
		} else if (this.scrollTop > 0 && this.scrollTop < offset) {
			scrollTopButton.classList.remove('o_hidden');
		} else {
			if (this.dataset.herderFixed === 'true') {
				this.classList.remove('o_list_herder_fixed');
			}
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

		let scrollingEl = scrollTopButton.parentElement;

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
