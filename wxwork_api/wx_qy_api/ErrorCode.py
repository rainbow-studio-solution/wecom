# -*- coding:utf-8 -*-

"""
全局错误码
企业应用每次调用接口时，可能获得正确或错误的返回码，企业可以根据返回码信息调试接口，排查错误。
注意：开发者的程序应该根据errcode来判断出错的情况，而不应该依赖errmsg来匹配，因为errmsg可能会调整。
=============
更新时间：2020-09-30
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
    "40039": "不合法的url长度",
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
    "40093": "jsapi签名错误",
    "40094": "不合法的URL",
    "40096": "不合法的外部联系人userid",
    "40097": "该成员尚未离职",
    "40098": "成员尚未实名认证",
    "40099": "接替成员的外部联系人数量已达上限",
    "40100": "此用户的外部联系人已经在转移流程中",
    "40102": "域名或IP不可与应用市场上架应用重复",
    "40123": "上传临时图片素材，图片格式非法",
    "40124": "推广活动里的sn禁止绑定",
    "40125": "无效的openuserid参数",
    "40126": "企业标签个数达到上限，最多为3000个",
    "40127": "不支持的uri schema",
    "40128": "客户转接过于频繁（90天内只允许转接一次，同一个客户最多只能转接两次）",
    "40129": "当前客户正在转接中",
    "40130": "原跟进人与接手人一样，不可继承",
    "40131": "handover_userid 并不是外部联系人的跟进人",
    "41001": "缺少access_token参数",
    "41002": "缺少corpid参数",
    "41004": "缺少secret参数",
    "41006": "缺少media_id参数",
    "41008": "缺少auth code参数",
    "41009": "缺少userid参数",
    "41010": "缺少url参数",
    "41011": "缺少agentid参数",
    "41016": "缺少title参数",
    "41019": "缺少 department 参数",
    "41017": "缺少tagid参数",
    "41021": "缺少suite_id参数",
    "41022": "缺少suite_access_token参数",
    "41023": "缺少suite_ticket参数",
    "41024": "缺少secret参数",
    "41025": "缺少permanent_code参数",
    "41033": "缺少 description 参数",
    "41035": "缺少外部联系人userid参数",
    "41036": "不合法的企业对外简称",
    "41037": "缺少「联系我」type参数",
    "41038": "缺少「联系我」scene参数",
    "41039": "无效的「联系我」type参数",
    "41040": "无效的「联系我」scene参数",
    "41041": "「联系我」使用人数超过限制",
    "41042": "无效的「联系我」style参数",
    "41043": "缺少「联系我」config_id参数",
    "41044": "无效的「联系我」config_id参数",
    "41045": "API添加「联系我」达到数量上限",
    "41046": "缺少企业群发消息id",
    "41047": "无效的企业群发消息id",
    "41048": "无可发送的客户",
    "41049": "缺少欢迎语code参数",
    "41050": "无效的欢迎语code",
    "41051": "客户和服务人员已经开始聊天了",
    "41052": "无效的发送时间",
    "41053": "客户未同意聊天存档",
    "41054": "该用户尚未激活",
    "41055": "群欢迎语模板数量达到上限",
    "41056": "外部联系人id类型不正确",
    "41057": "企业或服务商未绑定微信开发者账号",
    "41102": "缺少菜单名",
    "42001": "access_token已过期",
    "42007": "pre_auth_code已过期",
    "42009": "suite_access_token已过期",
    "42012": "jsapi_ticket不可用，一般是没有正确调用接口来创建jsapi_ticket",
    "42013": "小程序未登陆或登录态已经过期",
    "42014": "任务卡片消息的task_id不合法",
    "42015": "更新的消息的应用与发送消息的应用不匹配",
    "42016": "更新的task_id不存在",
    "42017": "按钮key值不存在",
    "42018": "按钮key值不合法",
    "42019": "缺少按钮key值不合法",
    "42020": "缺少按钮名称",
    "42021": "device_access_token 过期",
    "42022": "code已经被使用过。只能使用一次",
    "43004": "指定的userid未绑定微信或未关注微工作台（原企业号）",
    "43009": "企业未验证主体",
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
    "45029": "回包大小超过上限",
    "45032": "图文消息author参数长度超过限制",
    "45033": "接口并发调用超过限制",
    "45034": "url必须有协议头",
    "46003": "菜单未设置",
    "46004": "指定的用户不存在",
    "48002": "API接口无权限调用",
    "48003": "不合法的suite_id",
    "48004": "授权关系无效",
    "48005": "API接口已废弃",
    "48006": "接口权限被收回",
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
    "60021": "userid不在应用可见范围内",
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
    "60132": "is_leader_in_dept和department的元素个数不一致",
    "60136": "记录不存在",
    "60137": "家长手机号重复",
    "60203": "不合法的模版ID",
    "60204": "模版状态不可用",
    "60205": "模版关键词不匹配",
    "60206": "该种类型的消息只支持第三方独立应用使用",
    "60207": "第三方独立应用只允许发送模板消息",
    "60208": "第三方独立应用不支持指定@all，不支持参数toparty和totag",
    "65000": "学校已经迁移",
    "65001": "无效的关注模式",
    "65002": "导入家长信息数量过多",
    "65003": "学校尚未迁移",
    "65004": "组织架构不存在",
    "65005": "无效的同步模式",
    "65006": "无效的管理员类型",
    "65007": "无效的家校部门类型",
    "65008": "无效的入学年份",
    "65009": "无效的标准年级类型",
    "65010": "此userid并不是学生",
    "65011": "家长userid数量超过限制",
    "65012": "学生userid数量超过限制",
    "65013": "学生已有家长",
    "65014": "非学校企业",
    "65015": "父部门类型不匹配",
    "65018": "家长人数达到上限",
    "72023": "发票已被其他公众号锁定",
    "72024": "发票状态错误",
    "72037": "存在发票不属于该用户",
    "80001": "可信域名不正确，或者无ICP备案",
    "81001": "部门下的结点数超过限制（3W）",
    "81002": "部门最多15层",
    "81003": "标签下节点个数超过30000个",
    "81011": "无权限操作标签",
    "81012": "缺失可见范围",
    "81013": "UserID、部门ID、标签ID全部非法或无权限",
    "81014": "标签添加成员，单次添加user或party过多",
    "81015": "邮箱域名需要跟企业邮箱域名一致",
    "81016": "logined_userid字段缺失",
    "81017": "items字段大小超过限制（20）",
    "81018": "该服务商可获取名字数量配额不足",
    "81019": "items数组成员缺少id字段",
    "81020": "items数组成员缺少type字段",
    "81021": "items数组成员的type字段不合法",
    "82001": "指定的成员/部门/标签全部为空",
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
    "84069": "拨打方被限制拨打公费电话",
    "84070": "不支持的电话号码",
    "84071": "不合法的外部联系人授权码",
    "84072": "应用未配置客服",
    "84073": "客服userid不在应用配置的客服列表中",
    "84074": "没有外部联系人权限",
    "84075": "不合法或过期的authcode",
    "84076": "缺失authcode",
    "84077": "订单价格过高，无法受理",
    "84078": "购买人数不正确",
    "84079": "价格策略不存在",
    "84080": "订单不存在",
    "84081": "存在未支付订单",
    "84082": "存在申请退款中的订单",
    "84083": "非服务人员",
    "84084": "非跟进用户",
    "84085": "应用已下架",
    "84086": "订单人数超过可购买最大人数",
    "84087": "打开订单支付前禁止关闭订单",
    "84088": "禁止关闭已支付的订单",
    "84089": "订单已支付",
    "84090": "缺失user_ticket",
    "84091": "订单价格不可低于下限",
    "84092": "无法发起代下单操作",
    "84093": "代理关系已占用，无法代下单",
    "84094": "该应用未配置代理分润规则，请先联系应用服务商处理",
    "84095": "免费试用版，无法扩容",
    "84096": "免费试用版，无法续期",
    "84097": "当前企业有未处理订单",
    "84098": "固定总量，无法扩容",
    "84099": "非购买状态，无法扩容",
    "84100": "未购买过此应用，无法续期",
    "84101": "企业已试用付费版本，无法全新购买",
    "84102": "企业当前应用状态已过期，无法扩容",
    "84103": "仅可修改未支付订单",
    "84104": "订单已支付，无法修改",
    "84105": "订单已被取消，无法修改",
    "84106": "企业含有该应用的待支付订单，无法代下单",
    "84107": "企业含有该应用的退款中订单，无法代下单",
    "84108": "企业含有该应用的待生效订单，无法代下单",
    "84109": "订单定价不能未0",
    "84110": "新安装应用不在试用状态，无法升级为付费版",
    "84111": "无足够可用优惠券",
    "84112": "无法关闭未支付订单",
    "84113": "无付费信息",
    "84114": "虚拟版本不支持下单",
    "84115": "虚拟版本不支持扩容",
    "84116": "虚拟版本不支持续期",
    "84117": "在虚拟正式版期内不能扩容",
    "84118": "虚拟正式版期内不能变更版本",
    "84119": "当前企业未报备，无法进行代下单",
    "84120": "当前应用版本已删除",
    "84121": "应用版本已删除，无法扩容",
    "84122": "应用版本已删除，无法续期",
    "84123": "非虚拟版本，无法升级",
    "84124": "非行业方案订单，不能添加部分应用版本的订单",
    "84125": "购买人数不能少于最少购买人数",
    "84126": "购买人数不能多于最大购买人数",
    "84127": "无应用管理权限",
    "84128": "无该行业方案下全部应用的管理权限",
    "84129": "付费策略已被删除，无法下单",
    "84130": "订单生效时间不合法",
    "84200": "文件转译解析错误",
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
    "86224": "不是受限群，不允许使用该接口",
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
    "90200": "缺少小程序appid参数",
    "90201": "小程序通知的content_item个数超过限制",
    "90202": "小程序通知中的key长度不合法",
    "90203": "小程序通知中的value长度不合法",
    "90204": "小程序通知中的page参数不合法",
    "90206": "小程序未关联到企业中",
    "90207": "不合法的小程序appid",
    "90208": "小程序appid不匹配",
    "90300": "orderid 不合法",
    "90302": "付费应用已过期",
    "90303": "付费应用超过最大使用人数",
    "90304": "订单中心服务异常，请稍后重试",
    "90305": "参数错误，errmsg中有提示具体哪个参数有问题",
    "90306": "商户设置不合法，详情请见errmsg",
    "90307": "登录态过期",
    "90308": "在开启IP鉴权的前提下，识别为无效的请求IP",
    "90309": "订单已经存在，请勿重复下单",
    "90310": "找不到订单",
    "90311": "关单失败, 可能原因：该单并没被拉起支付页面; 已经关单；已经支付；渠道失败；单处于保护状态；等等",
    "90312": "退款请求失败, 详情请看errmsg",
    "90313": "退款调用频率限制，超过规定的阈值",
    "90314": "订单状态错误，可能未支付，或者当前状态操作受限",
    "90315": "退款请求失败，主键冲突，请核实退款refund_id是否已使用",
    "90316": "退款原因编号不对",
    "90317": "尚未注册成为供应商",
    "90318": "参数nonce_str 为空或者重复，判定为重放攻击",
    "90319": "时间戳为空或者与系统时间间隔太大",
    "90320": "订单token无效",
    "90321": "订单token已过有效时间",
    "90322": "旧套件（包含多个应用的套件）不支持支付系统",
    "90323": "单价超过限额",
    "90324": "商品数量超过限额",
    "90325": "预支单已经存在",
    "90326": "预支单单号非法",
    "90327": "该预支单已经结算下单",
    "90328": "结算下单失败，详情请看errmsg",
    "90329": "该订单号已经被预支单占用",
    "90330": "创建供应商失败",
    "90331": "更新供应商失败",
    "90332": "还没签署合同",
    "90333": "创建合同失败",
    "90338": "已经过了可退款期限",
    "90339": "供应商主体名包含非法字符",
    "90340": "创建客户失败，可能信息真实性校验失败",
    "90341": "退款金额大于付款金额",
    "90342": "退款金额超过账户余额",
    "90343": "退款单号已经存在",
    "90344": "指定的付款渠道无效",
    "90345": "超过5w人民币不可指定微信支付渠道",
    "90346": "同一单的退款次数超过限制",
    "90347": "退款金额不可为0",
    "90348": "管理端没配置支付密钥",
    "90349": "记录数量太大",
    "90350": "银行信息真实性校验失败",
    "90351": "应用状态异常",
    "90352": "延迟试用期天数超过限制",
    "90353": "预支单列表不可为空",
    "90354": "预支单列表数量超过限制",
    "90355": "关联有退款预支单，不可删除",
    "90356": "不能0金额下单",
    "90357": "代下单必须指定支付渠道",
    "90358": "预支单或代下单，不支持部分退款",
    "90359": "预支单与下单者企业不匹配",
    "90456": "必须指定组织者",
    "90457": "日历ID异常",
    "90458": "日历ID列表不能为空",
    "90459": "日历已删除",
    "90460": "日程已删除",
    "90461": "日程ID异常",
    "90462": "日程ID列表不能为空",
    "90463": "不能变更组织者",
    "90464": "参与者数量超过限制",
    "90465": "不支持的重复类型",
    "90466": "不能操作别的应用创建的日历/日程",
    "90467": "星期参数异常",
    "90468": "不能变更组织者",
    "90469": "每页大小超过限制",
    "90470": "页数异常",
    "90471": "提醒时间异常",
    "90472": "没有日历/日程操作权限",
    "90473": "颜色参数异常",
    "90474": "组织者不能与参与者重叠",
    "90475": "不是组织者的日历",
    "90479": "不允许操作用户创建的日程",
    "90500": "群主并未离职",
    "90501": "该群不是客户群",
    "90502": "群主已经离职",
    "90503": "满人 & 99个微信成员，没办法踢，要客户端确认",
    "90504": "群主没变",
    "90507": "离职群正在继承处理中",
    "90508": "离职群已经继承",
    "91040": "获取ticket的类型无效",
    "92000": "成员不在应用可见范围之内",
    "92001": "应用没有敏感信息权限",
    "92002": "不允许跨企业调用",
    "93000": "机器人webhookurl不合法或者机器人已经被移除出群",
    "93004": "机器人被停用",
    "93008": "不在群里",
    "94000": "应用未开启工作台自定义模式",
    "94001": "不合法的type类型",
    "94002": "缺少keydata字段",
    "94003": "keydata的items列表长度超出限制",
    "94005": "缺少list字段",
    "94006": "list的items列表长度超出限制",
    "94007": "缺少webview字段",
    "94008": "应用未设置自定义工作台模版类型",
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
    "301025": "审批开放接口参数错误",
    "301036": "不允许更新该用户的userid",
    "302003": "批量导入任务的文件中userid有重复",
    "302004": "组织架构不合法（1不是一棵树，2 多个一样的partyid，3 partyid空，4 partyid name 空，5 同一个父节点下有两个子节点 部门名字一样 可能是以上情况，请一一排查）",
    "302005": "批量导入系统失败，请重新尝试导入",
    "302006": "批量导入任务的文件中partyid有重复",
    "302007": "批量导入任务的文件中，同一个部门下有两个子部门名字一样",
    "2000002": "CorpId参数无效",
    "600001": "不合法的sn",
    "600002": "设备已注册",
    "600003": "不合法的硬件activecode",
    "600004": "该硬件尚未授权任何企业",
    "600005": "硬件Secret无效",
    "600007": "缺少硬件sn",
    "600008": "缺少nonce参数",
    "600009": "缺少timestamp参数",
    "600010": "缺少signature参数",
    "600011": "签名校验失败",
    "600012": "长连接已经注册过设备",
    "600013": "缺少activecode参数",
    "600014": "设备未网络注册",
    "600015": "缺少secret参数",
    "600016": "设备未激活",
    "600018": "无效的起始结束时间",
    "600020": "设备未登录",
    "600021": "设备sn已存在",
    "600023": "时间戳已失效",
    "600024": "固件大小超过5M",
    "600025": "固件名为空或者超过20字节",
    "600026": "固件信息不存在",
    "600027": "非法的固件参数",
    "600028": "固件版本已存在",
    "600029": "非法的固件版本",
    "600030": "缺少固件版本参数",
    "600031": "硬件固件不允许升级",
    "600032": "无法解析硬件二维码",
    "600033": "设备型号id冲突",
    "600034": "指纹数据大小超过限制",
    "600035": "人脸数据大小超过限制",
    "600036": "设备sn冲突",
    "600037": "缺失设备型号id",
    "600038": "设备型号不存在",
    "600039": "不支持的设备类型",
    "600040": "打印任务id不存在",
    "600041": "无效的offset或limit参数值",
    "600042": "无效的设备型号id",
    "600043": "门禁规则未设置",
    "600044": "门禁规则不合法",
    "600045": "设备已订阅企业信息",
    "600046": "操作id和用户userid不匹配",
    "600047": "secretno的status非法",
    "600048": "无效的指纹算法",
    "600049": "无效的人脸识别算法",
    "600050": "无效的算法长度",
    "600051": "设备过期",
    "600052": "无效的文件分块",
    "600053": "该链接已经激活",
    "600054": "该链接已经订阅",
    "600055": "无效的用户类型",
    "600056": "无效的健康状态",
    "600057": "缺少体温参数",
    "610001": "永久二维码超过每个员工5000的限制",
    "610003": "scene参数不合法",
    "610004": "userid不在客户联系配置的使用范围内",
    "640001": "微盘不存在当前空间",
    "640002": "文件不存在",
    "640003": "文件已删除",
    "640004": "无权限访问",
    "640005": "成员不在空间内",
    "640006": "超出当前成员拥有的容量",
    "640007": "超出微盘的容量",
    "640008": "没有空间权限",
    "640009": "非法文件名",
    "640010": "超出空间的最大成员数",
    "640011": "json格式不匹配",
    "640012": "非法的userid",
    "640013": "非法的departmentid",
    "640014": "空间没有有效的管理员",
    "640015": "不支持设置预览权限",
    "640016": "不支持设置文件水印",
    "640017": "微盘管理端未开通API 权限",
    "640018": "微盘管理端未设置编辑权限",
    "640019": "API 调用次数超出限制",
    "640020": "非法的权限类型",
    "640021": "非法的fatherid",
    "640022": "非法的文件内容的base64",
    "640023": "非法的权限范围",
    "640024": "非法的fileid",
    "640025": "非法的space_name",
    "640026": "非法的spaceid",
    "640027": "参数错误",
    "640028": "空间设置了关闭成员邀请链接",
    "640029": "只支持下载普通文件，不支持下载文件夹等其他非文件实体类型",
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
            if case(40039):
                return "不合法的url长度"
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
                return "jsapi签名错误"
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
                return "成员尚未实名认证"
                break
            if case(40099):
                return "接替成员的外部联系人数量已达上限"
                break
            if case(40100):
                return "此用户的外部联系人已经在转移流程中"
                break
            if case(40102):
                return "域名或IP不可与应用市场上架应用重复"
                break
            if case(40123):
                return "上传临时图片素材，图片格式非法"
                break
            if case(40124):
                return "推广活动里的sn禁止绑定"
                break
            if case(40125):
                return "无效的openuserid参数"
                break
            if case(40126):
                return "企业标签个数达到上限，最多为3000个"
                break
            if case(40127):
                return "不支持的uri schema"
                break
            if case(40128):
                return "客户转接过于频繁（90天内只允许转接一次，同一个客户最多只能转接两次）"
                break
            if case(40129):
                return "当前客户正在转接中"
                break
            if case(40130):
                return "原跟进人与接手人一样，不可继承"
                break
            if case(40131):
                return "handover_userid 并不是外部联系人的跟进人"
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
            if case(41033):
                return "缺少 description 参数"
                break
            if case(41035):
                return "缺少外部联系人userid参数"
                break
            if case(41036):
                return "不合法的企业对外简称"
                break
            if case(41037):
                return "缺少「联系我」type参数"
                break
            if case(41038):
                return "缺少「联系我」scene参数"
                break
            if case(41039):
                return "无效的「联系我」type参数"
                break
            if case(41040):
                return "无效的「联系我」scene参数"
                break
            if case(41041):
                return "「联系我」使用人数超过限制"
                break
            if case(41042):
                return "无效的「联系我」style参数"
                break
            if case(41043):
                return "缺少「联系我」config_id参数"
                break
            if case(41044):
                return "无效的「联系我」config_id参数"
                break
            if case(41045):
                return "API添加「联系我」达到数量上限"
                break
            if case(41046):
                return "缺少企业群发消息id"
                break
            if case(41047):
                return "无效的企业群发消息id"
                break
            if case(41048):
                return "无可发送的客户"
                break
            if case(41049):
                return "缺少欢迎语code参数"
                break
            if case(41050):
                return "无效的欢迎语code"
                break
            if case(41051):
                return "客户和服务人员已经开始聊天了"
                break
            if case(41052):
                return "无效的发送时间"
                break
            if case(41053):
                return "客户未同意聊天存档"
                break
            if case(41054):
                return "该用户尚未激活"
                break
            if case(41055):
                return "群欢迎语模板数量达到上限"
                break
            if case(41056):
                return "外部联系人id类型不正确"
                break
            if case(41057):
                return "企业或服务商未绑定微信开发者账号"
                break
            if case(41102):
                return "缺少菜单名"
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
            if case(42012):
                return "jsapi_ticket不可用，一般是没有正确调用接口来创建jsapi_ticket"
                break
            if case(42013):
                return "小程序未登陆或登录态已经过期"
                break
            if case(42014):
                return "任务卡片消息的task_id不合法"
                break
            if case(42015):
                return "更新的消息的应用与发送消息的应用不匹配"
                break
            if case(42016):
                return "更新的task_id不存在"
                break
            if case(42017):
                return "按钮key值不存在"
                break
            if case(42018):
                return "按钮key值不合法"
                break
            if case(42019):
                return "缺少按钮key值不合法"
                break
            if case(42020):
                return "缺少按钮名称"
                break
            if case(42021):
                return "device_access_token 过期"
                break
            if case(42022):
                return "code已经被使用过。只能使用一次"
                break
            if case(43004):
                return "指定的userid未绑定微信或未关注微工作台（原企业号）"
                break
            if case(43009):
                return "企业未验证主体"
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
            if case(45029):
                return "回包大小超过上限"
                break
            if case(45032):
                return "图文消息author参数长度超过限制"
                break
            if case(45033):
                return "接口并发调用超过限制"
                break
            if case(45034):
                return "url必须有协议头"
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
            if case(48006):
                return "接口权限被收回"
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
            if case(60021):
                return "userid不在应用可见范围内"
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
            if case(60132):
                return "is_leader_in_dept和department的元素个数不一致"
                break
            if case(60136):
                return "记录不存在"
                break
            if case(60137):
                return "家长手机号重复"
                break
            if case(60203):
                return "不合法的模版ID"
                break
            if case(60204):
                return "模版状态不可用"
                break
            if case(60205):
                return "模版关键词不匹配"
                break
            if case(60206):
                return "该种类型的消息只支持第三方独立应用使用"
                break
            if case(60207):
                return "第三方独立应用只允许发送模板消息"
                break
            if case(60208):
                return "第三方独立应用不支持指定@all，不支持参数toparty和totag"
                break
            if case(65000):
                return "学校已经迁移"
                break
            if case(65001):
                return "无效的关注模式"
                break
            if case(65002):
                return "导入家长信息数量过多"
                break
            if case(65003):
                return "学校尚未迁移"
                break
            if case(65004):
                return "组织架构不存在"
                break
            if case(65005):
                return "无效的同步模式"
                break
            if case(65006):
                return "无效的管理员类型"
                break
            if case(65007):
                return "无效的家校部门类型"
                break
            if case(65008):
                return "无效的入学年份"
                break
            if case(65009):
                return "无效的标准年级类型"
                break
            if case(65010):
                return "此userid并不是学生"
                break
            if case(65011):
                return "家长userid数量超过限制"
                break
            if case(65012):
                return "学生userid数量超过限制"
                break
            if case(65013):
                return "学生已有家长"
                break
            if case(65014):
                return "非学校企业"
                break
            if case(65015):
                return "父部门类型不匹配"
                break
            if case(65018):
                return "家长人数达到上限"
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
            if case(81003):
                return "标签下节点个数超过30000个"
                break
            if case(81011):
                return "无权限操作标签"
                break
            if case(81012):
                return "缺失可见范围"
                break
            if case(81013):
                return "UserID、部门ID、标签ID全部非法或无权限"
                break
            if case(81014):
                return "标签添加成员，单次添加user或party过多"
                break
            if case(81015):
                return "邮箱域名需要跟企业邮箱域名一致"
                break
            if case(81016):
                return "logined_userid字段缺失"
                break
            if case(81017):
                return "items字段大小超过限制（20）"
                break
            if case(81018):
                return "该服务商可获取名字数量配额不足"
                break
            if case(81019):
                return "items数组成员缺少id字段"
                break
            if case(81020):
                return "items数组成员缺少type字段"
                break
            if case(81021):
                return "items数组成员的type字段不合法"
                break
            if case(82001):
                return "指定的成员/部门/标签全部为空"
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
            if case(84069):
                return "拨打方被限制拨打公费电话"
                break
            if case(84070):
                return "不支持的电话号码"
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
            if case(84075):
                return "不合法或过期的authcode"
                break
            if case(84076):
                return "缺失authcode"
                break
            if case(84077):
                return "订单价格过高，无法受理"
                break
            if case(84078):
                return "购买人数不正确"
                break
            if case(84079):
                return "价格策略不存在"
                break
            if case(84080):
                return "订单不存在"
                break
            if case(84081):
                return "存在未支付订单"
                break
            if case(84082):
                return "存在申请退款中的订单"
                break
            if case(84083):
                return "非服务人员"
                break
            if case(84084):
                return "非跟进用户"
                break
            if case(84085):
                return "应用已下架"
                break
            if case(84086):
                return "订单人数超过可购买最大人数"
                break
            if case(84087):
                return "打开订单支付前禁止关闭订单"
                break
            if case(84088):
                return "禁止关闭已支付的订单"
                break
            if case(84089):
                return "订单已支付"
                break
            if case(84090):
                return "缺失user_ticket"
                break
            if case(84091):
                return "订单价格不可低于下限"
                break
            if case(84092):
                return "无法发起代下单操作"
                break
            if case(84093):
                return "代理关系已占用，无法代下单"
                break
            if case(84094):
                return "该应用未配置代理分润规则，请先联系应用服务商处理"
                break
            if case(84095):
                return "免费试用版，无法扩容"
                break
            if case(84096):
                return "免费试用版，无法续期"
                break
            if case(84097):
                return "当前企业有未处理订单"
                break
            if case(84098):
                return "固定总量，无法扩容"
                break
            if case(84099):
                return "非购买状态，无法扩容"
                break
            if case(84100):
                return "未购买过此应用，无法续期"
                break
            if case(84101):
                return "企业已试用付费版本，无法全新购买"
                break
            if case(84102):
                return "企业当前应用状态已过期，无法扩容"
                break
            if case(84103):
                return "仅可修改未支付订单"
                break
            if case(84104):
                return "订单已支付，无法修改"
                break
            if case(84105):
                return "订单已被取消，无法修改"
                break
            if case(84106):
                return "企业含有该应用的待支付订单，无法代下单"
                break
            if case(84107):
                return "企业含有该应用的退款中订单，无法代下单"
                break
            if case(84108):
                return "企业含有该应用的待生效订单，无法代下单"
                break
            if case(84109):
                return "订单定价不能未0"
                break
            if case(84110):
                return "新安装应用不在试用状态，无法升级为付费版"
                break
            if case(84111):
                return "无足够可用优惠券"
                break
            if case(84112):
                return "无法关闭未支付订单"
                break
            if case(84113):
                return "无付费信息"
                break
            if case(84114):
                return "虚拟版本不支持下单"
                break
            if case(84115):
                return "虚拟版本不支持扩容"
                break
            if case(84116):
                return "虚拟版本不支持续期"
                break
            if case(84117):
                return "在虚拟正式版期内不能扩容"
                break
            if case(84118):
                return "虚拟正式版期内不能变更版本"
                break
            if case(84119):
                return "当前企业未报备，无法进行代下单"
                break
            if case(84120):
                return "当前应用版本已删除"
                break
            if case(84121):
                return "应用版本已删除，无法扩容"
                break
            if case(84122):
                return "应用版本已删除，无法续期"
                break
            if case(84123):
                return "非虚拟版本，无法升级"
                break
            if case(84124):
                return "非行业方案订单，不能添加部分应用版本的订单"
                break
            if case(84125):
                return "购买人数不能少于最少购买人数"
                break
            if case(84126):
                return "购买人数不能多于最大购买人数"
                break
            if case(84127):
                return "无应用管理权限"
                break
            if case(84128):
                return "无该行业方案下全部应用的管理权限"
                break
            if case(84129):
                return "付费策略已被删除，无法下单"
                break
            if case(84130):
                return "订单生效时间不合法"
                break
            if case(84200):
                return "文件转译解析错误"
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
            if case(86224):
                return "不是受限群，不允许使用该接口"
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
            if case(90200):
                return "缺少小程序appid参数"
                break
            if case(90201):
                return "小程序通知的content_item个数超过限制"
                break
            if case(90202):
                return "小程序通知中的key长度不合法"
                break
            if case(90203):
                return "小程序通知中的value长度不合法"
                break
            if case(90204):
                return "小程序通知中的page参数不合法"
                break
            if case(90206):
                return "小程序未关联到企业中"
                break
            if case(90207):
                return "不合法的小程序appid"
                break
            if case(90208):
                return "小程序appid不匹配"
                break
            if case(90300):
                return "orderid 不合法"
                break
            if case(90302):
                return "付费应用已过期"
                break
            if case(90303):
                return "付费应用超过最大使用人数"
                break
            if case(90304):
                return "订单中心服务异常，请稍后重试"
                break
            if case(90305):
                return "参数错误，errmsg中有提示具体哪个参数有问题"
                break
            if case(90306):
                return "商户设置不合法，详情请见errmsg"
                break
            if case(90307):
                return "登录态过期"
                break
            if case(90308):
                return "在开启IP鉴权的前提下，识别为无效的请求IP"
                break
            if case(90309):
                return "订单已经存在，请勿重复下单"
                break
            if case(90310):
                return "找不到订单"
                break
            if case(90311):
                return "关单失败, 可能原因：该单并没被拉起支付页面; 已经关单；已经支付；渠道失败；单处于保护状态；等等"
                break
            if case(90312):
                return "退款请求失败, 详情请看errmsg"
                break
            if case(90313):
                return "退款调用频率限制，超过规定的阈值"
                break
            if case(90314):
                return "订单状态错误，可能未支付，或者当前状态操作受限"
                break
            if case(90315):
                return "退款请求失败，主键冲突，请核实退款refund_id是否已使用"
                break
            if case(90316):
                return "退款原因编号不对"
                break
            if case(90317):
                return "尚未注册成为供应商"
                break
            if case(90318):
                return "参数nonce_str 为空或者重复，判定为重放攻击"
                break
            if case(90319):
                return "时间戳为空或者与系统时间间隔太大"
                break
            if case(90320):
                return "订单token无效"
                break
            if case(90321):
                return "订单token已过有效时间"
                break
            if case(90322):
                return "旧套件（包含多个应用的套件）不支持支付系统"
                break
            if case(90323):
                return "单价超过限额"
                break
            if case(90324):
                return "商品数量超过限额"
                break
            if case(90325):
                return "预支单已经存在"
                break
            if case(90326):
                return "预支单单号非法"
                break
            if case(90327):
                return "该预支单已经结算下单"
                break
            if case(90328):
                return "结算下单失败，详情请看errmsg"
                break
            if case(90329):
                return "该订单号已经被预支单占用"
                break
            if case(90330):
                return "创建供应商失败"
                break
            if case(90331):
                return "更新供应商失败"
                break
            if case(90332):
                return "还没签署合同"
                break
            if case(90333):
                return "创建合同失败"
                break
            if case(90338):
                return "已经过了可退款期限"
                break
            if case(90339):
                return "供应商主体名包含非法字符"
                break
            if case(90340):
                return "创建客户失败，可能信息真实性校验失败"
                break
            if case(90341):
                return "退款金额大于付款金额"
                break
            if case(90342):
                return "退款金额超过账户余额"
                break
            if case(90343):
                return "退款单号已经存在"
                break
            if case(90344):
                return "指定的付款渠道无效"
                break
            if case(90345):
                return "超过5w人民币不可指定微信支付渠道"
                break
            if case(90346):
                return "同一单的退款次数超过限制"
                break
            if case(90347):
                return "退款金额不可为0"
                break
            if case(90348):
                return "管理端没配置支付密钥"
                break
            if case(90349):
                return "记录数量太大"
                break
            if case(90350):
                return "银行信息真实性校验失败"
                break
            if case(90351):
                return "应用状态异常"
                break
            if case(90352):
                return "延迟试用期天数超过限制"
                break
            if case(90353):
                return "预支单列表不可为空"
                break
            if case(90354):
                return "预支单列表数量超过限制"
                break
            if case(90355):
                return "关联有退款预支单，不可删除"
                break
            if case(90356):
                return "不能0金额下单"
                break
            if case(90357):
                return "代下单必须指定支付渠道"
                break
            if case(90358):
                return "预支单或代下单，不支持部分退款"
                break
            if case(90359):
                return "预支单与下单者企业不匹配"
                break
            if case(90456):
                return "必须指定组织者"
                break
            if case(90457):
                return "日历ID异常"
                break
            if case(90458):
                return "日历ID列表不能为空"
                break
            if case(90459):
                return "日历已删除"
                break
            if case(90460):
                return "日程已删除"
                break
            if case(90461):
                return "日程ID异常"
                break
            if case(90462):
                return "日程ID列表不能为空"
                break
            if case(90463):
                return "不能变更组织者"
                break
            if case(90464):
                return "参与者数量超过限制"
                break
            if case(90465):
                return "不支持的重复类型"
                break
            if case(90466):
                return "不能操作别的应用创建的日历/日程"
                break
            if case(90467):
                return "星期参数异常"
                break
            if case(90468):
                return "不能变更组织者"
                break
            if case(90469):
                return "每页大小超过限制"
                break
            if case(90470):
                return "页数异常"
                break
            if case(90471):
                return "提醒时间异常"
                break
            if case(90472):
                return "没有日历/日程操作权限"
                break
            if case(90473):
                return "颜色参数异常"
                break
            if case(90474):
                return "组织者不能与参与者重叠"
                break
            if case(90475):
                return "不是组织者的日历"
                break
            if case(90479):
                return "不允许操作用户创建的日程"
                break
            if case(90500):
                return "群主并未离职"
                break
            if case(90501):
                return "该群不是客户群"
                break
            if case(90502):
                return "群主已经离职"
                break
            if case(90503):
                return "满人 & 99个微信成员，没办法踢，要客户端确认"
                break
            if case(90504):
                return "群主没变"
                break
            if case(90507):
                return "离职群正在继承处理中"
                break
            if case(90508):
                return "离职群已经继承"
                break
            if case(91040):
                return "获取ticket的类型无效"
                break
            if case(92000):
                return "成员不在应用可见范围之内"
                break
            if case(92001):
                return "应用没有敏感信息权限"
                break
            if case(92002):
                return "不允许跨企业调用"
                break
            if case(93000):
                return "机器人webhookurl不合法或者机器人已经被移除出群"
                break
            if case(93004):
                return "机器人被停用"
                break
            if case(93008):
                return "不在群里"
                break
            if case(94000):
                return "应用未开启工作台自定义模式"
                break
            if case(94001):
                return "不合法的type类型"
                break
            if case(94002):
                return "缺少keydata字段"
                break
            if case(94003):
                return "keydata的items列表长度超出限制"
                break
            if case(94005):
                return "缺少list字段"
                break
            if case(94006):
                return "list的items列表长度超出限制"
                break
            if case(94007):
                return "缺少webview字段"
                break
            if case(94008):
                return "应用未设置自定义工作台模版类型"
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
            if case(301025):
                return "审批开放接口参数错误"
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
            if case(600001):
                return "不合法的sn"
                break
            if case(600002):
                return "设备已注册"
                break
            if case(600003):
                return "不合法的硬件activecode"
                break
            if case(600004):
                return "该硬件尚未授权任何企业"
                break
            if case(600005):
                return "硬件Secret无效"
                break
            if case(600007):
                return "缺少硬件sn"
                break
            if case(600008):
                return "缺少nonce参数"
                break
            if case(600009):
                return "缺少timestamp参数"
                break
            if case(600010):
                return "缺少signature参数"
                break
            if case(600011):
                return "签名校验失败"
                break
            if case(600012):
                return "长连接已经注册过设备"
                break
            if case(600013):
                return "缺少activecode参数"
                break
            if case(600014):
                return "设备未网络注册"
                break
            if case(600015):
                return "缺少secret参数"
                break
            if case(600016):
                return "设备未激活"
                break
            if case(600018):
                return "无效的起始结束时间"
                break
            if case(600020):
                return "设备未登录"
                break
            if case(600021):
                return "设备sn已存在"
                break
            if case(600023):
                return "时间戳已失效"
                break
            if case(600024):
                return "固件大小超过5M"
                break
            if case(600025):
                return "固件名为空或者超过20字节"
                break
            if case(600026):
                return "固件信息不存在"
                break
            if case(600027):
                return "非法的固件参数"
                break
            if case(600028):
                return "固件版本已存在"
                break
            if case(600029):
                return "非法的固件版本"
                break
            if case(600030):
                return "缺少固件版本参数"
                break
            if case(600031):
                return "硬件固件不允许升级"
                break
            if case(600032):
                return "无法解析硬件二维码"
                break
            if case(600033):
                return "设备型号id冲突"
                break
            if case(600034):
                return "指纹数据大小超过限制"
                break
            if case(600035):
                return "人脸数据大小超过限制"
                break
            if case(600036):
                return "设备sn冲突"
                break
            if case(600037):
                return "缺失设备型号id"
                break
            if case(600038):
                return "设备型号不存在"
                break
            if case(600039):
                return "不支持的设备类型"
                break
            if case(600040):
                return "打印任务id不存在"
                break
            if case(600041):
                return "无效的offset或limit参数值"
                break
            if case(600042):
                return "无效的设备型号id"
                break
            if case(600043):
                return "门禁规则未设置"
                break
            if case(600044):
                return "门禁规则不合法"
                break
            if case(600045):
                return "设备已订阅企业信息"
                break
            if case(600046):
                return "操作id和用户userid不匹配"
                break
            if case(600047):
                return "secretno的status非法"
                break
            if case(600048):
                return "无效的指纹算法"
                break
            if case(600049):
                return "无效的人脸识别算法"
                break
            if case(600050):
                return "无效的算法长度"
                break
            if case(600051):
                return "设备过期"
                break
            if case(600052):
                return "无效的文件分块"
                break
            if case(600053):
                return "该链接已经激活"
                break
            if case(600054):
                return "该链接已经订阅"
                break
            if case(600055):
                return "无效的用户类型"
                break
            if case(600056):
                return "无效的健康状态"
                break
            if case(600057):
                return "缺少体温参数"
                break
            if case(610001):
                return "永久二维码超过每个员工5000的限制"
                break
            if case(610003):
                return "scene参数不合法"
                break
            if case(610004):
                return "userid不在客户联系配置的使用范围内"
                break
            if case(640001):
                return "微盘不存在当前空间"
                break
            if case(640002):
                return "文件不存在"
                break
            if case(640003):
                return "文件已删除"
                break
            if case(640004):
                return "无权限访问"
                break
            if case(640005):
                return "成员不在空间内"
                break
            if case(640006):
                return "超出当前成员拥有的容量"
                break
            if case(640007):
                return "超出微盘的容量"
                break
            if case(640008):
                return "没有空间权限"
                break
            if case(640009):
                return "非法文件名"
                break
            if case(640010):
                return "超出空间的最大成员数"
                break
            if case(640011):
                return "json格式不匹配"
                break
            if case(640012):
                return "非法的userid"
                break
            if case(640013):
                return "非法的departmentid"
                break
            if case(640014):
                return "空间没有有效的管理员"
                break
            if case(640015):
                return "不支持设置预览权限"
                break
            if case(640016):
                return "不支持设置文件水印"
                break
            if case(640017):
                return "微盘管理端未开通API 权限"
                break
            if case(640018):
                return "微盘管理端未设置编辑权限"
                break
            if case(640019):
                return "API 调用次数超出限制"
                break
            if case(640020):
                return "非法的权限类型"
                break
            if case(640021):
                return "非法的fatherid"
                break
            if case(640022):
                return "非法的文件内容的base64"
                break
            if case(640023):
                return "非法的权限范围"
                break
            if case(640024):
                return "非法的fileid"
                break
            if case(640025):
                return "非法的space_name"
                break
            if case(640026):
                return "非法的spaceid"
                break
            if case(640027):
                return "参数错误"
                break
            if case(640028):
                return "空间设置了关闭成员邀请链接"
                break
            if case(640029):
                return "只支持下载普通文件，不支持下载文件夹等其他非文件实体类型"
                break
            if case():
                return "未知错误 %s" % errcode
