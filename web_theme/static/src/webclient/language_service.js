/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

export const languageService = {
	dependencies: ["user", "router", "cookie"],
	start(env, { user, router, cookie }) {
		const availableLanguages = session.langs;
		const currentLanguage = session.current_lang;

		return {
			availableLanguages,
			get allLanguages() {
				return availableLanguages;
			},
			get currentLanguage() {
				return currentLanguage;
			},
		};
	},
};

registry.category("services").add("language", languageService);
