/** @odoo-module **/

import {
    _lt
} from "@web/core/l10n/translation";
import {
    evaluateExpr
} from "@web/core/py_js/py";
import {
    registry
} from "@web/core/registry";
import {
    BooleanField
} from "@web/views/fields/boolean/boolean_field";
import {
    useService
} from "@web/core/utils/hooks";
import {
    OecProUpgradeDialog
} from "./oec_pro_upgrade_dialog";
import {
    standardFieldProps
} from "@web/views/fields/standard_field_props";

const {
    Component,
    useEffect,
    useRef,
    onMounted,
    onRendered,
} = owl;

export class OecProUpgradeBooleanField extends BooleanField {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.upgradeErpProfessional = true;
        // this.default_url = "http://osbzr.com/odoochina/china_addons";
        // this.default_image = "/web/static/img/enterprise_upgrade.jpg";

        // onMounted(() => {
        //     this.onMounted();
        // });
    }

    async onChange(newValue) {
        if (this.upgradeErpProfessional) {
            const dialogProps = {
                // title: _lt("Delete Property Field"),
                title: _lt("China Erp Professional App:") + this.props.app_name_string,
                url: this.props.url,
                image: this.props.image,
                // body: sprintf(
                //     _lt(
                //         'Are you sure you want to delete this property field? It will be removed for everyone using the "%s" %s.'
                //     ),
                //     this.parentName,
                //     this.parentString
                // ),


            };
            this.dialogService.add(
                OecProUpgradeDialog, dialogProps, {
                    onClose: () => {
                        this.props.update(false);
                    },
                }
            );
        } else {
            super.onChange(...arguments);
        }
    }

    onMounted() {
        // 在渲染组件之后，
        let self = this;
        // console.log(self);
    }
}
OecProUpgradeBooleanField.isUpgradeErpProField = true;

OecProUpgradeBooleanField.props = {
    ...standardFieldProps,
    url: {
        type: String,
        optional: true
    },
    image: {
        type: String,
        optional: true
    },
    app_name: {
        type: String,
        optional: true
    },
    app_name_string: {
        type: String,
        optional: true
    },
};
OecProUpgradeBooleanField.extractProps = ({
    attrs,
    field
}) => {
    // console.log(field);
    let url = attrs.url;
    let image = attrs.image;
    if (url === undefined) {
        url = "http://osbzr.com/odoochina/china_addons";
    }

    if (image === undefined) {
        image = "/web/static/img/enterprise_upgrade.jpg";
    }
    return {
        url: url,
        image: image,
        app_name: field.name,
        app_name_string: field.string,
    };
};

registry.category("fields").add("oec_pro_upgrade_boolean", OecProUpgradeBooleanField);