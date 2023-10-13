/** @odoo-module **/

import { FormController } from '@web/views/form/form_controller';
import { session } from '@web/session';
import { patch } from '@web/core/utils/patch';
import { append, createElement, setAttributes } from '@web/core/utils/xml';
import { scrollTo } from '@web/core/utils/scrolling';
import { onMounted, onWillUnmount, onPatched, useRef, useEffect, useState } from '@odoo/owl';

patch(FormController.prototype, 'web_theme.FormController', {
	setup() {
		this._super();
		// super.setup();
		this.offset = 300;
		this.theme = session.theme;
		this.displayScrollTopButton = this.theme['display_scroll_top_button'];
		this.chatter_position = this.theme['form_chatter_position'];

		const rootRef = useRef('root');
		this.scrollBarOffset = 300;
		this.state = useState({
			...this.state,
			content: {
				hasScrollBar: false,
				displayScrollButton: false,
				scrollingEl: null,
				topOffset: 0
			},
			form: {
				hasScrollBar: false,
				displayScrollButton: false,
				scrollingEl: null,
				topOffset: 0
			},
			chatter: {
				hasScrollBar: false,
				displayScrollButton: false,
				scrollingEl: null,
				topOffset: 0
			}
		});

		onMounted(() => {
			// if (rootRef.el.parentElement.classList.contains('modal-body')) {
			// 	return;
			// }
			// if (rootRef.el.classList.contains('o-settings-form-view')) {
			// 	return;
			// }
			// const contentEl = rootRef.el.querySelector('.o_content');
			// const formEl = rootRef.el.querySelector('.o_form_sheet_bg');
			// const chatterEl = rootRef.el.querySelector('.o_Chatter_scrollPanel');
			// if (contentEl) {
			// 	rootRef.el.dataset.chatterPosition = this.chatter_position;
			// 	contentEl.dataset.chatterPosition = this.chatter_position;
			// }
			// if (formEl) {
			// 	formEl.dataset.chatterPosition = this.chatter_position;
			// }
			// if (chatterEl) {
			// 	chatterEl.dataset.chatterPosition = this.chatter_position;
			// }
			// const chatterContainer = rootRef.el.querySelector('.o_FormRenderer_chatterContainer');
			// let formContainChatter = false;
			// if (chatterContainer && chatterContainer.parentElement === formEl) {
			// 	formContainChatter = true;
			// }
		});
	},

	get className() {
		var result = this._super(...arguments);
		if (this.chatter_position === 2) {
			result.o_xxs_form_view = false;
			result['o_xxl_form_view h-100'] = false;
		}
		return result;
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

		let scrollEl = scrollTopButton.parentElement;

		if (this.chatter_position === 1) {
			scrollEl = scrollTopButton.previousElementSibling.querySelector('.o_form_sheet_bg');
		}

		const duration = 500; //时间
		$(scrollEl).animate(
			{
				scrollTop: 0
			},
			duration
		);
		return false;
		// scrollTo(scrollEl, { isAnchor: true });
		// this.trigger_up("scrollTo", { top: 0 });
	}
});
