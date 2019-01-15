odoo.define('eis_web.login_layout', function (require) {
    "use strict";

    var Login = function () {

        return {
            init: function () {
                // handleLogin();

                $.backstretch([
                        "/eis_web/static/src/img/bg/1.jpg",
                        "/eis_web/static/src/img/bg/2.jpg",
                        "/eis_web/static/src/img/bg/3.jpg",
                        "/eis_web/static/src/img/bg/4.jpg"
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