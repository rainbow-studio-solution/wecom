/** @odoo-module */

import {
    Dialog
} from "@web/core/dialog/dialog";
import {
    useService
} from "@web/core/utils/hooks";

const {
    Component
} = owl;

export class OecProUpgradeDialog extends Component {
    setup() {
        this.orm = useService("orm");
        this.router = useService("router");
    }
    _confirmUpgrade() {
        // this.router.redirect(
        //     "https://www.odoo.com/odoo-enterprise/upgrade?num_users=" + usersCount
        // );
        window.open(this.props.url, '_blank');
    }
}
OecProUpgradeDialog.template = "oec.OecProUpgradeDialog";
OecProUpgradeDialog.components = {
    Dialog
};