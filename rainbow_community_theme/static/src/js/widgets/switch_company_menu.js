odoo.define('rainbow_community_theme.SwitchCompanyMenu', function (require) {
    "use strict";

    /**
     * In mobile, there is no switch company menu in the systray. Instead, it is
     * available from the Burger menu.
     * The purpose of this file is to remove the SwitchCompanyMenu widget from the
     * SystrayMenu items, before the SystrayMenu starts to instantiates them.
     */

    var config = require('web.config');
    if (!config.device.isMobile) {
        return;
    }

    var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
    var SystrayMenu = require('web.SystrayMenu');

    if (config.device.isMobile) {
        var index = SystrayMenu.Items.indexOf(SwitchCompanyMenu);
        if (index >= 0) {
            SystrayMenu.Items.splice(index, 1);
        }
    }

    const SwitchCompanyMenuMobile = SwitchCompanyMenu.extend({
        template: 'MobileCompanySwitcher',
        events: Object.assign({}, SwitchCompanyMenu.prototype.events, {
            'click .log_into': '_onSwitchCompanyClick',
            'click .toggle_company': '_onToggleCompanyClick',
        }),
    });

    return {
        SwitchCompanyMenuMobile: SwitchCompanyMenuMobile,
    };
});