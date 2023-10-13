/** @odoo-module **/

import { session } from '@web/session';
import { ActionContainer } from '@web/webclient/actions/action_container';
import { Footer } from '../footer/footer';
import { useService } from '@web/core/utils/hooks';
import {
	onMounted,
	onWillUnmount,
	onPatched,
	onWillDestroy,
	useExternalListener,
	useRef,
	useEffect,
	useState,
	Component
} from '@odoo/owl';

export class iErpActionContainer extends ActionContainer {
	setup() {
		super.setup();

		this.menuService = useService('menu');
		this.actionService = useService('action');
		this.title = useService('title');
		this.router = useService('router');

		this.theme = session.theme;
		this.open_action_in_tabs = this.theme['main_open_action_in_tabs'];
		this.state = useState({
			...this.state,
			activeTabId: 0,
			activeTabName: '',
			tabs: []
		});
		this.tabs = [];

		onMounted(() => {
			this.setTabPage();
		});
		onPatched(() => {
			// console.log(this.state);
		});

		//参考 _getActionInfo
	}

	setTabPage() {
		let menuId = Number(this.router.current.hash.menu_id || 0);
		let hasTab = false;
		_.forEach(this.state.tabs, (tab) => {
			if (tab.actionID === menuId) {
				hasTab = true;
			}
		});
		console.log(menuId, hasTab);
		if (menuId && !hasTab) {
			console.log('menuId', menuId);
			console.log('menu', this.menuService.getMenu(menuId));
			let tab = this.menuService.getMenu(menuId);
			this.state.tabs.push(tab);
		} else if (menuId && hasTab) {
			console.log('已存在');
		} else if (!menuId) {
			const currentController = this.actionService.currentController;
			console.log('不已存在 menuId', currentController);
			const actionId = currentController && currentController.action.id;
			const menu = this.menuService.getAll().find((m) => m.actionID === actionId);
			console.log('不已存在 menuId', menu);
		}
	}
}
iErpActionContainer.components = {
	...ActionContainer.components,
	Footer
};
iErpActionContainer.template = 'web_theme.ActionContainer';
