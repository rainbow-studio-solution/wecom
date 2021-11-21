// function pop_social_qrcode(obj) {
//     console.log(obj);
// }

odoo.define('website_china_extends.social_buttons', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;

    // var content = _t("<div class='card' style='width: 200px;'><img src='%s' class='card-img-top' alt='Focus on our WeChat official account'><div class='card-body' style='padding: 5px;'><h5 class='card-title text-center' style='margin: 0;'>%s</h5></div></div>");
    var content = _t("<div class='card' style='width: 200px;'><img src='%s' class='card-img-top' alt='%s'><div class='card-body' style='padding: 5px;'></div></div>");


    $(document).ready(function () {
        // $("a.pop_social_qrcode").popover({
        //     placement: $("a.pop_social_qrcode").data("placement"),
        //     trigger: 'hover',
        //     html: true,
        //     content: _.str.sprintf(content, $("a.pop_social_qrcode").data("img")),
        // });
        $("a.pop_social_qrcode").each(function () {
            $(this).popover({
                placement: $(this).data("placement"),
                trigger: 'hover',
                html: true,
                content: _.str.sprintf(content, $(this).data("img"), $(this).attr('title')),
            })
        })
    });
});