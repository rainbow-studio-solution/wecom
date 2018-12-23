odoo.define('rainbow_community_theme.LauncherMenu', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var utils = require('web.utils');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;
    var NBR_ICONS = 6;

    var LauncherMenu = Widget.extend({
        template: 'LauncherMenu',
        events: {
            'click .o_menuitem': '_onMenuitemClick',
            'input input.o_launcher_search_input': '_onMenuSearchInput',
            'compositionstart': '_onCompositionStart',
            'compositionend': '_onCompositionEnd',
        },
        /**
         * @override
         * @param {web.Widget} parent
         * @param {Object[]} menuData
         */
        init: function (parent, menuData) {
            this._super.apply(this, arguments);
            this._menuData = this._processMenuData(menuData);
            this._state = this._getInitialState();
        },
        /**
         * @override
         */
        start: function () {
            this.$input = this.$('input');
            this.$menuSearch = this.$('.o_launcher_menu_search');
            this.$mainContent = this.$('.o_launcher_menu_scrollable');
            return this._super.apply(this, arguments);
        },
        /**
         * @override
         */
        on_attach_callback: function () {
            core.bus.on("keydown", this, this._onKeydown);
            this._state = this._getInitialState();
            this.$input.val('');
            this._render();
        },
        /**
         * @override
         */
        on_detach_callback: function () {
            core.bus.off("keydown", this, this._onKeydown);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @returns {number}
         */
        getAppIndex: function () {
            return this._state.focus < this._state.apps.length ? this._state.focus : null;
        },
        /**
         * @returns {number}
         */
        getMenuIndex: function () {
            var state = this._state;
            return state.focus >= this._state.apps.length ? state.focus - this._state.apps.length : null;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @returns {Object} state
         * @returns {Object[]} state.apps      List of all menus that are apps
         * @returns {Object[]} state.menuItems List of all menus
         * @returns {number} state.focus       Index of focused element (app or menu item)
         */
        _getInitialState: function () {
            return {
                apps: _.where(this._menuData, {is_app: true}),
                menuItems: [],
                focus: null,
                isComposing: false,     // composing mode for input (e.g. japanese)
            };
        },
        /**
         * @private
         * @param {Object} menu           The considered opened menu
         * @param {string} menu.action    ID of the action linked to this menu
         * @param {number} menu.id
         * @param {boolean} [menu.is_app] A menu is an app if it has no parent
         * @param {number} menu.menu_id   (When menu not an app) id of the parent app
         */
        _openMenu: function (menu) {
            this.trigger_up(menu.is_app ? 'app_clicked' : 'menu_clicked', {
                menu_id: menu.id,
                action_id: menu.action,
            });
            if (!menu.is_app) {
                core.bus.trigger('change_menu_section', menu.menu_id);
            }
        },
        /**
         * @private
         * @param {Object} menuData                 The considered menu, (initially "Root")
         * @param {string} [menuData.action]
         * @param {number|false} menuData.id
         * @param {boolean} menuData.is_app         States whether the menu is an app or not
         * @param {number} menuData.menu_id         (When menu not an app) id of the parent app
         * @param {string} menuData.name
         * @param {number} [menuData.parent_id]
         * @param {string} [menuData.web_icon]      Path of the icon
         * @param {string} [menuData.web_icon_data] Base64 string representation of the web icon
         * @param {string} menuData.xmlid
         * @returns {Object[]}
         */
        _processMenuData: function (menuData) {
            var result = [];
            utils.traversePath(menuData, function (menuItem, parents) {
                if (!menuItem.id || !menuItem.action) {
                    return;
                }
                var item = {
                    parents: _.pluck(parents.slice(1), 'name').join(' / '),
                    label: menuItem.name,
                    id: menuItem.id,
                    xmlid: menuItem.xmlid,
                    action: menuItem.action ? menuItem.action.split(',')[1] : '',
                    is_app: !menuItem.parent_id,
                    web_icon: menuItem.web_icon,
                };
                if (!menuItem.parent_id) {
                    if (menuItem.web_icon_data) {
                        item.web_icon_data =
                            ('data:image/png;base64,' + menuItem.web_icon_data).replace(/\s/g, "");
                    } else if (item.web_icon) {
                        var iconData = item.web_icon.split(',');
                        item.web_icon = {
                            class: iconData[0],
                            color: iconData[1],
                            background: iconData[2],
                        };
                    } else {
                        item.web_icon_data = '/web_enterprise/static/src/img/default_icon_app.png';
                    }
                } else {
                    item.menu_id = parents[1].id;
                }
                result.push(item);
            });
            return result;
        },
        /**
         * @private
         */
        _render: function () {
            this.$menuSearch.toggleClass('o_bar_hidden', !this._state.isSearching);
            this.$mainContent.html(QWeb.render('LauncherMenu.Content', { widget: this }));
            var $focused = this.$mainContent.find('.o_focused');
            if ($focused.length && !config.device.isMobile) {
                if (!this._state.isComposing) {
                    $focused.focus();
                }
                this.$el.scrollTo($focused, {offset: {top:-0.5*this.$el.height()}});
            }

            var offset = window.innerWidth -
                (this.$mainContent.offset().left * 2 + this.$mainContent.outerWidth());
            if (offset) {
                this.$el.css('padding-left', "+=" + offset);
            }
        },
        /**
         * Apply fuzzy search on 'data.search', and update 'this._state.focus'
         * This is called by 'this._onKeydown' and 'this._onMenuSearchInput'
         *
         * @private
         * @param {Object} data
         * @param {number} [data.focus]  Move change of the focus (1: move down, -1: move top)
         * @param {string} [data.search] Input text displayed in the search bar
         */
        _update: function (data) {
            var self = this;
            if (data.search) {
                var options = {
                    extract: function (el) {
                        return el.label.split('/').reverse().join('/');
                    }
                };
                var searchResults = fuzzy.filter(data.search, this._menuData, options);
                var results = _.map(searchResults, function (result) {
                    return self._menuData[result.index];
                });
                this._state = _.extend(this._state, {
                    apps: _.where(results, {is_app: true}),
                    menuItems: _.where(results, {is_app: false}),
                    focus: results.length ? 0 : null,
                    isSearching: true,
                });
            }
            if (this._state.focus !== null && 'focus' in data) {
                var state = this._state;
                var nbrApps = state.apps.length;
                var nbrMenus = state.menuItems.length;
                var newIndex = data.focus + (state.focus || 0);
                if (newIndex < 0) {
                    newIndex = nbrApps + nbrMenus - 1;
                }
                if (newIndex >= nbrApps + nbrMenus) {
                    newIndex = 0;
                }
                if (newIndex >= nbrApps && state.focus < nbrApps && data.focus > 0) {
                    if (state.focus + data.focus - (state.focus % data.focus) < nbrApps) {
                        newIndex = nbrApps - 1;
                    } else {
                        newIndex = nbrApps;
                    }
                }
                if (newIndex < nbrApps && state.focus >= nbrApps && data.focus < 0) {
                    newIndex = nbrApps - (nbrApps % NBR_ICONS);
                    if (newIndex === nbrApps) {
                        newIndex = nbrApps - NBR_ICONS;
                    }
                }
                state.focus = newIndex;
            }
            this._render();
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {KeyboardEvent} ev
         */
        _onKeydown: function (ev) {
            var isEditable = ev.target.tagName === "INPUT" ||
                ev.target.tagName === "TEXTAREA" ||
                ev.target.isContentEditable;
            if (isEditable && ev.target !== this.$input[0]) {
                return;
            }
            var state = this._state;
            var elemFocused = state.focus !== null;
            var appFocused = elemFocused && state.focus < state.apps.length;
            var delta = appFocused ? NBR_ICONS : 1;
            var $input = this.$input;
            switch (ev.which) {
                case $.ui.keyCode.DOWN:
                    this._update({focus: elemFocused ? delta : 0});
                    ev.preventDefault();
                    break;
                case $.ui.keyCode.RIGHT:
                    if ($input.is(':focus') && $input[0].selectionEnd < $input.val().length) {
                        return;
                    }
                    this._update({focus: elemFocused ? 1 : 0});
                    ev.preventDefault();
                    break;
                case $.ui.keyCode.TAB:
                    if ($input.val() === "") {
                        return;
                    }
                    ev.preventDefault();
                    var f = elemFocused ? (ev.shiftKey ? -1 : 1) : 0;
                    this._update({focus: f});
                    break;
                case $.ui.keyCode.UP:
                    this._update({focus: elemFocused ? -delta : 0});
                    ev.preventDefault();
                    break;
                case $.ui.keyCode.LEFT:
                    if ($input.is(':focus') && $input[0].selectionStart > 0) {
                        return;
                    }
                    this._update({focus: elemFocused ? -1 : 0});
                    ev.preventDefault();
                    break;
                case $.ui.keyCode.ENTER:
                    if (elemFocused) {
                        var menus = appFocused ? state.apps : state.menuItems;
                        var index = appFocused ? state.focus : state.focus - state.apps.length;
                        this._openMenu(menus[index]);
                        ev.preventDefault();
                    }
                    return;
                case $.ui.keyCode.PAGE_DOWN:
                case $.ui.keyCode.PAGE_UP:
                case 16: // Shift
                case 17: // CTRL
                case 18: // Alt
                    break;
                case $.ui.keyCode.ESCAPE:
                    // clear text on search, hide it if no content before ESC
                    // hide home menu if there is an inner action
                    this._state = this._getInitialState();
                    this._state.isSearching = $input.val().length > 0;
                    $input.val("");
                    this._update({focus: 0, search: $input.val()});
                    if (!this._state.isSearching) {
                        this.trigger_up('hide_launcher_menu');
                    }
                    break;
                default:
                    if (!this.$input.is(':focus')) {
                        this.$input.focus();
                    }
            }
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onCompositionStart: function(ev) {
            this._state.isComposing = true;
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onCompositionEnd: function(ev) {
            this._state.isComposing = false;
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onMenuitemClick: function (ev) {
            ev.preventDefault();
            var menuId = $(ev.currentTarget).data('menu');
            this._openMenu(_.findWhere(this._menuData, {id: menuId}));
        },
        /**
         * @private
         * @param {KeyboardEvent} ev Keyboard interactions with the search bar
         */
        _onMenuSearchInput: function (ev) {
            if (!ev.target.value) {
                this._state = this._getInitialState();
                this._state.isSearching = true;
            }

            this._update({search: ev.target.value, focus: 0});
        }
    });

    return LauncherMenu;

});

