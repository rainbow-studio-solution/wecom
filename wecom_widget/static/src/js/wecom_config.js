//----------------------------------------
// Wecom config widgets
//----------------------------------------
odoo.define('wecom.wecom_config', function (require) {
    "use strict";

    var core = require('web.core');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var ListRenderer = require('web.ListRenderer');
    var FieldRegistry = require('web.field_registry');
    var _t = core._t;
    var config = require('web.config');
    var viewUtils = require('web.viewUtils');

    var WeComConfigRenderer = ListRenderer.extend({
        events: _.extend({}, ListRenderer.prototype.events, {
            'mouseenter .o_field_wecom_one2many_show': 'showHelpToolTip',
            'mouseleave .o_field_wecom_one2many_show': 'hideHelpToolTip',
            'click .o_wecom_config_checkbox': '_onClickWecomConfigCheckbox',
        }),
        init: function (parent, state, params) {
            var self = this;
            this.sectionFieldName = "is_wecom_config";

            this._super.apply(this, arguments);
        },

        _checkIfRecordIsSection: function (id) {
            var record = this._findRecordById(id);
            return record && record.data[this.sectionFieldName];
        },
        _findRecordById: function (id) {
            return _.find(this.state.data, function (record) {
                return record.id === id;
            });
        },
        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);
            $row.find("td:first").before($("<td/>").html(index + 1));
            var show_help_btn_html = _t("<button class='btn btn-default btn-sm o_field_wecom_one2many_show' data-placement='left' data-content='%s' html='true'><i class='fa fa-info-circle' aria-hidden='false'></i> %s</button>");
            var $show_help_btn = _.str.sprintf(show_help_btn_html, record.data["description"], _t("Show"));
            $($show_help_btn).attr("container", false);
            $row.find("td:last").after($("<td class='text-right'></td>").append($show_help_btn));
            return $row;
        },
        _renderBodyCell: function (record, node, index, options) {
            var $cell = this._super.apply(this, arguments);
            if (record.data.ttype == "boolean") {
                // options.mode = 'readonly';
            }
            if (record.data.ttype == "boolean" && node.attrs.name == this.format_field) {
                // $cell.addClass("o_wecom_config_boolean");
                // $cell.find("span").addClass("o_wecom_config_boolean");
                // let $checkbox = _.str.sprintf("<input id='%s' data-id='%s' class='o_wecom_config_checkbox' type='checkbox' name='%s' value='%s'/>", "checkbox" + record.id, record.res_id, node.attrs.name, record.data.value);
                // if (record.data.value.toLowerCase() == "true") {
                //     $checkbox = _.str.sprintf("<input id='%s' data-id='%s' class='o_wecom_config_checkbox' type='checkbox' checked='checked' name='%s' value='%s'/>", "checkbox" + record.id, record.res_id, node.attrs.name, record.data.value);
                // } else {
                //     $checkbox = _.str.sprintf("<input id='%s' data-id='%s' class='o_wecom_config_checkbox' type='checkbox' name='%s' value='%s'/>", "checkbox" + record.id, record.res_id, node.attrs.name, record.data.value);
                // }
                // $cell.prepend($checkbox);
            }

            if (record.data.ttype == "datetime" || record.data.ttype == "char") {
                options.mode = 'readonly';
            }

            var isSection = record.data[this.sectionFieldName];
            if (isSection) {
                if (node.attrs.widget === "handle" || node.attrs.name === "random_questions_count") {
                    return $cell;
                } else if (node.attrs.name === "title") {
                    var nbrColumns = this._getNumberOfCols();
                    if (this.handleField) {
                        nbrColumns--;
                    }
                    if (this.addTrashIcon) {
                        nbrColumns--;
                    }
                    if (record.data.questions_selection === "random") {
                        nbrColumns--;
                    }
                    $cell.attr('colspan', nbrColumns);
                } else {
                    $cell.removeClass('o_invisible_modifier');
                    return $cell.addClass('o_hidden');
                }
            }
            return $cell;
        },
        _onClickWecomConfigCheckbox: function (ev) {
            var self = this;
            // ev.stopPropagation();

            var checked = $(ev.target).prop('checked');
            console.log("checked", $(ev.target).data("id"), checked);
            $(ev.target).parent().addClass("text-nowrap");

            let value = "";
            if (checked) {
                $(ev.target).prop("checked", false);
                value = "False";
            } else {
                $(ev.target).prop("checked", true);
                value = "True";
            }

            if ($(ev.target).siblings().length > 0) {
                let $next = $(ev.target).next();
                console.log("length", $next.length)

                $next.addClass("w-auto");
                $next.text(value);
                $(ev.target).parent().attr("title", value);
                $.each(this.state.data, function (index, res) {
                    if (res.res_id == $(ev.target).data("id")) {
                        self._rpc({
                            model: 'wecom.app_config',
                            method: 'update_config',
                            args: ["", res.res_id, value],
                        }).then(function (result) {
                            console.log(res.data.value);
                            res.data.value = result;
                            console.log(res.data.value);
                            // console.log($next);
                            $next.text(result);
                        });
                    }
                });
            }
        },
        _onRowClicked: function (ev) {
            ev.preventDefault(); //阻止事件默认行为
            ev.stopPropagation(); //阻止事件冒泡
            this._super.apply(this, arguments);
        },
        _renderHeader: function () {
            var $thead = this._super.apply(this, arguments);
            $thead.find("th:first").before($("<th title='no.'>#</th>"));
            $thead.find("th:last").after($("<th title='help' class='text-center' width='0.4'><i class='fa fa-question-circle' aria-hidden='false'></i></th>"));
            return $thead;
        },
        _renderHeaderCell: function (node) {
            // 获取需要格式化的字段
            var self = this;
            var $th = this._super.apply(this, arguments);
            if (node.attrs.need_format) {
                this.format_field = node.attrs.name;
                // console.log(self.state.data)
                $.each(this.state.data, function (index, res) {
                    self._rpc({
                        model: 'wecom.app_config',
                        method: 'get_format_field_value_and_type',
                        args: ["", res.res_id, this.format_field],
                    }).then(function (result) {
                        res.data["ttype"] = result;
                        res.data["need_format"] = true;
                    })
                })
            }
            return $th;
        },
        _renderFooter: function () {
            var $footer = this._super.apply(this, arguments);
            $footer.find("td:first").before($("<td/>"));
            $footer.find("td:last").after($("<td/>"));
            return $footer;
        },

        _renderView: function () {
            var def = this._super.apply(this, arguments);
            var self = this;
            return def.then(function () {
                self.$('table.o_list_table').addClass('o_section_list_view w-100');
            });
        },
        showHelpToolTip: function (ev) {
            var help_content_text = "<div class='o_field_wecom_one2many_container'><div class='o_field_wecom_one2many_header'>%s</div><div class='o_field_wecom_one2many_text'>%s</div></div>";
            var options = {
                placement: 'left',
                title: _.str.sprintf(help_content_text, _t("Description"), $(ev.target).data("content")),
                trigger: 'hover',
                html: true,
            }
            $(ev.target).tooltip(options);
            $(ev.target).tooltip('show', true);
        },
        hideHelpToolTip: function (ev) {
            $(ev.target).tooltip('show', false);
        },
    });

    var WeComConfig = FieldOne2Many.extend({
        // description: _lt("WecomOne2many"),
        // className: 'o_field_wecom_one2many',
        // supportedFieldTypes: ['wecom_config'],
        // attrs:
        // - help: 帮助字段
        // - widget: "wecom_config"
        // value：
        // - data:数据
        init: function (parent, name, record, options) {
            // this._super.apply(this, arguments);
            // this.options = options;
            // this.widget = this.attrs.widget;
            this._super.apply(this, arguments);
            this.sectionFieldName = "is_wecom_config";
            this.rendered = false;
        },
        _getRenderer: function () {
            // if (this.attrs.widget === "wecom_config") {
            //     this.help_field = this.attrs.help;
            //     return ListRenderer;
            // }
            // return this._super.apply(this, arguments);
            if (this.view.arch.tag === 'tree') {
                // this.help_field = this.attrs.help;
                return WeComConfigRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });

    FieldRegistry.add('wecom_config', WeComConfig);
    return {
        WeComConfig: WeComConfig,
    };

});