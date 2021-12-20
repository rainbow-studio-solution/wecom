# -*- coding: utf-8 -*-

from lxml import etree as ET
from odoo import api, fields, models, _


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    def wecom_event_change_contact_user(self, type):
        """ 
        <xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[sys]]></FromUserName> 
            <CreateTime>1403610513</CreateTime>
            <MsgType><![CDATA[event]]></MsgType>
            <Event><![CDATA[change_contact]]></Event>
            <ChangeType>create_user</ChangeType>
            <UserID><![CDATA[zhangsan]]></UserID>
            <Name><![CDATA[张三]]></Name>
            <Department><![CDATA[1,2,3]]></Department>
            <MainDepartment>1</MainDepartment>
            <IsLeaderInDept><![CDATA[1,0,0]]></IsLeaderInDept>
            <Position><![CDATA[产品经理]]></Position>
            <Mobile>13800000000</Mobile>
            <Gender>1</Gender>
            <Email><![CDATA[zhangsan@gzdev.com]]></Email>
            <Status>1</Status>
            <Avatar><![CDATA[http://wx.qlogo.cn/mmopen/ajNVdqHZLLA3WJ6DSZUfiakYe37PKnQhBIeOQBO4czqrnZDS79FH5Wm5m4X69TBicnHFlhiafvDwklOpZeXYQQ2icg/0]]></Avatar>
            <Alias><![CDATA[zhangsan]]></Alias>
            <Telephone><![CDATA[020-123456]]></Telephone>
            <Address><![CDATA[广州市]]></Address>
            <ExtAttr>
                <Item>
                <Name><![CDATA[爱好]]></Name>
                <Type>0</Type>
                <Text>
                    <Value><![CDATA[旅游]]></Value>
                </Text>
                </Item>
                <Item>
                <Name><![CDATA[卡号]]></Name>
                <Type>1</Type>
                <Web>
                    <Title><![CDATA[企业微信]]></Title>
                    <Url><![CDATA[https://work.weixin.qq.com]]></Url>
                </Web>
                </Item>
            </ExtAttr>
        </xml>
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        result = {}

        for event, element in ET.iterparse(xml_tree):
            print(element.tag, element.text)
