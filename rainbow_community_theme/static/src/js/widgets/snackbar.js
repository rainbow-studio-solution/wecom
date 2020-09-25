odoo.define('rainbow_community_theme.SnackBar', function (require) {
    'use strict';

    var config = require('web.config');
    if (!config.device.isMobile) {
        return;
    }

    const Widget = require('web.Widget');

    const SnackBar = Widget.extend({
        template: 'SnackBar',
        events: {
            'click .o_snackbar_button': '_onClickButton'
        },
        /**
         *
         * @param parent
         * @param options
         *    actionText : the text to display on Action button
         *    delay : The delay in ms use to display snackbar (use -1 to cancel auto hide)
         *    message : the text to display on snackbar
         *    onComplete : Callback fire when delay use to show the snackbar is over
         *    onActionClick : Callback fire when user click on action button
         */
        init(parent, options) {
            this._super(...arguments);
            this.message = options.message || '';
            this.delay = options.delay || 1000;
            this.onComplete = options.onComplete;
            this.actionText = options.actionText || '';
            this.onActionClick = options.onActionClick;
            this._timeout = false;
        },
        /**
         * @private
         */
        _delayedAction() {
            if (this.onComplete) {
                this.onComplete();
            }
            this.destroy();
        },

        /**
         * @private
         */
        _onClickButton(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            if (this.onActionClick) {
                this.onActionClick();
            }
            if (this._timeout) {
                clearTimeout(this._timeout);
            }
            this.destroy();
        },

        /**
         * Use to dismiss the displayed snackbar and destroy the widget
         */
        dismiss() {
            this.destroy();
        },
        /**
         * Display the snackbar to the body and applying a delay before calling the onComplete callback
         * if the delay is a negative number, the snackbar is always show and doesn't call the onComplete callback
         */
        show() {
            this.appendTo($('body'));
            const hasValidDelay = this.delay > -1;
            if (hasValidDelay) {
                this._timeout = setTimeout(() => this._delayedAction(), this.delay);
            }
        },
    });
    return SnackBar;

});