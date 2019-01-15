odoo.define('eis_web_theme.MenuMobile', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var Menu = require('web.Menu');

    var QWeb = core.qweb;

    if (!config.device.isMobile) {
        return;
    }

    Menu.include({
        events: _.extend({}, Menu.prototype.events, {
            'click .o_mobile_menu_toggle': '_onOpenSubMenu',
            'click .o_menu_item': '_on_secondary_menu_click',
        }),
        menusTemplate: 'SubMenu.sections.mobile',

        /**
         * @override
         */
        start: function () {
            return this._super.apply(this, arguments).then(this._renderSubMenu.bind(this));
        },
        /**
         * @override
         */
        destroy: function () {
            this.$subMenu.remove();
            this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _closeSubMenu: function () {
            var self = this;
            this.$subMenu.animate({left: '100%'}, 200, function () {
                self.$subMenu.addClass("o_hidden");
            });
        },
        /**
         * @private
         */
        _renderSubMenu: function () {
            this.$subMenu = $(QWeb.render('SubMenu', {session: session}));
            this.$subMenu.addClass("o_hidden");

            this.$('.o_menu_brand').appendTo(this.$subMenu.find('.o_sub_menu_topbar'));
            this.$section_placeholder.appendTo(this.$subMenu.find('.o_sub_menu_app'));

            this.$subMenu.on('click', '.o_sub_menu_close', this._onCloseSubMenu.bind(this));
            // this.$subMenu.on('click', '.o_sub_menu_company', this._onCompanyClicked.bind(this));
            // this.$subMenu.on('click', '.o_sub_menu_topbar.o_toggler', this._onTopbarClicked.bind(this));
            this.$subMenu.on('click', '.o_sub_menu_section', this._onSubMenuSectionClick.bind(this));

            $('body').append(this.$subMenu);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Toggles the clicked sub menu
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onSubMenuSectionClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $target = $(ev.currentTarget);
            $target.toggleClass('show');
            $target.find('> a .toggle_icon').toggleClass('fa-chevron-down fa-chevron-right');
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onCloseSubMenu: function (ev) {
            ev.stopPropagation();
            this._closeSubMenu();
        },

        /**
         * Opens burger menu in mobile
         *
         * @private
         * @param {MouseEvent} event
         */
        _onOpenSubMenu: function (ev) {
            ev.preventDefault();

            // update the burger menu content: either display the submenus (if we
            // are in an app, and if it contains submenus) or the user menu
            var displaySubMenus = !this.launcher_menu_displayed;
            if (displaySubMenus) {
                var app = _.findWhere(this.menu_data.children, {id: this.current_primary_menu});
                displaySubMenus = !!(app && app.children.length);
            }
            // this.$subMenu.find('.o_sub_menu_topbar').toggleClass('o_toggler', displaySubMenus);
            // this.$subMenu.find('.o_sub_menu_content').toggleClass('o_sub_menu_dark', displaySubMenus);
            // this.$subMenu.find('.o_sub_menu_caret').toggleClass('o_hidden', !displaySubMenus);
            this.$subMenu.find('.o_sub_menu_app').toggleClass('o_hidden', !displaySubMenus);
            // this.$subMenu.find('.o_sub_menu_user').toggleClass('o_hidden', displaySubMenus);

            // display the burger menu
            this.$subMenu.css({left: '100%'});
            this.$subMenu.animate({left: '0%'}, 200).removeClass('o_hidden');
        },
        /**
         * @override
         * @private
         */
        _on_secondary_menu_click: function () {
            this._super.apply(this, arguments);
            this._closeSubMenu();
        },
        /**
         * Toggles user menu and app submenus
         *
         * @private
         */
        _onTopbarClicked: function () {
            this.$subMenu.find('.o_sub_menu_content').toggleClass('o_sub_menu_dark');
            // this.$subMenu.find('.o_sub_menu_caret').toggleClass('dropup');
            // this.$subMenu.find('.o_sub_menu_app, .o_sub_menu_user').toggleClass('o_hidden');
            this.$subMenu.find('.o_sub_menu_app .fa-chevron-down').toggleClass('fa-chevron-down fa-chevron-right');
        },
         _onMenuitemClick: function () {
            this._super.apply(this, arguments);
            this._closeSubMenu();
        },
    });

});
