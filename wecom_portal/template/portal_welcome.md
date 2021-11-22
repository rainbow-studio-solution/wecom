# Your Account ${object.user_id.name}

## Dear ${object.user_id.name or ''},

## You have been given access to ${object.user_id.company_id.name}'s portal.

## Your login account data is:

> Username: ${object.user_id.login or ''}

> Portal: <a href="${'portal_url' in ctx and ctx['portal_url'] or ''}">${'portal_url' in ctx and ctx['portal_url'] or ''}</a>

> Database: ${'dbname' in ctx and ctx['dbname'] or ''}

## You can set or change your password via the following url:

> <a href="${object.user_id.signup_url}">${object.user_id.signup_url}</a>

## ${object.wizard_id.welcome_message or ''}

---------------
#### ${object.user_id.company_id.name}
` ${object.user_id.company_id.phone} % if object.user_id.company_id.email | <a href="'mailto:%s' % ${object.user_id.company_id.email}" style="text-decoration:none; color: #454748;">${object.user_id.company_id.email}</a> % endif % if object.user_id.company_id.website  | <a href="'%s' % ${object.user_id.company_id.website}" style="text-decoration:none; color: #454748;"> ${object.user_id.company_id.website} </a> % endif`