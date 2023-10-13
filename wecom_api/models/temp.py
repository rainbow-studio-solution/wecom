# -*- coding: utf-8 -*-

import requests
import pandas as pd
pd.set_option('display.max_columns', 10)
pd.set_option("max_colwidth", 200)
pd.set_option("display.width", 200)
pd.set_option('display.max_rows', 200)
from lxml import etree


url = "https://developer.work.weixin.qq.com/document/path/90313"
anchor = "//h2[@data-sign='12309549435022fd54b0549f5968b4c2']"
codes = "//h5"
methods ="//p[@data-type='p']"

page_text = requests.get(url=url).text
tree = etree.HTML(page_text)     # type: ignore

anchor_elemen = tree.xpath(anchor)
codes_elements = tree.xpath(codes)
methods_elements = tree.xpath(methods)

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
    error["sequence"] = index

    errors.append(error)
df = pd.DataFrame(errors)
print(df)
