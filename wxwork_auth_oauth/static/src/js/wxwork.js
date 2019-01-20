odoo.define('wxwork', function (require) {
    "use strict";

    $(function(){
        (function ($) {
            var url = $(".wxwork").parent().attr('href')
            var re1 = new RegExp("client_id","g"); //第一个参数是你要替换的字符串，第二个参数指替换所有的
            var re2 = new RegExp("token","g"); //第一个参数是你要替换的字符串，第二个参数指替换所有的
            // var re3 = new RegExp(state,"g");
            var new_url1 = url.replace(re1,"appid");
            var new_url2 = new_url1.replace(re2,"code");
            // var new_url3 = new_url2.replace(state,"abcd1234")+"#wechat_redirect";
            $(".wxwork").parent().attr('href',new_url2+"#wechat_redirect");
            // $(".wxwork").attr('href',new_url3+"#wechat_redirect");
        })(jQuery);
    });
});
