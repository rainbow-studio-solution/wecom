odoo.define('wecom_base.app_config', function (require) {
    'use strict';
    var viewRegistry = require('web.view_registry');

    var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');
    var ListRenderer = require('web.ListRenderer');


    // var WecomAppsFormRenderer = FormRenderer.extend({
    //     start: function () {
    //         var self = this;
    //         return this._super.apply(this, arguments)
    //         // return this._super.apply(this, arguments).then(function () {
    //         //     var $app_config_ids_table = self.$el.find("div[name='app_config_ids']").find("table");
    //         //     var timer = setInterval(function () {
    //         //         if ($app_config_ids_table.css("table-layout") != "fixed") {
    //         //             clearInterval(timer);
    //         //         } else {
    //         //             $app_config_ids_table.css("table-layout", "auto");
    //         //         }
    //         //     }, 500);
    //         // });
    //     },
    //     setLocalState: function (state) {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function () {
    //             var $app_config_ids_table = self.$el.find("div[name='app_config_ids']").find("table");
    //             console.log("setLocalState", $app_config_ids_table)
    //             console.log("setLocalState", $app_config_ids_table.length)
    //             if ($app_config_ids_table.length > 0) {
    //                 $app_config_ids_table.css("table-layout", "auto");
    //             }
    //             // var timer = setInterval(function () {
    //             //     if ($app_config_ids_table.css("table-layout") != "fixed") {
    //             //         clearInterval(timer);
    //             //     } else {
    //             //         $app_config_ids_table.css("table-layout", "auto");
    //             //     }
    //             // }, 500);
    //         });
    //     },
    //     _renderTagNotebook: function (node) {
    //         var self = this;
    //         var $headers = $('<ul class="nav nav-tabs">');
    //         var $pages = $('<div class="tab-content">');
    //         // renderedTabs is used to aggregate the generated $headers and $pages
    //         // alongside their node, so that their modifiers can be registered once
    //         // all tabs have been rendered, to ensure that the first visible tab
    //         // is correctly activated
    //         var renderedTabs = _.map(node.children, function (child, index) {
    //             var pageID = _.uniqueId('notebook_page_');
    //             var $header = self._renderTabHeader(child, pageID);
    //             var $page = self._renderTabPage(child, pageID);
    //             self._handleAttributes($header, child);
    //             $headers.append($header);
    //             $pages.append($page);
    //             return {
    //                 $header: $header,
    //                 $page: $page,
    //                 node: child,
    //             };
    //         });

    //         var $app_config_ids_table = self.$el.find("div[name='app_config_ids']").find("table");
    //         console.log("_renderTagNotebook", $app_config_ids_table)
    //         console.log("_renderTagNotebook", $app_config_ids_table.length)
    //         console.log("_renderTagNotebook", renderedTabs)
    //         return this._super.apply(this, arguments)
    //     }
    // });

    // var WecomAppsFormView = FormView.extend({
    //     config: _.extend({}, FormView.prototype.config, {
    //         // Controller: WecomAppsFormController,
    //         Renderer: WecomAppsFormRenderer
    //     }),
    // });

    // viewRegistry.add('wecom_apps_form', WecomAppsFormView);

});