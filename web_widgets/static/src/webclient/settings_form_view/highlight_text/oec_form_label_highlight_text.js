/** @odoo-module **/
import {
    FormLabel
} from "@web/views/form/form_label";
import {
    HighlightText
} from "@web/webclient/settings_form_view/highlight_text/highlight_text";
import {
    FormLabelHighlightText
} from "@web/webclient/settings_form_view/highlight_text/form_label_highlight_text";

export class OecFormLabelHighlightText extends FormLabelHighlightText {
    setup() {
        super.setup();
        // Odoo 企业版
        const isEnterprise = odoo.info && odoo.info.isEnterprise;
        if (
            this.props.fieldInfo &&
            this.props.fieldInfo.FieldComponent &&
            this.props.fieldInfo.FieldComponent.isUpgradeField &&
            !isEnterprise
        ) {
            this.upgradeEnterprise = true;
        }

        // China erp professional
        if (this.props.fieldInfo.FieldComponent.isUpgradeErpProField) {
            this.upgradeErpProfessional = true;
        } else { 
            this.upgradeErpProfessional = false;
        }

        
    }
    get className() {
        if (this.props.className) {
            return this.props.className;
        }
        return super.className;
    }
}

// OecFormLabelHighlightText.template = "oec.FormLabelHighlightText";
OecFormLabelHighlightText.components = {
    HighlightText
};