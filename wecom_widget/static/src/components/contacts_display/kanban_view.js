/** @odoo-module **/

import {
    registry
} from "@web/core/registry";
import {
    useService
} from "@web/core/utils/hooks";
import {
    kanbanView
} from "@web/views/kanban/kanban_view";
import {
    KanbanRenderer
} from "@web/views/kanban/kanban_renderer";
import {
    KanbanController
} from "@web/views/kanban/kanban_controller";
import {
    KanbanDropdownMenuWrapper
} from "@web/views/kanban/kanban_dropdown_menu_wrapper";
import {
    KanbanRecord
} from "@web/views/kanban/kanban_record";

const {
    Component,
    useState
} = owl;