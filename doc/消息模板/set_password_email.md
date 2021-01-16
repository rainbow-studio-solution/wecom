Welcome to Odoo
# ${object.name}

Dear ${object.name},  
  
You have been invited by ${object.create_uid.name} of ${object.company_id.name} to connect on Odoo.

[Accept invitation](${object.signup_url})

% set website_url = object.env['ir.config_parameter'].sudo().get_param('web.base.url') Your Odoo domain is: **[${website_url}](${website_url})**

Your sign in email is: **<a href="/web/login?login=${object.email}" target="_blank">${object.email}</a>**

Your sign in email is: [${object.email}]('/web/login?login=${object.email}'){:target="_blank"}

Never heard of Odoo? It’s an all-in-one business software loved by 3+ million users. It will considerably improve your experience at work and increase your productivity.

Have a look at the <font color="warning"><a href='https://www.odoo.com/page/tour?utm_source=db&amp;utm_medium=auth' target='_blank'>Odoo Tour</a></font> to discover the tool.

Enjoy Odoo!

The ${object.company_id.name} Team
  

#  
**${object.company_id.name}**
 
${object.company_id.phone} 
    % if object.company_id.email 
    |[${object.company_id.email}]('mailto:%s' % ${object.company_id.email}) 
% endif
% if object.company_id.website 
    | [${object.company_id.website}]('%s' %${object.company_id.website}) 
% endif  
Powered by [Odoo](https://www.odoo.com?utm_source=db&utm_medium=auth)  
