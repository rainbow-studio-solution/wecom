/** @odoo-module **/

import { NavBar } from '@web/webclient/navbar/navbar';
import { useService, useBus } from '@web/core/utils/hooks';
import { session } from '@web/session';
import { useEffect, useRef } from '@odoo/owl';

export class iErpNavBar extends NavBar {
	setup() {
		super.setup();
		this.dm = useService('drawer_menu');
		this.menuAppsRef = useRef('menuApps');
		this.navRef = useRef('nav');

		// 主题
		this.theme = session.theme;
		this.menu_layout_mode = this.theme['menu_layout_mode'];
		this.main_submenu_position = this.theme['main_submenu_position'];
		// console.log("iErpNavBar", this.menu_layout_mode);

		useBus(this.env.bus, 'DRAWER-MENU:TOGGLED', () => this._updateMenuAppsIcon());
		useEffect(() => this._updateMenuAppsIcon());
	}
	get hasBackgroundAction() {
		return this.dm.hasBackgroundAction;
	}
	get isInApp() {
		return !this.dm.hasDrawerMenu;
	}
	_updateMenuAppsIcon() {
		if (this.menu_layout_mode === 3) {
			const menuAppsEl = this.menuAppsRef.el;
			menuAppsEl.classList.toggle('o_hidden', !this.isInApp && !this.hasBackgroundAction);
			menuAppsEl.classList.toggle('o_menu_toggle_back', !this.isInApp && this.hasBackgroundAction);
			const { _t } = this.env;
			const title = !this.isInApp && this.hasBackgroundAction ? _t('Previous view') : _t('Drawer menu');
			menuAppsEl.title = title;
			menuAppsEl.ariaLabel = title;

			const menuBrand = this.navRef.el.querySelector('.o_menu_brand');
			if (menuBrand) {
				menuBrand.classList.toggle('o_hidden', !this.isInApp);
			}

			const appSubMenus = this.appSubMenus.el;
			if (appSubMenus) {
				appSubMenus.classList.toggle('o_hidden', !this.isInApp);
			}
		}
	}
}
iErpNavBar.template = 'web_theme.iErpNavBar';
