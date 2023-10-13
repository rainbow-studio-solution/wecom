odoo.define('web_theme.Dialog', function (require) {
	'use strict';

	const config = require('web.config');
	if (!config.device.isMobile) {
		return;
	}

	const Dialog = require('web.Dialog');

	Dialog.include({
		/**
		 * @override
		 *
		 * @param {Widget} parent
		 * @param {Array} options.headerButtons
		 */
		init(parent, { headerButtons }) {
			this._super.apply(this, arguments);
			this.headerButtons = headerButtons || [];
		},

		/**
		 * Renders the header as a "Top App Bar" layout :
		 * - navigation icon: right arrow that closes the dialog;
		 * - title: same as on desktop;
		 * - action buttons: optional actions related to the current screen.
		 * Only applied for fullscreen dialog.
		 *
		 * Also, get the current scroll position for mobile devices in order to
		 * maintain offset while dialog is closed.
		 *
		 * @override
		 */
		async willStart() {
			const prom = await this._super.apply(this, arguments);
			if (this.renderHeader && this.fullscreen) {
				const $modalHeader = this.$modal.find('.modal-header');
				$modalHeader.find('button.btn-close').remove();
				const $navigationBtn = $('<button>', {
					class: 'btn fa fa-arrow-left',
					'data-bs-dismiss': 'modal',
					'aria-label': 'close'
				});
				$modalHeader.prepend($navigationBtn);
				const $btnContainer = $('<div>');
				this._setButtonsTo($btnContainer, this.headerButtons);
				$modalHeader.append($btnContainer);
			}
			// need to get scrollPosition prior opening the dialog else body will scroll to
			// top due to fixed position applied on it with help of 'modal-open' class.
			this.scrollPosition = {
				top: window.scrollY || document.documentElement.scrollTop,
				left: window.scrollX || document.documentElement.scrollLeft
			};
			return prom;
		},

		/**
		 * Scroll to original position while closing modal in mobile devices
		 *
		 * @override
		 */
		destroy() {
			if (this.$modal && $('.modal[role="dialog"]').filter(':visible').length <= 1) {
				// in case of multiple open dialogs, only reset scroll while closing the last one
				// (it can be done only if there's no fixed position on body and thus by removing
				// 'modal-open' class responsible for fixed position)
				this.$modal.closest('body').removeClass('modal-open');
				window.scrollTo(this.scrollPosition);
			}
			this._super(...arguments);
		}
	});
});
