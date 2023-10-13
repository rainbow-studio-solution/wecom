/** @odoo-module **/

import { isMobileOS } from "@web/core/browser/feature_detection";
import * as BarcodeScanner from "@web/webclient/barcode/barcode_scanner";
import { useChildRef, useOwnedDialogs, useService } from "@web/core/utils/hooks";
// import { browser } from "@web/core/browser/browser";
import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { Component, onMounted, onWillUnmount, onWillStart, useRef } from "@odoo/owl";
import { useInputField } from "@web/views/fields/input_field_hook";

export class CharBarcodeField extends CharField {

    setup() {
        super.setup();
		this.orm = useService('orm');
		this.rpc = useService('rpc');
        this.notification = useService("notification");
        this.input = useRef("input");
        let postData = [];
        let obj = {
            company_id: this.props.record.context.allowed_company_ids[0],
        };
        postData.push(obj);
        this.postData = postData;
        useInputField({ getValue: () => this.props.value || "", parse: (v) => this.parse(v) });
        onMounted(this.onMounted);
        onWillUnmount(this.onWillUnmount);
        // onWillStart(() => {
		// 	this.onWillStart();
		// });

    }

    scanCode() {
        return new Promise((resolve, reject) => {
            let result_val = "";
            this.orm.call('wecom.client_api', 'getBarcodeWXConfig', [this.postData]).then((result) => {
                if (result.code === 0) {
                    let config = result.configs[0];
                    wx.config({
                        beta: true,
                        debug: false,
                        appId: config.corpid,
                        timestamp: config.timestamp,
                        nonceStr: config.nonceStr,
                        signature: config.signature,
                        jsApiList: config.jsApiList,
                        success: function (res) {
                            alert('请求微信成功');
                        },
                        fail: function (res) {
                            console.log('查看错误信息' + res);
                            this.notification.add(this.env._t("请确认是手机企业微信"), {
                                type: "warning",});
                            if (res.errMsg.indexOf('function not exist') > -1) {
                                alert('版本过低请升级');
                            }
                        }
                    });
                    wx.ready(() => {
                        wx.scanQRCode({
                            desc: "scanQRCode desc",
                            needResult: 1,
                            scanType: ["qrCode", "barCode"],
                            success: function(e) {
                                // alert(JSON.stringify(e))
                                result_val = e.resultStr;
                                resolve(result_val); // 在成功回调中使用 resolve 返回结果
                            },
                            error: res => {
                                if (res.errMsg.indexOf("function_not_exist") > 0) {
                                    alert("版本过低请升级");
                                }
                                reject(res); // 在失败回调中使用 reject 返回错误信息
                            }
                        });
                    });
                    wx.error((function(e) {
                        alert(e.errMsg)
                    }));
                }
            });
        });
    }
    
    async onBarcodeBtnClick() {

        this.scanCode().then(result => {
            console.log(result); // 输出扫描结果
            this.input.el.value = result
            this.input.el.focus(); // Focus the input
            this.props.update(result); 
        }).catch(error => {
            console.log(error); // 输出错误信息
            this.notification.add(this.env._t("Please, scan again !"), {
            type: "warning",});
        });
        // if (barcode) {
        //     // await this.onBarcodeScanned(barcode);
        //     if ("vibrate" in browser.navigator) {
        //         browser.navigator.vibrate(100);
        //     }
        // } else {
        //     this.notification.add(this.env._t("Please, scan again !"), {
        //         type: "warning",
        //     });
        // }
        // // this.props.value = barcode;
        // this.input.el.value = barcode
        // this.input.el.focus(); // Focus the input
        // this.props.update(barcode); 
        // // this.props.value = barcode;
    }

}

CharBarcodeField.props = {
    ...CharField.props,
};
CharBarcodeField.defaultProps = {
    ...CharField.defaultProps,
};

CharBarcodeField.displayName = _lt("charBarcodeField");
CharBarcodeField.template = "wecom_widget.charBarcodeField";
CharBarcodeField.supportedTypes = ["char"];

CharBarcodeField.extractProps = (args) => {
    return {
        ...CharField.extractProps(args),
    };
};

registry.category("fields").add("char_barcode", CharBarcodeField);

