/** @odoo-module */

import {
    X2ManyField
} from "@web/views/fields/x2many/x2many_field";
import {
    registry
} from "@web/core/registry";

import {
    standardFieldProps
} from "@web/views/fields/standard_field_props";

import {
    One2ManyConfigListRenderer
} from "./one2many_config_list_renderer";
const {
    Component,
    useRef
} = owl;

export class One2ManyConfigField extends X2ManyField {
    setup() {
        super.setup();
    }
    get rendererProps() {
        const configProps = super.rendererProps;
        let help_field = this.activeField.help || this.activeField.rawAttrs.help || "";
        if (help_field != "") {
            configProps.help_field = help_field;
            let help_string = this.props.value.fields[help_field].string;
            configProps.help_string = help_string;
        }
        return configProps;
    }
}

One2ManyConfigField.supportedTypes = ["one2many_config"];
One2ManyConfigField.components = {
    ...X2ManyField.components,
    ListRenderer: One2ManyConfigListRenderer,
};

registry.category("fields").add("one2many_config", One2ManyConfigField);