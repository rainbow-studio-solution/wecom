odoo.define('wecom_widget.ImageURL', function (require) {
    "use strict";

    var CharImageUrl = require('web.basic_fields').CharImageUrl;;
    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var _t = core._t;
    var qweb = core.qweb;
    var WeComImageUrl = CharImageUrl.extend({
        _renderReadonly: function () {
            var self = this;
            const url = this.value;
            if (url) {
                var $img = $(qweb.render("WeComImageUrl", {
                    widget: this,
                    url: url
                }));
                // override css size attributes (could have been defined in css files)
                // if specified on the widget
                const width = this.nodeOptions.size ? this.nodeOptions.size[0] : this.attrs.width;
                const height = this.nodeOptions.size ? this.nodeOptions.size[1] : this.attrs.height;
                const class_name = this.nodeOptions.class;

                if (width) {
                    $img.attr('width', width);
                    $img.css('max-width', width + 'px');
                }
                if (height) {
                    $img.attr('height', height);
                    $img.css('max-height', height + 'px');
                }

                if (class_name) {
                    this.$el.addClass(class_name);
                }

                this.$('> img').remove();
                this.$el.prepend($img);

                $img.one('error', function () {
                    $img.attr('src', self.placeholder);
                    self.displayNotification({
                        type: 'info',
                        message: _t("Could not display the specified image url."),
                    });
                });
            }

            return this._super.apply(this, arguments);
        },
    });
    fieldRegistry.add('wecom_image_url', WeComImageUrl);
    return {
        WeComImageUrl: WeComImageUrl
    };
});