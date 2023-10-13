$(function () {
    'use strict'
    // var ajax = require('web.ajax');
    document.onreadystatechange = function (env) {
        let form = document.getElementById('lock-form');

        if (!form) {
            return;
        }

        let password = "";
        let error = "";
        let message = "";
        let redirect = "";
        let storage_mode = 0;

        const lockScreenInfoKey = "lockScreenInfo";
        let lock_info_local_storage = JSON.parse(window.localStorage.getItem(lockScreenInfoKey));

        const showOrHidePasswordButton = document.getElementById('show_or_hide_password');

        const unlock_button = document.getElementById('o_unlock_button');
        const confirm_logout_button = document.getElementById('o_confirm_logout_button');
        const login = document.getElementById('login');

        // form 提交事件
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            } else {
                event.preventDefault()
                event.stopPropagation()
                const alerts = form.querySelector('.alert');
                alerts.classList.add('d-none');
                verifyPassword();
            }

            form.classList.add('was-validated')
        }, false)

        let pawInput = document.getElementById('password');
        pawInput.style.fontFamily = "password";
        // 密码输入框输入事件
        pawInput.addEventListener('input', function (event) {
            password = event.target.value;
            if (pawInput.value.length > 0) {
                unlock_button.disabled = false;
                showOrHidePasswordButton.classList.remove("d-none");
                form.classList.remove('was-validated')
            } else {
                unlock_button.disabled = true;
                form.classList.add('was-validated')
                showOrHidePasswordButton.classList.add("d-none");
            }
        }, false)

        // 显示或隐藏密码
        showOrHidePasswordButton.addEventListener('click', function (event) {
            event.preventDefault();
            const showOrHidePasswordIcon = document.getElementById('show_or_hide_password_icon');
            if (pawInput.style.fontFamily == "password") {
                pawInput.style.fontFamily = "initial";
                showOrHidePasswordIcon.classList.add("bi-eye");
                showOrHidePasswordIcon.classList.remove("bi-eye-slash");
            } else {
                pawInput.style.fontFamily = "password";
                showOrHidePasswordIcon.classList.add("bi-eye-slash");
                showOrHidePasswordIcon.classList.remove("bi-eye");
            }
        }, false)

        // 确认注销按钮点击事件
        confirm_logout_button.addEventListener('click', function (event) {
            event.preventDefault();
            window.location.href = "/web/session/logout?redirect=/web/login";
        }, false)

        function verifyPassword() {
            var params = {
                'login': login.value,
                'password': password,
            };
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: '/web/unlock',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    'jsonrpc': "2.0",
                    'method': "call",
                    "params": params
                }),
                success: function (data) {
                    let result = data.result;
                    // console.log(result);
                    if (result.hasOwnProperty("error")) {
                        error = result.error;
                        _showError();
                    } else if (result.hasOwnProperty("message")) {
                        message = result.message;
                        storage_mode = result.storage_mode;
                        if (storage_mode === 1) {
                            let lock_info = lock_info_local_storage;
                            // console.log(lock_info);
                            if (lock_info.href) {
                                redirect = lock_info.href;
                            } else {
                                redirect = "/web";
                            }
                        } else {
                            if (result.href) {
                                redirect = result.href;
                            } else {
                                redirect = "/web";
                            }
                        }
                        _unlock();
                    }
                },
                error: function (data) {
                    console.error("ERROR ", data);
                },
            })
        }

        function _showError() {
            const alert = document.querySelector('.alert-danger');
            alert.classList.remove('d-none');
            const span = document.querySelector('span.error');
            span.innerHTML = error;
        }

        function _unlock() {
            const alert = document.querySelector('.alert-success');
            alert.classList.remove('d-none');
            const span = document.querySelector('span.message');
            span.innerHTML = message;

            _countdown();
        }

        function _countdown() {
            const countdown = document.querySelector('.countdown-line');
            countdown.classList.remove('d-none');
            var timeleft = 3;
            var downloadTimer = setInterval(function () {
                timeleft--;
                document.querySelector("span#countdown_number").innerHTML = timeleft;
                if (timeleft <= 0) {
                    clearInterval(downloadTimer);

                    if (storage_mode === 1) {
                        let lock_info = lock_info_local_storage;
                        lock_info["state"] = false;
                        window.localStorage.setItem(lockScreenInfoKey, JSON.stringify(lock_info));
                    }

                    countdown.classList.add('d-none');
                    window.location = redirect;
                }
            }, 1000);
        }

        function _onRelogin() {}

        function _confirmLogout() {
            window.location.href = "/web/session/logout?redirect=/web/login";
        }
    }
});