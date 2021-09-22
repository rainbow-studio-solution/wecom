# -*- coding: utf-8 -*-

# import werkzeug
from werkzeug.urls import Href
import requests
import hashlib
from odoo import api, fields, models, _
from urllib import parse
from odoo.exceptions import RedirectWarning, UserError


def urlplus(url, params):
    return Href(url)(params or None)
    # return werkzeug.Href(url)(params or None)


class Partner(models.Model):
    _inherit = "res.partner"

    def get_lat_and_lon(self, address=None):
        """
        [summary]
        用户可通过该功能，将结构化地址（省/市/区/街道/门牌号）解析为对应的位置坐标。地址结构越完整，地址内容越准确，解析的坐标精度越高
        请求示例:   http://api.map.baidu.com/geocoding/v3/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation
        请求方式：  GET
        文档地址:   https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding&diff=prev&oldid=13599       
        """
        baidu_maps_api_key = (
            self.env["website"].get_current_website().baidu_maps_api_key
        )

        request_url = (
            "http://api.map.baidu.com/geocoding/v3?address=%s&output=json&ak=%s"
            % (address, baidu_maps_api_key)
        )
        # headers = {"Content-type": "application/x-www-form-urlencoded"}
        headers = {"Content-type": "application/json", "Accept": "text/plain"}

        req = requests.get(request_url, headers=headers)
        req.raise_for_status()
        data = req.json()

        if data["status"] != 0:
            pass
        else:
            return "%s,%s" % (
                data["result"]["location"]["lng"],
                data["result"]["location"]["lat"],
            )

    def baidu_map_img(self, zoom=15, width=298, height=298):
        """[summary]
        文档： https://lbsyun.baidu.com/index.php?title=static
        服务地址:   https://api.map.baidu.com/staticimage/v2
        
        Args:
            zoom (int, optional): [description]. Defaults to 15.
            width (int, optional): [description]. Defaults to 298.
            height (int, optional): [description]. Defaults to 298.

        Returns:
            [type]: [description]
        """
        baidu_maps_api_key = (
            self.env["website"].get_current_website().baidu_maps_api_key
        )

        country_name = self.country_id and self.country_id.name or ""
        state_name = self.state_id and self.state_id.name or ""
        city_name = self.city or ""
        street_name = self.street or ""
        street2_name = self.street2 or ""
        coordinate = self.get_lat_and_lon(
            "%s%s%s" % (state_name, city_name, street_name,)
        )  # 坐标

        # labelsStyle：label, font, bold, fontSize, fontColor, background。 各参数使用","分隔，如有默认值则可为空。
        """
        参数名称    说明                                        默认值
        content    标签内容，字符最大数目为15                    无
        font        0：微软雅黑；                               0
                    1：宋体；
                    2：Times New Roman;
                    3：Helvetica
        bold        0：非粗体；                                 0
                    1：粗体
        fontSize    字体大小，可选值[1,72]                      10
        fontColor   字体颜色，取值范围：[0x000000, 0xffffff]    0xFFFFFF
        background  背景色，取值范围：[0x000000, 0xffffff]      0x5288d8
        """
        # "1,14,0xFF0000,0xffffff,1"
        labelStyle = "%s,%s,%s,%s,%s,%s" % (self.name, 0, 12, 0xFF0000, 0xFFFFFF, 0)

        params = {
            "ak": baidu_maps_api_key,
            "markers": coordinate,
            "center": coordinate,
            "height": "%s" % height,
            "width": "%s" % width,
            "zoom": zoom,
            "copyright": 1,
            "labels": coordinate,
            # "labelStyles": "%s,%s" % (self.name, "1,14,0xFF0000,0xffffff,1"),
            "labelStyles": "%s" % (labelStyle),
        }

        return urlplus("//api.map.baidu.com/staticimage/v2", params)

    def baidu_map_link(self):
        """[summary]
        文档：http://lbsyun.baidu.com/index.php?title=uri
        Returns:
            [type]: [description]
        """
        partner_name = self.name
        city_name = self.city or ""
        street_name = self.street or ""
        street2_name = self.street2 or ""
        params = {
            "address": "%s,%s,%s" % (city_name, street_name, street2_name),
            "output": "html",
            "city": "%s" % city_name,
            "src": "odoo",
        }

        return urlplus("//api.map.baidu.com/geocoder", params)

