odoo.define('web_theme.relational_fields', function (require) {
	'use strict';

	var config = require('web.config');
	if (!config.device.isMobile) {
		return;
	}

	/**
	 * In this file, we override some relational fields to improve the UX in mobile.
	 */

	var core = require('web.core');
	var relational_fields = require('web.relational_fields');

	var FieldStatus = relational_fields.FieldStatus;
	var FieldMany2One = relational_fields.FieldMany2One;
	var FieldX2Many = relational_fields.FieldX2Many;

	var qweb = core.qweb;

	FieldStatus.include({
		/**
		 * Override the custom behavior of FieldStatus to hide it if it is not set,
		 * in mobile (which is the default behavior for fields).
		 *
		 * @returns {boolean}
		 */
		isEmpty: function () {
			return !this.isSet();
		},

		//--------------------------------------------------------------------------
		// Private
		//--------------------------------------------------------------------------

		/**
		 * @override
		 * @private
		 */
		_render: function () {
			this.$el.html(
				qweb.render('FieldStatus.content.mobile', {
					selection: this.status_information,
					status: _.findWhere(this.status_information, {
						selected: true
					}),
					clickable: this.isClickable
				})
			);
		}
	});

	/**
	 * Override the Many2One to prevent autocomplete and open kanban view in mobile for search.
	 */

	FieldMany2One.include({
		start: function () {
			var superRes = this._super.apply(this, arguments);
			this.$input.prop('readonly', true);
			return superRes;
		},
		//--------------------------------------------------------------------------
		// Private
		//--------------------------------------------------------------------------

		/**
		 * Don't bind autocomplete in the mobile as it uses a different mechanism
		 * On clicking Many2One will directly open popup with kanban view
		 *
		 * @private
		 * @override
		 */
		_bindAutoComplete: function () {},

		/**
		 * override to add selectionMode option to search create popup option
		 *
		 * @private
		 * @override
		 */
		_getSearchCreatePopupOptions: function () {
			var self = this;
			var searchCreatePopupOptions = this._super.apply(this, arguments);
			_.extend(searchCreatePopupOptions, {
				selectionMode: true,
				on_clear: function () {
					self.reinitialize(false);
				}
			});
			return searchCreatePopupOptions;
		},

		/**
		 * We always open Many2One search dialog for select/update field value
		 * instead of autocomplete
		 *
		 * @private
		 * @override
		 */
		_toggleAutoComplete: function () {
			this._searchCreatePopup('search');
		}
	});

	FieldX2Many.include({
		//--------------------------------------------------------------------------
		// Private
		//--------------------------------------------------------------------------

		/**
		 * @override
		 * @private
		 */
		_renderButtons: function () {
			var result = this._super.apply(this, arguments);
			if (this.$buttons) {
				this.$buttons
					.find('.btn-secondary')
					.removeClass('btn-secondary')
					.addClass('btn-primary btn-add-record');
			}
			return result;
		}
	});
});
