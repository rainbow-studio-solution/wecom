# 您的账号 ${object.user_id.name}

## 尊敬的 ${object.user_id.name or ''},

## 您已经获得了${object.user_id.company_id.name}的门户。

## 您的登录账户数据是:

> 用户名: ${object.user_id.login or ''}

> 门户地址: <a href="${'portal_url' in ctx and ctx['portal_url'] or ''}">${'portal_url' in ctx and ctx['portal_url'] or ''}</a>

> 数据库: ${'dbname' in ctx and ctx['dbname'] or ''}

## 您可以通过以下URL设置或更改密码：

> <a href="${object.user_id.signup_url}">${object.user_id.signup_url}</a>

## ${object.wizard_id.welcome_message or ''}

#### ${object.user_id.company_id.name}
` ${object.user_id.company_id.phone} % if object.user_id.company_id.email | <a href="'mailto:%s' % ${object.user_id.company_id.email}" style="text-decoration:none; color: #454748;">${object.user_id.company_id.email}</a> % endif % if object.user_id.company_id.website  | <a href="'%s' % ${object.user_id.company_id.website}" style="text-decoration:none; color: #454748;"> ${object.user_id.company_id.website} </a> % endif`
            