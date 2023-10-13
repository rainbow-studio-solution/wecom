/** @odoo-module **/

import {
    browser
} from "@web/core/browser/browser";
import {
    Tooltip
} from "@web/core/tooltip/tooltip";
import {
    useService
} from "@web/core/utils/hooks";

const {
    Component,
    useRef,
} = owl;

export class DisplayPasswordButton extends Component {
    setup() {
        this.button = useRef("button");
        this.popover = useService("popover");

        this.encryption_status = this.props.encrypted;
    }

    showTooltip() {
        const closeTooltip = this.popover.add(this.button.el, Tooltip, {
            tooltip: this.encryption_status ? this.props.encryptedText : this.props.decryptedText,
        });
        browser.setTimeout(() => {
            closeTooltip();
        }, 2000);
    }

    onClick() {
        let icon = this.button.el.firstChild;

        this.encryption_status = !this.encryption_status;
        if (this.encryption_status) {
            icon.classList.remove("fa-eye");
            icon.classList.add("fa-eye-slash");
        } else {
            icon.classList.remove("fa-eye-slash");
            icon.classList.add("fa-eye");
        }

        this.button.el.previousElementSibling.type = "text";
        this.button.el.previousElementSibling.dataset.encrypted = this.encryption_status;
        this.showTooltip();
    }
}
DisplayPasswordButton.template = "web.DisplayPasswordButton";
DisplayPasswordButton.props = {
    className: {
        type: String,
        optional: true
    },
    encrypted: {
        type: Boolean,
        optional: true
    },
    encryptedText: {
        type: String,
        optional: true
    },
    decryptedText: {
        type: String,
        optional: true
    },
    content: {
        type: [String, Object],
        optional: true
    },
};