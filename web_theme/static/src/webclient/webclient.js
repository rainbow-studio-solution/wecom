/** @odoo-module **/

import { WebClient } from '@web/webclient/webclient';
import { useService } from '@web/core/utils/hooks';
import { session } from '@web/session';

import { SideNav } from './sidenav/sidenav';
import { iErpNavBar } from './navbar/navbar';
import { iErpActionContainer } from './actions/action_container';

const legacy_session = require('web.session'); // 需要访问allowed_company_ids，故使用 legacy 的代码，不能使用 @web/session
const { Component, onMounted, onPatched, useExternalListener, useState, useEffect } = owl;

export class iErpWebClient extends WebClient {
	setup() {
		super.setup();
		this.dm = useService('drawer_menu');
		useService('plus_legacy_service_provider');

		// 主题
		this.theme = legacy_session.theme;

		this.menu_layout_mode = this.theme['menu_layout_mode']; // 全局主菜单模式
		this.sidebar_fixed = this.theme['sidebar_fixed']; // 侧边栏固定
		this.sidebar_default_minimized = this.theme['sidebar_default_minimized']; // 侧边栏默认折叠
		this.sidebar_hover_maximize = this.theme['sidebar_hover_maximize']; // 侧边栏悬停展开

		this.sidebarMinimize = false;
		if (!this.sidebar_fixed || this.sidebar_default_minimized) {
			this.sidebarMinimize = true;
		}

		this.chatter_position = this.theme['form_chatter_position'];

		let system_name = legacy_session.system_name;
		let current_cid = legacy_session.user_context.allowed_company_ids[0]; //当前公司id

		if (legacy_session.display_company_name) {
			let allowed_companies = legacy_session.user_companies.allowed_companies;
			let current_company_name = getCurrentCompanyName(); //当前公司名称
			function getCurrentCompanyName() {
				for (var key in allowed_companies) {
					let company = allowed_companies[key];
					if (company.id === current_cid) {
						return company.name;
					}
				}
			}
			system_name = _.str.sprintf('%s - %s', current_company_name, system_name);
		}

		this.title.setParts({
			zopenerp: system_name
		});

		onMounted(() => {
			// 定义挂载组件时应该执行的代码的钩子

			// super.onMounted();
			// 设置body data
			this.el = document.body;
			// 使用 dataset 操作data要比使用getAttribute稍微慢些.
			this.el.setAttribute('data-menu-mode', this.menu_layout_mode);
			this.el.setAttribute('data-sidebar-fixed', this.sidebar_fixed);
			this.el.setAttribute('data-sidebar-default-minimized', this.sidebar_default_minimized);
			this.el.setAttribute('data-sidebar-hover-maximize', this.sidebar_hover_maximize);

			if (this.sidebarMinimize) {
				this.el.setAttribute('data-sidebar-minimize', 'on');
			} else {
				this.el.setAttribute('data-sidebar-minimize', 'off');
			}

			if (this.chatter_position === 2) {
				this.el.setAttribute('data-chatter-position', 'wrap');
			}
		});
	}

	_loadDefaultApp() {
		super._loadDefaultApp();
		if (this.menu_layout_mode === 3) {
			return this.dm.toggle(true);
		}
	}
}
iErpWebClient.components = {
	...WebClient.components,
	ActionContainer: iErpActionContainer,
	NavBar: iErpNavBar,
	SideNav
};
iErpWebClient.template = 'web_theme.WebClient';
