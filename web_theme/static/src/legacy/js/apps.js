odoo.define('web_theme.apps', function (require) {
	'use strict';

	var Apps = require('web.Apps');

	Apps.include({
		// Do nothing on update count as needactions have been removed
		_on_update_count: function () {}
	});
});
