# -*- coding: utf-8 -*-

import operator
import requests
import logging
from urllib.parse import quote, unquote
import pandas as pd

# pd.set_option("max_colwidth", 4096)
# pd.set_option("max_colwidth", 10)

from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class WecomServerApiError(models.Model):
    _name = "wecom.service_api_error"
    _description = "Wecom Server API Error"
    _order = "sequence"

    name = fields.Char(
        "Error description",
        required=True,
        readonly=True,
    )
    code = fields.Integer(
        "Error code",
        required=True,
        readonly=True,
    )

    method = fields.Html(
        "Treatment method",
        readonly=True,
    )

    sequence = fields.Integer(default=0)

    def get_error_by_code(self, code):
        res = self.search(
            [("code", "=", code)],
            limit=1,
        )
        return {
            "code": res.code,        # type: ignore
            "name": res.name,    # type: ignore
            "method": res.method, # type: ignore
        }

    def cron_pull_global_error_code(self):
        self.get_api_error_eode()

    @api.model
    def get_api_error_eode(self):
        """
        使用爬虫爬取 全局错误码
        URL的一般格式为： protocol://hostname[:port]/path/[;parameters][?query]#fragment
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        url = ir_config.get_param("wecom.global_error_code_url")

        codes = ir_config.get_param("wecom.global_error_code_item_selection_code")

        state = False
        msg= ""
        try:
            _logger.info(_("Start pulling the global error code of WeCom."))
            page_text = requests.get(url=url).text
            tree = etree.HTML(page_text)     # type: ignore

            codes_elements = tree.xpath(codes)

            methods = []

            for code_element in codes_elements:
                code_element_str = code_element.xpath("text()")[0]
                error_code = code_element_str.split("：", 1)[1:][0]

                method_element = code_element.getnext()
                method = etree.tostring(method_element, encoding="utf-8", pretty_print=True ).decode()   # type: ignore

                if " " in error_code:
                    # 一个元素存在多个错误码
                    multiple_codes = error_code.split(" ", 1)
                    for multiple_code in multiple_codes:
                        multiple_dic = {}
                        multiple_dic["code"] = multiple_code
                        multiple_dic["method"] = method
                        methods.append(multiple_dic)
                else:
                    dic = {}
                    dic["code"] = error_code
                    dic["method"] = method
                    methods.append(dic)

            table = tree.xpath("//div[@class='cherry-table-container']/table")  # 取出表格
            table = etree.tostring(
                table[0], encoding="utf-8"   # type: ignore
            ).decode()  # 将第一个表格转成string格式
            table = table.replace("<th>错误码</th>", "<th>code</th>")
            table = table.replace("<th>错误说明</th>", "<th>name</th>")
            table = table.replace("<th>排查方法</th>", "<th>method</th>")

            df = pd.read_html(table, encoding="utf-8", header=0)[0]  # pandas读取table
            if 'Unnamed: 3' in df.columns:
                del df['Unnamed: 3']

            error_results = list(df.T.to_dict().values())  # 转换成列表嵌套字典的格式

            errors = []
            for index, error in enumerate(error_results):
                if (error["code"] == 40054) or (error["code"] == 40055):
                    error["method"] = self.replaceMethod(str(error["code"]), methods)
                elif error["method"] == "查看帮助":
                    error["method"] = self.replaceMethod(str(error["code"]), methods)
                error["sequence"] = index
                errors.append(error)

        except Exception as e:
            msg = _("Failed to pull WeCom global error code, reason:%s") % str(e)
            _logger.warning(msg)
            state = False
        else:
            # 写入到odoo
            for error in errors:
                res = self.search(
                    [("code", "=", error["code"])],
                    limit=1,
                )
                if not res:
                    self.sudo().create(
                        {
                            "code": error["code"],
                            "name": error["name"],
                            "method": error["method"],
                            "sequence": error["sequence"],
                        }
                    )
                else:
                    res.sudo().write(    # type: ignore
                        {
                            "name": error["name"],
                            "method": error["method"],
                            "sequence": error["sequence"],
                        }
                    )
            state = True
            msg = _("Successfully pulled the WeCom global error code!")
            _logger.info(msg)

        finally:
            return {"state": state, "msg": msg}

    def replaceMethod(self, code, methods):
        """
        替换 排查方法
        """
        df = pd.DataFrame(methods)
        method = df["method"][df["code"] == code].to_string(
            index=False
        )  # 取 包含指定code 值的 "method"列

        if method[-2:] == "\\n":
            method = method[:-2] # 去掉最后的换行符

        return method

    def getMiddleStr(self, content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]
