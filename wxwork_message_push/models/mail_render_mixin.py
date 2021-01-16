# -*- coding: utf-8 -*-
import babel
import copy
import functools
import logging
import re
import dateutil.relativedelta as relativedelta
from werkzeug import urls

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import safe_eval

_logger = logging.getLogger(__name__)

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment

    jinja_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    jinja_template_env.globals.update(
        {
            "str": str,
            "quote": urls.url_quote,
            "urlencode": urls.url_encode,
            "datetime": safe_eval.datetime,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "reduce": functools.reduce,
            "map": map,
            "round": round,
            # dateutil.relativedelta is an old-style class and cannot be directly
            # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
            # is needed, apparently.
            "relativedelta": lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
        }
    )
    jinja_safe_template_env = copy.copy(jinja_template_env)
    jinja_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    @api.model
    def _render_wxwork_message_template_qweb(
        self, template_src, model, res_ids, add_context=None
    ):
        view = (
            self.env.ref(template_src, raise_if_not_found=False)
            or self.env["ir.ui.view"]
        )
        results = dict.fromkeys(res_ids, u"")
        if not view:
            return results

        # prepare template variables
        variables = self._render_qweb_eval_context()
        if add_context:
            variables.update(**add_context)

        for record in self.env[model].browse(res_ids):
            variables["object"] = record
            try:
                render_result = view._render(
                    variables, engine="ir.qweb", minimal_qcontext=True
                )
            except Exception as e:
                _logger.info(
                    "Failed to render template : %s (%d)" % (template_src, view.id),
                    exc_info=True,
                )
                raise UserError(
                    _("Failed to render template : %s (%d)") % (template_src, view.id)
                )
            results[record.id] = render_result

        return results

    @api.model
    def _render_wxwork_message_template_jinja(
        self, template_txt, model, res_ids, add_context=None
    ):
        """ 
        使用jinja在模型给定的记录和ID列表上呈现基于字符串的模板。

        除了_render_jinja_eval_context给出的通用评估上下文外，还根据每个记录添加了一些新变量。

          * ``object``: 记录基于哪个模板呈现；

        :param str template_txt: 呈现的模板文字
        :param str model: 我们要在其上执行呈现的记录的模型名称
        :param list res_ids: 记录ID列表（均属于同一模型）

        :return dict: {res_id: 根据记录呈现的模板字符串}
        """
        no_autoescape = self._context.get("safe")
        results = dict.fromkeys(res_ids, u"")
        if not template_txt:
            return results

        # try to load the template
        # try:
        #     print("jinja", template_txt)
        #     jinja_env = jinja_safe_template_env if no_autoescape else jinja_template_env
        #     template = jinja_env.from_string(tools.ustr(template_txt))
        # except Exception:
        #     _logger.info("Failed to load template %r", template_txt, exc_info=True)
        #     return results
        template = template_txt
        # prepare template variables
        variables = self._render_jinja_eval_context()
        if add_context:
            variables.update(**add_context)
        safe_eval.check_values(variables)

        # TDE CHECKME
        # records = self.env[model].browse(it for it in res_ids if it)  # filter to avoid browsing [None]
        if any(r is None for r in res_ids):
            raise ValueError(_("Unsuspected None"))

        for record in self.env[model].browse(res_ids):
            variables["object"] = record
            try:
                render_result = template.render(variables)
            except Exception as e:
                _logger.info("Failed to render template : %s" % e, exc_info=True)
                raise UserError(_("Failed to render template : %s", e))
            if render_result == u"False":
                render_result = u""
            results[record.id] = render_result
        print("jinja", results)
        return results

    @api.model
    def _render_wxwork_message_template_postprocess(self, rendered):
        """ 
        后处理的工具方法。 在这种方法中，我们确保将本地链接('/shop/Basil-1')替换为全局链接 ('https://www.mygardin.com/hop/Basil-1').

        :param rendered:  ``_render_template``的结果
        :return dict: 渲染的更新版本
        """

        for res_id, html in rendered.items():
            rendered[res_id] = self._replace_local_links(html)
        return rendered

    @api.model
    def _render_wxwork_message_template(
        self,
        template_src,
        model,
        res_ids,
        engine="jinja",
        add_context=None,
        post_process=False,
    ):
        """ 
        使用给定的渲染引擎在给定的模型/ res_ids设计的记录上渲染给定的字符串。 目前仅支持jinja。

        :param str template_src: 要渲染的模板文本（jinja）或视图的XML ID（qweb），可以清除，但是，我们很着急
        :param str model: 我们要在其上执行呈现的记录的模型名称
        :param list res_ids: 记录ID列表（均属于同一模型）
        :param string engine: jinja
        :param post_process: 执行渲染的str / html后处理（请参见``_render_wxwork_message_template_postprocess``）

        :return dict: {res_id: 根据记录呈现的模板字符串}
        """
        # print(res_ids, template_src)
        print(template_src, model, res_ids, add_context)
        if not isinstance(res_ids, (list, tuple)):
            raise ValueError(
                _("Template rendering should be called only using on a list of IDs.")
            )
        if engine not in ("jinja", "qweb"):
            # print("no qweb jinja")
            raise ValueError(_("Template rendering supports only jinja or qweb."))

        if engine == "qweb":
            # print("qweb")
            rendered = self._render_wxwork_message_template_qweb(
                template_src, model, res_ids, add_context=add_context
            )
        else:
            # 处理企业微信消息内容
            rendered = self._render_wxwork_message_template_jinja(
                template_src, model, res_ids, add_context=add_context
            )
        if post_process:
            # print("post_process")
            rendered = self._render_wxwork_message_template_postprocess(rendered)

        return rendered

    def _render_wxwork_message_field(
        self, field, res_ids, compute_lang=False, set_lang=False, post_process=False
    ):
        """
        给定一些记录ID，渲染在所有记录上呈现的模板的给定字段。

        :param list res_ids: 记录ID的列表（均属于self.model定义的同一模型）
        :param compute_lang: 根据template.lang计算渲染语言
        :param set_lang: 强制语言
        :param post_process: 执行渲染的str / html后处理（请参见 '_render_wxwork_message_template'）

        :return dict: {res_id：基于记录的呈现模板的字符串}
        """

        self.ensure_one()
        if compute_lang:
            templates_res_ids = self._classify_per_lang(res_ids)
        elif set_lang:
            templates_res_ids = {set_lang: (self.with_context(lang=set_lang), res_ids)}
        else:
            templates_res_ids = {self._context.get("lang"): (self, res_ids)}

        return dict(
            (res_id, rendered)
            for lang, (template, tpl_res_ids) in templates_res_ids.items()
            for res_id, rendered in template._render_wxwork_message_template(
                template[field], template.model, tpl_res_ids, post_process=post_process
            ).items()
        )

