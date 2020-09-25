odoo.define('rainbow_community_theme.SidebarMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var Widget = require('web.Widget');
    var config = require('web.config');
    var QWeb = core.qweb;

    var SidebarMenu = Widget.extend({
        template: 'SiderbarMenu',
        menusTemplate: 'SiderbarMenu.FirstLevelMenu',
        animationDuration: 200,
        events: {
            'click a[data-menu]': '_openSideMenuLinkClick',
            // 'click li > a.nav-toggle, li > a > span.nav-toggle': 'toggle_sidebar_menu',
            'mouseenter .o_main_sidebar': '_expandSideMenu',
            'mouseleave .o_main_sidebar': '_collapsedSideMenu',
        },
        init: function (parent, menu_data, mode, state, position) {
            var self = this;
            this._super.apply(this, arguments);

            this.menu_data = menu_data;
            this.mode = mode;
            this.state = state;
            this.position = position;
            if (this.mode === 'expand') {
                this.isExpand = true;
            } else {
                this.isExpand = false;
            }
        },
        start: function () {
            var self = this;
            this.$section_placeholder = this.$('.o_main_sidebar');
            self.initSidebarScroll();
            self.handleSidebarSize();
            $(window).resize(function () {
                //窗体变化时触发 重新处理sidebar高度
                self.handleSidebarSize();
            });
            self.handleSidebarMenu();
            core.bus.on('toggle_sidebar_mode', this, this.toggle_sidebar_mode); // 展开/折叠sidebar
            core.bus.on('toggle_sidebar_link_active', this, this.toggle_sidebar_link_active); // 切换sidebar菜单的active状态
            return this._super.apply(this, arguments).then(this._renderSidebarMenu.bind(this));
        },
        toggle_sidebar_mode: function (sidebar_menu) {
            /*
            接收 header menu 折叠 / 展开 按钮事件的传递值，且处理sidebar的状态
            */
            console.log("toggle_sidebar_mode");
            this.isExpand = !!sidebar_menu;
            this.$section_placeholder.toggleClass('o_sidebar_menu_expand', this.isExpand)
                .toggleClass('o_sidebar_menu_collapsed', !this.isExpand);
        },
        _renderSidebarMenu: function () {
            this.$firstMenu = $(QWeb.render(this.menusTemplate, {
                menu_data: this.menu_data,
                mode: this.mode,
                state: this.state,
                position: this.position,
            }));
            this.$section_placeholder.append(this.$firstMenu);
            this.toggle_sidebar_link_active(this.state.menu_id);
        },
        _expandSideMenu: function (event) {
            /*
            isExpand=false 且sidebar处于折叠状态 ，鼠标指针穿过元素时的事件
            */
            var self = this;
            if (!this.isExpand && this.$section_placeholder.hasClass('o_sidebar_menu_collapsed')) {
                this.$section_placeholder.addClass("o_sidebar_menu_expand").removeClass("o_sidebar_menu_collapsed");
            } else {
                return
            }
        },
        _collapsedSideMenu: function (event) {
            /*
            isExpand=false 且sidebar处于展开状态 ，鼠标指针离开元素时的事件
            */
            if (!this.isExpand && this.$section_placeholder.hasClass('o_sidebar_menu_expand')) {
                this.$section_placeholder.removeClass("o_sidebar_menu_expand").addClass("o_sidebar_menu_collapsed");
            } else {
                return
            }
        },
        _openSideMenuLinkClick: function (ev) {
            ev.preventDefault();
            var self = this;
            var menu_id = $(ev.currentTarget).data('menu');
            var action_id = $(ev.currentTarget).data('action-id');
            var primary_menu_id = $(ev.currentTarget).parents('.top-menu').data('menu');
            if ($(ev.currentTarget).attr('href') != 'javascript:;') {
                this.trigger_up('menu_clicked', {
                    id: menu_id,
                    action_id: action_id,
                    previous_menu_id: menu_id || primary_menu_id,
                });
                core.bus.trigger('change_menu_section', primary_menu_id); //传递值给menu
                self.toggle_sidebar_link_active(menu_id);
            }
        },
        toggle_sidebar_link_active: function (link_menu_id) {
            /*
            切换 sidebar的菜单Active状态
            */
            // console.log(link_menu_id);
            if (!link_menu_id) {
                //安装website时，会出现menu_id为空的情况
                return
            } else {
                var sidebar = this.$section_placeholder;
                var menu = sidebar.find('a[data-menu=' + link_menu_id + ']');
                // console.log(link_menu_id, menu.length);
                if (!menu.data('menu')) {
                    return;
                } else {
                    sidebar.find('li.active').removeClass('active');
                    sidebar.find('li.open').removeClass('open');
                    sidebar.find('> a > .arrow.open').removeClass('open');
                    sidebar.find('span.selected').remove();
                    sidebar.find('> .sub-menu').slideUp();

                    menu.parents('li').each(function () {
                        // console.log($(this).length, $(this).data('menu'))
                        $(this).addClass('active');
                        $(this).find('> a > span.arrow').addClass('open');

                        if ($(this).parent('ul.o_main_sidebar').length === 1) {
                            $(this).find('> a').append('<span class="selected"></span>');
                        }

                        if ($(this).children('ul.sub-menu').length === 1) {
                            $(this).addClass('open');
                        }
                    });
                    console.log("开始滚动", (menu.position()).top);
                    sidebar.slimScroll({
                        scrollTo: (menu.position()).top,
                        // scrollTo: (menu.parents('.top-menu').position()).top,
                        width: '100%',
                    });
                }
            }

        },
        toggle_sidebar_menu: function (ev) {
            /*
            sidebar 打开子菜单
            */
            var self = this;
            var sidebar = this.$section_placeholder;
            var that = $(ev.currentTarget).closest('.nav-item').children('.nav-link');
            var hasSubMenu = that.next().hasClass('sub-menu');
            var parent = that.parent().parent();
            var the = that;
            var sub = that.next();

            var slideSpeed = parseInt(sidebar.data("slide-speed"));
            var keepExpand = sidebar.data("keep-expanded");

            if (!keepExpand) {
                parent.children('li.open').children('a').children('.arrow').removeClass('open');
                parent.children('li.open').children('.sub-menu:not(.always-open)').slideUp(slideSpeed);
                parent.children('li.open').removeClass('open');
            }

            if (sub.is(":visible")) {
                $('.arrow', the).removeClass("open");
                the.parent().removeClass("open");
                the.next().hide();
                if ($('body').hasClass('o_sidebar_collapsed') === false) {
                    console.log("toggle_sidebar_menu1");
                    sidebar.slimScroll({
                        scrollTo: (the.position()).top,
                        width: '100%',
                    });
                }
            } else if (hasSubMenu) {
                $('.arrow', the).addClass("open");
                the.parent().addClass("open");
                the.next().show();
                if ($('body').hasClass('o_sidebar_collapsed') === false) {
                    console.log("toggle_sidebar_menu2");
                    sidebar.slimScroll({
                        scrollTo: (the.position()).top,
                        // scrollTo: (the.parents('.top-menu').position()).top,
                        width: '100%',
                        height: parseInt(self.handleSidebarSize())
                    });
                }
            }

            ev.preventDefault();
        },

        initSidebarScroll: function () {
            /*
            初始化sidebar滚动条
            */
            var self = this;
            var sidebar = this.$section_placeholder;
            sidebar.slimScroll({
                wheelStep: 20, //滚轮滚动量
                size: '7px',
                color: '#bbb',
                railColor: 'transparent',
                alwaysVisible: false, //是否 始终显示组件
                allowPageScroll: true, //是否 使用滚轮到达顶端/底端时，滚动窗口
                railDraggable: true, //是否 滚动条可拖动
                railVisible: true, //是否 显示轨道
                disableFadeOut: true, //是否 鼠标经过可滚动区域时显示组件，离开时隐藏组件
                railOpacity: 0.3,
                width: '100%',
                height: parseInt(self.handleSidebarSize())
            });
        },
        handleSidebarMenu: function () {
            /*
            处理sidebar点击事件
            */
            var self = this;
            var sidebar = this.$section_placeholder;
            sidebar.on('click', 'li > a.nav-toggle, li > a > span.nav-toggle', function (e) {

                var that = $(this).closest('.nav-item').children('.nav-link');
                var hasSubMenu = that.next().hasClass('sub-menu');
                var parent = that.parent().parent();
                var the = that;
                var sub = that.next();

                var slideSpeed = parseInt(sidebar.data("slide-speed"));
                var keepExpand = sidebar.data("keep-expanded");

                if (!keepExpand) {
                    parent.children('li.open').children('a').children('.arrow').removeClass('open');
                    parent.children('li.open').children('.sub-menu:not(.always-open)').slideUp(slideSpeed);
                    parent.children('li.open').removeClass('open');
                }

                if (sub.is(":visible")) {
                    $('.arrow', the).removeClass("open");
                    the.parent().removeClass("open");
                    // the.next().hide();
                    // if ($('body').hasClass('o_sidebar_collapsed') === false) {
                    //     sidebar.slimScroll({
                    //         scrollTo: (the.position()).top,
                    //         width: '100%',
                    //     });
                    // }
                    sub.slideUp(slideSpeed, function () {
                        if ($('body').hasClass('o_sidebar_collapsed') === false) {
                            sidebar.slimScroll({
                                'scrollTo': (the.position()).top
                            });
                        }
                        self.handleSidebarSize();
                    });
                } else if (hasSubMenu) {
                    $('.arrow', the).addClass("open");
                    the.parent().addClass("open");
                    // the.next().show();

                    // if ($('body').hasClass('o_sidebar_collapsed') === false) {
                    //     console.log(the, the.position().top);
                    //     sidebar.slimScroll({
                    //         // height: parseInt(self.handleSidebarSize()),
                    //         scrollTo: (the.position()).top,
                    //         // scrollTo: (the.next().position()).top,
                    //         // scrollTo: (the.parents('.top-menu').position()).top,
                    //         width: '100%',

                    //     });
                    // }
                    sub.slideDown(slideSpeed, function () {
                        if ($('body').hasClass('o_sidebar_collapsed') === false) {
                            sidebar.slimScroll({
                                'scrollTo': (the.position()).top
                            });
                        }
                        self.handleSidebarSize();
                    });
                }
                e.preventDefault();
            });

        },
        handleSidebarSize: function () {
            var self = this;
            var body = $('body');
            var sidebar = this.$section_placeholder;
            var available_height;
            var slimScrollDiv = $('.slimScrollDiv');

            // 判断是否显示页脚
            if (session.theme.footer === 'show') {
                available_height = self.getViewPort().height - 79;
            } else {
                available_height = self.getViewPort().height - 46;
            }
            if (slimScrollDiv.length > 0) {
                slimScrollDiv.css('height', available_height);
            }

            sidebar.css('height', available_height);
            sidebar.attr('data-height', available_height);
            console.log("总高度", available_height)
            return available_height;
        },
        getViewPort: function () {
            var e = window,
                a = 'inner';
            if (!('innerWidth' in window)) {
                a = 'client';
                e = document.documentElement || document.body;
            }

            return {
                width: e[a + 'Width'],
                height: e[a + 'Height']
            };
        },
    });
    return SidebarMenu;
});