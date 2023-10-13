odoo.define('web_mobile.barcode_fields', function (require) {
"use strict";

var field_registry = require('web.field_registry');
require('web._field_registry');
var relational_fields = require('web.relational_fields');

const { _t } = require('web.core');
const BarcodeScanner = require('@web/webclient/barcode/barcode_scanner');

/**
 * Override the Many2One to open a dialog in mobile.
 */
var FieldMany2OneBarcode = relational_fields.FieldMany2One.extend({
    template: "FieldMany2OneBarcode",
    events: _.extend({}, relational_fields.FieldMany2One.prototype.events, {
        'click .o_barcode': '_onBarcodeButtonClick',
    }),

    /**
     * @override
     */
    start: function () {
        var result = this._super.apply(this, arguments);
        this._startBarcode();
        return result;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * External button is visible
     *
     * @return {boolean}
     * @private
     */
    _isExternalButtonVisible: function () {
        return this.$external_button.is(':visible');
    },
    /**
     * Hide the search more option
     *
     * @param {Array} values
     */
    _manageSearchMore(values) {
        return values;
    },
    /**
     * @override
     * @private
     */
    _renderEdit: function () {
        this._super.apply(this, arguments);
        // Hide button if a record is set or external button is visible
        if (this.$barcode_button) {
            this.$barcode_button.toggle(!this._isExternalButtonVisible());
        }
    },
    /**
     * Initialisation of barcode button
     *
     * @private
     */
    _startBarcode: function () {
        this.$barcode_button = this.$('.o_barcode');
        // Hide button if a record is set
        this.$barcode_button.toggle(!this.isSet());
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * On click on button
     *
     * @private
     */
    async _onBarcodeButtonClick() {
        const barcode = await BarcodeScanner.scanBarcode();
        if (barcode) {
            this._onBarcodeScanned(barcode);
            if ('vibrate' in window.navigator) {
                window.navigator.vibrate(100);
            }
        } else {
            this.displayNotification({
                type: 'warning',
                message: 'Please, scan again !',
            });
        }
    },
    /**
     * When barcode is scanned
     *
     * @param barcode
     * @private
     */
    async _onBarcodeScanned(barcode) {
        const results = await this._search(barcode);
        const records = results.filter(r => !!r.id);
        if (records.length === 1) {
            this._setValue({ id: records[0].id });
        } else {
            const dynamicFilters = [{
                description: _.str.sprintf(_t('Quick search: %s'), barcode),
                domain: [['id', 'in', records.map(r => r.id)]],
            }];
            this._searchCreatePopup("search", false, {}, dynamicFilters);
        }
    },
});

if (BarcodeScanner.isBarcodeScannerSupported()) {
    field_registry.add('many2one_barcode', FieldMany2OneBarcode);
}

return FieldMany2OneBarcode;
});
