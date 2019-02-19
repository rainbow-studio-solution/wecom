odoo.define( function (require) {
    "use strict";

    /**
     * author: i@renjie.me
     * 参考资料 https://renjie.me/2016/09/10/odoo-form-view-pic-url-widget/
     */

    var core = require('web.core');
    var form_widget_registry = core.form_widget_registry;
    var FieldUrl = form_widget_registry.get('url');

    var PicUrl = FieldUrl.extend({
        template: 'PicUrl',
        placeholder: "/web/static/src/img/placeholder.png",
        render_value: function() {
            var self = this;
            if (!self.get("effective_readonly")) {
                self._super();
            } else {
                var src = self.get('value') || self.placeholder;
                var $img = self.$el.find('img')
                if(src){
                    $img.load(function() {
                        if(self.options.size){
                            var width = self.options.size[0];
                            var height = self.options.size[1];
                            $img.css({
                                "max-width": "" + width + "px",
                                "min-width": "" + width + "px",
                                "max-height": "" + height + "px",
                                "min-height": "" + height + "px"
                            });
                        }
                    });
                    $img.on('error', function() {
                        $img.attr('src', self.placeholder);
                    });
                    $img.attr({
                        src: src,
                        alt: self.node.attrs.alt,
                        title: self.node.attrs.title
                    }).show();
                }
            }
        }
    });
    form_widget_registry.add('pic', PicUrl);

});
