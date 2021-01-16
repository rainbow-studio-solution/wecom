% set invited_users = ctx['invited_users']
# Pending Invitations

Dear ${object.name or ''}, 
  
You added the following user(s) to your database but they haven't registered yet:

% for invited_user in invited_users:
####   ${invited_user}
% endfor
  
Follow up with them so they can access your database and start working with you.

Have a nice day!

The ${object.company_id.name} Team
# 