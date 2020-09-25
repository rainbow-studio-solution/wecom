odoo.define('web.WebClient', function (require) {
    "use strict";

    var AbstractWebClient = require('web.AbstractWebClient');
    var ActionManager = require('web.ActionManager');
    var config = require('web.config');
    var core = require('web.core');
    var data_manager = require('web.data_manager');
    var dom = require('web.dom');
    var session = require('web.session');

    var LauncherMenu = require('rainbow_community_theme.LauncherMenu');
    var Menu = require('rainbow_community_theme.Menu');
    var SidebarMenu = require('rainbow_community_theme.SidebarMenu');
    var Footer = require('rainbow_community_theme.Footer');

    return AbstractWebClient.extend({
        custom_events: _.extend({}, AbstractWebClient.prototype.custom_events, {
            app_clicked: 'on_app_clicked',
            menu_clicked: 'on_menu_clicked',
            show_launcher_menu: '_onShowLauncherMenu',
            hide_launcher_menu: '_onHideLauncherMenu',
            sidebar_expand: '_onExpandSidebarMenu',
            sidebar_collapse: '_onCollapseSidebarMenu',
        }),
        init: function () {
            this._super.apply(this, arguments);
            this.launcher_menu_displayed = false;
            this.sidebar_menu_status = false;
        },
        start: function () {
            core.bus.on('change_menu_section', this, function (menu_id) {
                this.do_push_state(_.extend($.bbq.getState(), {
                    menu_id: menu_id,
                }));
            });
            return this._super.apply(this, arguments)
                .then(this._renderSidebarMenu.bind(this))
                .then(this._renderFooter.bind(this));
        },
        setLauncherMenuBg: function (display) {
            var src = "/rainbow_community_theme/static/src/img/launcher/bg-" + session.theme.launcher_bg;
            if (session.theme.launcher_bg_status === 'enable') {
                if (display) {
                    this.$el.css("background", "linear-gradient(to right bottom, rgba(119, 113, 126, 0.9) 0%, rgba(201, 168, 169, 0) 100%), url(" + src + ")");
                    // this.$el.css("background", "url(" + src + "),linear-gradient(to right bottom, rgba(119, 113, 126, 0.9) 0%, rgba(201, 168, 169, 0) 100%)");
                    this.$el.css("background-size", "cover");
                } else {
                    this.$el.attr("style", "");
                }
            }
        },
        bind_events: function () {
            var self = this;
            this._super.apply(this, arguments);
            this.$el.on('click', 'a', function (ev) {
                var disable_anchor = ev.target.attributes.disable_anchor;
                if (disable_anchor && disable_anchor.value === "true") {
                    return;
                }

                var href = ev.target.attributes.href;
                if (href) {
                    if (href.value[0] === '#' && href.value.length > 1) {
                        if (self.$("[id='" + href.value.substr(1) + "']").length) {
                            ev.preventDefault();
                            self.trigger_up('scrollTo', {
                                'selector': href.value
                            });
                        }
                    }
                }
            });
        },
        load_menus: function () {
            return (odoo.loadMenusPromise || odoo.reloadMenus())
                .then(function (menuData) {
                    // Compute action_id if not defined on a top menu item
                    for (var i = 0; i < menuData.children.length; i++) {
                        var child = menuData.children[i];
                        if (child.action === false) {
                            while (child.children && child.children.length) {
                                child = child.children[0];
                                if (child.action) {
                                    menuData.children[i].action = child.action;
                                    break;
                                }
                            }
                        }
                    }
                    odoo.loadMenusPromise = null;
                    return menuData;
                });
        },
        show_application: function () {
            var self = this;
            this.set_title();

            const insertMenu = () => {
                this.menu.$el.prependTo(this.$el);
            };

            return this.menu_dp.add(this.instanciate_menu_widgets()).then(function () {
                $(window).bind('hashchange', self.on_hashchange);

                // Listen to 'scroll' event in launcher_menu and propagate it on main bus
                self.launcher_menu.$el.on('scroll', core.bus.trigger.bind(core.bus, 'scroll'));

                // If the url's state is empty, we execute the user's launcher action if there is one (we
                // show the launcher menu if not)
                // If it is not empty, we trigger a dummy hashchange event so that `self.on_hashchange`
                // will take care of toggling the launcher menu and loading the action.
                var state = $.bbq.getState(true);
                if (_.keys(state).length === 1 && _.keys(state)[0] === "cids") {
                    return self.menu_dp.add(self._rpc({
                            model: 'res.users',
                            method: 'read',
                            args: [session.uid, ["action_id"]],
                        }))
                        .then(function (result) {
                            var data = result[0];
                            if (data.action_id) {
                                return self.do_action(data.action_id[0]).then(function () {
                                    self.toggle_launcher_menu(false);
                                    self.menu.change_menu_section(self.menu.action_id_to_primary_menu_id(data.action_id[0]));
                                });
                            } else {
                                self.toggle_launcher_menu(true);
                            }
                        });
                } else {
                    return self.on_hashchange();
                }
            }).then(insertMenu).guardedCatch(insertMenu);
        },

        instanciate_menu_widgets: function () {
            var self = this;
            var defs = [];
            var position = session.theme.submenu_position;
            return this.load_menus().then(function (menu_data) {
                self.menu_data = menu_data;
                self.launcher_menu = new LauncherMenu(self, menu_data);
                self.menu = new Menu(self, menu_data, position);
                defs.push(self.launcher_menu.appendTo(document.createDocumentFragment()));
                defs.push(self.menu.appendTo(document.createDocumentFragment()));
                return Promise.all(defs);
            });
        },
        _renderSidebarMenu: function () {
            var self = this;
            if (!config.device.isMobile) {
                return this.load_menus().then(function (menu_data) {
                    self.menu_data = menu_data;
                    var state = $.bbq.getState(true); //简略信息
                    // self.action_manager.getCurrentAction() //详细信息
                    var mode = session.theme.sidebar_mode;
                    var position = session.theme.submenu_position;
                    if (self.$('.o_main').find('.o_main_sidenav_wrapper').length > 0) {
                        self.$('.o_main').find('.o_main_sidenav_wrapper').remove();
                    }
                    var sidebar_menu = new SidebarMenu(self, menu_data, mode, state, position);
                    var fragment = document.createDocumentFragment();
                    return sidebar_menu.appendTo(fragment).then(function () {
                        //向目标开头插入sidebar_menu
                        dom.prepend(self.$('.o_main'), fragment, {
                            in_DOM: true,
                            callbacks: [{
                                widget: sidebar_menu
                            }],
                        });
                    });
                });
            }
        },
        _renderFooter: function () {
            var self = this;

            if (this.$el.find('.o_footer').length > 0) {
                this.$el.find('.o_footer').remove();
            }

            this.footer = new Footer(this, session.theme.footer);
            var fragment = document.createDocumentFragment();
            this.footer.appendTo(fragment).then(function () {
                //向目标结尾处插入footer
                dom.append(self.$('.o_main').parent(), fragment, {
                    in_DOM: true,
                    callbacks: [{
                        widget: self.footer
                    }],
                });
            });
        },
        set_action_manager: function () {
            var self = this;
            this.action_manager = new ActionManager(this, session.user_context);
            var fragment = document.createDocumentFragment();
            return this.action_manager.appendTo(fragment).then(function () {
                //向目标结尾处插入action_manager
                if (!config.device.isMobile) {
                    dom.append(self.$('.o_main'), fragment, {
                        in_DOM: true,
                        callbacks: [{
                            widget: self.action_manager
                        }],
                    });
                } else {
                    dom.append(self.$el, fragment, {
                        in_DOM: true,
                        callbacks: [{
                            widget: self.action_manager
                        }],
                    });
                }

            })
        },
        // --------------------------------------------------------------
        // do_*
        // --------------------------------------------------------------
        /**
         * Extends do_action() to toggle the home menu off if the action isn't displayed in a dialog
         */
        do_action: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function (action) {
                if (self.launcher_menu_displayed && action.target !== 'new' &&
                    action.type !== 'ir.actions.act_window_close') {
                    self.toggle_launcher_menu(false);
                }
                return action;
            });
        },
        // --------------------------------------------------------------
        // URL state handling
        // --------------------------------------------------------------
        on_hashchange: function (event) {
            if (this._ignore_hashchange) {
                this._ignore_hashchange = false;
                return Promise.resolve();
            }

            var self = this;
            return this.clear_uncommitted_changes().then(function () {
                var stringstate = $.bbq.getState(false);
                if (!_.isEqual(self._current_state, stringstate)) {
                    var state = $.bbq.getState(true);
                    if (state.action || (state.model && (state.view_type || state.id))) {
                        return self.menu_dp.add(self.action_manager.loadState(state, !!self._current_state)).then(function () {
                            if (state.menu_id) {
                                if (state.menu_id !== self.menu.current_primary_menu) {
                                    core.bus.trigger('change_menu_section', state.menu_id);
                                }
                            } else {
                                var action = self.action_manager.getCurrentAction();
                                if (action) {
                                    var menu_id = self.menu.action_id_to_primary_menu_id(action.id);
                                    core.bus.trigger('change_menu_section', menu_id);
                                }
                            }
                            self.toggle_launcher_menu(false);
                        }).guardedCatch(self.toggle_launcher_menu.bind(self, true));
                    } else if (state.menu_id) {
                        var action_id = self.menu.menu_id_to_action_id(state.menu_id);
                        return self.menu_dp.add(self.do_action(action_id, {
                            clear_breadcrumbs: true
                        })).then(function () {
                            core.bus.trigger('change_menu_section', state.menu_id);
                            self.toggle_launcher_menu(false);
                        });
                    } else {
                        self.toggle_launcher_menu(true);
                    }
                }
                self._current_state = stringstate;
            }, function () {
                if (event) {
                    self._ignore_hashchange = true;
                    window.location = event.originalEvent.oldURL;
                }
            });
        },
        // --------------------------------------------------------------
        // Menu handling
        // --------------------------------------------------------------
        on_app_clicked: function (ev) {
            var self = this;
            return this.menu_dp.add(data_manager.load_action(ev.data.action_id))
                .then(function (result) {
                    return self.action_mutex.exec(function () {
                        return new Promise(function (resolve, reject) {
                            var options = _.extend({}, ev.data.options, {
                                clear_breadcrumbs: true,
                                action_menu_id: ev.data.menu_id,
                            });
                            Promise.resolve(self._openMenu(result, options)).guardedCatch(function () {
                                self.toggle_launcher_menu(true);
                                resolve();
                            }).then(function () {
                                self._on_app_clicked_done(ev)
                                    .then(resolve)
                                    .guardedCatch(reject);
                            });
                        });
                    });
                });
        },
        _on_app_clicked_done: function (ev) {
            // console.log(ev.data.menu_id);
            core.bus.trigger('change_menu_section', ev.data.menu_id);
            this.toggle_launcher_menu(false);
            this._renderSidebarMenu(); //点击重新加载sidebar
            this._renderFooter(); //点击重新加载footer
            return Promise.resolve();
        },
        on_menu_clicked: function (ev) {
            var self = this;
            return this.menu_dp.add(data_manager.load_action(ev.data.action_id))
                .then(function (result) {
                    return self.action_mutex.exec(function () {
                        return self._openMenu(result, {
                            clear_breadcrumbs: true
                        });
                    });
                }).then(function () {
                    self._renderFooter(); //点击重新加载footer
                    self.$el.removeClass('o_mobile_menu_opened');
                });
        },
        /**
         * Open the action linked to a menu.
         * This function is mostly used to allow override in other modules.
         *
         * @private
         * @param {Object} action
         * @param {Object} options
         * @returns {Promise}
         */
        _openMenu: function (action, options) {
            return this.do_action(action, options);
        },
        toggle_launcher_menu: function (display) {
            if (display === this.launcher_menu_displayed) {
                return; // nothing to do (prevents erasing previously detached webclient content)
            }
            if (display) {
                var self = this;

                this.clear_uncommitted_changes().then(function () {
                    // Save the current scroll position
                    self.scrollPosition = self.getScrollPosition();

                    // Detach the web_client contents
                    var $to_detach = self.$el.contents()
                        .not(self.menu.$el)
                        .not('.o_loading')
                        .not('.o_in_launcher_menu')
                        .not('.o_notification_manager');
                    self.web_client_content = document.createDocumentFragment();
                    dom.detach([{
                        widget: self.action_manager
                    }], {
                        $to_detach: $to_detach
                    }).appendTo(self.web_client_content);

                    // Attach the launcher_menu
                    self.append_launcher_menu();
                    self.$el.addClass('o_launcher_menu_background');
                    self.setLauncherMenuBg(display);
                    // Save and clear the url
                    self.url = $.bbq.getState();
                    if (location.hash) {
                        self._ignore_hashchange = true;
                        $.bbq.pushState('#home', 2); // merge_mode 2 to replace the current state
                    }
                    $.bbq.pushState({
                        'cids': self.url.cids
                    }, 0);

                    self.menu.toggle_mode(true, self.action_manager.getCurrentAction() !== null);
                });
            } else {
                dom.detach([{
                    widget: this.launcher_menu
                }]);
                dom.append(this.$el, [this.web_client_content], {
                    in_DOM: true,
                    callbacks: [{
                        widget: this.action_manager
                    }],
                });
                this.trigger_up('scrollTo', this.scrollPosition);
                this.launcher_menu_displayed = false;
                this.$el.removeClass('o_launcher_menu_background');
                this.setLauncherMenuBg(display);
                this.menu.toggle_mode(false, this.action_manager.getCurrentAction() !== null);
            }

        },
        append_launcher_menu: function () {
            dom.append(this.$el, [this.launcher_menu.$el], {
                in_DOM: true,
                callbacks: [{
                    widget: this.launcher_menu
                }],
            });
            this.launcher_menu_displayed = true;
        },
        _onShowLauncherMenu: function () {
            this.toggle_launcher_menu(true);
        },
        _onHideLauncherMenu: function () {
            if (this.action_manager.getCurrentAction() !== null) {
                // Restore the url
                $.bbq.pushState(this.url, 2); // merge_mode 2 to replace the current state
                this.toggle_launcher_menu(false);
            }
        },
        toggle_sidebar_menu: function (status) {
            var self = this;
            if (!config.device.isMobile) {
                // var sidebarMenu = self.$el.find('.o_main_sidebar');
                if (status) {
                    self.$el.removeClass('o_sidebar_collapsed').addClass('o_sidebar_expand');
                    // sidebarMenu.addClass("o_sidebar_menu_expand").removeClass("o_sidebar_menu_collapsed");
                } else {
                    self.$el.removeClass('o_sidebar_expand').addClass('o_sidebar_collapsed');
                    // sidebarMenu.addClass("o_sidebar_menu_collapsed").removeClass("o_sidebar_menu_expand");
                }
                core.bus.trigger('toggle_sidebar_mode', status);
            }
        },
        _onExpandSidebarMenu: function () {
            // console.log("web", "执行展开")
            this.sidebar_menu_status = true;
            this.toggle_sidebar_menu(true);
        },
        _onCollapseSidebarMenu: function () {
            // console.log("web", "执行折叠")
            this.sidebar_menu_status = false;
            this.toggle_sidebar_menu(false);
        },
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Overrides to return the left and top scroll positions of the webclient
         * in mobile (as it is the main scrolling element in that case).
         *
         * @returns {Object} with keys left and top
         */
        getScrollPosition: function () {
            if (config.device.isMobile) {
                return {
                    left: $(window).scrollLeft(),
                    top: $(window).scrollTop(),
                };
            }
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _onScrollTo: function (ev) {
            if (config.device.isMobile) {
                var offset = {
                    top: ev.data.top,
                    left: ev.data.left || 0
                };
                if (!offset.top) {
                    offset = dom.getPosition(document.querySelector(ev.data.selector));
                }
                $(window).scrollTop(offset.top);
                $(window).scrollLeft(offset.left);
            }
            this._super.apply(this, arguments);
        },
    });

});