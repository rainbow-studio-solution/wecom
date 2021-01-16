# Your Account

Dear ${object.name},  
  
A password reset was requested for the Odoo account linked to this email.
You may change your password by following this link which will remain valid during 24 hours:

[Change password](${object.signup_url})

If you do not expect this, you can safely ignore this email.  
  
Thanks,
% if user.signature:  
    ${user.signature | safe} 
% endif  

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
