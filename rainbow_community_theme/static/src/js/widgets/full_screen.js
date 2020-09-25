odoo.define('rainbow_community_theme.FullScreen', function (require) {
    "use strict";

    $(document).ready(function() {
        $('body').on('click', '.o_user_fullscreen', function (e) {
            onToggleFullScreen();

            $(window).trigger('resize');
        });
    });

    function onToggleFullScreen() {
        if (
            (document.fullScreenElement && document.fullScreenElement !== null) ||
            (!document.mozFullScreen && !document.webkitIsFullScreen)
        ) {
            if (document.documentElement.requestFullScreen) {
                document.documentElement.requestFullScreen();
            } else if (document.documentElement.mozRequestFullScreen) {
                document.documentElement.mozRequestFullScreen();
            } else if (document.documentElement.webkitRequestFullScreen) {
                document.documentElement.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
            } else if (document.documentElement.msRequestFullscreen) {
                if (document.msFullscreenElement) {
                    document.msExitFullscreen();
                } else {
                    document.documentElement.msRequestFullscreen();
                }
            }
        } else {
            if (document.cancelFullScreen) {
                document.cancelFullScreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitCancelFullScreen) {
                document.webkitCancelFullScreen();
            }
        }
    }


});



