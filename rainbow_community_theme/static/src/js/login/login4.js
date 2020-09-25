odoo.define('rainbow_community_theme.login', function (require) {
    "use strict";
    var Login = function () {
        var handleLogin = function () {
            //数据库切换
            jQuery(document).ready(function () {
                $('#database_list').select2({
                    width: '100%',
                });
                $("#database_list").change(function () {
                    window.location.href = '/web?db=' + $(this).children('option:selected').val();
                })
            });
        };

        return {
            init: function () {
                handleLogin();
                $.backstretch([
                    "/rainbow_community_theme/static/src/img/pages/login/1.jpg",
                    "/rainbow_community_theme/static/src/img/pages/login/2.jpg",
                    "/rainbow_community_theme/static/src/img/pages/login/3.jpg",
                    "/rainbow_community_theme/static/src/img/pages/login/4.jpg"
                ], {
                    fade: 1000,
                    duration: 8000
                });
            }
        };
    }();

    jQuery(document).ready(function () {
        Login.init();
    });
});