/** @odoo-module **/

import {
    Dialog
} from "@web/core/dialog/dialog";
import {
    _lt
} from "@web/core/l10n/translation";
import {
    Markup
} from 'web.utils';
const {
    Component,
} = owl;

export class WecomApiErrorDialog extends Component {
    setup() {
        this.title = this.props.title;
        this.size = this.props.size;
        this.code = this.props.code;
        this.description = this.props.description;
        this.method = Markup(this.props.method);
        this.details = this.props.details;

        this.bodyClass = "bg-warning";
        this.contentClass = "bg-warning";
    }
}
WecomApiErrorDialog.components = {
    Dialog
};
WecomApiErrorDialog.template = "wecom.WecomApiErrorDialog";
WecomApiErrorDialog.title = _lt("Wecom API Error");