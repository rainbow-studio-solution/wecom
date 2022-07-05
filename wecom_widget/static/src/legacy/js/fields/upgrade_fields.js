odoo.define('wecom.upgrade_widgets', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var field_registry = require('web.field_registry');
    var framework = require('web.framework');
    var relational_fields = require('web.relational_fields');

    var _t = core._t;
    var QWeb = core.qweb;

    var FieldBoolean = basic_fields.FieldBoolean;
    var FieldRadio = relational_fields.FieldRadio;


    /**
     * Mixin that defines the common functions shared between Boolean and Radio
     * upgrade widgets
     */
    var AbstractWecomFieldUpgrade = {
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Redirects the user to the wecom-professional/uprade page
         *
         * @private
         * @returns {Promise}
         */
        _confirmUpgrade: function () {
            window.open("https://www.rstudio.xyz", '_blank');
            // window.location.href = "https://www.rstudio.xyz"
            // return this._rpc({
            //         model: 'res.users',
            //         method: 'search_count',
            //         args: [
            //             [
            //                 ["share", "=", false]
            //             ]
            //         ],
            //     })
            //     .then(function (data) {
            //         framework.redirect("https://www.rstudio.xyz");
            //     });
        },
        /**
         * This function is meant to be overridden to insert the ‘Professional’ label
         * JQuery node at the right place.
         *
         * @abstract
         * @private
         * @param {jQuery} $professionalLabel the ‘Professional’label to insert
         */
        _insertProfessionalLabel: function ($professionalLabel) {},
        /**
         * Opens the Upgrade dialog.
         *
         * @private
         * @returns {Dialog} the instance of the opened Dialog
         */
        _openDialog: function () {
            var message = $(QWeb.render('WecomProfessionalUpgrade'));

            var buttons = [{
                    text: _t("Upgrade now"),
                    classes: 'btn-primary',
                    close: true,
                    click: this._confirmUpgrade.bind(this),
                },
                {
                    text: _t("Cancel"),
                    close: true,
                },
            ];

            return new Dialog(this, {
                size: 'medium',
                buttons: buttons,
                $content: $('<div>', {
                    html: message,
                }),
                title: _t("Wecom Professional"),
            }).open();
        },
        /**
         * @override
         * @private
         */
        _render: function () {
            this._super.apply(this, arguments);
            this._insertProfessionalLabel($("<span>", {
                text: _t("Wecom Professional"),
                'class': "badge badge-primary oe_inline o_wecom_pro_label"
            }));
        },
        /**
         * This function is meant to be overridden to reset the $el to its initial
         * state.
         *
         * @abstract
         * @private
         */
        _resetValue: function () {},

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent} event
         */
        _onInputClicked: function (event) {
            // event.stopPropagation();
            var self = this;
            // event.preventDefault();
            if ($(event.currentTarget).prop("checked")) {
                console.log("选中");
                var addon_name = $(event.target).parent().attr("name").split("module_")[1];
                // 判断是否存在模块
                this._rpc({
                        model: 'ir.module.module',
                        method: 'check_wecom_addons_exist',
                        kwargs: {
                            addon_name: addon_name,
                        },
                    })
                    .then(function (data) {
                        if (!data["exist"]) {
                            console.log("不存在")
                            self._openDialog().on('closed', this, this._resetValue.bind(this));
                        } else {
                            console.log("存在")
                            // self._rpc({
                            //     model: 'ir.module.module',
                            //     method: 'button_immediate_install',
                            //     args: [
                            //         [data["moduleId"]]
                            //     ],
                            // })
                            $(event.currentTarget).trigger('checked');
                        }
                        // $(event.currentTarget).trigger('checked');
                    });

            } else {
                console.log("未选中");
                $(event.currentTarget).trigger('checked');
            }
        },

    };

    var UpgradeWecomProfessionalSuiteBoolean = FieldBoolean.extend(AbstractWecomFieldUpgrade, {
        supportedFieldTypes: [],
        events: _.extend({}, AbstractField.prototype.events, {
            'click input': '_onInputClicked',
        }),
        /**
         * Re-renders the widget with the label
         *
         * @param {jQuery} $label
         */
        renderWithLabel: function ($label) {
            this.$label = $label;
            console.log("renderWithLabel", this.$label);
            this._render();
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _insertProfessionalLabel: function ($professionalLabel) {
            var self = this;
            var $el = this.$label || this.$el;

            setTimeout(function () {
                if (self.$el.parent().length > 0) {
                    self.$label = self.$el.parent().next().find("label");
                    self.$label.append('&nbsp;').append($professionalLabel);
                    return;
                }
            }, 500);
        },
        /**
         * @override
         * @private
         */
        _resetValue: function () {
            this.$input.prop("checked", false).change();
        },
    });

    var UpgradeWecomProfessionalSuiteRadio = FieldRadio.extend(AbstractWecomFieldUpgrade, {
        supportedFieldTypes: [],
        events: _.extend({}, FieldRadio.prototype.events, {
            'click input:last': '_onInputClicked',
        }),

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        isSet: function () {
            return true;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _insertProfessionalLabel: function ($professionalLabel) {
            this.$('label').last().append('&nbsp;').append($professionalLabel);
        },
        /**
         * @override
         * @private
         */
        _resetValue: function () {
            this.$('input').first().prop("checked", true).click();
        },
    });



    field_registry
        .add('wecom_pro_suite_boolean', UpgradeWecomProfessionalSuiteBoolean)
        .add('wecom_pro_suite_radio', UpgradeWecomProfessionalSuiteRadio);
});