# -*- coding: utf-8 -*-

from odoo import api, models, fields, _, exceptions


class Challenge(models.Model):
    """
    游戏化挑战 
    分配给具有复发和奖励规则的人员的一组预定义目标 
    如果定义了'user_ids'，并且'period'不同于'one'，则将在每个期间将集合分配给用户（例如：如果选择了'monthly'，则每月每个1号）
    """

    _inherit = "gamification.challenge"

