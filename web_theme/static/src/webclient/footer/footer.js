/** @odoo-module **/

import { browser } from '@web/core/browser/browser';
import { useBus, useService } from '@web/core/utils/hooks';
import { _t } from '@web/core/l10n/translation';
import { session } from '@web/session';
import { fuzzyLookup } from '@web/core/utils/search';
const legacy_session = require('web.session'); // 需要访问allowed_company_ids，故使用 legacy 的代码，不能使用 @web/session

const {
	Component,
	onMounted,
	onRendered,
	onWillRender,
	onWillDestroy,
	onWillUnmount,
	onPatched,
	onWillUpdateProps,
	useExternalListener,
	useEffect,
	useState,
	useRef
} = owl;

export class Footer extends Component {
	setup() {
		super.setup();

		// 主题
		this.theme = session.theme;
		this.menu_layout_mode = this.theme['menu_layout_mode'];
		this.display_footer = this.theme['display_footer'];
		this.display_footer_copyright = this.theme['display_footer_copyright'];
		this.display_footer_document = this.theme['display_footer_document'];
		this.display_footer_support = this.theme['display_footer_support'];

		this.copyright = this.theme['copyright'];
		this.documentation_url = this.theme['documentation_url'];
		this.support_url = this.theme['support_url'];
	}
}
Footer.template = 'web_theme.Footer';
Footer.components = {};
