/** @odoo-module **/

// import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, onWillUnmount, onPatched, useRef, useEffect, useState } from '@odoo/owl';

patch(KanbanRenderer.prototype, 'web_theme.KanbanRenderer', {
	setup() {
		this._super();

		this.offset = 300;
		this.theme = session.theme;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];

		const rootRef = useRef('root');

		onMounted(() => {
			const scrollEl = rootRef.el;
			if (scrollEl.scrollHeight > scrollEl.clientHeight) {
				scrollEl.addEventListener('scroll', this.scrollEl);
			}
		});
	},
	onScrollEl() {
		const offset = 300;
		const scrollTopButton = this.querySelector('.o_scroll_top');
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
