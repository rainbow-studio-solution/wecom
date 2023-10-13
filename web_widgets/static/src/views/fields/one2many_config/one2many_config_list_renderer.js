/** @odoo-module */

import { useSortable } from '@web/core/utils/sortable';
import { ListRenderer } from '@web/views/list/list_renderer';

import { Markup } from 'web.utils';
import { usePopover } from '@web/core/popover/popover_hook';

const { Component, useEffect, useRef } = owl;

class One2ManyConfigPopOver extends Component {
	setup() {
		super.setup();

		// useSortable({
		//     enable: false,
		// })
	}
}
One2ManyConfigPopOver.template = 'web_widgets.One2ManyConfigPopOver';

export class One2ManyConfigListRenderer extends ListRenderer {
	setup() {
		super.setup();
		this.button = useRef('showTooltipButton');
		this.popover = usePopover();

		let help_field = this.props.help_field;
		if (help_field != '') {
			this.help_field = help_field;
			let help_string = this.props.help_string;
			this.help_string = help_string;
		}
		// console.log("setup", this.props);
	}

	get title() {
		return this.props.help_string;
	}

	onClickSortColumn(column) {
		// 覆盖父类的方法，不执行排序
		// 不允许排序
		// console.log("onClickSortColumn", column);
		return;
	}

	getColumnClass(column) {
		// 移除 "cursor-pointer" 类
		let classNames = super.getColumnClass(column);
		classNames = classNames.replace('cursor-pointer', '');
		return classNames;
	}

	_onOpenPopover(ev, record) {
		let help_field = ev.target.dataset.helpField;
		let help_content = record.data[help_field];
		if (this.popoverCloseFn) {
			this.closePopover();
		}
		this.popoverCloseFn = this.popover.add(
			ev.currentTarget,
			this.constructor.components.Popover,
			{
				title: this.title,
				content: Markup(help_content),
				onClose: this.closePopover
			},
			{
				position: 'left'
			}
		);
	}
	closePopover() {
		this.popoverCloseFn();
		this.popoverCloseFn = null;
	}
}

One2ManyConfigListRenderer.template = 'web_widgets.One2ManyConfigListRenderer';
One2ManyConfigListRenderer.recordRowTemplate = 'web_widgets.One2ManyConfigListRenderer.RecordRow';
One2ManyConfigListRenderer.props = [...ListRenderer.props, 'help_field', 'help_string'];
One2ManyConfigListRenderer.components = {
	...ListRenderer.components,
	Popover: One2ManyConfigPopOver
};
