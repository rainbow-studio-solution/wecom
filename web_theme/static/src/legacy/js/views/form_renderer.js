odoo.define('web_theme.MobileFormRenderer', function (require) {
	'use strict';

	const config = require('web.config');
	if (!config.device.isMobile) {
		return;
	}

	/**
	 * This file defines the MobileFormRenderer, an extension of the FormRenderer
	 * implementing some tweaks to improve the UX in mobile.
	 */

	const core = require('web.core');
	const FormRenderer = require('web.FormRenderer');

	const qweb = core.qweb;

	FormRenderer.include({
		/**
		 * Reset the 'state' of the drop down
		 * @override
		 */
		updateState: function () {
			this.isStatusbarButtonsDropdownOpen = undefined;
			return this._super(...arguments);
		},

		//--------------------------------------------------------------------------
		// Private
		//--------------------------------------------------------------------------

		/**
		 * Show action drop-down if there are multiple visible buttons/widgets.
		 *
		 * @private
		 * @override
		 */
		_renderStatusbarButtons: function (buttons) {
			// Removes 'o_invisible_modifier' buttons in addition to those that match this selector:
			// .o_form_view.o_form_editable .oe_read_only {
			//     display: none !important;
			// }
			const $visibleButtons = buttons.filter((button) => {
				return !(
					$(button).hasClass('o_invisible_modifier') ||
					(this.mode === 'edit' && $(button).hasClass('oe_read_only'))
				);
			});

			if ($visibleButtons.length > 1) {
				const $statusbarButtonsDropdown = $(
					qweb.render('StatusbarButtonsDropdown', {
						open: this.isStatusbarButtonsDropdownOpen
					})
				);
				$statusbarButtonsDropdown.find('.btn-group').on('show.bs.dropdown', () => {
					this.isStatusbarButtonsDropdownOpen = true;
				});
				$statusbarButtonsDropdown.find('.btn-group').on('hide.bs.dropdown', () => {
					this.isStatusbarButtonsDropdownOpen = false;
				});
				const $dropdownMenu = $statusbarButtonsDropdown.find('.dropdown-menu');
				buttons.forEach((button) => {
					const dropdownButton = $(button).addClass('dropdown-item');
					return $dropdownMenu.append(dropdownButton);
				});
				return $statusbarButtonsDropdown;
			}
			buttons.forEach((button) => $(button).removeClass('dropdown-item'));
			return this._super.apply(this, arguments);
		},
		/**
		 * Update the UI statusbar button after all modifiers are updated.
		 *
		 * @override
		 * @private
		 */
		_updateAllModifiers: function () {
			return this._super.apply(this, arguments).then(() => {
				const $statusbarButtonsContainer = this.$('.o_statusbar_buttons');
				const $statusbarButtons = $statusbarButtonsContainer.find('button.btn').toArray();
				$statusbarButtonsContainer.replaceWith(this._renderStatusbarButtons($statusbarButtons));
			});
		}
	});
});
