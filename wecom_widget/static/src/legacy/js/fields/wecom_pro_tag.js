/** 
 * <widget name="wecom_pro_tag"/>，仅用于 class = o_settings_container, 如下使用
 * 
 *  <div class="col-12 col-lg-6 o_setting_box" id="wecom_web_theme_install">
 *      <div class="o_setting_left_pane">
 *          <field name="module_wecom_web_theme"/>
 *      </div>
 *      <div class="o_setting_right_pane" id="wecom_web_theme_settings">
 *          <label for="module_wecom_web_theme" string="Wecom Web Theme" />
 *          <widget name="wecom_pro_tag"/>
 *      </div>
 *  </div>
 */

odoo.define('wecom.pro_tag', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t;
    var QWeb = core.qweb;


    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');



    var WecomProfessionalSuiteTag = Widget.extend({
        template: 'WecomProfessionalTag',
        upgrade_template: 'WecomProfessionalUpgrade',
        events: {
            'click': '_onTagClicked',
        },
        _onTagClicked: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            var self = this;
            var $box = self.$el.parents(".o_setting_box");

            var addon_name = $box.find(".o_setting_left_pane").contents().attr("name").split("module_")[1];

            this._rpc({
                model: 'ir.module.module',
                method: 'check_wecom_addons_exist',
                kwargs: {
                    addon_name: addon_name,
                },
            }).then(function (data) {
                if (!data) {
                    self._openDialog();
                }
            })
        },

        _openDialog: function () {
            var message = $(QWeb.render(this.upgrade_template));

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
        _confirmUpgrade: function () {
            window.open("https://www.rstudio.xyz", '_blank');
        },
    });

    widget_registry.add('wecom_pro_tag', WecomProfessionalSuiteTag);
    return WecomSettingsNavigationMenu;
});