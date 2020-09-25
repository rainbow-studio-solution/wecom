odoo.define('web.SearchPanelMobile', function (require) {

    var config = require('web.config');
    if (!config.device.isMobile) {
        return;
    }

    var core = require('web.core');
    var SearchPanel = require('web.SearchPanel');

    var qweb = core.qweb;

    SearchPanel.include({
        tagName: 'details',
        summaryTemplate: 'SearchPanel.SummaryMobile',
        events: _.extend({}, SearchPanel.prototype.events, {
            'click .o_search_panel_mobile_bottom_close': '_onClickClose',
        }),

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Close the SearchPanel
         */
        close: function () {
            this.el.removeAttribute('open');
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Compute to create the ancestor tree with all previous category names.
         *
         * @private
         * @returns {Object[]}
         */
        _getCategorySelection: function () {
            var self = this;
            return Object.keys(this.categories).reduce(function (selection, categoryId) {
                var category = self.categories[categoryId];
                if (category.activeValueId) {
                    var orderedCategoryIDs = [category.activeValueId].concat(self._getAncestorValueIds(category, category.activeValueId));
                    var orderedCategoryNames = orderedCategoryIDs.map(function (valueId) {
                        return category.values[valueId].display_name;
                    });
                    selection.push({
                        values: orderedCategoryNames,
                        icon: category.icon,
                        color: category.color,
                    });
                }
                return selection;
            }, []);
        },
        /**
         * Compute and return an array of the current filters' selection to be displayed in
         * the summary of the SearchPanel.
         *
         * @private
         * @returns {Object[]}
         */
        _getFilterSelection: function () {
            var self = this;

            function nameOfCheckedValues(values) {
                return Object.keys(values).filter(function (valueId) {
                    return values[valueId].checked;
                }).map(function (valueId) {
                    return values[valueId].name;
                });
            }

            return Object.keys(this.filters).reduce(function (selection, filterId) {
                var filter = self.filters[filterId];
                var values = [];
                if (filter.groups) {
                    values = _.flatten(Object.keys(filter.groups).map(function (groupId) {
                        return nameOfCheckedValues(filter.groups[groupId].values);
                    }));
                } else if (filter.values) {
                    values = nameOfCheckedValues(filter.values);
                }
                if (values.length) {
                    selection.push({
                        values: values,
                        icon: filter.icon,
                        color: filter.color,
                    });
                }
                return selection;
            }, []);
        },
        /**
         * @override
         * @private
         */
        _render: function () {
            this._super.apply(this, arguments);
            this.$el.prepend(qweb.render(this.summaryTemplate, {
                categories: this._getCategorySelection(),
                filters: this._getFilterSelection(),
            }));
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onClickClose: function (ev) {
            ev.preventDefault();
            this.close();
        },
    });


});