# 如何使用封装好的企业微信API

## Demo：获取企业微信部门列表

```
# 初始化API 模型对象
# 参数为：公司对象，secret字段的名称，以及令牌类型
wxapi = self.env["wecom.service_api"].init_api(
    company, "contacts_secret", "contacts"
)

# "DEPARTMENT_LIST"是请求的API类型，通过API类型生成 调用企业微信的API URL
response = wxapi.httpCall(
    self.env["wecom.service_api_list"].get_server_api_call(
        "DEPARTMENT_LIST"
    ),
    {
        "id": str(company.contacts_sync_hr_department_id),
    },
)
```

## 建议：调用API的时候，尽量使用 try except 抛出异常的方式
```
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


try:
    ....
    ....
    ....
except ApiException as e:
    # 弹框显示异常
    return self.env["wecom.tools"].ApiExceptionDialog(ex)
```