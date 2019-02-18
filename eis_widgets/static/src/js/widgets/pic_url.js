odoo.define('eis_widgets.pic_url', function (require) {
"use strict";

/**
 * This widget render a Pie Chart. It is used in the dashboard view.
 */

var core = require('web.core');
var Domain = require('web.Domain');
var viewRegistry = require('web.view_registry');
var Widget = require('web.Widget');
var widgetRegistry = require('web.widget_registry');

var qweb = core.qweb;

var PicUrl = Widget.extend({


});

widgetRegistry.add('pic_url', PicUrl);

return PicUrl;

});
