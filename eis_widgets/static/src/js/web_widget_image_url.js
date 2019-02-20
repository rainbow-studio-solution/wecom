/**
 * 参考资料
 * https://apps.odoo.com/apps/modules/11.0/web_widget_image_url/
 * https://renjie.me/2016/09/10/odoo-form-view-pic-url-widget/
 */

odoo.define('eis_widgets.FieldImageURL', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var registry = require('web.field_registry');
    var QWeb = core.qweb;
    var _t = core._t;

    var UrlImage = AbstractField.extend({
        className: 'o_attachment_image',
        template: 'FieldImageURL',
        placeholder: "/web/static/src/img/placeholder.png",
        supportedFieldTypes: ['char'],

        url(){
            return this.value ? this.value : this.placeholder;
        },

        _render() {
            this._super(arguments);

            var self = this;
            var $img = this.$("img:first");
            $img.on('error', function() {
                $img.attr('src', self.placeholder);
                self.do_warn(_t("Image"), _t("Could not display the selected image."));
            });
        }
    });
    registry.add('image_url', UrlImage);
});
