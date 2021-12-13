//----------------------------------------
// Wxwork One2many help widgets
//----------------------------------------
odoo.define('wxwork.one2many_help_fields', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var RelationalFields = require('web.relational_fields');
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var session = require('web.session');
    var field_utils = require('web.field_utils');


    var FieldOne2ManyHlep = RelationalFields.FieldOne2Many.extend({
        description: _lt("One2manyHelp"),
        className: 'o_field_one2many_help',
        supportedFieldTypes: ['one2many_help'],
        // attrs:
        // - help: 帮助字段
        // - widget: "one2many_help"
        // value：
        // - data:数据
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.options = options;
            this.widget = this.attrs.widget;

        },
        _getRenderer: function () {
            if (this.attrs.widget === "one2many_help") {
                this.help_field = this.attrs.help;
                return ListRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });



    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'focus .o_field_one2many_help_show': 'showHelpToolTip',
        }),
        init: function (parent, state, params) {
            this._super.apply(this, arguments);

            if (parent.attrs.widget === "one2many_help") {
                this.help_records = parent.value.data;
                this.is_one2many_help = true;
            } else {
                this.is_one2many_help = false;
            }
        },

        _renderHeader: function () {
            var $thead = this._super.apply(this, arguments);
            if (this.is_one2many_help) {
                $thead.find("th:first").before($("<th>#</th>"));
                $thead.find("th:last").after($("<th class='text-center'><i class='fa fa-question-circle' aria-hidden='false'></i></th>"));
            }

            return $thead;
        },
        _renderRow: function (record, index) {
            var self = this;
            var $row = this._super.apply(this, arguments);

            if (this.is_one2many_help) {
                var data_id = $row.data("id");
                var help = this.help_records.find(item => item.id === data_id).data["description"];
                $row.find("td:first").before($("<td/>").html(index + 1));

                var show_help_btn_html = _t("<button class='btn btn-default btn-sm o_field_one2many_help_show' data-trigger='tooltip' data-placement='left' data-html='true' data-original-title='%s' data-trigger='hover' data-content='%s'><i class='fa fa-info-circle' aria-hidden='false'></i> %s</button>");

                var $show_help_btn = _.str.sprintf(show_help_btn_html, _t("Description"), help, _t("Show help"));

                // $($show_help_btn).tooltip({
                //     trigger: 'hover',
                //     html: true,
                //     delay: 300,
                //     content: help
                // })

                $row.find("td:last").after($("<td class='text-right'></td>").append($show_help_btn));
            }
            return $row;
        },
        _renderFooter: function () {
            const $footer = this._super.apply(this, arguments);
            if (this.is_one2many_help) {
                $footer.find("td:first").before($("<td/>"));
                $footer.find("td:last").after($("<td/>"));
            }
            return $footer;
        },
        showHelpToolTip: function (ev) {
            $(ev.target).tooltip();
            // $(ev).popover({
            //     placement: 'left',
            //     trigger: 'click hover',
            //     html: true,
            //     content: help,
            // })
        },
    });

    fieldRegistry.add('one2many_help', FieldOne2ManyHlep);
    return {
        FieldOne2ManyHlep: FieldOne2ManyHlep,
    };

});