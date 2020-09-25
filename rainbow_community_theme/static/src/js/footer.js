odoo.define('rainbow_community_theme.Footer', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var config = require('web.config');
    var QWeb = core.qweb;
    var session = require('web.session');

    var _t = core._t;

    var documentation_url = 'https://www.odoo.com/documentation/user';
    var documentation_dev_url = 'https://www.odoo.com/documentation';
    var poweredby_url = 'https://www.odoo.com';

    var Footer = Widget.extend({
        template: 'Footer',
        events: {
            'click div.scroll-to-top': '_goTopClick',
        },
        init: function (parent, display, info) {
            this._super.apply(this, arguments);
            this.info = info;
            this.offset = 200;
            this.duration = 500;

            if (config.device.isMobile) {
                this.footer_display = false;
            } else {
                if (display === 'show') {
                    this.footer_display = true;
                } else {
                    this.footer_display = false;
                }
            }
            var session = this.getSession();
        },
        start: function () {
            var self = this;
            self.handleGoTop();

            setTimeout(function () {
                self.setLinkUrl();
            }, 1000);
        },
        _goTopClick: function (ev) {
            // var self = this;
            // if (config.device.isMobile) {
            //     ev.preventDefault();
            //     $('html, body').animate({
            //         scrollTop: 0
            //     }, this.duration);
            //     return false;
            // } else {
            //     if ($(".settings").length > 0) {
            //         ev.preventDefault();
            //         $(".settings").animate({
            //             scrollTop: 0
            //         }, this.duration);
            //         return false;
            //     } else {
            //         ev.preventDefault();
            //         $(".o_content").animate({
            //             scrollTop: 0
            //         }, this.duration);
            //         return false;
            //     }
            // }
            if ($(".settings").length > 0) {
                ev.preventDefault();
                $(".settings").animate({
                    scrollTop: 0
                }, this.duration);
                return false;
            } else {
                ev.preventDefault();
                $(".o_content").animate({
                    scrollTop: 0
                }, this.duration);
                return false;
            }
        },
        handleGoTop: function () {
            var self = this;
            if (config.device.isMobile) {
                $(window).bind("touchend touchcancel touchleave", function (e) {
                    if ($(".settings").length > 0) {
                        $(".settings").scroll(function () {
                            if ($(this).scrollTop() > self.offset) {
                                $('.scroll-to-top').fadeIn(self.duration);
                            } else {
                                $('.scroll-to-top').fadeOut(self.duration);
                            }
                        });
                    } else {
                        $(".o_content").scroll(function () {
                            if ($(this).scrollTop() > self.offset) {
                                $('.scroll-to-top').fadeIn(self.duration);
                            } else {
                                $('.scroll-to-top').fadeOut(self.duration);
                            }
                        });
                    }
                });
            } else {
                if ($(".settings").length > 0) {
                    // console.log("settings", $(".settings").length);
                    $(".settings").scroll(function () {
                        if ($(this).scrollTop() > self.offset) {
                            $('.scroll-to-top').fadeIn(self.duration);
                        } else {
                            $('.scroll-to-top').fadeOut(self.duration);
                        }
                    });
                } else {
                    // console.log("o_content", $(".o_content").length);
                    $(".o_content").scroll(function () {
                        if ($(this).scrollTop() > self.offset) {
                            $('.scroll-to-top').fadeIn(self.duration);
                        } else {
                            $('.scroll-to-top').fadeOut(self.duration);
                        }
                    });
                }
            }
        },
        setLinkUrl: function () {
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
                    if (val.key === 'rainbow.documentation_url') {
                        documentation_url = val.value;
                    }
                    if (val.key === 'rainbow.documentation_dev_url') {
                        documentation_dev_url = val.value
                    };
                    if (val.key === 'rainbow.poweredby_url') {
                        poweredby_url = val.value;
                    }


                    self.$("a[data-link='poweredby']").attr("href", poweredby_url);
                    self.$("a[data-link='documentation']").attr("href", documentation_url);
                    self.$("a[data-link='documentation_dev']").attr("href", documentation_dev_url);

                    // 控制用户菜单的链接 显示和隐藏
                    if (val.key === 'rainbow.show_poweredby' && val.value === "False") {
                        self.$("a[data-link='poweredby']").hide();
                    }
                    if (val.key === 'rainbow.show_documentation' && val.value === "False") {
                        self.$("a[data-link='documentation']").hide();
                        self.$("span[data-link='documentation']").hide();
                    }
                    if (val.key === 'rainbow.show_documentation_dev' && val.value === "False") {
                        self.$("a[data-link='documentation_dev']").hide();
                        self.$("span[data-link='documentation_dev']").hide();
                    }
                })
            })
        }
    });
    return Footer;
});