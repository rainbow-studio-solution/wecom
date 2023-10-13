/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

export const legacyServiceProvider = {
	dependencies: ["drawer_menu"],
	start({ services }) {
		browser.addEventListener("show-drawer-menu", () => {
			services.drawer_menu.toggle(true);
		});
	},
};

registry
	.category("services")
	.add("plus_legacy_service_provider", legacyServiceProvider);
