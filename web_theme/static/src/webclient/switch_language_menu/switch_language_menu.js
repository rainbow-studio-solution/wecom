/** @odoo-module **/

import { session } from "@web/session";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

import { Component, useState } from "@odoo/owl";

export class SwitchLanguageMenu extends Component {
	setup() {
		this.languageService = useService("language");
		this.user = useService("user");
		this.rpc = useService("rpc");
		this.actionService = useService("action");
		this.state = useState({ languagesToToggle: [] });

		this.allLanguages = this.languageService.allLanguages;
		this.currentLanguage = this.languageService.currentLanguage;
	}
	// mounted() {
	// 	super.mounted();
	// 	// 在元素渲染、DOM添加之后调用。
	// }
	async toggleLanguage(lang) {
		if (lang.id == this.currentLanguage.id) {
			return;
		} else {
			const result = await this.rpc("/web/lang/toggle", {
				context: this.user.context,
				lang: lang,
			});
			if (result) {
				browser.location.reload();
			}
		}
	}
}

SwitchLanguageMenu.template = "SwitchLanguageMenu";
SwitchLanguageMenu.components = { Dropdown, DropdownItem };
SwitchLanguageMenu.toggleDelay = 1000;

export const systrayItem = {
	Component: SwitchLanguageMenu,
	isDisplayed(env) {
		const { availableLanguages } = env.services.language;
		if (availableLanguages.length > 1 && !env.isSmall) {
			return true;
		} else {
			return false;
		}
	},
};

registry.category("systray").add("SwitchLanguageMenu", systrayItem, {
	sequence: 1,
});
