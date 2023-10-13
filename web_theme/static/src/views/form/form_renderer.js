/** @odoo-module **/

import { FormRenderer } from '@web/views/form/form_renderer';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { onMounted, onWillUnmount, onPatched, useExternalListener, useRef, useEffect, useState } from '@odoo/owl';

import { scrollTo } from '@web/core/utils/scrolling';

patch(FormRenderer.prototype, 'web_theme.FormRenderer', {
	setup() {
		this._super();
		this.theme = session.theme;

		this.offset = 300;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];
		this.chatter_position = this.theme['form_chatter_position'];

		const rootRef = useRef('compiled_view_root');

		this.state = useState({
			...this.state
		});
		onMounted(() => {
			// 使用 ResizeObserver 监听元素尺寸变化
			const resizeObserver = new ResizeObserver((entries) => {
				const formEl = entries[0].target;
				if (formEl != null) {
					let scrollEl = formEl.parentElement;

					if (this.chatter_position === 1) {
						scrollEl = formEl.querySelector('.o_form_sheet_bg');
					}

					if (scrollEl != null) {
						if (scrollEl.scrollHeight > scrollEl.clientHeight) {
							if (this.chatter_position === 1) {
								scrollEl.addEventListener('scroll', this.onScrollFormEl);
							}
							if (this.chatter_position === 2) {
								scrollEl.addEventListener('scroll', this.onScrollContentEl);
							}
						}
					}
				}
			});
			if (rootRef.el != null) {
				resizeObserver.observe(rootRef.el);
			}
		});
	},
	onScrollContentEl() {
		const offset = 300;
		const scrollTopButton = this.querySelector('.o_scroll_top');

		if (this.scrollTop > offset) {
			scrollTopButton.classList.remove('o_hidden');
		} else {
			scrollTopButton.classList.add('o_hidden');
		}
	},
	onScrollFormEl() {
		const offset = 300;
		const scrollTopButton = this.parentElement.parentElement.querySelector('.o_scroll_top');

		if (this.scrollTop > offset) {
			scrollTopButton.classList.remove('o_hidden');
		} else {
			scrollTopButton.classList.add('o_hidden');
		}
	}
});
