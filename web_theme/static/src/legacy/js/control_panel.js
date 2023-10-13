odoo.define('web_theme.ControlPanel', function (require) {
	'use strict';

	const ControlPanel = require('web.ControlPanel');
	const { device } = require('web.config');
	const { patch } = require('web.utils');

	const { onMounted, useExternalListener, useRef, useState, useEffect } = owl;
	const STICKY_CLASS = 'o_mobile_sticky';

	if (!device.isMobile) {
		return;
	}

	/**
	 * Control panel: mobile layout
	 *
	 * This patch handles the scrolling behaviour of the control panel in a mobile
	 * environment: the panel sticks to the top of the window when scrolling into
	 * the view. It is revealed when scrolling up and hiding when scrolling down.
	 * The panel's position is reset to default when at the top of the view.
	 */
	patch(ControlPanel.prototype, 'web_theme.ControlPanel', {
		setup() {
			this._super();

			this.controlPanelRef = useRef('controlPanel');

			this.state = useState({
				showSearchBar: false,
				showMobileSearch: false,
				showViewSwitcher: false
			});

			this.onWindowClick = this._onWindowClick.bind(this);
			this.onScrollThrottled = this._onScrollThrottled.bind(this);

			useExternalListener(window, 'click', this.onWindowClick);
			useEffect(() => {
				const scrollingEl = this._getScrollingElement();
				scrollingEl.addEventListener('scroll', this.onScrollThrottled);
				this.controlPanelRef.el.style.top = '0px';
				return () => {
					scrollingEl.removeEventListener('scroll', this.onScrollThrottled);
				};
			});
			onMounted(() => {
				this.oldScrollTop = 0;
				this.lastScrollTop = 0;
				this.initialScrollTop = this._getScrollingElement().scrollTop;
			});
		},

		//---------------------------------------------------------------------
		// Private
		//---------------------------------------------------------------------

		_getScrollingElement() {
			return this.controlPanelRef.el.parentElement;
		},

		/**
		 * Get today's date (number).
		 * @private
		 * @returns {number}
		 */
		_getToday() {
			return new Date().getDate();
		},

		/**
		 * Reset mobile search state
		 * @private
		 */
		_resetSearchState() {
			Object.assign(this.state, {
				showSearchBar: false,
				showMobileSearch: false,
				showViewSwitcher: false
			});
		},

		//---------------------------------------------------------------------
		// Handlers
		//---------------------------------------------------------------------

		/**
		 * Show or hide the control panel on the top screen.
		 * The function is throttled to avoid refreshing the scroll position more
		 * often than necessary.
		 * @private
		 */
		_onScrollThrottled() {
			if (!this.controlPanelRef.el || this.isScrolling) {
				return;
			}
			this.isScrolling = true;
			requestAnimationFrame(() => (this.isScrolling = false));

			const scrollTop = this._getScrollingElement().scrollTop;
			const delta = Math.round(scrollTop - this.oldScrollTop);

			if (scrollTop > this.initialScrollTop) {
				// Beneath initial position => sticky display
				this.controlPanelRef.el.classList.add(STICKY_CLASS);
				this.lastScrollTop =
					delta < 0
						? // Going up
						  Math.min(0, this.lastScrollTop - delta)
						: // Going down | not moving
						  Math.max(-this.controlPanelRef.el.offsetHeight, -this.controlPanelRef.el.offsetTop - delta);
				this.controlPanelRef.el.style.top = `${this.lastScrollTop}px`;
			} else {
				// Above initial position => standard display
				this.controlPanelRef.el.classList.remove(STICKY_CLASS);
				this.lastScrollTop = 0;
			}
			this.oldScrollTop = scrollTop;
		},

		/**
		 * Reset mobile search state on switch view.
		 * @private
		 */
		_onSwitchView() {
			this._resetSearchState();
		},

		/**
		 * @private
		 * @param {MouseEvent} ev
		 */
		_onWindowClick(ev) {
			if (this.state.showViewSwitcher && !ev.target.closest('.o_cp_switch_buttons')) {
				this.state.showViewSwitcher = false;
			}
		}
	});

	patch(ControlPanel, 'web_theme.ControlPanel', {
		template: 'web_theme._ControlPanel'
	});
});
