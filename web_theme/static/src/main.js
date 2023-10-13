/** @odoo-module **/

import { startWebClient } from "@web/start";
import { iErpWebClient } from "./webclient/webclient";

/**
 此文件启动  webclient。在清单中，它将替换社区版 main.js 加载不同的webclient类（ iErpWebClient 而不是 webclient）
 */

startWebClient(iErpWebClient);
