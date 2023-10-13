/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { FormCompiler } from "@web/views/form/form_compiler";
import { MailFormCompiler } from "@mail/views/form/form_controller";
import { ViewCompiler, getModifier } from "@web/views/view_compiler";
import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { SIZES } from "@web/core/ui/ui_service";
import {
	append,
	setAttributes,
	combineAttributes,
	createElement,
	createTextNode,
	getTag,
} from "@web/core/utils/xml";
import { localization } from "@web/core/l10n/localization";

patch(FormCompiler.prototype, "wep_plus", {
	setup() {
		this._super();
		this.uiService = useService("ui");
		this.theme = session.theme;
		this.displayScrollTopButton = this.theme["display_scroll_top_button"];
		this.scrollBarOffset = 300;
	},
	compile(node, params) {
		// TODO no chatter if in dialog?

		let WRAP = false;
		if (
			session.theme["form_chatter_position"] === 2 ||
			this.uiService.size < SIZES.XXL
		) {
			WRAP = true;
		}

		const res = this._super(node, params);
		const chatterContainerHookXml = res.querySelector(
			".o_FormRenderer_chatterContainer"
		);
		if (!chatterContainerHookXml) {
			return res; // no chatter, keep the result as it is
		}
		const chatterContainerXml =
			chatterContainerHookXml.querySelector("ChatterContainer");
		setAttributes(chatterContainerXml, {
			hasExternalBorder: "true",
			hasMessageListScrollAdjust: "false",
			isInFormSheetBg: "false",
			saveRecord: "this.props.saveButtonClicked",
		});
		if (
			chatterContainerHookXml.parentNode.classList.contains(
				"o_form_sheet"
			)
		) {
			return res; // if chatter is inside sheet, keep it there
		}
		const formSheetBgXml = res.querySelector(".o_form_sheet_bg"); //
		const parentXml = formSheetBgXml && formSheetBgXml.parentNode;
		if (!parentXml) {
			return res; // miss-config: a sheet-bg is required for the rest
		}
		if (params.hasAttachmentViewerInArch) {
			// in sheet bg (attachment viewer present) 在工作表bg中（存在附件查看器）
			const sheetBgChatterContainerHookXml =
				chatterContainerHookXml.cloneNode(true);
			sheetBgChatterContainerHookXml.classList.add("o-isInFormSheetBg");
			setAttributes(sheetBgChatterContainerHookXml, {
				"t-if": `this.props.hasAttachmentViewer`,
			});
			append(formSheetBgXml, sheetBgChatterContainerHookXml);
			const sheetBgChatterContainerXml =
				sheetBgChatterContainerHookXml.querySelector(
					"ChatterContainer"
				);
			setAttributes(sheetBgChatterContainerXml, {
				isInFormSheetBg: "true",
			});
		}

		// after sheet bg (standard position, below form) 表格bg后（标准位置，表格下方）
		setAttributes(chatterContainerHookXml, {
			"t-if": `!this.props.hasAttachmentViewer and ${WRAP}`,
		});
		if (WRAP) {
			append(formSheetBgXml, chatterContainerHookXml);
		} else {
			append(parentXml, chatterContainerHookXml);
		}

		return res;
	},

	compileForm(el, params) {
		const form = this._super(el, params);
		

		return form;
	},

	compileSheet(el, params) {
		const sheetBG = this._super(el, params);

		// if (this.displayScrollTopButton) {
		// 	// 在 className = 'o_form_sheet_bg' 的元素中显示 滚动到顶部的按钮
		// 	console.log("显示滚动到顶部的按钮");
		// 	append(sheetBG, ScrollTopAction);
		// }

		return sheetBG;
	},
});
