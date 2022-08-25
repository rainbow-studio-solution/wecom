# -*- coding: utf-8 -*-

from odoo import api, models, tools, _

import logging

_logger = logging.getLogger(__name__)

class WecomApiToolsAction(models.AbstractModel):
    _name = "wecomapi.tools.data"
    _description = "Wecom API Tools - Data"


    def union_data_set(self, set1, set2):
        """
        2个数据集的并集
        :param set1: 数据集1
        :param set2: 数据集2
        :returns: 并集 的
        """
        # set1.union(set2)
        return set1 | set2

    def difference_data_set(self, set1, set2):
        """
        2个数据集的差集
        :param set1: 数据集1
        :param set2: 数据集2
        :returns: 差集
        """
        # set1.difference(set2)
        return set1 - set2

    def intersection_data_set(self, set1, set2):
        """
        2个数据集的交集
        :param set1: 数据集1
        :param set2: 数据集2
        :returns: 交集
        """
        # set1.intersection(set2)
        return set1 & set2