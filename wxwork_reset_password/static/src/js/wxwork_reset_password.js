odoo.define('wxwork_reset_password.Rrset', function (require) {
    "use strict";

    var UIBootbox = function () {
        var handleDemo = function() {
            $(".reset-password-wxwork-qr").click(function(){
                bootbox.dialog({
                    animate: true,
                    locale: "zh_CN",
                    closeButton: true,
                    className : "reset-password-wxwork-dialog",
                    title: "企业微信扫码重置密码",
                    message: "<iframe height='380px' width='390px' marginheight='0' marginwidth='0' scrolling='no' frameborder='0' align='middle' src='https://open.work.weixin.qq.com/wwopen/sso/qrConnect?agentid=1000003&redirect_uri=https://eis.ouyahotels.com/wxwork/auth_oauth/qr&appid=wwe22b76fff8c9d3b4&state=%7BMpM:+5,+MrM:+Mhttps%253A%252F%252Feis.ouyahotels.com%252FwebM,+MdM:+MeisM%7D'/>",
                    buttons: {
                        cancel: {
                            label: "关闭",
                            className: 'btn-danger',

                        },
                    }
                });
            });
        }

        return {
            //main function to initiate the module
            init: function () {
                handleDemo();
            }
        };

    }();

    jQuery(document).ready(function() {
        UIBootbox.init();
    });
});


