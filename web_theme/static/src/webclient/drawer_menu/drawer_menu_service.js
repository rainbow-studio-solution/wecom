/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Mutex } from "@web/core/utils/concurrency";
import { useService } from "@web/core/utils/hooks";
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { ControllerNotFoundError } from "@web/webclient/actions/action_service";
import { DrawerMenu } from "./drawer_menu";

import { Component, onMounted, onWillUnmount, xml } from "@odoo/owl";

export const drawerMenuService = {
	dependencies: ["action", "router"],
	start(env) {
		let hasDrawerMenu = false; // true iff the DrawerMenu is currently displayed
		let hasBackgroundAction = false; // true iff there is an action behind the DrawerMenu
		const mutex = new Mutex(); // used to protect against concurrent toggling requests

		class DrawerMenuAction extends Component {
			setup() {
				this.router = useService("router");
				this.menus = useService("menu");
				this.DrawerMenuProps = {
					apps: computeAppsAndMenuItems(
						this.menus.getMenuAsTree("root")
					).apps,
				};
				onMounted(() => this.onMounted());
				onWillUnmount(this.onWillUnmount);
			}
			async onMounted() {
				const { breadcrumbs } = this.env.config;
				hasDrawerMenu = true;
				hasBackgroundAction = breadcrumbs.length > 0;
				this.router.pushState(
					{ menu_id: undefined },
					{ lock: false, replace: true }
				);
				this.env.bus.trigger("DRAWER-MENU:TOGGLED");
			}
			onWillUnmount() {
				hasDrawerMenu = false;
				hasBackgroundAction = false;
				const currentMenuId = this.menus.getCurrentApp();
				if (currentMenuId) {
					this.router.pushState(
						{ menu_id: currentMenuId.id },
						{ lock: true }
					);
				}
				this.env.bus.trigger("DRAWER-MENU:TOGGLED");
			}
		}
		DrawerMenuAction.components = { DrawerMenu };
		DrawerMenuAction.target = "current";
		DrawerMenuAction.template = xml`<DrawerMenu t-props="DrawerMenuProps"/>`;

		registry.category("actions").add("menu", DrawerMenuAction);

		env.bus.on("DRAWER-MENU:TOGGLED", null, () => {
			document.body.classList.toggle(
				"o_home_menu_background",
				hasDrawerMenu
			);
		});

		return {
			get hasDrawerMenu() {
				return hasDrawerMenu;
			},
			get hasBackgroundAction() {
				return hasBackgroundAction;
			},
			async toggle(show) {
				return mutex.exec(async () => {
					show = show === undefined ? !hasDrawerMenu : Boolean(show);
					if (show !== hasDrawerMenu) {
						if (show) {
							await env.services.action.doAction("menu");
						} else {
							try {
								await env.services.action.restore();
							} catch (err) {
								if (!(err instanceof ControllerNotFoundError)) {
									throw err;
								}
							}
						}
					}
					// hack: wait for a tick to ensure that the url has been updated before
					// switching again
					return new Promise((r) => setTimeout(r));
				});
			},
		};
	},
};

registry.category("services").add("drawer_menu", drawerMenuService);
