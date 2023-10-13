/** @odoo-module **/

import {
    _lt
} from "@web/core/l10n/translation";
import {
    registry
} from "@web/core/registry";

import {
    archParseBoolean
} from "@web/views/utils";
import {
    useInputField
} from "@web/views/fields/input_field_hook";
import {
    standardFieldProps
} from "@web/views/fields/standard_field_props";
import {
    DisplayPasswordButton
} from "./display_password_button";

const {
    Component,
    useEffect,
    useRef,
    onMounted,
    onRendered,
} = owl;


// --------------------------------------------------------------------------------
// DisplayPasswordChar
// --------------------------------------------------------------------------------
export class DisplayPasswordCharField extends Component {
    setup() {
        this.encryptedText = this.env._t("String encrypted");
        this.decryptedText = this.env._t("String decrypted");
        this.encrypted = true; // 是否加密

        this.inputareaRef = useRef("input");
        useInputField({
            getValue: () => this.props.value.trim() || "",
            refName: "input"
        });
        onMounted(() => {
            this.onMounted();
        });
        onRendered(() => {
            this.onRendered();
        });
    }
    onMounted() {
        // 在渲染组件之后，
        let self = this;
        // console.log(self);
        this.input = this.inputareaRef.el;
        // this.input.type = "password";
        // setTimeout(() => {
        //     self.input.type = "text";
        // }, 1000)
        if (this.input.value.trim() != "") {
            this.input.dataset.encrypted = true;
        } else {
            this.input.dataset.encrypted = false;
        }
    }
    onRendered() {
        // 在渲染组件之前，会用来初始化一些数据等
        if (this.props.value.trim() != "") {
            this.encrypted = true;
        } else {
            this.encrypted = false;
        }
    }

    onInput() {
        // console.log("onInput", this.input.value.trim());
        if (this.input.value.trim() != "") {
            this.input.type = "text";
            this.input.dataset.encrypted = true;

        } else {
            this.input.dataset.encrypted = false;
            this.input.type = "text";
        }
        // console.log(this.props.value.trim());
    }
}
DisplayPasswordCharField.template = "web.DisplayPasswordCharField";
DisplayPasswordCharField.components = {
    DisplayPasswordButton
};
DisplayPasswordCharField.props = {
    ...standardFieldProps,
    className: {
        type: String,
        optional: true
    },
    placeholder: {
        type: String,
        optional: true
    },
    shouldTrim: {
        type: Boolean,
        optional: true
    },
    encrypted: {
        type: Boolean,
        optional: true
    },
};
DisplayPasswordCharField.displayName = _lt("Text is displayed in password characters");
DisplayPasswordCharField.supportedTypes = ["char"];
// DisplayPasswordCharField.props = {
//     className: { type: String, optional: true },
// };
DisplayPasswordCharField.extractProps = ({
    attrs,
    field,
}) => {
    let encrypted = attrs.require_encryption;
    if (encrypted === undefined) {
        encrypted = true;
    } else {
        encrypted = archParseBoolean(encrypted);
    }
    return {
        shouldTrim: field.trim,
        placeholder: attrs.placeholder,
        encrypted: encrypted,
    };
};

registry.category("fields").add("DisplayPasswordChar", DisplayPasswordCharField);