number of line before edit in the file functions.py: 880

1. Write a new helper function named check_inputname_is_valid to replace the if statement: 

if len(name_last) > 50 or len(name_last) < 1:   
    raise ValueError("name_last not is between 1 and 50 characters in length")
to make the code more maintainable

changed function: auth_register, setname

number_of_line after : 877

The benefit for this change is if the website admin wants to change the max length of users' first and last name, they can easily change the parameter in this function and will be applied in all functions.

2. Write a new helper function named check_uid_is_valid to replace the if statement: 
if u_id < 0 or u_id >= len(DATA['userlist']):
to make the code more maintainable

changed function: checkTokenIsActive, authlogout, admin_userpermission_change


3. Write a new helper function named check_channel_is_valid to replace the if statement: 
if channel_id >= len(DATA['channellist']) or channel_id < 0:
to make the code more maintainable

changed function: channel_addowner, channel_removeowner, channel_messages, standup_send, channel_detail,channel_invite, channel_leave, standup_start, message_sendlater, channel_join

number_of_line after : 878

4. Write a new helper function named user_is_admin to replace the if statement: 
DATA['userlist'][u_id]['privilege'] == 3:
to check if a user is admin

changed function: 
    channel_removeowner, channel_addowner, channel_messages, admin_userpermission_change, message_send, standup_send, channel_join, channel_detail, standup_start, message_edit, message_remove, message_sendlater, message_pin, message_unpin

This change is solving the 'DRY' problems, since it replace the repeat code in checking whether is an admin or not from "DATA['userlist'][u_id]['privilege'] == 3:" with a helper function so that the space of source code is reduced and avoid some situation that makes the code break if change is made

5. Write a new helper function named check_message_is_valid(message_id) the source code is:

    def check_message_is_valid(message_id):
        global DATA
        if message_id < 0 or message_id >= len(DATA['message_list']) or DATA['message_list'][message_id]['is_removed'] == True:  
            raise ValueError("message is not valid")

changed function: 
    channel_removeowner, channel_addowner, channel_messages, admin_userpermission_change, message_send, standup_send, channel_join, channel_detail, standup_start, message_edit,message_remove, message_sendlater, message_pin, message_unpin

This purpose of this code is to check whether the message with the message_id is exsiting and it is not been removed. There are totally 5 functions require this function, apply this code will help to reduce the repetition codes in the source and avoid code break.

6. Write a new helper function named check_email(email) to check whether the email is exsit and it has not been used by other users, and the source code for that function is:

def check_email(email):
    global DATA
    if checkEmailInList(email) == True:
        raise ValueError("Email address is already being used by another user")
    if re.search(valid_email,email) == None:
        raise ValueError("Email entered is not a valid")

channged function: auth_register, set_email