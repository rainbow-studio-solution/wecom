Your Account
# ${object.name}

Dear ${object.name},  
  
Your account has been successfully created!

Your login is **${object.email}**

To gain access to your account, you can use the following link:

<font color="warning">[Go to My Account](/web/login?auth_login=${object.email})</font>

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
