/** @odoo-module **/
import { browser } from '@web/core/browser/browser';
import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { session } from '@web/session';
import { _t } from 'web.core';

import { ThemeConfigPage } from './theme_panel';

const { useEffect, Component, onMounted, hooks, useState } = owl;

export class ThemeConfigMenu extends Component {
	setup() {
		super.setup();

		this.user = useService('user');
		this.rpc = useService('rpc');
		this.orm = useService('orm');
		this.notification = useService('notification');
		this.theme = session.theme;

		this.default_theme = this.getDefaultTheme(this.theme);

		this.menu_layout_mode = this.default_theme['menu_layout_mode'];
		this.menu_layout_modes = this.default_theme['menu_layout_modes'];

		this.state = useState({
			isopen: false
		});

		this.main_submenu_position = this.default_theme['main_submenu_position'];
		this.sidebar_display_number_of_submenus = this.default_theme['sidebar_display_number_of_submenus'];
		this.sidebar_fixed = this.default_theme['sidebar_fixed'];
		this.sidebar_show_minimize_button = this.default_theme['sidebar_show_minimize_button'];
		this.sidebar_default_minimized = this.default_theme['sidebar_default_minimized'];
		this.sidebar_hover_maximize = this.default_theme['sidebar_hover_maximize'];

		onMounted(() => {
			this.onMounted();
		});
		useEffect(() => this.useEffect());
	}

	constructor() {
		super(...arguments);
	}

	onMounted() {}
	useEffect() {}

	// -------------------------------------------------------------------------
	// Handlers
	// -------------------------------------------------------------------------
	openThemePanel() {
		this.state.isopen = true;
		// console.log("openThemePanel", this.state.isopen);
	}

	closeThemePanel() {
		this.state.isopen = false;
		// console.log("closeThemePanel", this.state.isopen);
	}

	// initThemePanel() {
	//     var self = this;
	//     var $panel = $(this.el).find('.o_theme_panel_body');
	//     var new_default_theme = this.getDefaultTheme(this.theme);
	// }

	setThemeItem(ev) {
		var self = this;
		const tagName = $(ev.currentTarget).prop('tagName');
		const id = $(ev.currentTarget).prop('id');

		let new_theme = this.getDefaultTheme(this.theme);
		if (this.new_theme) {
			new_theme = this.new_theme;
		}

		if (tagName == 'SELECT') {
			const selected_val = $(ev.currentTarget).children('option:selected').val();
			this.change_select(selected_val, $(ev.currentTarget));
			new_theme[id] = selected_val;
		} else if (tagName == 'INPUT') {
			const isCheck = $(ev.currentTarget).prop('checked');
			if (isCheck) {
				// 处理互斥
				if (id == 'sidebar_fixed') {
					$('input#sidebar_default_minimized').prop('checked', false);
					new_theme['sidebar_default_minimized'] = false;
				}
				if (id == 'sidebar_default_minimized') {
					$('input#sidebar_fixed').prop('checked', false);
					new_theme['sidebar_fixed'] = false;
				}
			}
			new_theme[id] = isCheck;
		}

		this.new_theme = new_theme;
		self.setDefaultTheme();
	}

	setDefaultTheme() {
		var self = this;
		this.footerEL = this.el.querySelector('#o_theme_panel_footer');
		//比较主题的值是否发生变化
		if (JSON.stringify(self.new_theme) == JSON.stringify(self.default_theme)) {
			this.footerEL.classList.add('o_hidden');
		} else {
			this.footerEL.classList.remove('o_hidden');
		}

		this.body = document.body;
		this.body.setAttribute('data-menu-mode', self.new_theme.menu_layout_mode);
		this.body.setAttribute('data-sidebar-fixed', self.new_theme.sidebar_fixed);
		this.body.setAttribute('data-sidebar-default-minimized', self.new_theme.sidebar_default_minimized);
		this.body.setAttribute('data-sidebar-hover-maximize', self.new_theme.sidebar_hover_maximize);
	}

	async saveTheme() {
		var self = this;
		const result = await this.orm.call('res.users', 'set_user_theme', [session.uid, self.new_theme]);

		if (result) {
			this.default_theme = this.new_theme;
			// this.backdropEL.classList.add("o_hidden"); //隐藏遮罩
			// this.themePanel.classList.remove("show"); //隐藏主题设置面板

			const title = result['title'];
			const message = result['message'];
			if (result['state']) {
				this.notification.add(message, {
					title: title,
					type: 'success',
					sticky: true,
					buttons: [
						{
							name: _t('Refresh'),
							onClick: () => {
								browser.location.reload();
								this.env.bus.trigger('CLEAR-CACHES');
							},
							primary: true
						}
					]
				});
			} else {
				this.notification.add(message, {
					title: title,
					type: 'warning',
					sticky: false
				});
			}
		}
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
		if (self.hasKey('menu_layout_modes', theme)) {
			default_theme['menu_layout_modes'] = theme['menu_layout_modes'];
		} else {
			default_theme['menu_layout_modes'] = [
				{
					id: '1',
					name: '侧边栏',
					icon: 'bi-window-sidebar'
				},
				{
					id: '2',
					name: 'Favorites',
					icon: 'bi-layout-text-window-reverse'
				},
				{
					id: '3',
					name: 'Drawer',
					icon: 'bi-window-dock'
				}
			];
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
	change_select(value, select) {
		select.children('option').each(function (index, element) {
			$(element).removeAttr('selected');
			if ($(element)[0].value == value) {
				$(element).attr('selected', 'selected');
			}
		});
	}
	hasKey(key, obj) {
		if (obj.hasOwnProperty(key)) {
			return true;
		} else {
			return false;
		}
	}
}

ThemeConfigMenu.template = 'web_theme.ThemeConfigMenu';
ThemeConfigMenu.components = {
	ThemeConfigPage
};

export const systrayItem = {
	Component: ThemeConfigMenu,
	isDisplayed(env) {
		const disable_customization = session.theme.disable_customization;
		return !disable_customization;
	}
};

registry.category('systray').add('ThemeConfigMenu', systrayItem, {
	sequence: -1
});
