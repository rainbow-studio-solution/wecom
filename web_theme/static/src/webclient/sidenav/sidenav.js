/** @odoo-module **/

import { browser } from '@web/core/browser/browser';
import { useBus, useService } from '@web/core/utils/hooks';
import { _t } from '@web/core/l10n/translation';
import { fuzzyLookup } from '@web/core/utils/search';
const legacy_session = require('web.session'); // 需要访问allowed_company_ids，故使用 legacy 的代码，不能使用 @web/session

const {
	Component,
	onMounted,
	onRendered,
	onWillRender,
	onWillDestroy,
	onWillUnmount,
	onPatched,
	onWillUpdateProps,
	useExternalListener,
	useEffect,
	useState,
	useRef
} = owl;

/**
 * SideNav menu
 * 该组件处理不同可用应用程序和菜单之间的显示和导航。
 *
 *! 组件示例图：
 **┌ <div class="accordion accordion-flush" id="menu-accordion-1"> ---------------------------┐
 **│ ┌ <div class="accordion-item" id="menu-item-1"> ---------------------------------------┐ │
 **│ │ ┌ <h2 class="accordion-header"  id="menu-header-1"> -------------------------------┐ │ │
 **│ │ │ ┌ <a class="accordion-button collapsed" id="menu-link-1" href="#"> ------------┐ │ │ │
 **| | | |   data-bs-toggle="collapse"                                                  | | | |
 **| | | |   aria-expanded="false"                                                      │ │ │ │
 **| | | |   data-bs-target="#menu-collapse-1"                                          │ │ │ │
 **| | | |   aria-controls="menu-collapse-1"                                            │ │ │ │
 **| | | | >                                                                            │ │ │ │
 **| │ │ │ ┌ <span class="menu-icon"> ------------------------------------------------┐ │ │ │ │
 **| │ │ │ │  <i class="fa fa-home"></i>                                              │ │ │ │ │
 **| │ │ │ └ </span> -----------------------------------------------------------------┘ │ │ │ │
 **| │ │ │ - <span class="menu-lable"/>                                                 │ │ │ │
 **| │ │ └ <a/> ------------------------------------------------------------------------┘ │ │ │
 **| │ └ </h2> ---------------------------------------------------------------------------┘ │ │
 **| │ ┌ <div class="accordion-collapse collapse" id="menu-collapse-1"  折叠的选项 --------┐ │ │
 **| | |     aria-labelledby="menu-header-1"                                              │ │ │
 **| | |     data-bs-parent="#menu-accordion-1"                                           │ │ │
 **| │ │ >                                                                                │ │ │
 **| │ │ ┌ <div class="accordion-body" id="menu-body-1> --------------------------------┐ │ │ │
 **| │ │ │ - [Next level menu]  从<div class="accordion accordion-flush">开始循环        │ │ │ │
 **| │ │ └ </div>-----------------------------------------------------------------------┘ │ │ │
 **| │ └ </div>---------------------------------------------------------------------------┘ │ │
 **| └ </div> ------------------------------------------------------------------------------┘ │
 **└ </div>-----------------------------------------------------------------------------------┘

 *! 注意:
 1. ".collapse"类用于指定一个折叠元素 (示例中的 <div>); 点击按钮后会在隐藏与显示之间切换。
 2. 控制内容的隐藏与显示，需要在 <a> 或 <button> 元素上添加 data-bs-toggle="collapse" 属性。 data-bs-target="#id" 属性是对应折叠的内容 (<div id="menu-collapse-1">)。
 3. <a> 元素上你可以使用 href 属性来代替 data-bs-target 属性.
 4. 默认情况下折叠的内容是隐藏的，你可以添加 ".show" 类让内容默认显示:
 5. 使用 data-bs-parent 属性来确保所有的折叠元素在指定的父元素下，这样就能实现在一个折叠选项显示时其他选项就隐藏。

 *
 * @extends Component
 */

export class SideNav extends Component {
	setup() {
		super.setup();
		let self = this;

		this.rpc = useService('rpc');
		this.orm = useService('orm');
		this.sidenav = useRef('sidenav');
		this.actionService = useService('action');
		this.menuService = useService('menu');
		this.router = useService('router');

		this.menuData = this.menuService.getMenuAsTree('root');
		// console.log(this.menuData)

		this.theme = legacy_session.theme;

		this.default_theme = this.getDefaultTheme(this.theme);

		this.current_cid = legacy_session.user_context.allowed_company_ids[0];

		this.menu_layout_mode = this.default_theme['menu_layout_mode'];
		this.main_submenu_position = this.default_theme['main_submenu_position'];
		this.sidebar_display_number_of_submenus = this.default_theme['sidebar_display_number_of_submenus'];
		this.sidebar_fixed = this.default_theme['sidebar_fixed'];
		this.sidebar_show_minimize_button = this.default_theme['sidebar_show_minimize_button'];
		this.sidebar_default_minimized = this.default_theme['sidebar_default_minimized'];
		this.sidebar_hover_maximize = this.default_theme['sidebar_hover_maximize'];

		this.sidebarMinimize = false;
		if (!this.sidebar_fixed || this.sidebar_default_minimized) {
			this.sidebarMinimize = true;
		}

		onMounted(() => {
			this.onMounted();
		});
		onWillRender(() => {
			this.onWillRender();
		});
		onRendered(() => {
			this.onRendered();
		});
		onWillUpdateProps(() => {
			this.onWillUpdateProps();
		});
		onPatched(() => {
			this.onPatched();
		});
		// onWillUnmount(this.onWillUnmount);
		// useBus(this.env.bus, "ROUTE_CHANGE", this.loadRouterState);

		this.currentMenuId = Number(this.router.current.hash.menu_id || 0);
		if (!this.currentMenuId) {
			this.currentMenuId = this.menuData.children[0];
		}
		this.currentAppId = this.menuService.getMenu(this.currentMenuId).appID;

		// 搜索
		this.allApps = this.menuData.children.map((mid) => self.menuService.getMenu(mid));
		this.availableApps = this.allApps;
		this.displayedMenuItems = [];
		this.inputRef = useRef('input');
		this.mainContentRef = useRef('mainContent');
		this.state = useState({
			focusedIndex: null,
			isSearching: false,
			query: ''
			// isIosApp: isIosApp(),
		});
	}

	// async loadRouterState() {
	//     let stateLoaded = await this.actionService.loadState();
	//     let menuId = Number(this.router.current.hash.menu_id || 0);
	//     console.warn("loadRouterState", stateLoaded)
	//     console.warn("loadRouterState", menuId);
	//     if (!stateLoaded && menuId) {
	//         // Determines the current actionId based on the current menu
	//         console.log("1-!stateLoaded && menuId")
	//     }

	//     if (stateLoaded && !menuId) {
	//         // Determines the current menu based on the current action
	//         console.log("2-stateLoaded && !menuId")
	//     }

	//     if (menuId) {
	//         // Sets the menu according to the current action
	//         console.log("3-stateLoaded && !menuId")
	//     }

	//     if (!stateLoaded) {
	//         // If no action => falls back to the default app
	//         console.log("4-stateLoaded && !menuId")
	//     }
	// }

	onWillRender() {
		// 用于定义在渲染组件之前应该执行的代码的钩子
		// console.log("onWillRender");
		// 声明 this.el，以便于 在 其他生命周期中 调用
	}
	onRendered() {
		// 定义组件渲染后应该执行的代码的钩子
		// console.log("onRendered");
	}

	async onWillUpdateProps() {
		// 每次重新挂载时都会重置状态
		this.state.focusedIndex = null;
		this.state.isSearching = false;
		this.state.query = '';
		this.inputRef.el.value = '';

		this.availableApps = this.allApps;
		this.displayedMenuItems = [];
	}

	onMounted() {
		// 定义挂载组件时应该执行的代码的钩子
		// console.log("onMounted");
		// 声明 this.el，以便于 在 其他生命周期中 调用
		// this.el = this.__owl__.bdom.el;
		this.el = this.sidenav.el;
		this.$el = $(this.el);

		this.body = document.body;

		this.$el.on('mouseenter', '.o_sidenav_header_logo', this._onMouseEnter.bind(this));
		this.$el.on('mouseenter', '.o_sidenav_search', this._onMouseEnter.bind(this));
		this.$el.on('mouseenter', '.o_main_sidenav', this._onMouseEnter.bind(this));
		this.$el.on('mouseleave', '.o_sidenav_header_logo', this._onMouseLeave.bind(this));
		this.$el.on('mouseleave', '.o_sidenav_search', this._onMouseLeave.bind(this));
		this.$el.on('mouseleave', '.o_main_sidenav', this._onMouseLeave.bind(this));

		let menuId = Number(this.router.current.hash.menu_id || 0);
		const currentController = this.actionService.currentController;
		let actionId = currentController && currentController.action.id;
		if (menuId === 0 && !actionId) {
			// 处理安装 oec_base 后,使用 ir.actions.todo 跳转菜单后，侧边栏无法正确菜单状态问题
			let hash = browser.location.hash.substring(1);
			let params = $.deparam(hash);
			if (params.hasOwnProperty('action') && Object.keys(params).length === 2) {
				actionId = Number(params.action);
				this.handle_todo_menu(actionId);
			}
			// actionId = Number(params.action);
			// this.handle_todo_menu(actionId)
		}

		this.initializeMenu();

		// this._updateScrollBarWidth();
	}
	async handle_todo_menu(actionId) {
		let self = this;
		// http://localhost:8069/web#action=167&cids=1
		let xmlid = '';
		if (!actionId) {
			return false;
		}
		const result = await this.orm.call('ir.actions.act_window', 'get_model_name_by_action_id', [actionId]);
		if (
			result['res_model'] == 'res.config.settings' &&
			result['type'] == 'ir.actions.act_window' &&
			result['xml_id'] == 'oec_base.oec_configurator'
		) {
			xmlid = 'oec_base.menu_base_config';
		}
		if (
			result['res_model'] == 'res.config.settings' &&
			result['type'] == 'ir.actions.act_window' &&
			result['xml_id'] == 'oec_im_wecom_base.wecom_configurator'
		) {
			// xmlid = "oec_im_wecom_base.wecom_config_settings_action"
			xmlid = 'oec_im_wecom_base.menu_wecom_configuration';
		}

		if (xmlid) {
			// console.log("xmlid", xmlid)
			const menus = this.el.querySelector('a.accordion-button');
			const menu_collapse = this.el.querySelector('div.accordion-collapse');
			menus.classList.remove('active');
			menu_collapse.classList.remove('show');

			const current_active_menu = this.el.querySelector(`a[data-xmlid="${xmlid}"]`);
			current_active_menu.classList.add('active');
			const current_active_menu_id = Number(current_active_menu.dataset.id);

			const current_active_menu_data = this.menuService.getMenu(current_active_menu_id);
			const current_active_app_id = current_active_menu_data['appID'];
			const current_active_app_menu = this.el.querySelector(`a[data-menu="${current_active_app_id}"]`);
			const current_active_app_menu_collapse = this.el.querySelector(
				`div[id="menu-collapse-${current_active_app_id}"]`
			);

			current_active_app_menu.classList.add('active');
			current_active_app_menu_collapse.classList.add('show');
		}
	}

	onPatched() {
		// 在发生改变时执行，此方法在元素根据新状态重新渲染之前进行调用。
		if (this.state.focusedIndex !== null && !this.env.isSmall) {
			const selectedItem = document.querySelector('.o_sidenav_search_offcanvas_body .o_menuitem.o_focused');
			// 当 TAB 由外部管理时，class o_focused 消失。
			if (selectedItem) {
				// Center window on the focused item
				selectedItem.scrollIntoView({
					block: 'center'
				});
				selectedItem.focus();
			}
		}
		// this._updateScrollBarWidth();
	}
	onWillUnmount() {
		// console.log("mounted");
	}

	initializeMenu() {
		// 初始化菜单
		// let $app_menu = this.$el.find("a#menu-link-" + this.currentAppId);
		// $app_menu.addClass("active");
		if (this.currentMenuId) {
			let $menu = this.$el.find('a#menu-link-' + this.currentMenuId);
			$menu.addClass('active');
			if (!this.sidebarMinimize) {
				$menu.parents('.collapse').addClass('show');
			}
		}
	}

	//---------------------------------------------------------------------
	// Getters
	//---------------------------------------------------------------------
	/**
	 * @returns {(number|null)}
	 */
	get appIndex() {
		const appLength = this.displayedApps.length;
		const focusedIndex = this.state.focusedIndex;
		return focusedIndex < appLength ? focusedIndex : null;
	}

	/**
	 * @returns {Object[]}
	 */
	get displayedApps() {
		return this.availableApps;
	}

	/**
	 * @returns {number}
	 */
	get maxIconNumber() {
		const w = window.innerWidth;
		if (w < 576) {
			return 3;
		} else if (w < 768) {
			return 4;
		} else {
			return 6;
		}
	}

	/**
	 * @returns {(number|null)}
	 */
	get menuIndex() {
		const appLength = this.displayedApps.length;
		const focusedIndex = this.state.focusedIndex;
		return focusedIndex >= appLength ? focusedIndex - appLength : null;
	}

	//-----------------------------------------------
	// Private
	//-----------------------------------------------

	_toggleSideNav(ev) {
		ev.preventDefault();
		let $toggle_btn = $(ev.currentTarget);
		let $toggle_icon = $(ev.currentTarget).find('span.svg-icon');

		if (this.sidebarMinimize) {
			this.body.setAttribute('data-sidebar-minimize', 'off');
			this.$el.find('.accordion-collapse.show').removeClass('o_hidden');
			$toggle_icon.removeClass('active');
			$toggle_btn.attr('title', _t('Collapse sidebar menu'));
			this.sidebarMinimize = false;
		} else {
			this.body.setAttribute('data-sidebar-minimize', 'on');
			this.$el.find('.accordion-collapse.show').addClass('o_hidden');
			$toggle_icon.addClass('active');
			$toggle_btn.attr('title', _t('Expand the sidebar menu'));
			this.sidebarMinimize = true;
		}
	}
	_onMouseEnter(ev) {
		// 滑入侧边栏时，展开侧边栏
		ev.preventDefault();
		if (this.sidebarMinimize) {
			this.$el.addClass('sidebar-maximize');
			this.$el.find('.accordion-collapse.show').removeClass('o_hidden');

			let $menu = this.$el.find('a#menu-link-' + this.currentMenuId);
			$menu.parents('.collapse').addClass('show');
		}
	}

	_onMouseLeave(ev) {
		// 滑出侧边栏时，收起侧边栏
		ev.preventDefault();
		if (this.sidebarMinimize) {
			this.$el.removeClass('sidebar-maximize');
			this.$el.find('.accordion-collapse.show').addClass('o_hidden');
		}
	}

	//-----------------------------------------------
	// Handlers
	//-----------------------------------------------
	_openMenu(ev, menu) {
		let $menu = $(ev.currentTarget);
		this.$el.find('.accordion-button').removeClass('active');
		$menu.addClass('active');
		if (!$menu.hasClass('app')) {
			let $app_menu = this.$el.find('a#menu-link-' + menu.appID);
			$app_menu.addClass('active');
		}
		if (this.env.isSmall) {
			// 手机端，点击菜单时，隐藏
			const close_btn = this.el.querySelector('#o_sidenav_mobile_close');
			close_btn.click();
		}
		$menu.addClass('active');
		if (menu) {
			return this.menuService.selectMenu(menu);
		}
	}

	getMenuItemIcon(level) {
		// 获取应用下的子菜单图标
		// 5级子菜单的图标，应该够使用了，不够请自行添加
		let icon = '';
		switch (level) {
			case 1:
				icon = 'fa fa-circle';
				break;
			case 2:
				icon = 'fa fa-dot-circle-o';
				break;
			case 3:
				icon = 'fa fa-circle-o';
				break;
			case 4:
				icon = 'fa fa-square';
				break;
			case 5:
				icon = 'fa fa-square-o';
				break;
			default:
				icon = 'fa fa-square-o';
		}
		return icon;
	}

	getDefaultTheme(theme) {
		// 获取默认主题
		var self = this;
		var default_theme = {};

		// main
		if (self.hasKey('menu_layout_mode', theme)) {
			default_theme['menu_layout_mode'] = theme['menu_layout_mode'];
		} else {
			default_theme['menu_layout_mode'] = '1';
		}
		if (self.hasKey('main_submenu_position', theme)) {
			default_theme['main_submenu_position'] = theme['main_submenu_position'];
		} else {
			default_theme['main_submenu_position'] = '3';
		}

		// sidebar
		if (self.hasKey('sidebar_display_number_of_submenus', theme)) {
			default_theme['sidebar_display_number_of_submenus'] = theme['sidebar_display_number_of_submenus'];
		} else {
			default_theme['sidebar_display_number_of_submenus'] = true;
		}

		if (self.hasKey('sidebar_fixed', theme)) {
			default_theme['sidebar_fixed'] = theme['sidebar_fixed'];
		} else {
			default_theme['sidebar_fixed'] = true;
		}

		if (self.hasKey('sidebar_show_minimize_button', theme)) {
			default_theme['sidebar_show_minimize_button'] = theme['sidebar_show_minimize_button'];
		} else {
			default_theme['sidebar_show_minimize_button'] = false;
		}

		if (self.hasKey('sidebar_default_minimized', theme)) {
			default_theme['sidebar_default_minimized'] = theme['sidebar_default_minimized'];
		} else {
			default_theme['sidebar_default_minimized'] = false;
		}

		if (self.hasKey('sidebar_hover_maximize', theme)) {
			default_theme['sidebar_hover_maximize'] = theme['sidebar_hover_maximize'];
		} else {
			default_theme['sidebar_hover_maximize'] = false;
		}

		return default_theme;
	}

	hasKey(key, obj) {
		if (obj.hasOwnProperty(key)) {
			return true;
		} else {
			return false;
		}
	}

	_onAppClick(ev, app) {
		this._openMenu(ev, app);
	}
	_onMenuitemClick(ev, menu) {
		this._openMenu(ev, menu);
	}
}

SideNav.template = 'web_theme.SideNav';
SideNav.components = {};
