# -*- coding: utf-8 -*-

from odoo import api, models, tools, _

class WecomApiToolsDictionary(models.AbstractModel):
    _name = "wecomapi.tools.dictionary"
    _description = "Wecom API Tools - Dictionary"


    def check_dictionary_keywords(self, dictionary, key):
        """
        检查字典中是否存在key
        """
        # dictionary, key = (self.value[0], self.value[1])
        if key in dictionary.keys():
            return dictionary[key]
        else:
            return None