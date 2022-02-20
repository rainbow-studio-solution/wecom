//----------------------------------------
// Wecom One2many widgets
//----------------------------------------

var FIELD_CLASSES = {
    char: 'o_list_char',
    float: 'o_list_number',
    integer: 'o_list_number',
    monetary: 'o_list_number',
    text: 'o_list_text',
    many2one: 'o_list_many2one',
};

odoo.define('wecom.x2many', function (require) {
    "use strict";

    var core = require('web.core');
    var _lt = core._lt;
    var _t = core._t;
    var RelationalFields = require('web.relational_fields');
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var viewUtils = require('web.viewUtils');
    var field_utils = require('web.field_utils');


    var WeComX2Many = RelationalFields.FieldX2Many.extend({
        description: _lt("WecomX2many"),
        className: 'o_field_wecom_one2many',
        supportedFieldTypes: ['wecom_x2many'],
        // attrs:
        // - help: 帮助字段
        // - format: 需要格式化的字段
        // - widget: "wecom_x2many"
        // value：
        // - data:数据
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.options = options;
            this.widget = this.attrs.widget;
        },
        // start: async function () {
        //     if (this.attrs.widget === "wecom_x2many") {
        //         this.help_field = this.attrs.help;
        //         this.format_field = this.attrs.format;
        //         this.type_field = this.attrs.type;
        //         // console.log("start", this.attrs)
        //     }
        //     return this._super.apply(this, arguments);
        // },
        _getRenderer: function () {
            if (this.attrs.widget === "wecom_x2many") {
                this.help_field = this.attrs.help;
                this.format_field = this.attrs.format;
                this.type_field = this.attrs.type;
                // console.log("_getRenderer", this.help_field)
                // console.log("_getRenderer", this.format_field)
                return ListRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'mouseenter .o_field_wecom_one2many_show': 'showHelpToolTip',
            'mouseleave .o_field_wecom_one2many_show': 'hideHelpToolTip',
            // 'click button.remove_obj_from_tag': 'remove_obj_from_tag',
        }),
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            if (parent.hasOwnProperty("attrs")) {
                if (parent.attrs.widget === "wecom_x2many") {
                    this.model = state.model // 当前model
                    this.res_ids = state.res_ids // 当前model的ids
                    this.help_field = parent.help_field;
                    this.format_field = parent.format_field;
                    this.type_field = parent.type_field;
                    // console.log(state)
                    // console.log(parent.help_field, parent.format_field, parent.type_field)
                    // console.log("ListRenderer init", state)
                    // console.log("ListRenderer init parent", parent)
                    // console.log("ListRenderer init params", params)
                    this.parent_res_id = parent.res_id; //当前Form的res_id
                    this.help_records = parent.value.data;
                    this.is_wecom_one2many = true;

                    if (parent.record.data.hasOwnProperty('is_wecom_category')) {
                        this.is_wecom_tag = parent.record.data.is_wecom_category;
                    }

                    if (parent.value.fields.hasOwnProperty(this.help_field)) {
                        this.show_help = true
                    } else {
                        this.show_help = false
                    }
                    if (parent.value.fields.hasOwnProperty(this.format_field)) {
                        if (parent.value.fields.hasOwnProperty(this.format_field) != "undefined") {
                            this.need_format = true
                        } else {
                            this.need_format = false
                        }
                    }
                } else {
                    this.is_wecom_one2many = false;
                }
            }
        },
        // _renderView: function () {
        //     var self = this;
        //     return this._super.apply(this, arguments).then(function () {
        //         if (self.is_wecom_one2many) {
        //             if (self.state.data.length > 0) {
        //                 if (self.show_help) {
        //                     self.$('.o_list_table').addClass('w-auto');
        //                 } else {
        //                     self.$('.o_list_table').addClass('w-100');
        //                 }
        //             } else {
        //                 self.$('.o_list_table').addClass('w-100');
        //             }
        //         }
        //     });
        // },
        _getNumberOfCols: function () {
            var n = this.columns.length;
            if (this.is_wecom_one2many) {
                n += 2;
            }
            return this.hasSelectors ? n + 1 : n;
        },
        _renderHeader: function () {
            var $thead = this._super.apply(this, arguments);
            if (this.is_wecom_one2many) {

                $thead.find("th:first").before($("<th title='no.'>#</th>"));
                if (this.show_help) {
                    $thead.find("th:last").after($("<th title='help' class='text-center' width='0.4'><i class='fa fa-question-circle' aria-hidden='false'></i></th>"));
                }
                if (self.is_wecom_tag) {
                    $thead.find("td.o_list_record_remove_header").remove();
                }
            }
            return $thead;
        },
        _renderRow: function (record, index) {
            var self = this;
            var $row = this._super.apply(this, arguments);

            if (this.is_wecom_one2many) {
                $row.find("td:first").before($("<td/>").html(index + 1));
                var data_id = $row.data("id");
                if (this.show_help) {
                    if (this.state.data.length > 0) {

                        var help = this.state.data.find(item => item.id === data_id).data[this.help_field];
                        var title = _t("No help description");
                        if (help != "") {
                            title = help;
                        }
                        var show_help_btn_html = _t("<button class='btn btn-default btn-sm o_field_wecom_one2many_show' data-placement='left' data-content='%s' html='true'><i class='fa fa-info-circle' aria-hidden='false'></i> %s</button>");

                        var $show_help_btn = _.str.sprintf(show_help_btn_html, title, _t("Show"));
                        $($show_help_btn).attr("container", false);
                        $row.find("td:last").after($("<td class='text-right'></td>").append($show_help_btn));


                    } else {
                        $row.find("td:last").after($("<td class='text-right'></td>"));
                    }
                }
                if (self.is_wecom_tag) {
                    $row.find("td.o_list_record_remove").remove();
                }
                if (this.need_format) {
                    // console.log("need_format", data_id)
                }
            }
            return $row;
        },
        _renderBodyCell: function (record, node, colIndex, options) {
            var self = this;
            var tdClassName = 'o_data_cell';
            // if (node.tag === 'button_group') {
            //     tdClassName += ' o_list_button';
            // } else if (node.tag === 'field') {
            //     tdClassName += ' o_field_cell';
            //     var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
            //     if (typeClass) {
            //         tdClassName += (' ' + typeClass);
            //     }
            //     if (node.attrs.widget) {
            //         tdClassName += (' o_' + node.attrs.widget + '_cell');
            //     }
            // }
            // if (node.attrs.editOnly) {
            //     tdClassName += ' oe_edit_only';
            // }
            // if (node.attrs.readOnly) {
            //     tdClassName += ' oe_read_only';
            // }
            // 获取 格式化字段的类型
            if (this.need_format) {
                var $td = $('<td>', {
                    class: tdClassName,
                    tabindex: -1
                });
                var name = node.attrs.name;
                var field = this.state.fields[name];
                var value = record.data[name];
                var formatter = field_utils.format[field.type];
                var formatOptions = {
                    escape: true,
                    data: record.data,
                    isPassword: 'password' in node.attrs,
                    digits: node.attrs.digits && JSON.parse(node.attrs.digits),
                };
                var formattedValue = formatter(value, field, formatOptions);
                var title = '';
                if (field.type !== 'boolean') {
                    title = formatter(value, field, _.extend(formatOptions, {
                        escape: false
                    }));
                }
                $td = $td.html(formattedValue).attr('title', title).attr('name', name);
                console.log($td)
                return $td;
            }

        },
        get_format_field_value_and_type: function (field_name) {
            return self._rpc({
                model: 'wecom.app_config',
                method: 'get_format_field_value_and_type',
                args: [],
            })
        },
        _renderButton: function (record, node) {
            var self = this;
            var nodeWithoutWidth = Object.assign({}, node);
            delete nodeWithoutWidth.attrs.width;

            let extraClass = '';
            if (node.attrs.icon) {
                // if there is an icon, we force the btn-link style, unless a btn-xxx
                // style class is explicitely provided
                const btnStyleRegex = /\bbtn-[a-z]+\b/;
                if (!btnStyleRegex.test(nodeWithoutWidth.attrs.class)) {
                    extraClass = 'btn-link o_icon_button';
                }
            }
            var $button = viewUtils.renderButtonFromNode(nodeWithoutWidth, {
                extraClass: extraClass,
            });
            this._handleAttributes($button, node);
            this._registerModifiers(node, record, $button);

            if (record.res_id) {
                // TODO this should be moved to a handler
                // if ($button[0].hasOwnProperty('name')) {
                //     if ($button[0].name == "remove_obj_from_tag" && !self.is_wecom_tag) {
                //         $button.css("display", "none")
                //     }
                // }
                if ($button[0].name == "remove_obj_from_tag" && !self.is_wecom_tag) {
                    $button.css("display", "none")
                }

                $button.on("click", function (e) {
                    e.stopPropagation();
                    if (self.is_wecom_tag) {
                        self.remove_obj_from_tag(record)
                    } else {
                        self.trigger_up('button_clicked', {
                            attrs: node.attrs,
                            record: record,
                        });
                    }
                });
            } else {
                if (node.attrs.options.warn) {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        self.do_warn(false, _t('Please click on the "save" button first'));
                    });
                } else {
                    $button.prop('disabled', true);
                }
            }
            return $button;
        },

        _renderFooter: function () {
            const $footer = this._super.apply(this, arguments);
            if (this.is_wecom_one2many) {
                $footer.find("td:first").before($("<td/>"));
                if (this.show_help) {
                    $footer.find("td:last").after($("<td/>"));
                }
            }
            return $footer;
        },
        remove_obj_from_tag: function (record) {
            var self = this;
            self._rpc({
                model: 'hr.employee.category',
                method: 'remove_obj_from_tag',
                args: ["", self.parent_res_id, record.model, record.res_id],
            }).then(function (result) {
                // console.log("请求", result);
                // return result
                if (result) {
                    self.trigger_up('reload');
                }
            })
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

    fieldRegistry.add('wecom_x2many', WeComX2Many);
    return {
        WeComX2Many: WeComX2Many,
    };

});