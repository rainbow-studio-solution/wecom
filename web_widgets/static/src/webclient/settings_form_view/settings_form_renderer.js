/** @odoo-module **/

import {
    SettingsFormRenderer
} from "@web/webclient/settings_form_view/settings_form_renderer";
import {
    OecFormLabelHighlightText
} from "./highlight_text/oec_form_label_highlight_text";

SettingsFormRenderer.components.FormLabel = OecFormLabelHighlightText;