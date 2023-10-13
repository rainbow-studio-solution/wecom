/** @odoo-module **/
import { browser } from "@web/core/browser/browser";

import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "web.core";
import { getCookie, setCookie } from "web.utils.cookies";

const {
	useEffect,
	Component,
	onWillStart,
	onMounted,
	onWillPatch,
	onPatched,
	useState,
	useRef,
} = owl;

export class ThemeConfigPage extends Component {
	setup() {
		// this.themeConfigPanel = useRef("ThemeConfigPanel");
		// this.themeConfigPanelBackdrop = useRef("ThemeConfigPanelBackdrop");

		this.user = useService("user");
		this.rpc = useService("rpc");
		this.orm = useService("orm");
		this.notification = useService("notification");
		this.cookieServices = useService("cookie");
		this.uiService = useService("ui");

		this.theme = session.theme;
		// this.theme.is_dark_mode = this.cookieServices.current.color_scheme === "dark" ? true : false;
		console.log("this.theme", this.theme);
		this.default_theme = this.getDefaultTheme(this.theme);
		this.new_theme = this.getDefaultTheme(this.theme);

		this.state = useState({
			theme_has_changed: false,
			// 1.main
			is_dark_mode:
				this.cookieServices.current.color_scheme === "dark"
					? true
					: false,

			main_open_action_in_tabs:
				this.default_theme["main_open_action_in_tabs"],
			current_submenu_position:
				this.default_theme["main_submenu_position"],
			// 2.layout
			current_layout_mode: this.default_theme["menu_layout_mode"],
			// 3.color
			current_theme_color: this.default_theme["theme_color"],
			// 4.sidebar
			sidebar_display_number_of_submenus:
				this.default_theme["sidebar_display_number_of_submenus"],
			sidebar_fixed: this.default_theme["sidebar_fixed"],
			sidebar_show_minimize_button:
				this.default_theme["sidebar_show_minimize_button"],
			sidebar_default_minimized:
				this.default_theme["sidebar_default_minimized"],
			sidebar_hover_maximize:
				this.default_theme["sidebar_hover_maximize"],
			// 5.header
			// 6.views
			display_scroll_top_button:
				this.default_theme["display_scroll_top_button"],
			list_herder_fixed: this.default_theme["list_herder_fixed"],
			list_rows_limit: this.default_theme["list_rows_limit"],
			current_chatter_position:
				this.default_theme["form_chatter_position"],
			// 7.footer
			display_footer: this.default_theme["display_footer"],
			display_footer_document:
				this.default_theme["display_footer_document"],
			display_footer_support:
				this.default_theme["display_footer_support"],
		});

		// 1.main
		this.main_submenu_position =
			this.default_theme["main_submenu_position"];
		this.main_submenu_positions = this.theme["main_submenu_positions"];

		// 2.layout
		this.menu_layout_mode = this.default_theme["menu_layout_mode"];
		this.menu_layout_modes = this.theme["menu_layout_modes"];

		// 3.Theme color
		this.theme_color = this.default_theme["theme_color"];
		this.theme_colors = this.theme["theme_colors"];

		// 4.SideNavbar
		this.sidebar_display_number_of_submenus =
			this.default_theme["sidebar_display_number_of_submenus"];
		this.sidebar_fixed = this.default_theme["sidebar_fixed"];
		this.sidebar_show_minimize_button =
			this.default_theme["sidebar_show_minimize_button"];
		this.sidebar_default_minimized =
			this.default_theme["sidebar_default_minimized"];
		this.sidebar_hover_maximize =
			this.default_theme["sidebar_hover_maximize"];

		// 6.Views
		this.display_scroll_top_button =
			this.default_theme["display_scroll_top_button"];
		this.list_herder_fixed = this.default_theme["list_herder_fixed"];
		this.list_rows_limit = this.default_theme["list_rows_limit"];
		this.list_rows_limits = this.theme["list_rows_limits"];
		this.form_chatter_position =
			this.default_theme["form_chatter_position"];
		this.form_chatter_positions = this.theme["form_chatter_positions"];

		onMounted(() => {
			if (
				JSON.stringify(this.new_theme) ==
				JSON.stringify(this.default_theme)
			) {
				// console.log("未变化");
				this.state.theme_has_changed = false;
			} else {
				// console.log("已变化");
				this.state.theme_has_changed = true;
			}
		});
		onPatched(() => {
			// console.log("onPatched-theme", this.new_theme, this.default_theme);
			if (
				JSON.stringify(this.new_theme) ==
				JSON.stringify(this.default_theme)
			) {
				// console.log("未变化");
				this.state.theme_has_changed = false;
			} else {
				// console.log("已变化");
				this.state.theme_has_changed = true;
			}
		});
	}

	// 1.main
	onToggleDarkMode(isDark) {
		this.state.is_dark_mode = !isDark;

		let scheme = "light";
		if (this.state.is_dark_mode) {
			scheme = "dark";
		}
		setCookie("color_scheme", scheme);
		this.uiService.block();
		browser.location.reload();
	}

	onToggleMainOpenActionInTabs(state) {
		this.state.main_open_action_in_tabs = !state;
		this.new_theme["main_open_action_in_tabs"] = !state;
	}

	onChangeSubmenuPosition(mode) {
		if (mode.id != this.state.current_submenu_position) {
			this.state.current_submenu_position = mode.id;
			this.new_theme["main_submenu_position"] = mode.id;
		}
	}

	// 2.layout
	onChangeLayoutMode(mode) {
		if (mode.id != this.state.current_layout_mode) {
			this.state.current_layout_mode = mode.id;
			this.new_theme["menu_layout_mode"] = mode.id;
		}
	}

	// 3.color
	onClickThemeColor(color) {
		if (color.code != this.state.current_theme_color) {
			this.state.current_theme_color = color.code;
			this.new_theme["theme_color"] = color.code;
		}
	}
	// 4.sidebar
	onToggleSidebarDisplayNumberOfSubmenus(state) {
		this.state.sidebar_display_number_of_submenus = !state;
		this.new_theme["sidebar_display_number_of_submenus"] = !state;
	}
	onToggleSidebarFixed(state) {
		this.state.sidebar_fixed = !state;
		this.new_theme["sidebar_fixed"] = !state;
	}
	onToggleSidebarShowMinimizeButton(state) {
		this.state.sidebar_show_minimize_button = !state;
		this.new_theme["sidebar_show_minimize_button"] = !state;
	}
	onToggleSidebarDefaultMinimizedn(state) {
		this.state.sidebar_default_minimized = !state;
		this.new_theme["sidebar_default_minimized"] = !state;
	}
	onToggleSidebarHoverMaximize(state) {
		this.state.sidebar_hover_maximize = !state;
		this.new_theme["sidebar_hover_maximize"] = !state;
	}

	// 5.header

	// 6.views
	onToggleDisplayScrollTopButton(state) {
		this.state.display_scroll_top_button = !state;
		this.new_theme["display_scroll_top_button"] = !state;
	}
	onToggleListHerderFixed(state) {
		this.state.list_herder_fixed = !state;
		// console.log("onToggleListHerderFixed", ev.target.checked);
		this.new_theme["list_herder_fixed"] = !state;
	}
	onChangeListRowsLimit(ev) {
		// console.log(ev.target.value);
		this.state.list_rows_limit = ev.target.value;
		this.new_theme["list_rows_limit"] = ev.target.value;
	}
	onChangeChatterPosition(position) {
		if (position.id != this.state.current_chatter_position) {
			this.state.current_chatter_position = position.id;
			this.new_theme["form_chatter_position"] = position.id;
		}
	}

	// 7.Footer
	onToggleDisplayFooter(state) {
		this.state.display_footer = !state;
		this.new_theme["display_footer"] = !state;
	}
	onToggleDisplayFooterDocument(state) {
		this.state.display_footer_document = !state;
		this.new_theme["display_footer_document"] = !state;
	}
	onToggleDisplayFooterSupport(state) {
		this.state.display_footer_support = !state;
		this.new_theme["display_footer_support"] = !state;
	}

	closeThemePanel() {
		this.state.current_layout_mode = this.default_theme["menu_layout_mode"];
		this.state.theme_has_changed = false;
		this.new_theme = this.default_theme;
	}

	setThemeItem(ev) {
		var self = this;
		const tagName = $(ev.currentTarget).prop("tagName");
		const id = $(ev.currentTarget).prop("id");

		let new_theme = this.getDefaultTheme(this.theme);
		if (this.new_theme) {
			new_theme = this.new_theme;
		}

		if (tagName == "SELECT") {
			const selected_val = $(ev.currentTarget)
				.children("option:selected")
				.val();
			this.change_select(selected_val, $(ev.currentTarget));
			new_theme[id] = selected_val;
		} else if (tagName == "INPUT") {
			const isCheck = $(ev.currentTarget).prop("checked");
			if (isCheck) {
				// 处理互斥
				if (id == "sidebar_fixed") {
					$("input#sidebar_default_minimized").prop("checked", false);
					new_theme["sidebar_default_minimized"] = false;
				}
				if (id == "sidebar_default_minimized") {
					$("input#sidebar_fixed").prop("checked", false);
					new_theme["sidebar_fixed"] = false;
				}
			}
			new_theme[id] = isCheck;
		}

		this.new_theme = new_theme;
		self.setDefaultTheme();
	}

	setDefaultTheme() {
		var self = this;
		this.footerEL = this.el.querySelector("#o_theme_panel_footer");
		//比较主题的值是否发生变化
		if (
			JSON.stringify(self.new_theme) == JSON.stringify(self.default_theme)
		) {
			this.footerEL.classList.add("o_hidden");
		} else {
			this.footerEL.classList.remove("o_hidden");
		}

		this.body = document.body;
		this.body.setAttribute(
			"data-menu-mode",
			self.new_theme.menu_layout_mode
		);
		this.body.setAttribute(
			"data-sidebar-fixed",
			self.new_theme.sidebar_fixed
		);
		this.body.setAttribute(
			"data-sidebar-default-minimized",
			self.new_theme.sidebar_default_minimized
		);
		this.body.setAttribute(
			"data-sidebar-hover-maximize",
			self.new_theme.sidebar_hover_maximize
		);
	}

	async saveTheme() {
		var self = this;
		const result = await this.orm.call("res.users", "set_user_theme", [
			session.uid,
			self.new_theme,
		]);

		if (result) {
			this.default_theme = this.new_theme;
			// this.backdropEL.classList.add("o_hidden"); //隐藏遮罩
			// this.themePanel.classList.remove("show"); //隐藏主题设置面板

			const title = result["title"];
			const message = result["message"];
			if (result["state"]) {
				this.notification.add(message, {
					title: title,
					type: "success",
					sticky: true,
					buttons: [
						{
							name: _t("Refresh"),
							onClick: () => {
								browser.location.reload();
								this.env.bus.trigger("CLEAR-CACHES");
							},
							primary: true,
						},
					],
				});
			} else {
				this.notification.add(message, {
					title: title,
					type: "warning",
					sticky: false,
				});
			}
		}
	}

	getDefaultTheme(theme) {
		// 获取默认主题
		var self = this;
		var default_theme = {};

		// 1.main
		if (self.hasKey("main_open_action_in_tabs", theme)) {
			default_theme["main_open_action_in_tabs"] =
				theme["main_open_action_in_tabs"];
		} else {
			default_theme["main_open_action_in_tabs"] = 1;
		}
		if (self.hasKey("main_submenu_position", theme)) {
			default_theme["main_submenu_position"] =
				theme["main_submenu_position"];
		} else {
			default_theme["main_submenu_position"] = "3";
		}

		// 2.layout
		if (self.hasKey("menu_layout_mode", theme)) {
			default_theme["menu_layout_mode"] = theme["menu_layout_mode"];
		} else {
			default_theme["menu_layout_mode"] = 1;
		}

		// 3.Theme color
		if (self.hasKey("theme_color", theme)) {
			default_theme["theme_color"] = theme["theme_color"];
		} else {
			default_theme["theme_color"] = "default";
		}

		// 6. sidebar
		if (self.hasKey("sidebar_display_number_of_submenus", theme)) {
			default_theme["sidebar_display_number_of_submenus"] =
				theme["sidebar_display_number_of_submenus"];
		} else {
			default_theme["sidebar_display_number_of_submenus"] = true;
		}

		if (self.hasKey("sidebar_fixed", theme)) {
			default_theme["sidebar_fixed"] = theme["sidebar_fixed"];
		} else {
			default_theme["sidebar_fixed"] = true;
		}

		if (self.hasKey("sidebar_show_minimize_button", theme)) {
			default_theme["sidebar_show_minimize_button"] =
				theme["sidebar_show_minimize_button"];
		} else {
			default_theme["sidebar_show_minimize_button"] = false;
		}

		if (self.hasKey("sidebar_default_minimized", theme)) {
			default_theme["sidebar_default_minimized"] =
				theme["sidebar_default_minimized"];
		} else {
			default_theme["sidebar_default_minimized"] = false;
		}

		if (self.hasKey("sidebar_hover_maximize", theme)) {
			default_theme["sidebar_hover_maximize"] =
				theme["sidebar_hover_maximize"];
		} else {
			default_theme["sidebar_hover_maximize"] = false;
		}

		// 6.VIEWS
		if (self.hasKey("display_scroll_top_button", theme)) {
			default_theme["display_scroll_top_button"] =
				theme["display_scroll_top_button"];
		} else {
			default_theme["display_scroll_top_button"] = true;
		}

		if (self.hasKey("list_herder_fixed", theme)) {
			default_theme["list_herder_fixed"] = theme["list_herder_fixed"];
		} else {
			default_theme["list_herder_fixed"] = false;
		}

		if (self.hasKey("list_rows_limit", theme)) {
			default_theme["list_rows_limit"] = theme["list_rows_limit"];
		} else {
			default_theme["list_rows_limit"] = 80;
		}

		if (self.hasKey("form_chatter_position", theme)) {
			default_theme["form_chatter_position"] =
				theme["form_chatter_position"];
		} else {
			default_theme["form_chatter_position"] = 1;
		}

		// 7.Footer
		if (self.hasKey("display_footer", theme)) {
			default_theme["display_footer"] = theme["display_footer"];
		} else {
			default_theme["display_footer"] = true;
		}
		if (self.hasKey("display_footer_document", theme)) {
			default_theme["display_footer_document"] =
				theme["display_footer_document"];
		} else {
			default_theme["display_footer_document"] = true;
		}
		if (self.hasKey("display_footer_support", theme)) {
			default_theme["display_footer_support"] =
				theme["display_footer_support"];
		} else {
			default_theme["display_footer_support"] = true;
		}

		return default_theme;
	}
	change_select(value, select) {
		select.children("option").each(function (index, element) {
			$(element).removeAttr("selected");
			if ($(element)[0].value == value) {
				$(element).attr("selected", "selected");
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

ThemeConfigPage.template = "web.ThemeConfigPanel";
