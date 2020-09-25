odoo.define('rainbow_community_theme.ThemePanel', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var UserMenu = require('web.UserMenu');
    var session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;

    UserMenu.include({
        thmemeTemplate: 'Theme.settings.panel',
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;

            return this._super.apply(this, arguments).then(function () {
                self.$el.on('click', 'a[id=theme-option]', function (ev) {
                    ev.preventDefault();
                    var fun = self['open_dialog'];
                    fun.call(self, $(this));
                });
            });
        },
        open_dialog: function () {
            var self = this;
            var dialog_title = _t("THEME SETTINGS PANEL");

            //size: small medium  large
            var dialog = new Dialog(this, {
                size: 'small',
                // dialogClass: 'theme-panel-content',
                title: dialog_title,
                buttons: [{
                    text: 'Save',
                    classes: 'btn-primary',
                    close: true,
                    click: this._onSave.bind(this)
                }, ],
                $content: QWeb.render('Theme.settings.panel', {
                    current: session.theme.color,
                    launcher_bg_status: session.theme.launcher_bg_status,
                    current_bg: session.theme.launcher_bg,
                    submenu_position: session.theme.submenu_position,
                    sidebar_mode: session.theme.sidebar_mode,
                    sidebar_position: session.theme.sidebar_position,
                    footer: session.theme.footer,
                })
            });
            dialog.opened().then(function () {
                self.init_dialog(dialog);
            });
            dialog.open();
        },
        init_dialog: function (dialog) {
            var self = this;

            var color = session.theme.color;
            var launcher_bg_status = session.theme.launcher_bg_status;
            var launcher_bg = session.theme.launcher_bg;
            var submenu_position = session.theme.submenu_position;
            var mode = session.theme.sidebar_mode;
            var sidebar_position = session.theme.sidebar_position;
            var footer = session.theme.footer;
            this.$btndiv = dialog.$modal.find('.theme-btn');

            //"modal-dialog
            // dialog.$modal.find("div.modal-dialog").css("width", "320px");
            // dialog.$modal.find("div.modal-dialog").css("background", "none");
            dialog.$modal.find("div.modal-content").css("background", "none");
            // dialog.$modal.find("div.modal-body").css("width", "320px");
            // if (color === 'default') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#3D3D3D");
            //     console.log("default");
            // } else if (color === 'darkblue') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#364150");
            //     console.log("darkblue");
            // } else if (color === 'blue') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#4276A4");
            //     console.log("blue");
            // } else if (color === 'grey') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#364150");
            //     console.log("grey");
            // } else if (color === 'light') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#E1E1E1");
            //     console.log("light");
            // } else if (color === 'light2') {
            //     dialog.$modal.find("div.modal-body").css("backgroundColor", "#E1E1E1");
            //     console.log("light2");
            // }

            dialog.$modal.find("header").css("display", "none");
            dialog.$modal.find("footer").css("display", "none");
            this.$panel = dialog.$modal.find('.theme-panel');
            $('.theme-close', this.$panel).click(function () {
                dialog.$modal.modal('hide');
            });

            $('.theme-colors > ul > li', this.$panel).click(function () {
                color = $(this).attr("data-style");
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
                $('.theme-colors > ul > li', this.$panel).removeClass("current");
                $(this).addClass("current");
            });
            $('select.launcher-bg-status-option', this.$panel).change(function () {
                launcher_bg_status = $(this).children('option:selected').val();
                if (launcher_bg_status === 'enable') {
                    $('.launcher-bg-option').removeClass('o_hidden');
                } else {
                    $('.launcher-bg-option').addClass('o_hidden');
                }
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
            });
            $('.launcher-bg-option> ul > li', this.$panel).click(function () {
                launcher_bg = $(this).attr("data-img");
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
                $('.launcher-bg-option> ul > li', this.$panel).removeClass("current");
                $(this).addClass("current");
            });
            $('.launcher-bg-option> ul > li', this.$panel).dblclick(function (ev) {
                self.open_img_modal($(ev.currentTarget).data('img'));
            });
            $('select.submenu-pos-option', this.$panel).change(function () {
                submenu_position = $(this).children('option:selected').val();
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
            });
            $('select.sidebar-option', this.$panel).change(function () {
                mode = $(this).children('option:selected').val();
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
            });
            $('select.sidebar-pos-option', this.$panel).change(function () {
                sidebar_position = $(this).children('option:selected').val();
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
            });
            $('select.page-footer-option', this.$panel).change(function () {
                footer = $(this).children('option:selected').val();
                self.setTheme(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer);
            });

            dialog.$modal.on('click', 'button.theme-save', function () {
                dialog.$modal.find("footer").find("button.btn-primary").trigger('click');
            });

            if (launcher_bg_status === 'enable') {
                $('.launcher-bg-option').removeClass('o_hidden');
            } else {
                $('.launcher-bg-option').addClass('o_hidden');
            }
        },
        check_change: function (color, launcher_bg_status, launcher_bg, apps_num, mode, position, footer) {
            var self = this;
            if (color != session.theme.color || launcher_bg_status != session.theme.launcher_bg_status || launcher_bg != session.theme.launcher_bg || apps_num != session.theme.submenu_position || mode != session.theme.sidebar_mode || position != session.theme.sidebar_position || footer != session.theme.footer) {
                return true;
            } else {
                return false;
            }
        },
        setTheme: function (color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer) {
            var self = this;
            if (self.check_change(color, launcher_bg_status, launcher_bg, submenu_position, mode, sidebar_position, footer)) {
                this.$btndiv.removeClass("o_hidden");
            } else {
                this.$btndiv.addClass("o_hidden");
            }
        },
        _onSave: function () {
            var self = this;
            var color = this.$panel.find('.theme-colors').find('li.current').attr("data-style");
            var launcher_bg_status = this.$panel.find('select.launcher-bg-status-option').children('option:selected').val();
            var launcher_bg = this.$panel.find('.launcher-bg-option').find('li.current').attr("data-img");
            var submenu_position = this.$panel.find('select.submenu-pos-option').children('option:selected').val();
            var mode = this.$panel.find('select.sidebar-option').children('option:selected').val();
            var sidebar_position = this.$panel.find('select.sidebar-pos-option').children('option:selected').val();
            var footer = this.$panel.find('select.page-footer-option').children('option:selected').val();
            // console.log("launcher_bg_status", launcher_bg_status);
            return this._rpc({
                model: 'res.users',
                method: 'set_theme',
                args: [session.uid, {
                    'theme_color': color,
                    'launcher_bg_status': launcher_bg_status,
                    'launcher_bg': launcher_bg,
                    'submenu_position': submenu_position,
                    'sidebar_mode': mode,
                    'sidebar_position': sidebar_position,
                    'theme_footer': footer,
                }],
            }).then(function (result) {
                self.do_action({
                    type: 'ir.actions.client',
                    res_model: 'res.users',
                    tag: 'reload_context',
                    target: 'current',
                });
            });
        },
        open_img_modal: function (img) {
            //size: small medium  large
            var dialog = new Dialog(this, {
                size: 'large',
                // dialogClass: 'theme-panel-content',
                // title: dialog_title,
                buttons: [],
                $content: QWeb.render('Theme.launcher.preview', {
                    img: img,
                })
            });
            dialog.opened().then(function () {
                dialog.$modal.find("div.modal-dialog").css("background", "none");
                dialog.$modal.find("div.modal-content").css("background", "none");
                dialog.$modal.find("div.modal-content").css("border", "none");
                dialog.$modal.find("header").css("display", "none");
                dialog.$modal.find("footer").css("display", "none");


                $('.lb-close', dialog.$modal).click(function () {
                    dialog.$modal.modal('hide');
                });
            });
            dialog.open();
        }
    });
});