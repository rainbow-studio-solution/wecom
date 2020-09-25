odoo.define('rainbow_community_theme.UserMenu', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var UserMenu = require('web.UserMenu');

    var _t = core._t;
    var QWeb = core.qweb;

    var documentation_url = 'https://www.odoo.com/documentation/user';
    var documentation_dev_url = 'https://www.odoo.com/documentation';
    var support_url = 'https://www.odoo.com/help';
    var account_title = 'My Online Account';
    var account_url = 'https://accounts.odoo.com/account';;

    UserMenu.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            if (config.device.isMobile) {
                this.className = 'o_user_menu_mobile';
                this.tagName = 'ul';
                this.template = undefined;
            }
            var self = this;
            var session = this.getSession();
            setTimeout(function () {
                self.bindLangList(session);
                self.setUserMenuUrl();
                self.remove_space_characters();
                self.setUserIcon();

            }, 1000);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            if (config.device.isMobile) {
                this.$el.append(QWeb.render('UserMenu.Actions'));
            }
            // return this._super.apply(this, arguments);
            return this._super.apply(this, arguments).then(function () {
                if (!config.device.isMobile) {
                    //给非当前默认语言添加事件
                    self.$el.on('click', 'a[data-lang-menu=lang]', function (ev) {
                        ev.preventDefault();
                        var fun = self['_onMenuToggleLang'];
                        fun.call(self, $(this));
                    });
                    //锁定屏幕
                    self.$el.on('click', 'a[data-menu=lock]', function (ev) {
                        ev.preventDefault();
                        var fun = self['_onMenuLock'];
                        fun.call(self, $(this));
                    });
                    //控制debug显示
                    if (config.isDebug() === "assets") {
                        self.$('a[data-menu=debugassets]').hide();
                    } else if (config.isDebug()) {
                        self.$('a[data-menu=debug]').hide();
                    } else {
                        self.$('a[data-menu=quitdebug]').hide();
                    }
                }
            });
        },
        bindLangList: function (session) {
            var self = this;
            var current_lang = self.$('a[data-lang-menu=current_lang]');
            var lang_menu = current_lang.parent().find('.dropdown-menu');
            var current_lang_flag = "";
            self._rpc({
                model: 'res.lang',
                method: 'search_read',
                domain: [],
                fields: ['name', 'code'],
                lazy: false,
            }).then(function (res) {
                _.each(res, function (lang) {
                    if (lang['code'] === session.user_context.lang) {
                        if (res.length > 1) {
                            current_lang.attr({
                                "role": "button",
                                "title": lang['name'],
                                "href": "#",
                                "class": "dropdown-toggle",
                                "data-toggle": "dropdown",
                                "data-display": "static",
                                "aria-expanded": "false",
                                "data-lang-id": lang['code']
                            });
                            current_lang_flag = "<img class='oe_topbar_flag' src=/rainbow_community_theme/static/src/img/flags/" +
                                lang['code'] + ".png/>";
                            current_lang.append(current_lang_flag);
                        } else {
                            current_lang.attr({
                                "role": "button",
                                "title": lang['name'],
                            });
                            current_lang_flag = "<img class='oe_topbar_flag' src=/rainbow_community_theme/static/src/img/flags/" +
                                lang['code'] + ".png/>";
                            current_lang.append(current_lang_flag);
                        }
                    } else {
                        if (res.length > 1) {
                            var non_current_lang = "<a role='menuitem' href='#' class='dropdown-item' " +
                                "data-lang-menu='lang' data-lang-id=" + lang['code'] + ">" +
                                "<img class='flag' src=/rainbow_community_theme/static/src/img/flags/" + lang['code'] + ".png/>" +
                                "<span>" + lang['name'] + "</span></a>";
                            lang_menu.append(non_current_lang);
                        }
                    }
                });
            })
        },
        setUserMenuUrl: function () {
            var self = this;
            var session = this.getSession();
            self._rpc({
                model: 'ir.config_parameter',
                method: 'search_read',
                domain: [
                    ['key', '=like', 'rainbow.%']
                ],
                fields: ['key', 'value'],
                lazy: false,
            }).then(function (res) {
                $.each(res, function (key, val) {
                    // 设置用户菜单的跳转链接
                    if (val.key === 'rainbow.documentation_url')
                        documentation_url = val.value;
                    if (val.key === 'rainbow.documentation_dev_url')
                        documentation_dev_url = val.value;
                    if (val.key === 'rainbow.support_url')
                        support_url = val.value;
                    if (val.key === 'rainbow.account_title')
                        account_title = val.value;
                    if (val.key === 'rainbow.account_url')
                        account_url = val.value;

                    // 控制用户菜单的链接 显示和隐藏
                    if (val.key === "rainbow.show_lang" && val.value === "False") {
                        self.$('a[data-lang-menu=current_lang]').hide();
                    }
                    if (session.user_context.uid > 2 || (val.key === 'rainbow.show_debug' && val.value === "False")) {
                        self.$('a[data-menu=debug]').hide();
                        self.$('a[data-menu=debugassets]').hide();
                        self.$('a[data-menu=quitdebug]').hide();
                    }
                    if (val.key === 'rainbow.show_documentation' && val.value === "False") {
                        self.$("a[data-menu='documentation']").hide();
                    }
                    if (val.key === 'rainbow.show_documentation_dev' && val.value === "False") {
                        self.$("a[data-menu='documentation_dev']").hide();
                    }
                    if (val.key === 'rainbow.show_support' && val.value === "False") {
                        self.$('a[data-menu=support]').hide();
                    }
                    if (val.key === 'rainbow.show_account' && val.value === "False") {
                        self.$('a[data-menu=account]').hide();
                    }
                    // if (val.key === 'rainbow.account_title' && val.value) {
                    //     self.$('a[data-menu="account"]').html("<i class=\"fa fa-ticket\"/>" + account_title);
                    // }
                });
            })
        },
        remove_space_characters: function () {
            //遍历移除用户菜单中的空格
            var self = this;
            self.$('a[data-menu]').each(function () {
                $(this).text($(this).text().trim())
            });
        },
        setUserIcon: function () {
            //安装HR模块后，会替换掉用户菜单的“我的配置”菜单项
            var self = this;

            if (self.$('a[data-menu="debug"]').find('i').length === 0)
                self.$('a[data-menu="debug"]').prepend("<i class='fa fa-bug'></i>");
            if (self.$('a[data-menu="debugassets"]').find('i').length === 0)
                self.$('a[data-menu="debugassets"]').prepend("<i class='fa fa-bug'></i>");
            if (self.$('a[data-menu="quitdebug"]').find('i').length === 0)
                self.$('a[data-menu="quitdebug"]').prepend("<i class='fa fa-bug'></i>");

            if (self.$('a[data-menu="documentation"]').find('i').length === 0)
                self.$('a[data-menu="documentation"]').prepend("<i class='fa fa-book'></i>");
            if (self.$('a[data-menu="documentation_dev"]').find('i').length === 0)
                self.$('a[data-menu="documentation_dev"]').prepend("<i class='fa fa-book'></i>");
            if (self.$('a[data-menu="support"]').find('i').length === 0)
                self.$('a[data-menu="support"]').prepend("<i class='fa fa-handshake-o'></i>");
            if (self.$('a[data-menu="settings"]').find('i').length === 0)
                self.$('a[data-menu="settings"]').prepend("<i class='fa fa-user-circle-o'></i>");
            if (self.$('a[data-menu="account"]').find('i').length === 0)
                self.$('a[data-menu="account"]').prepend("<i class='fa fa-ticket'></i>");
            if (self.$('a[data-menu="lock"]').find('i').length === 0)
                self.$('a[data-menu="lock"]').prepend("<i class='fa fa-lock'></i>");
            if (self.$('a[data-menu="logout"]').find('i').length === 0)
                self.$('a[data-menu="logout"]').prepend("<i class='fa fa-sign-out'></i>");
            if (self.$('a[data-menu="shortcuts"]').find('i').length === 0)
                self.$('a[data-menu="shortcuts"]').prepend("<i class='fa fa-keyboard-o'></i>");
        },
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * @override
         */
        do_action() {
            return this._super(...arguments)
                .then(resp => {
                    core.bus.trigger('close_o_burger_menu');
                    return resp;
                });
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _onMenuDocumentation: function () {
            window.open(documentation_url, '_blank');
        },
        _onMenuSupport: function () {
            window.open(support_url, '_blank');
        },

        //增加的方法
        _onMenuLock: function () {
            // this.trigger_up('clear_uncommitted_changes', {
            //     callback: this.do_action.bind(this, 'lock'),
            // });
            // window.location = "/web/lock";
            window.location = "/web/lock";
        },
        _onMenuDebug: function () {
            window.location = $.param.querystring(window.location.href, 'debug=1');
        },
        _onMenuDebugassets: function () {
            window.location = $.param.querystring(window.location.href, 'debug=assets');
        },
        _onMenuQuitdebug: function () {
            window.location = $.param.querystring(window.location.href, 'debug=0');
        },
        _onMenuToggleLang: function (ev) {
            var self = this;
            var lang = ($(ev).data("lang-id"));
            // if(!lang){
            //     return ;
            // }else {
            var session = this.getSession();
            return this._rpc({
                model: 'res.users',
                method: 'write',
                args: [session.uid, {
                    'lang': lang
                }],
            }).then(function (result) {
                self.do_action({
                    type: 'ir.actions.client',
                    res_model: 'res.users',
                    tag: 'reload_context',
                    target: 'current',
                });
            });

            // }
        }
    });

});