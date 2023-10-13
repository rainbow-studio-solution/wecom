# -*- coding: utf-8 -*-

import os
import platform
import base64
from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _
from odoo.modules import get_resource_path
import logging

_logger = logging.getLogger(__name__)


class Module(models.Model):
	_inherit = "ir.module.module"

	@api.model
	def get_module_installation_status(self, addon_name=None):
		"""
		获取 addon 是否安装
		"""
		addon = self.sudo().search([("name", "=", addon_name)])
		print(addon)
		if not addon:
			# return {
			#     "exist": False,
			#     "moduleId": 0,
			# }
			return False
		else:
			# addon.button_install()
			# return {
			#     "exist": True,
			#     "moduleId": addon.id,
			# }
			return True

	@api.model
	def upload_office_documents(
		self, file_name, module_name, storage_path, data_base64_str
	):
		"""
		上传office 文档到模块下的静态目录
		"""
		file_format = file_name.split(".")[1]
		print(type(data_base64_str))
		# word_file_binary = base64.b64encode(data_base64)
		today = datetime.today().strftime("%Y%m%d")
		timestamp = datetime.timestamp(datetime.now())

		office_document_store_path = get_resource_path(
			module_name, "static", storage_path, today
		)
		if not os.path.exists(office_document_store_path):
			os.makedirs(office_document_store_path)

		file_path = ""
		if platform.system() == "Linux" or platform.system() == "Darwin":
			file_path = "%s/%s.%s" % (
				office_document_store_path,
				timestamp,
				file_format,
			)
		else:
			file_path = "%s\\%s.%s" % (
				office_document_store_path,
				timestamp,
				file_format,
			)

		web_path = "/%s/static/%s/%s/%s.%s" % (
			module_name,
			storage_path,
			today,
			timestamp,
			file_format,
		)
		# print(file_path,web_path)

		result = {}
		try:
			with open(file_path, "wb") as f:
				f.write(base64.b64decode(data_base64_str))
		except Exception as e:
			result = {
				"state": False,
				"file_name": "",
				"web_path": "",
				"msg": _("Failed to upload file %s, reason:%s" % (file_name, str(e))),
			}
		else:
			new_file_name = "%s.%s" % (timestamp, file_format)
			result = {
				"state": True,
				"file_name": file_name,
				"new_file_name": new_file_name,
				"web_path": web_path,
				"msg": _("Successfully uploaded %s" % file_name),
			}
		return result
