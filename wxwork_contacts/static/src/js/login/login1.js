odoo.define('login1', function (require) {
    "use strict";
    var Login = function () {
        var handleLogin = function() {
            //数据库切换
            var currentdb = $("#db_list li.selected").text().trim();
            $(document).ready(function() {

                $("ul#db_list").on("click","li",function(){
                    $("#db").val($(this).text().trim());
                    if($(this).text().trim()!= currentdb)
                        window.location.href= '/web?db='+$(this).text().trim();

                })
            });

            $('.login-form input').keypress(function (e) {
                if (e.which == 13) {
                    if ($('.login-form').validate().form()) {
                        $('.login-form').submit();
                    }
                    return false;
                }
            });
        }

        var handleRegister = function() {

            $('.register-form input').keypress(function(e) {
                if (e.which == 13) {
                    if ($('.register-form').validate().form()) {
                        $('.register-form').submit();
                    }
                    return false;
                }
            });

            jQuery('#register-btn').click(function() {
                jQuery('.login-form').hide();
                jQuery('.register-form').show();
            });

            jQuery('#register-back-btn').click(function() {
                jQuery('.login-form').show();
                jQuery('.register-form').hide();
            });
        }

        return {
            init: function () {
                handleLogin();
                handleRegister();
            }
        };
    }();

    jQuery(document).ready(function() {
        Login.init();
    });
});