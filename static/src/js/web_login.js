odoo.define('rainbow_community_theme.login_layout', function (require) {
    "use strict";

    var Login = function () {

        return {
            init: function () {
                // handleLogin();

                $.backstretch([
                        "/rainbow_community_theme/static/src/img/bg/1.jpg",
                        "/rainbow_community_theme/static/src/img/bg/2.jpg",
                        "/rainbow_community_theme/static/src/img/bg/3.jpg",
                        "/rainbow_community_theme/static/src/img/bg/4.jpg"
                    ], {
                        fade: 1000,
                        duration: 8000
                    }
                );
            }
        };
    }();

    jQuery(document).ready(function() {
        Login.init();
    });

});