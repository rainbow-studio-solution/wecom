/** @odoo-module **/

import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { append, createElement } from "@web/core/utils/xml";
import spreadsheet from "@spreadsheet/o_spreadsheet/o_spreadsheet_extended";
/** @typedef {import("@spreadsheet/o_spreadsheet/o_spreadsheet").Model} Model */
const { onMounted, onPatched, onWillDestroy, useRef, useState, xml } = owl;
var VerticalScrollBar =
	spreadsheet.components.Grid.components.VerticalScrollBar;

patch(VerticalScrollBar.prototype, "spreadsheet.Grid.VerticalScrollBar", {
	setup() {
		this._super();
		this.max_offset = 300;
		this.theme = session.theme;
		this.displayScrollTopButton = this.theme["display_scroll_top_button"];

		const { scrollY, scrollX } =
			this.env.model.getters.getActiveSheetScrollInfo();
		this.state = useState({
			...this.state,
			offsetY: scrollY,
			showScrollButton: false,
		});

		onMounted(() => {
			// const rootEl = this.__owl__.bdom.parentEl;
			// const rootEl = $(this.__owl__.bdom.parentEl).parents(
			// 	".o_renderer"
			// )[0];
			// console.log(rootEl);
			// const scrollTopEl = this.makeScrollTopButton();
			// append(rootEl, scrollTopEl);
		});
		onPatched(() => {
			if (this.state.offsetY > this.max_offset) {
				this.state.showScrollButton = true;
			} else {
				this.state.showScrollButton = false;
			}
			console.log(
				"onPatched",
				this.state.offsetY,
				this.state.showScrollButton
			);
		});
	},
	onScroll(offset) {
		this._super(...arguments);

		const { scrollY, scrollX } =
			this.env.model.getters.getActiveSheetScrollInfo();
		this.state.offsetY = scrollY;
		// console.log("onScroll", offset, offsetScrollbarY);
	},
	makeScrollTopButton() {
		let scrollTopIconRect = createElement("rect");
		scrollTopIconRect.setAttribute("opacity", "0.5");
		scrollTopIconRect.setAttribute("x", "13");
		scrollTopIconRect.setAttribute("y", "6");
		scrollTopIconRect.setAttribute("width", "13");
		scrollTopIconRect.setAttribute("height", "2");
		scrollTopIconRect.setAttribute("rx", "1");
		scrollTopIconRect.setAttribute("transform", "rotate(90 13 6)");
		scrollTopIconRect.setAttribute("fill", "currentColor");

		let scrollTopIconPath = createElement("path");
		scrollTopIconPath.setAttribute(
			"d",
			"M12.5657 8.56569L16.75 12.75C17.1642 13.1642 17.8358 13.1642 18.25 12.75C18.6642 12.3358 18.6642 11.6642 18.25 11.25L12.7071 5.70711C12.3166 5.31658 11.6834 5.31658 11.2929 5.70711L5.75 11.25C5.33579 11.6642 5.33579 12.3358 5.75 12.75C6.16421 13.1642 6.83579 13.1642 7.25 12.75L11.4343 8.56569C11.7467 8.25327 12.2533 8.25327 12.5657 8.56569Z"
		);
		scrollTopIconPath.setAttribute("fill", "currentColor");

		let scrollTopIcon = createElement("svg");
		scrollTopIcon.setAttribute("width", "24");
		scrollTopIcon.setAttribute("height", "24");
		scrollTopIcon.setAttribute("viewBox", "0 0 24 24");
		scrollTopIcon.setAttribute("fill", "none");
		scrollTopIcon.setAttribute("xmlns", "http://www.w3.org/2000/svg");

		append(scrollTopIcon, scrollTopIconRect);
		append(scrollTopIcon, scrollTopIconPath);

		let scrollTopSpan = createElement("span");
		scrollTopSpan.className = "svg-icon";

		append(scrollTopSpan, scrollTopIcon);

		let scrollTopEl = createElement("div");
		scrollTopEl.className = "o_scroll_top o_hidden position-fixed";
		// scrollTopEl.setAttribute(
		// 	"t-on-click.stop",
		// 	"(ev) => this.onClickScrollToTop(ev)"
		// );
		append(scrollTopEl, scrollTopSpan);
		return scrollTopEl;
	},
});
