odoo.define('web_theme.ListControllerMobile', function (require) {
	'use strict';

	const config = require('web.config');
	if (!config.device.isMobile) {
		return;
	}

	const ListController = require('web.ListController');

	ListController.include({
		events: Object.assign({}, ListController.prototype.events, {
			'click .o_discard_selection': '_onDiscardSelection'
		}),

		//--------------------------------------------------------------------------
		// Public
		//--------------------------------------------------------------------------

		/**
		 * In mobile, we hide the "export" button.
		 *
		 * @override
		 */
		renderButtons() {
			this._super(...arguments);
			this.$buttons.find('.o_list_export_xlsx').hide();
		},
		/**
		 * In mobile, we hide the "export" button.
		 *
		 * @override
		 */
		updateButtons() {
			this._super(...arguments);
			this.$buttons.find('.o_list_export_xlsx').hide();
		},

		/**
		 * In mobile, we let the selection banner be added to the ControlPanel to enable the ActionMenus.
		 *
		 * @override
		 */
		async updateControlPanel() {
			const value = await this._super(...arguments);
			const displayBanner = Boolean(this.$selectionBox);
			if (displayBanner) {
				this._controlPanelWrapper.el.querySelector('.o_cp_bottom').prepend(this.$selectionBox[0]);
			}
			return value;
		},

		//--------------------------------------------------------------------------
		// Handlers
		//--------------------------------------------------------------------------

		/**
		 * Discard the current selection by unselecting any selected records.
		 *
		 * @private
		 */
		_onDiscardSelection() {
			this.renderer.$('tbody .o_list_record_selector input:not(":disabled")').prop('checked', false);
			this.renderer._updateSelection();
		}
	});
});
