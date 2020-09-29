# -*- coding:utf-8 -*-

"""
全局错误码
企业应用每次调用接口时，可能获得正确或错误的返回码，企业可以根据返回码信息调试接口，排查错误。
注意：开发者的程序应该根据errcode来判断出错的情况，而不应该依赖errmsg来匹配，因为errmsg可能会调整。
=============
更新时间：2020-09-29
"""

ERRCODE = {
    "-1": "系统繁忙",
    "0": "请求成功",
    "40001": "不合法的secret参数",
    "40003": "无效的UserID",
    "40004": "不合法的媒体文件类型",
    "40005": "不合法的type参数",
    "40006": "不合法的文件大小",
    "40007": "不合法的media_id参数",
    "40008": "不合法的msgtype参数",
    "40009": "上传图片大小不是有效值",
    "40011": "上传视频大小不是有效值",
    "40013": "不合法的CorpID",
    "40014": "不合法的access_token",
    "40016": "不合法的按钮个数",
    "40017": "不合法的按钮类型",
    "40018": "不合法的按钮名字长度",
    "40019": "不合法的按钮KEY长度",
    "40020": "不合法的按钮URL长度",
    "40022": "不合法的子菜单级数",
    "40023": "不合法的子菜单按钮个数",
    "40024": "不合法的子菜单按钮类型",
    "40025": "不合法的子菜单按钮名字长度",
    "40026": "不合法的子菜单按钮KEY长度",
    "40027": "不合法的子菜单按钮URL长度",
    "40029": "不合法的oauth_code",
    "40031": "不合法的UserID列表",
    "40032": "不合法的UserID列表长度",
    "40033": "不合法的请求字符",
    "40035": "不合法的参数",
    "40050": "chatid不存在",
    "40054": "不合法的子菜单url域名",
    "40055": "不合法的菜单url域名",
    "40056": "不合法的agentid",
    "40057": "不合法的callbackurl或者callbackurl验证失败",
    "40058": "不合法的参数",
    "40059": "不合法的上报地理位置标志位",
    "40063": "参数为空",
    "40066": "不合法的部门列表",
    "40068": "不合法的标签ID",
    "40070": "指定的标签范围结点全部无效",
    "40071": "不合法的标签名字",
    "40072": "不合法的标签名字长度",
    "40073": "不合法的openid",
    "40074": "news消息不支持保密消息类型",
    "40077": "不合法的pre_auth_code参数",
    "40078": "不合法的auth_code参数",
    "40080": "不合法的suite_secret",
    "40082": "不合法的suite_token",
    "40083": "不合法的suite_id",
    "40084": "不合法的permanent_code参数",
    "40085": "不合法的的suite_ticket参数",
    "40086": "不合法的第三方应用appid",
    "40088": "jobid不存在",
    "40089": "批量任务的结果已清理",
    "40091": "secret不合法",
    "40092": "导入文件存在不合法的内容",
    "40093": "不合法的jsapi_ticket参数",
    "40094": "不合法的URL",
    "40096": "不合法的外部联系人userid",
    "40097": "该成员尚未离职",
    "40098": "接替成员尚未实名认证",
    "40099": "接替成员的外部联系人数量已达上限",
    "40100": "此用户的外部联系人已经在转移流程中",
    "41001": "缺少access_token参数",
    "41002": "缺少corpid参数",
    "41004": "缺少secret参数",
    "41006": "缺少media_id参数",
    "41008": "缺少auth code参数",
    "41009": "缺少userid参数",
    "41010": "缺少url参数",
    "41011": "缺少agentid参数",
    "41033": "缺少 description 参数",
    "41035": "缺少外部联系人userid参数",
    "41016": "缺少title参数",
    "41019": "缺少 department 参数",
    "41017": "缺少tagid参数",
    "41021": "缺少suite_id参数",
    "41022": "缺少suite_access_token参数",
    "41023": "缺少suite_ticket参数",
    "41024": "缺少secret参数",
    "41025": "缺少permanent_code参数",
    "42001": "access_token已过期",
    "42007": "pre_auth_code已过期",
    "42009": "suite_access_token已过期",
    "43004": "指定的userid未绑定微信或未关注微工作台（原企业号）",
    "44001": "多媒体文件为空",
    "44004": "文本消息content参数为空",
    "45001": "多媒体文件大小超过限制",
    "45002": "消息内容大小超过限制",
    "45004": "应用description参数长度不符合系统限制",
    "45007": "语音播放时间超过限制",
    "45008": "图文消息的文章数量不符合系统限制",
    "45009": "接口调用超过限制",
    "45022": "应用name参数长度不符合系统限制",
    "45024": "帐号数量超过上限",
    "45026": "触发删除用户数的保护",
    "45032": "图文消息author参数长度超过限制",
    "45033": "接口并发调用超过限制",
    "46003": "菜单未设置",
    "46004": "指定的用户不存在",
    "48002": "API接口无权限调用",
    "48003": "不合法的suite_id",
    "48004": "授权关系无效",
    "48005": "API接口已废弃",
    "50001": "redirect_url未登记可信域名",
    "50002": "成员不在权限范围",
    "50003": "应用已禁用",
    "60001": "部门长度不符合限制",
    "60003": "部门ID不存在",
    "60004": "父部门不存在",
    "60005": "部门下存在成员",
    "60006": "部门下存在子部门",
    "60007": "不允许删除根部门",
    "60008": "部门已存在",
    "60009": "部门名称含有非法字符",
    "60010": "部门存在循环关系",
    "60011": "指定的成员/部门/标签参数无权限",
    "60012": "不允许删除默认应用",
    "60020": "访问ip不在白名单之中",
    "60028": "不允许修改第三方应用的主页 URL",
    "60102": "UserID已存在",
    "60103": "手机号码不合法",
    "60104": "手机号码已存在",
    "60105": "邮箱不合法",
    "60106": "邮箱已存在",
    "60107": "微信号不合法",
    "60110": "用户所属部门数量超过限制",
    "60111": "UserID不存在",
    "60112": "成员name参数不合法",
    "60123": "无效的部门id",
    "60124": "无效的父部门id",
    "60125": "非法部门名字",
    "60127": "缺少department参数",
    "60129": "成员手机和邮箱都为空",
    "72023": "发票已被其他公众号锁定",
    "72024": "发票状态错误",
    "72037": "存在发票不属于该用户",
    "80001": "可信域名不正确，或者无ICP备案",
    "81001": "部门下的结点数超过限制（3W）",
    "81002": "部门最多15层",
    "81011": "无权限操作标签",
    "81013": "UserID、部门ID、标签ID全部非法或无权限",
    "81014": "标签添加成员，单次添加user或party过多",
    "82001": "指定的成员/部门/标签全部无效",
    "82002": "不合法的PartyID列表长度",
    "82003": "不合法的TagID列表长度",
    "84014": "成员票据过期",
    "84015": "成员票据无效",
    "84019": "缺少templateid参数",
    "84020": "templateid不存在",
    "84021": "缺少register_code参数",
    "84022": "无效的register_code参数",
    "84023": "不允许调用设置通讯录同步完成接口",
    "84024": "无注册信息",
    "84025": "不符合的state参数",
    "84052": "缺少caller参数",
    "84053": "缺少callee参数",
    "84054": "缺少auth_corpid参数",
    "84055": "超过拨打公费电话频率",
    "84056": "被拨打用户安装应用时未授权拨打公费电话权限",
    "84057": "公费电话余额不足",
    "84058": "caller 呼叫号码不支持",
    "84059": "号码非法",
    "84060": "callee 呼叫号码不支持",
    "84061": "不存在外部联系人的关系",
    "84062": "未开启公费电话应用",
    "84063": "caller不存在",
    "84064": "callee不存在",
    "84065": "caller跟callee电话号码一致",
    "84066": "服务商拨打次数超过限制",
    "84067": "管理员收到的服务商公费电话个数超过限制",
    "84071": "不合法的外部联系人授权码",
    "84072": "应用未配置客服",
    "84073": "客服userid不在应用配置的客服列表中",
    "84074": "没有外部联系人权限",
    "85002": "包含不合法的词语",
    "85004": "每企业每个月设置的可信域名不可超过20个",
    "85005": "可信域名未通过所有权校验",
    "86001": "参数 chatid 不合法",
    "86003": "参数 chatid 不存在",
    "86004": "参数 群名不合法",
    "86005": "参数 群主不合法",
    "86006": "群成员数过多或过少",
    "86007": "不合法的群成员",
    "86008": "非法操作非自己创建的群",
    "86101": "仅群主才有操作权限",
    "86201": "参数 需要chatid",
    "86202": "参数 需要群名",
    "86203": "参数 需要群主",
    "86204": "参数 需要群成员",
    "86205": "参数 字符串chatid过长",
    "86206": "参数 数字chatid过大",
    "86207": "群主不在群成员列表",
    "86215": "会话ID已经存在",
    "86216": "存在非法会话成员ID",
    "86217": "会话发送者不在会话成员列表中",
    "86220": "指定的会话参数不合法",
    "90001": "未认证摇一摇周边",
    "90002": "缺少摇一摇周边ticket参数",
    "90003": "摇一摇周边ticket参数不合法",
    "90100": "非法的对外属性类型",
    "90101": "对外属性：文本类型长度不合法",
    "90102": "对外属性：网页类型标题长度不合法",
    "90103": "对外属性：网页url不合法",
    "90104": "对外属性：小程序类型标题长度不合法",
    "90105": "对外属性：小程序类型pagepath不合法",
    "90106": "对外属性：请求参数不合法",
    "91040": "获取ticket的类型无效",
    "301002": "无权限操作指定的应用",
    "301005": "不允许删除创建者",
    "301012": "参数 position 不合法",
    "301013": "参数 telephone 不合法",
    "301014": "参数 english_name 不合法",
    "301015": "参数 mediaid 不合法",
    "301016": "上传语音文件不符合系统要求",
    "301017": "上传语音文件仅支持AMR格式",
    "301021": "参数 userid 无效",
    "301022": "获取打卡数据失败",
    "301023": "useridlist非法或超过限额",
    "301024": "获取打卡记录时间间隔超限",
    "301036": "不允许更新该用户的userid",
    "302003": "批量导入任务的文件中userid有重复",
    "302004": "组织架构不合法（1不是一棵树，2 多个一样的partyid，3 partyid空，4 partyid name 空，5 同一个父节点下有两个子节点 部门名字一样 可能是以上情况，请一一排查）",
    "302005": "批量导入系统失败，请重新尝试导入",
    "302006": "批量导入任务的文件中partyid有重复",
    "302007": "批量导入任务的文件中，同一个部门下有两个子部门名字一样",
    "2000002": "CorpId参数无效",
}


class Errcode(object):
    def __init__(self, errcode):
        self.errcode = errcode
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.errcode in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

    def getErrcode(errcode):
        for case in Errcode(errcode):
            if case(-1):
                return "系统繁忙"
                break
            if case(0):
                return "请求成功"
                break
            if case(40001):
                return "不合法的secret参数"
                break
            if case(40003):
                return "无效的UserID"
                break
            if case(40004):
                return "不合法的媒体文件类型"
                break
            if case(40005):
                return "不合法的type参数"
                break
            if case(40006):
                return "不合法的文件大小"
                break
            if case(40007):
                return "不合法的media_id参数"
                break
            if case(40008):
                return "不合法的msgtype参数"
                break
            if case(40009):
                return "上传图片大小不是有效值"
                break
            if case(40011):
                return "上传视频大小不是有效值"
                break
            if case(40013):
                return "不合法的CorpID"
                break
            if case(40014):
                return "不合法的access_token"
                break
            if case(40016):
                return "不合法的按钮个数"
                break
            if case(40017):
                return "不合法的按钮类型"
                break
            if case(40018):
                return "不合法的按钮名字长度"
                break
            if case(40019):
                return "不合法的按钮KEY长度"
                break
            if case(40020):
                return "不合法的按钮URL长度"
                break
            if case(40022):
                return "不合法的子菜单级数"
                break
            if case(40023):
                return "不合法的子菜单按钮个数"
                break
            if case(40024):
                return "不合法的子菜单按钮类型"
                break
            if case(40025):
                return "不合法的子菜单按钮名字长度"
                break
            if case(40026):
                return "不合法的子菜单按钮KEY长度"
                break
            if case(40027):
                return "不合法的子菜单按钮URL长度"
                break
            if case(40029):
                return "不合法的oauth_code"
                break
            if case(40031):
                return "不合法的UserID列表"
                break
            if case(40032):
                return "不合法的UserID列表长度"
                break
            if case(40033):
                return "不合法的请求字符"
                break
            if case(40035):
                return "不合法的参数"
                break
            if case(40050):
                return "chatid不存在"
                break
            if case(40054):
                return "不合法的子菜单url域名"
                break
            if case(40055):
                return "不合法的菜单url域名"
                break
            if case(40056):
                return "不合法的agentid"
                break
            if case(40057):
                return "不合法的callbackurl或者callbackurl验证失败"
                break
            if case(40058):
                return "不合法的参数"
                break
            if case(40059):
                return "不合法的上报地理位置标志位"
                break
            if case(40063):
                return "参数为空"
                break
            if case(40066):
                return "不合法的部门列表"
                break
            if case(40068):
                return "不合法的标签ID"
                break
            if case(40070):
                return "指定的标签范围结点全部无效"
                break
            if case(40071):
                return "不合法的标签名字"
                break
            if case(40072):
                return "不合法的标签名字长度"
                break
            if case(40073):
                return "不合法的openid"
                break
            if case(40074):
                return "news消息不支持保密消息类型"
                break
            if case(40077):
                return "不合法的pre_auth_code参数"
                break
            if case(40078):
                return "不合法的auth_code参数"
                break
            if case(40080):
                return "不合法的suite_secret"
                break
            if case(40082):
                return "不合法的suite_token"
                break
            if case(40083):
                return "不合法的suite_id"
                break
            if case(40084):
                return "不合法的permanent_code参数"
                break
            if case(40085):
                return "不合法的的suite_ticket参数"
                break
            if case(40086):
                return "不合法的第三方应用appid"
                break
            if case(40088):
                return "jobid不存在"
                break
            if case(40089):
                return "批量任务的结果已清理"
                break
            if case(40091):
                return "secret不合法"
                break
            if case(40092):
                return "导入文件存在不合法的内容"
                break
            if case(40093):
                return "不合法的jsapi_ticket参数"
                break
            if case(40094):
                return "不合法的URL"
                break
            if case(40096):
                return "不合法的外部联系人userid"
                break
            if case(40097):
                return "该成员尚未离职"
                break
            if case(40098):
                return "接替成员尚未实名认证"
                break
            if case(40099):
                return "接替成员的外部联系人数量已达上限"
                break
            if case(40100):
                return "此用户的外部联系人已经在转移流程中"
                break
            if case(41001):
                return "缺少access_token参数"
                break
            if case(41002):
                return "缺少corpid参数"
                break
            if case(41004):
                return "缺少secret参数"
                break
            if case(41006):
                return "缺少media_id参数"
                break
            if case(41008):
                return "缺少auth code参数"
                break
            if case(41009):
                return "缺少userid参数"
                break
            if case(41010):
                return "缺少url参数"
                break
            if case(41011):
                return "缺少agentid参数"
                break
            if case(41033):
                return "缺少 description 参数"
                break
            if case(41035):
                return "缺少外部联系人userid参数"
                break
            if case(41016):
                return "缺少title参数"
                break
            if case(41019):
                return "缺少 department 参数"
                break
            if case(41017):
                return "缺少tagid参数"
                break
            if case(41021):
                return "缺少suite_id参数"
                break
            if case(41022):
                return "缺少suite_access_token参数"
                break
            if case(41023):
                return "缺少suite_ticket参数"
                break
            if case(41024):
                return "缺少secret参数"
                break
            if case(41025):
                return "缺少permanent_code参数"
                break
            if case(42001):
                return "access_token已过期"
                break
            if case(42007):
                return "pre_auth_code已过期"
                break
            if case(42009):
                return "suite_access_token已过期"
                break
            if case(43004):
                return "指定的userid未绑定微信或未关注微工作台（原企业号）"
                break
            if case(44001):
                return "多媒体文件为空"
                break
            if case(44004):
                return "文本消息content参数为空"
                break
            if case(45001):
                return "多媒体文件大小超过限制"
                break
            if case(45002):
                return "消息内容大小超过限制"
                break
            if case(45004):
                return "应用description参数长度不符合系统限制"
                break
            if case(45007):
                return "语音播放时间超过限制"
                break
            if case(45008):
                return "图文消息的文章数量不符合系统限制"
                break
            if case(45009):
                return "接口调用超过限制"
                break
            if case(45022):
                return "应用name参数长度不符合系统限制"
                break
            if case(45024):
                return "帐号数量超过上限"
                break
            if case(45026):
                return "触发删除用户数的保护"
                break
            if case(45032):
                return "图文消息author参数长度超过限制"
                break
            if case(45033):
                return "接口并发调用超过限制"
                break
            if case(46003):
                return "菜单未设置"
                break
            if case(46004):
                return "指定的用户不存在"
                break
            if case(48002):
                return "API接口无权限调用"
                break
            if case(48003):
                return "不合法的suite_id"
                break
            if case(48004):
                return "授权关系无效"
                break
            if case(48005):
                return "API接口已废弃"
                break
            if case(50001):
                return "redirect_url未登记可信域名"
                break
            if case(50002):
                return "成员不在权限范围"
                break
            if case(50003):
                return "应用已禁用"
                break
            if case(60001):
                return "部门长度不符合限制"
                break
            if case(60003):
                return "部门ID不存在"
                break
            if case(60004):
                return "父部门不存在"
                break
            if case(60005):
                return "部门下存在成员"
                break
            if case(60006):
                return "部门下存在子部门"
                break
            if case(60007):
                return "不允许删除根部门"
                break
            if case(60008):
                return "部门已存在"
                break
            if case(60009):
                return "部门名称含有非法字符"
                break
            if case(60010):
                return "部门存在循环关系"
                break
            if case(60011):
                return "指定的成员/部门/标签参数无权限"
                break
            if case(60012):
                return "不允许删除默认应用"
                break
            if case(60020):
                return "访问ip不在白名单之中"
                break
            if case(60028):
                return "不允许修改第三方应用的主页 URL"
                break
            if case(60102):
                return "UserID已存在"
                break
            if case(60103):
                return "手机号码不合法"
                break
            if case(60104):
                return "手机号码已存在"
                break
            if case(60105):
                return "邮箱不合法"
                break
            if case(60106):
                return "邮箱已存在"
                break
            if case(60107):
                return "微信号不合法"
                break
            if case(60110):
                return "用户所属部门数量超过限制"
                break
            if case(60111):
                return "UserID不存在"
                break
            if case(60112):
                return "成员name参数不合法"
                break
            if case(60123):
                return "无效的部门id"
                break
            if case(60124):
                return "无效的父部门id"
                break
            if case(60125):
                return "非法部门名字"
                break
            if case(60127):
                return "缺少department参数"
                break
            if case(60129):
                return "成员手机和邮箱都为空"
                break
            if case(72023):
                return "发票已被其他公众号锁定"
                break
            if case(72024):
                return "发票状态错误"
                break
            if case(72037):
                return "存在发票不属于该用户"
                break
            if case(80001):
                return "可信域名不正确，或者无ICP备案"
                break
            if case(81001):
                return "部门下的结点数超过限制（3W）"
                break
            if case(81002):
                return "部门最多15层"
                break
            if case(81011):
                return "无权限操作标签"
                break
            if case(81013):
                return "UserID、部门ID、标签ID全部非法或无权限"
                break
            if case(81014):
                return "标签添加成员，单次添加user或party过多"
                break
            if case(82001):
                return "指定的成员/部门/标签全部无效"
                break
            if case(82002):
                return "不合法的PartyID列表长度"
                break
            if case(82003):
                return "不合法的TagID列表长度"
                break
            if case(84014):
                return "成员票据过期"
                break
            if case(84015):
                return "成员票据无效"
                break
            if case(84019):
                return "缺少templateid参数"
                break
            if case(84020):
                return "templateid不存在"
                break
            if case(84021):
                return "缺少register_code参数"
                break
            if case(84022):
                return "无效的register_code参数"
                break
            if case(84023):
                return "不允许调用设置通讯录同步完成接口"
                break
            if case(84024):
                return "无注册信息"
                break
            if case(84025):
                return "不符合的state参数"
                break
            if case(84052):
                return "缺少caller参数"
                break
            if case(84053):
                return "缺少callee参数"
                break
            if case(84054):
                return "缺少auth_corpid参数"
                break
            if case(84055):
                return "超过拨打公费电话频率"
                break
            if case(84056):
                return "被拨打用户安装应用时未授权拨打公费电话权限"
                break
            if case(84057):
                return "公费电话余额不足"
                break
            if case(84058):
                return "caller 呼叫号码不支持"
                break
            if case(84059):
                return "号码非法"
                break
            if case(84060):
                return "callee 呼叫号码不支持"
                break
            if case(84061):
                return "不存在外部联系人的关系"
                break
            if case(84062):
                return "未开启公费电话应用"
                break
            if case(84063):
                return "caller不存在"
                break
            if case(84064):
                return "callee不存在"
                break
            if case(84065):
                return "caller跟callee电话号码一致"
                break
            if case(84066):
                return "服务商拨打次数超过限制"
                break
            if case(84067):
                return "管理员收到的服务商公费电话个数超过限制"
                break
            if case(84071):
                return "不合法的外部联系人授权码"
                break
            if case(84072):
                return "应用未配置客服"
                break
            if case(84073):
                return "客服userid不在应用配置的客服列表中"
                break
            if case(84074):
                return "没有外部联系人权限"
                break
            if case(85002):
                return "包含不合法的词语"
                break
            if case(85004):
                return "每企业每个月设置的可信域名不可超过20个"
                break
            if case(85005):
                return "可信域名未通过所有权校验"
                break
            if case(86001):
                return "参数 chatid 不合法"
                break
            if case(86003):
                return "参数 chatid 不存在"
                break
            if case(86004):
                return "参数 群名不合法"
                break
            if case(86005):
                return "参数 群主不合法"
                break
            if case(86006):
                return "群成员数过多或过少"
                break
            if case(86007):
                return "不合法的群成员"
                break
            if case(86008):
                return "非法操作非自己创建的群"
                break
            if case(86101):
                return "仅群主才有操作权限"
                break
            if case(86201):
                return "参数 需要chatid"
                break
            if case(86202):
                return "参数 需要群名"
                break
            if case(86203):
                return "参数 需要群主"
                break
            if case(86204):
                return "参数 需要群成员"
                break
            if case(86205):
                return "参数 字符串chatid过长"
                break
            if case(86206):
                return "参数 数字chatid过大"
                break
            if case(86207):
                return "群主不在群成员列表"
                break
            if case(86215):
                return "会话ID已经存在"
                break
            if case(86216):
                return "存在非法会话成员ID"
                break
            if case(86217):
                return "会话发送者不在会话成员列表中"
                break
            if case(86220):
                return "指定的会话参数不合法"
                break
            if case(90001):
                return "未认证摇一摇周边"
                break
            if case(90002):
                return "缺少摇一摇周边ticket参数"
                break
            if case(90003):
                return "摇一摇周边ticket参数不合法"
                break
            if case(90100):
                return "非法的对外属性类型"
                break
            if case(90101):
                return "对外属性：文本类型长度不合法"
                break
            if case(90102):
                return "对外属性：网页类型标题长度不合法"
                break
            if case(90103):
                return "对外属性：网页url不合法"
                break
            if case(90104):
                return "对外属性：小程序类型标题长度不合法"
                break
            if case(90105):
                return "对外属性：小程序类型pagepath不合法"
                break
            if case(90106):
                return "对外属性：请求参数不合法"
                break
            if case(91040):
                return "获取ticket的类型无效"
                break
            if case(301002):
                return "无权限操作指定的应用"
                break
            if case(301005):
                return "不允许删除创建者"
                break
            if case(301012):
                return "参数 position 不合法"
                break
            if case(301013):
                return "参数 telephone 不合法"
                break
            if case(301014):
                return "参数 english_name 不合法"
                break
            if case(301015):
                return "参数 mediaid 不合法"
                break
            if case(301016):
                return "上传语音文件不符合系统要求"
                break
            if case(301017):
                return "上传语音文件仅支持AMR格式"
                break
            if case(301021):
                return "参数 userid 无效"
                break
            if case(301022):
                return "获取打卡数据失败"
                break
            if case(301023):
                return "useridlist非法或超过限额"
                break
            if case(301024):
                return "获取打卡记录时间间隔超限"
                break
            if case(301036):
                return "不允许更新该用户的userid"
                break
            if case(302003):
                return "批量导入任务的文件中userid有重复"
                break
            if case(302004):
                return "组织架构不合法（1不是一棵树，2 多个一样的partyid，3 partyid空，4 partyid name 空，5 同一个父节点下有两个子节点 部门名字一样 可能是以上情况，请一一排查）"
                break
            if case(302005):
                return "批量导入系统失败，请重新尝试导入"
                break
            if case(302006):
                return "批量导入任务的文件中partyid有重复"
                break
            if case(302007):
                return "批量导入任务的文件中，同一个部门下有两个子部门名字一样"
                break
            if case(2000002):
                return "CorpId参数无效"
                break
            if case():
                return "未知错误 %s" % errcode
