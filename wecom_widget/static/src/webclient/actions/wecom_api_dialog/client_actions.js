/** @odoo-module **/

import {
    registry
} from "@web/core/registry";
import {
    WecomApiErrorDialog
} from "./wecom_api_error_dialog";



export function wecomApiDialogAction(env, action) {
    const params = action.params || {};
    env.services.dialog.add(WecomApiErrorDialog, params, {});
}
registry.category("actions").add("wecom_api_error_dialogs", wecomApiDialogAction);