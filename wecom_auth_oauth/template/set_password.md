## 亲爱的 ${object.name},
您好！首先请允许我代表我们公司欢迎您的加入。这是来自 ${object.company_id.name} 的 ${object.create_uid.name} 为您开通系统账号的邀请邮件。请您点击
[接受邀请](${object.signup_url})
% set website_url = object.env['ir.config_parameter'].sudo().get_param('web.base.url') 
> 系统登陆地址为： [${website_url}](${website_url})
> 您的登录账号是: [${object.login}](/web/login?login=${object.login})
#### 我们公司的工作忠旨是严格，创新，诚信。您的加入将为我们带来新鲜的血液，带来创新的思维，以及为我们树立良好的公司形象！
#### 祝您在本公司，工作愉快，实现自己的人生价值！
## ${object.company_id.name}
<font color=\"comment"\>电话:${object.company_id.phone} </font>
% if object.company_id.email 
<font color=\"comment"\>E-mail:${object.company_id.email}</font>
% endif 
% if object.company_id.website
<font color=\"comment"\>网站:${object.company_id.website}</font>
% endif 