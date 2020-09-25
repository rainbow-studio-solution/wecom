odoo.define('rainbow_community_theme.SwipeItemMixin', function () {

    const ANIMATION_SWIPE_DURATION = 250;
    const SWIPE_ACTIVATION_THRESHOLD = 15;
    const SWIPE_ITEM_DATA_KEY = 'swipe_item';
    const ACTION_DIRECTION = Object.freeze({
        LEFT: 'left',
        RIGHT: 'right',
        NONE: false
    });
    const SWIPE_AXES = Object.freeze({
        HORIZONTAL: 'horizontal',
        VERTICAL: 'vertical',
        NONE: false
    });

    return {
        events: {
            'touchstart .o_swipe_item': '_onTouchStart',
            'touchmove .o_swipe_item': '_onTouchMove',
            'touchend .o_swipe_item': '_onTouchEnd',
        },

        /**
         * @param {Object} options
         * @param {Object} options.actions
         * @param {string[]} options.actions.classesImage
         * @param {string} options.actions.backgroundClassColor
         * @param {Function} options.actions.allowSwipe
         * @param {Function} options.actions.actionCallback
         * @param {Function} options.actions.avoidRestorePositionElement
         * @param {string} options.selectorTarget
         */
        init(options) {
            this.actions = options.actions;
            this.selectorTarget = options.selectorTarget;
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * Add the class into the target element to be able to swipe.
         */
        addClassesToTarget() {
            this.$(this.selectorTarget).addClass('o_swipe_item');
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Add the element actions elements to the DOM
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         */
        _addSwipeElement(target) {
            target.classList.add('o_swipe_current');
            target.parentElement.classList.add('overflow-hidden');
            // Note: use of jQuery for readability
            $('<div/>').addClass('o_swipe_separator').prependTo(target);
            for (const [key, value] of Object.entries(this.actions)) {
                $('<div/>').addClass(['o_swipe_action', key])
                    .append($('<span/>').addClass(value.classesImage))
                    .prependTo(target);
                this._setSwipeData(target, 'actionThreshold', {
                    [key]: this._calculateActionThreshold(target, key)
                });
            }
        },

        /**
         * Called when item moving with touch
         *
         * @private
         * @param {TouchEvent} ev
         * @param {'left' | 'right'} action
         * @return {boolean} true if action allowed
         */
        _allowSwipe(ev, action) {
            if (this.actions[action] && this.actions[action].allowSwipe) {
                return this.actions[action].allowSwipe(ev);
            }
            return false;
        },

        /**
         * Calculate the threshold for action
         * the value is width of icon + 2 times the padding for the icon
         *
         * @private
         * @param {HTMLElement | EventTarget} targetElement
         * @param {'left' | 'right'} swipeDirection
         * @return {number}
         */
        _calculateActionThreshold(targetElement, swipeDirection) {
            const iconElement = targetElement.querySelector(`.o_swipe_action.${swipeDirection} .fa`);
            const iconParentElement = iconElement.parentElement;
            return parseFloat(getComputedStyle(iconElement).width) + (2 * parseFloat(getComputedStyle(iconParentElement).paddingLeft));
        },

        /**
         * Return the max position of the div for a specific direction
         *
         * @private
         * @param {'left' | 'right'} swipeDirection
         * @return {string}
         */
        _getMaxPosition(swipeDirection) {
            if (swipeDirection === ACTION_DIRECTION.LEFT) {
                return '-100%';
            } else if (swipeDirection === ACTION_DIRECTION.RIGHT) {
                return '100%';
            }
        },

        /**+
         * Return the action element of the target
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {'left' | 'right'} action
         * @return {HTMLElement | EventTarget | null}
         */
        _getSwipeActionElement(target, action) {
            if (action) {
                return target.querySelector(`.o_swipe_action.${action}`);
            }
            return target.querySelector(`.o_swipe_action`);
        },

        /**
         * Return the axes bigger than the threshold
         *
         * @private
         * @param {Object} touchDelta
         * @param {number} touchDelta.xDelta
         * @param {number} touchDelta.yDelta
         * @return {'horizontal' | 'vertical' | false}
         */
        _getSwipeAxes(touchDelta) {
            if (Math.abs(touchDelta.yDelta) > SWIPE_ACTIVATION_THRESHOLD) {
                return SWIPE_AXES.VERTICAL;
            } else if (Math.abs(touchDelta.xDelta) > SWIPE_ACTIVATION_THRESHOLD) {
                return SWIPE_AXES.HORIZONTAL;
            }
            return SWIPE_AXES.NONE;
        },

        /**
         * Return the object containing all information for swipe
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {string} key
         * @return {*}
         */
        _getSwipeData(target, key) {
            return $(target).data(SWIPE_ITEM_DATA_KEY)[key];
        },

        /**
         * Get the direction of the swipe
         *
         * @param {Object} touchDelta
         * @param {number} touchDelta.xDelta
         * @param {number} touchDelta.yDelta
         * @returns {false | 'left' | 'right'}
         */
        _getSwipeDirection(touchDelta) {
            if (touchDelta.xDelta > 0) {
                return ACTION_DIRECTION.RIGHT;
            } else if (touchDelta.xDelta < 0) {
                return ACTION_DIRECTION.LEFT;
            }
            return ACTION_DIRECTION.NONE;
        },

        /**
         * Get the delta between two touch
         *
         * @private
         * @param {TouchEvent} event
         * @param {HTMLElement | EventTarget} target
         * @returns {{xDelta: number, yDelta: number}}
         */
        _getTouchDelta(event, target) {
            const touch = this._getTouchPosition(event);
            const touchStart = this._getSwipeData(target, 'touchStart');
            return {
                xDelta: touch.x - touchStart.x + this._getSwipeData(target, 'startLeft'),
                yDelta: touch.y - touchStart.y
            };
        },

        /**
         * Return position an object with x, y of the touch event
         *
         * @private
         * @param {TouchEvent} event
         * @returns {{x: number, y: number}}
         */
        _getTouchPosition(event) {
            return {
                x: event.changedTouches[0].clientX,
                y: event.changedTouches[0].clientY
            };
        },

        /**
         * Check if the threshold is reach
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {Object} touchDelta
         * @param {number} touchDelta.xDelta
         * @param {number} touchDelta.yDelta
         * @param {false | 'left' | 'right'} swipeDirection
         * @returns {false | 'left' | 'right'}
         */
        _isThresholdReach(target, touchDelta, swipeDirection) {
            if (Math.abs(touchDelta.xDelta) < this._getSwipeData(target, 'actionThreshold')[swipeDirection]) {
                return false;
            }
            return swipeDirection;
        },

        /**
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {false | 'left' | 'right'} swipeDirection
         * @param {string | number} toPosition
         * @param {string, 'px', '%'} unit
         * @return {Promise}
         */
        _moveElementAndActionWithAnimation(target, swipeDirection, toPosition, unit = 'px') {
            return this._moveWithAnimation(target, toPosition, {
                step: (now) => this._updateSwipeActionPosition(target, swipeDirection, -now, unit)
            });
        },

        /**
         * Apply a left css property to the node with animation
         *
         * @private
         * @param {HTMLElement | EventTarget} element
         * @param {string | number} left
         * @param {Object} customOptions
         * @return {Promise}
         */
        _moveWithAnimation(element, left, customOptions = {}) {
            return $(element)
                .animate({
                    left: left,
                }, Object.assign({}, {
                    duration: ANIMATION_SWIPE_DURATION,
                }, customOptions)).promise();
        },

        /**
         * When the user end the swipe action
         *
         * @private
         * @param {TouchEvent} ev
         * @param {false | Function} callback
         * @param {Function} restore callback to restore position
         */
        _performSwipeEndAction(ev, callback, restore = () => {}) {
            if (callback) {
                callback(ev, restore);
            }
        },

        /**
         * Restore the DOM like before swipe
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         */
        async _restoreDOMLikeBeforeSwipe(target) {
            await this._moveElementAndActionWithAnimation(target, null, 0);
            $(target).find('.o_swipe_action, .o_swipe_separator').remove();
            target.classList.remove('o_swipe_current');
            target.parentElement.classList.remove('overflow-hidden');
            this._setSwipeData(target, 'swipeDirection', false);
            this._setSwipeData(target, 'swipeAxes', false);
        },

        /**
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {string} key
         * @param {*} value
         */
        _setSwipeData(target, key, value) {
            const tmpData = $(target).data(SWIPE_ITEM_DATA_KEY);
            if (typeof tmpData[key] === 'object') {
                Object.assign(tmpData[key], value);
            } else {
                tmpData[key] = value;
            }
            $(target).data(SWIPE_ITEM_DATA_KEY, tmpData);
        },

        /**
         * Update the node element for the current action
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {false | 'left' | 'right'} action
         * @param {number} xDelta
         */
        _updateSwipeActionElement(target, action, xDelta) {
            const actionOptions = this.actions[action];
            if (actionOptions) {
                const swipeActionElement = this._getSwipeActionElement(target, action);
                const max = this._getSwipeData(target, 'actionThreshold')[action];
                swipeActionElement.classList.add(actionOptions.backgroundClassColor);
                swipeActionElement.style.opacity = Math.abs(xDelta / max);
            }
        },

        /**
         * Update the view of action swipe at the correct position if swipeDirection is valid
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {false | 'left' | 'right'} swipeDirection
         * @param {number} left
         * @param {string, 'px', '%'} unit
         */
        _updateSwipeActionPosition(target, swipeDirection, left, unit = 'px') {
            const swipeActionElement = this._getSwipeActionElement(target, swipeDirection);
            if (swipeActionElement) {
                swipeActionElement.style.left = `${left}${unit}`;
            }
        },

        /**
         * Update the view to show the swipe at the correct position
         *
         * @private
         * @param {HTMLElement | EventTarget} target
         * @param {false | 'left' | 'right'} swipeDirection
         * @param {number} left
         */
        _updateSwipePosition(target, swipeDirection, left) {
            target.style.left = `${left}px`;
            this._updateSwipeActionPosition(target, swipeDirection, -left);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {TouchEvent} ev
         */
        _onTouchStart(ev) {
            const target = ev.currentTarget;
            if (!target.matches(this.selectorTarget)) {
                return;
            }

            $(target).data(SWIPE_ITEM_DATA_KEY, {
                touchStart: this._getTouchPosition(ev),
                startLeft: $(target).css('left') === 'auto' ? 0 : parseInt($(target).css('left'), 10),
                swipeDirection: false,
                swipeAxes: false,
                actionThreshold: {},
            });
        },

        /**
         * @private
         * @param {TouchEvent} ev
         */
        _onTouchMove(ev) {
            const target = ev.currentTarget;
            if (!target.matches(this.selectorTarget)) {
                return;
            }

            const touchDelta = this._getTouchDelta(ev, target);
            const swipeDirection = this._getSwipeDirection(touchDelta);

            if (this._getSwipeData(target, 'swipeAxes') === false) {
                this._setSwipeData(target, 'swipeAxes', this._getSwipeAxes(touchDelta));
            }

            if (this._getSwipeData(target, 'swipeAxes') !== SWIPE_AXES.HORIZONTAL) {
                return;
            }
            ev.preventDefault();

            const allowSwipe = this._allowSwipe(ev, swipeDirection);

            // Check if element in the DOM is ready for swipe
            if (!target.classList.contains('o_swipe_current') && allowSwipe) {
                this._addSwipeElement(target);
            }

            if (allowSwipe) {
                this._setSwipeData(target, 'swipeDirection', swipeDirection);
            } else {
                if (!(this._getSwipeData(target, 'swipeDirection') && this._getSwipeData(target, 'swipeDirection') === swipeDirection)) {
                    this._updateSwipePosition(target, swipeDirection, 0);
                }
                return;
            }

            this._updateSwipePosition(target, swipeDirection, touchDelta.xDelta);
            this._updateSwipeActionElement(target, swipeDirection, touchDelta.xDelta);
        },

        /**
         * @private
         * @param {TouchEvent} ev
         */
        async _onTouchEnd(ev) {
            const target = ev.currentTarget;
            if (!target.matches(this.selectorTarget)) {
                return;
            }

            const touchDelta = this._getTouchDelta(ev, target);
            const swipeDirection = this._getSwipeDirection(touchDelta);

            if (this._getSwipeData(target, 'swipeAxes') !== SWIPE_AXES.HORIZONTAL) {
                return;
            }
            ev.preventDefault();

            if (!this._allowSwipe(ev, swipeDirection)) {
                this._restoreDOMLikeBeforeSwipe(target);
                return;
            }

            const swipeDirectionWithThresholdReach = this._isThresholdReach(target, touchDelta, swipeDirection);

            const action = this.actions[swipeDirectionWithThresholdReach];

            if (action) {
                if (swipeDirectionWithThresholdReach) {
                    await this._moveElementAndActionWithAnimation(target, swipeDirectionWithThresholdReach, this._getMaxPosition(swipeDirectionWithThresholdReach), '%');
                }
                if (!(action.avoidRestorePositionElement && action.avoidRestorePositionElement(swipeDirection, target, ev))) {
                    await this._moveElementAndActionWithAnimation(target, swipeDirectionWithThresholdReach, 0);
                }
                this._performSwipeEndAction(ev, action.actionCallback, () => {
                    target.style.left = 0;
                });
            }
            this._restoreDOMLikeBeforeSwipe(target);
        },
    };
});