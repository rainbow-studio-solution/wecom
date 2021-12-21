WECOM_USER_MAPPING_ODOO_EMPLOYEE = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称;
    "Department": "department_ids",  # 成员部门列表，仅返回该应用有查看权限的部门id
    "MainDepartment": "department_id",  # 主部门
    "IsLeaderInDept": "",  # 表示所在部门是否为上级，0-否，1-是，顺序与Department字段的部门逐一对应
    "DirectLeader": "",  # 直属上级
    "Mobile": "mobile_phone",  # 手机号码
    "Position": "job_title",  # 职位信息
    "Gender": "",  # 性别，1表示男性，2表示女性
    "Email": "work_email",  # 邮箱;
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Avatar": "avatar",  # 头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可。
    "Alias": "alias",  # 成员别名
    "Telephone": "work_phone",  # 座机;
    "Address": "work_location",  # 地址;
    "ExtAttr": {
        "Type": "",  # 扩展属性类型: 0-本文 1-网页
        "Text": "",  # 文本属性类型，扩展属性类型为0时填写
        "Value": "",  # 文本属性内容
        "Web": "",  # 网页类型属性，扩展属性类型为1时填写
        "Title": "",  # 网页的展示标题
        "Url": "",  # 网页的url
    },  # 扩展属性;
}
