odoo.define('rainbow_community_theme.Sidebar', function (require) {
    "use strict";

    var session = require('web.session');

    $(function(){
        (function ($) {
            $.delDebug = function (url) {
                var str = url.match(/web(\S*)#/);
                url = url.replace("str/g","");
                return url;
            }
            $.addDebug = function (url) {
                url = url.replace(/(.{4})/,"$1?debug");
                return url;
            }
            $.addDebugWithAssets = function (url) {
                url = url.replace(/(.{4})/,"$1?debug=assets");
                return url;
            }
        })(jQuery);


        $("#sidebar_menu a").each(function(){
            var url = $(this).attr('href');
            if (session.debug ==false)
                $(this).attr('href',$.delDebug(url));
            if (session.debug ==1)
                $(this).attr('href',$.addDebug(url));
            if (session.debug =='assets')
                $(this).attr('href',$.addDebugWithAssets(url));
        });


        $('body').on('click', '.o_menu_sidebar_toggler', function (e) {
            if ($(".o_main_sidebar_wrapper").hasClass("sidebar_hide")) {
                $(".o_main_sidebar_wrapper").addClass("sidebar_show");
                $(".o_main_sidebar_wrapper").removeClass("sidebar_hide");
                $(".o_menu_logo").addClass("logo_show");
                $(".o_menu_logo").removeClass("logo_hide");
            }
            else if ($(".o_main_sidebar_wrapper").hasClass("sidebar_show")) {
                $(".o_main_sidebar_wrapper").addClass("sidebar_hide");
                $(".o_main_sidebar_wrapper").removeClass("sidebar_show")
                $(".o_menu_logo").addClass("logo_hide");
                $(".o_menu_logo").removeClass("logo_show");
            }
            else {
                $(".o_main_sidebar_wrapper").addClass("sidebar_hide");
                $(".o_menu_logo").addClass("logo_hide");
            }
        });

        //change事件监听Tab、Enter按键，同时焦点转移至其它界面组件时也会触发此事件。
        $('#sidebar_search').on('change', function () {
            var str  = $("#sidebar_search").val().trim();
            if(!isEmpty(str)){
                $("#sidebar_menu li[title!='"+str+"']").addClass("li_hide");
                $("#sidebar_menu li[title*='"+str+"']").removeClass("li_hide");
            }
            else {
                $("#sidebar_menu li").removeClass("li_hide");
            }
        });
        $('#sidebar_search_clear').on('click', function () {
            $(" #sidebar_search").val("");
            $("#sidebar_menu li").removeClass("li_hide");
        });
    });

});

//判断字符是否为空的方法
function isEmpty(obj){
    if(typeof obj == "undefined" || obj == null || obj == ""){
        return true;
    }else{
        return false;
    }
}
