#COMP1531 porject iteration 2
#write by HaoweiLou
#group H17A-Huawei
#starting a 13 Oct 2019
import re
import hashlib
import jwt
import random
import urllib.request
import os
from datetime import datetime, timezone, timedelta
from PIL import Image
from werkzeug.exceptions import HTTPException
class ValueError(HTTPException):
    code = 400
    message = 'No message specified'


#-------------------->Haowei Part START<-----------------------------
class AccessError(HTTPException):
    code = 400
    message = 'No message specified'

valid_email = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

DATA = {
    'userlist' : [],
    'channellist' : [],
    'reset_code_list': [],
    'message_list':[]
}
SECRET = 'Huawei'

def clearDATA():
    global DATA
    DATA = {
    'userlist' : [],
    'channellist' : [],
    'reset_code_list': [],
    'message_list':[]
}

def generateToken(username,u_id):
    global SECRET
    return jwt.encode({'username':username,'u_id':u_id},SECRET,algorithm='HS256').decode('utf-8')

def getUserFromToken(token):
    global SECRET
    global DATA
    decoded = jwt.decode(token,SECRET, algorithm = ['HS256'])
    return decoded['u_id']

def checkTokenIsActive(token):
    global DATA
    userlist = DATA['userlist']
    u_id = getUserFromToken(token)
    if check_uid_is_valid(u_id) == False:
        return
    if userlist[u_id]['active'] == False:
        raise AccessError("Token is not active")
    else:
        return
    raise ValueError("User with token is not valid")

def checkEmailInList(email):
    global DATA
    userlist = DATA['userlist']
    for users in userlist:
        if email == users['email']:
            return True
    return False

def getImageURLByToken(token):
    if type(token) == str:
        u_id = str(getUserFromToken(token))
    elif type(token) == int:
        u_id = str(token)
    photo_path = './image/' + u_id + '.jpg'
    if not os.path.exists(photo_path):
        photo_path = './image?file=default.jpg'
    else:
        photo_path = "./image?file="+u_id+".jpg"
    return photo_path

def check_inputname_is_valid(name):
    if len(name) > 50 or len(name) < 1: 
        raise ValueError("the user's name not is between 1 and 50 characters in length")

def check_uid_is_valid(u_id):
    global DATA
    if u_id < 0 or u_id >= len(DATA['userlist']): 
        return False
    return True

def check_channel_is_valid(channel_id):
    global DATA
    if channel_id >= len(DATA['channellist']) or channel_id < 0:
        raise ValueError(f'Channel {channel_id} is not a valid channel')

def check_message_is_valid(message_id):
    global DATA
    if message_id < 0 or message_id >= len(DATA['message_list']) or DATA['message_list'][message_id]['is_removed'] == True:  
        raise ValueError("message is not valid")

def user_is_admin(u_id):
    global DATA
    if DATA['userlist'][u_id]['privilege'] == 3:
        return False
    return True

def check_email(email):
    global DATA
    if checkEmailInList(email) == True:
        raise ValueError("Email address is already being used by another user")
    if re.search(valid_email,email) == None:
        raise ValueError("Email entered is not a valid")
    


def auth_register(email, password, name_first, name_last):
    global DATA
    userlist = DATA['userlist']
    check_email(email)
    if len(password) < 6:
        raise ValueError("Password entered is less than 6 characters long")
    check_inputname_is_valid(name_first)
    check_inputname_is_valid(name_last)

    hashedPassword = hashlib.sha256(password.encode()).hexdigest()
    #set handle for the user, if handle is already exsit, add number to make it unique
    handle = name_first.lower() + name_last.lower()
    number = -1      
    for i in range(len(userlist)):
        if handle == userlist[i]['handle_str']:
            number += 1
            handle += str(number)
            i = 0

    new_user = {
        'email' : email,
        'password' : hashedPassword,
        'name_first' : name_first,
        'name_last' : name_last,
        'u_id' : len(userlist),
        'handle_str' : handle,
        'active' : True,
        'privilege' : 0,
        'reset_code' : None
    }
    #if the new_user is first user in the slack, he is going to be the onwer
    if new_user['u_id'] == 0:
        new_user['privilege'] = 1
    else:
        new_user['privilege'] = 3
    
    userlist.append(new_user)
    token = generateToken(email,new_user['u_id'])
    return {'u_id':new_user['u_id'],'token':token}

def auth_login(email,password):
    global DATA
    userlist = DATA['userlist']
    hashedPassword = hashlib.sha256(password.encode()).hexdigest()

    if re.search(valid_email,email) == None:
        raise ValueError("Email entered is not a valid email")
    if checkEmailInList(email) == False:
        raise ValueError("Email entered does not belong to a user")
    dest_user = None
    for user in userlist:
        if email == user['email']:
            dest_user = user
            break
    if dest_user['password'] != hashedPassword:
        raise ValueError("Password is not correct")

    token = generateToken(email,dest_user['u_id'])
    dest_user['active'] = True
    return {'u_id':dest_user['u_id'],'token': token}

def auth_logout(token):
    u_id = getUserFromToken(token)
    global DATA
    userlist = DATA['userlist']
    if check_uid_is_valid(u_id):
        return {'is_success' : False}
    userlist[u_id]['active'] = False
    return {'is_success': True}

def auth_resetpassword_request(email):
    global DATA
    reset_code = random.randint(100000,999999)
    #generate a new, unused random number have 6 digit
    while reset_code in DATA['reset_code_list']:
        reset_code = random.randint(100000,999999)

    dest_user = None
    #check if user is in userlist
    for user in DATA['userlist']:
        if user['email'] == email:
            dest_user = user
            break
    #if user already sent request return nothing
    if dest_user and dest_user['reset_code'] is None:
        dest_user['reset_code'] = reset_code
        DATA['reset_code_list'].append(reset_code)
        return reset_code
    
    return None

def auth_resetpassword_reset(reset_code, password):
    global DATA
    reset_code = reset_code
    dest_user = None
    if len(password) < 6:
        raise ValueError("Password entered is not a valid password")
    
    if reset_code not in DATA['reset_code_list']:
        raise ValueError("reset_code is not a valid reset code")

    dest_user = None
    for user in DATA['userlist']:
        if user['reset_code'] == reset_code:
            dest_user = user
            dest_user['password'] = hashlib.sha256(password.encode()).hexdigest()
            user['reset_code'] = None
            DATA['reset_code_list'].remove(reset_code)
            break
            
    return {}
    
def user_profile(token,u_id):
    checkTokenIsActive(token)
    global DATA
    userlist = DATA['userlist']
    dest = None        
    for user in userlist:
        if user['u_id'] == u_id:
            dest = user
            break
    
    if dest == None:
        raise ValueError(f"User with {u_id} is not a valid user")
    
    photo_path = getImageURLByToken(u_id)

    return {'email':dest['email'],'name_first':dest['name_first'],
            'name_last':dest['name_last'],'handle_str':dest['handle_str'],
            'profile_img_url': photo_path[1:]}

def setname(token,name_first, name_last):
    checkTokenIsActive(token)
    check_inputname_is_valid(name_first)
    check_inputname_is_valid(name_last)
    u_id = getUserFromToken(token)
    global DATA
    userlist = DATA['userlist']

    userlist[u_id]['name_first'] = name_first
    userlist[u_id]['name_last'] = name_last

    return {}

def setemail(token,email):
    checkTokenIsActive(token)
    global DATA
    userlist = DATA['userlist']
    check_email(email)
    u_id = getUserFromToken(token)
    userlist[u_id]['email'] = email
    return {}

def sethandle(token,handle_str):
    checkTokenIsActive(token)
    global DATA
    userlist = DATA['userlist']
    if len(handle_str) >20 or len(handle_str) < 3:
        raise ValueError("handle_str must be between 3 and 20 characters")
    for user in userlist:
        if user['handle_str'] == handle_str:
            raise ValueError("handle is already used by another user")
    
    u_id = getUserFromToken(token)

    userlist[u_id]['handle_str'] = handle_str

def channel_create(token, name, is_public):
    checkTokenIsActive(token)
    if is_public == 'true' or is_public == True:
        is_public = True
    else:
        is_public = False

    if len(name) > 20 or len(name) <= 0:
        raise ValueError("Name is more than 20 characters long")
    u_id = getUserFromToken(token)
    global DATA
    channellist = DATA['channellist']
    channel_id = len(channellist)

    new_channel = {
        'name' : name,
        'channel_id' : channel_id,
        'is_public' : is_public,
        'owner' : [u_id],
        'member' : [u_id],
        'stand_up': {}
    }
    new_channel['name'] = name
    
    channellist.append(new_channel)
    
    return {'channel_id':channel_id}

def channel_addowner(token, channel_id, u_id):
    checkTokenIsActive(token)
    global DATA
    check_channel_is_valid(channel_id)
    channel = DATA['channellist'][channel_id]
    if u_id in channel['owner']:
        raise ValueError(f'When user with user id {u_id} is already an owner of the channel')
    owner = getUserFromToken(token)
    if owner not in channel['owner'] and not user_is_admin(u_id):
        raise AccessError(f"{owner} is not an owner of channel {channel_id}")
    
    channel['owner'].append(u_id)
    if u_id not in channel['member']:
        channel['member'].append(u_id)
    return {}

def channel_removeowner(token, channel_id, u_id):
    checkTokenIsActive(token)
    global DATA
    check_channel_is_valid(channel_id)
    channel = DATA['channellist'][channel_id]
    if u_id not in channel['owner']:
        raise ValueError(f'When user with user id {u_id} is not an owner of the channel')
    owner = getUserFromToken(token)
    if owner not in channel['owner'] and not user_is_admin(owner):
        raise AccessError('the authorised user is not a member or admin of channel or slack')
    if owner == u_id:
        raise AccessError('the authorised user can not remove himself as a owner')
    channel['owner'].remove(u_id)
    return {}

def channel_messages(token, channel_id, start):
    checkTokenIsActive(token)
    global DATA
    check_channel_is_valid(channel_id)
    channel = DATA['channellist'][channel_id]
    u_id = getUserFromToken(token)
    #raise error if user is not in the channel, and he is not an slac admin and channel is a private channel
    if u_id not in channel['member'] and not user_is_admin(u_id) and channel['is_public'] == False:
        raise AccessError('Authorised user is not a member of channel with channel_id')
    message_list = []
    for message in DATA['message_list']:
        #if the message is in the dest channel, and has not been removed, add it into the output message list
        if message['channel_id'] == channel_id and message['is_removed'] == False and datetime.utcnow() >= message['time_created']:
            return_reacts = []
            for react in message['reacts']:
                new_react = {'react_id': react['react_id'], 'u_ids':react['u_ids'], 'is_this_user_reacted':(u_id in react['u_ids'])}
                return_reacts.append(new_react)

            return_message = {
                'message_id' : message['message_id'],
                'u_id' :  message['u_id'],
                'message' : message['message'],
                'time_created' : message['time_created'].replace(tzinfo=timezone.utc).timestamp(),
                'reacts' : return_reacts,
                'is_pinned': message['is_pinned']
            }
            message_list.append(return_message)

    if start >= len(message_list) and len(message_list) != 0:
        raise ValueError('start is greater than or equal to the total number of messages in the channel')

    message_list = sorted(message_list, key = lambda i: i['time_created'], reverse= True)
    if start + 50 >= len(message_list):
        end = -1
    else:
        end = start + 50
    return {'messages' : message_list[start:50], 'start' : start, 'end' : end}

def admin_userpermission_change(token, u_id, permission_id):
    global DATA
    checkTokenIsActive(token)
    owner = getUserFromToken(token)
    # when the token refer to a user that is not an owner or admin
    if not user_is_admin(owner):
        raise AccessError(f"{owner} is not an admin or owner")
    if DATA['userlist'][u_id]['privilege'] == 1 and DATA['userlist'][owner]['privilege'] == 2:
        raise AccessError(f"{owner} is cannot change {u_id}'s privileges")
    if check_uid_is_valid(u_id) == False:
        raise ValueError(f"{u_id} does not refer to a valid user")
    if permission_id > 3 or permission_id <= 0:
        raise ValueError(f"{permission_id} does not refer to a value permission")
    
    DATA['userlist'][u_id]['privilege'] = permission_id

    return {}

def channels_list(token):
    global DATA
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    channels = []
    for channel in DATA['channellist']:
        if u_id in channel['member']:
            new_channel = {
                'channel_id' : channel['channel_id'],
                'name' : channel['name']
            }
            channels.append(new_channel)
    return {'channels':channels}

def channels_listall(token):
    global DATA
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    channels = []
    for channel in DATA['channellist']:
        new_channel = {
            'channel_id' : channel['channel_id'],
            'name' : channel['name']
        }
        channels.append(new_channel)
    return {'channels':channels}
    
def message_send(token, channel_id, message):
    global DATA
    checkTokenIsActive(token)
    if len(message) > 1000:
        raise ValueError('Message is more than 1000 characters')
    u_id = getUserFromToken(token)
    dest_channel = DATA['channellist'][channel_id]
    #raise error if the user is not a member of channel and he is not an admin
    if u_id not in dest_channel['member'] and not user_is_admin(u_id):
        raise AccessError(f'{u_id} is not join the channel  {channel_id}')
    #assume its unread at first, and not pinned
    react = {
        'react_id' : 1,
        'u_ids' : []
    }
    new_message = {
        'message_id' : len(DATA['message_list']),
        'u_id' : u_id,
        'channel_id' : channel_id,
        'message' : message,
        'time_created' : datetime.utcnow(),
        'is_unread' : True,
        'reacts' : [react],
        'is_pinned': False,
        'is_removed' : False
    }
    DATA['message_list'].append(new_message)
    return {'message_id' : new_message['message_id']}

def standup_send(token, channel_id, message):
    #if the channel_id is not valid, raise error
    check_channel_is_valid(channel_id)
    #if length of the message is over 1000 word raise error
    if len(message) > 1000:
        raise ValueError('Message is more than 1000 characters')
    channel = DATA['channellist'][channel_id]
    #if there is no standup function or the time is out aleardy, raise accesserror
    #update the channel standup status
    channel['stand_up']['is_active'] = channel['stand_up']['timeout'] > datetime.utcnow()
    if channel['stand_up']['is_active'] == False:
        raise AccessError('The standup time has stopped')
    if channel['stand_up'] == {}:
        raise AccessError('No stand up happened in this channel')
    #if user is not in channel and he is not an admin of slack, raise accesserror
    u_id = getUserFromToken(token)
    user = DATA['userlist'][u_id]
    if u_id not in channel['member'] and not user_is_admin(u_id):
        raise AccessError('The authorised user is not a member of the channel that the message is within')
    #find the message that the standup of the channel is going to send
    message_id = channel['stand_up']['message_id']
    dest_message = DATA['message_list'][message_id]
    #add the new message from stand up send into the message's queque
    dest_message['message'] = dest_message['message'] + user['handle_str'] + ': ' + message + '\n'
    return {}

def user_profile_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    if urllib.request.urlopen(img_url).getcode() != 200:
        raise ValueError('img_url is returns an HTTP status other than 200')
    if not img_url.lower().endswith('.jpg'):
        raise ValueError('Image uploaded is not a JPG')

    image_address = './image/' + str(getUserFromToken(token)) + '.jpg' 
    urllib.request.urlretrieve(img_url,image_address)
    image_object = Image.open(image_address)
    width,height = image_object.size

    if (x_start < 0 or x_start > width or x_end < 0 or x_end > width or 
        y_start < 0 or y_start > height or y_end < 0 or y_end > height ):
        os.remove(image_address)
        raise ValueError('x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL')
    if (x_start >= x_end or y_start >= y_end):
        os.remove(image_address)
        raise ValueError('Wrong input since the start value cannot be equal or greater than end value')
    cropped = image_object.crop((x_start, y_start, x_end, y_end))
    cropped.save(image_address)
    return {}

def standup_is_active(token,channel_id):
    checkTokenIsActive(token)
    channel = DATA['channellist'][channel_id]
    if channel['stand_up'] == {} or channel['stand_up']['timeout'] < datetime.utcnow():
        is_active = False
        channel['stand_up'] = {}
        timeout = None
    else:
        is_active = True
        timeout = channel['stand_up']['timeout'].replace(tzinfo=timezone.utc).timestamp()
    return {'is_active':is_active, 'time_finish':timeout}
#-------------------->Haowei Part END<-----------------------------
'''
Below part is writen by Haokai
Include channel_detail, channel_join, channel_invite, channel_join
'''
#-------------------->Haokai Part START<-----------------------------
# Given a channel_id of a channel that the authorised user can join, 
# adds them to that channel

######## imports are needed ########
def channel_join(token, channel_id):
    # check if the channel_id is valid
    # if not, raise a ValueError
    check_channel_is_valid(channel_id)
    channel = DATA["channellist"][channel_id]
    
    # check if the token is valid
    # if not, raise a ValueError
    # if yes, get the u_id
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    
    # check if the channel is private,
    # if yes, raise AccessError
    if channel["is_public"] == False and not user_is_admin(u_id):
        raise AccessError(f"Error, channel {channel_id} is private")
    
    # check if the user is already in the channel
    # if yes, print an apporipriate message
    if u_id in channel['member']:
        return {}
    
    # if no errors are raised,
    # add the user to the channel
    channel["member"].append(u_id)
    #if the user is the only person in the channel, make him to be the owner
    if len(channel['owner']) == 0:
        channel['owner'].append(u_id)
    return {}

def channel_detail(token, channel_id):
    # check if the token is valid
    # if not, raise ValueError
    global DATA
    checkTokenIsActive(token)
        
    # get u_id from token
    u_id = getUserFromToken(token)
    
    # check if the channel is valid
    # if not, raise ValueError
    check_channel_is_valid(channel_id)
        
    # get chann.el from channel_id
    channel = DATA["channellist"][channel_id]
    
    # check if the user is in the channel
    # if not, raise AccessError
    if u_id not in channel["member"] and not user_is_admin(u_id) and channel['is_public'] == False:
        raise AccessError(f"Error, user {u_id} is not in the channel")
    
    # if no errors are raised, 
    # use channel["owner"] to get a list of names of owners
    # use channel["member"] to get a list of names of members
    owner_names = []
    member_names = []
    for i in channel["owner"]:
        tmp = {
            'u_id': i,
            'name_first': DATA['userlist'][i]['name_first'],
            'name_last':DATA['userlist'][i]['name_last'],
            'profile_img_url':getImageURLByToken(i)[1:]
        }
        owner_names.append(tmp)
        
    for j in channel["member"]:
        tmp = {
            'u_id': j,
            'name_first': DATA['userlist'][j]['name_first'],
            'name_last':DATA['userlist'][j]['name_last'],
            'profile_img_url':getImageURLByToken(j)[1:]
        }
        member_names.append(tmp)
        
    # return {name, owner_members, all_members}
    return {'name':channel["name"], 'owner_members':owner_names, 'all_members':member_names}

def channel_invite(token, channel_id, u_id):
    # check if the channel_id refers to a vaild channel,
    # if no, raise a ValueError
    # if yes, get the channel by channel_id
    check_channel_is_valid(channel_id)
    channel = DATA["channellist"][channel_id]
    
    # check if the token is valid
    # if no, raise a ValueError
    # if yes, get the inviter's u_id by the token
    checkTokenIsActive(token)
    inviter_id = getUserFromToken(token)
    
    # check if the u_id refers to a valid user,
    # if not, raise a ValueError
    if u_id < 0 or u_id >= len(DATA["userlist"]):
        raise ValueError(f"Error, invalid user {u_id}is invited")
    
    # check if the inviter is in the channel
    # if not, raise an AccessError
    if inviter_id not in channel["member"]:
        raise AccessError(f"Error, inviter {inviter_id} is not in the channel")
    
    # check if the user is already in the channel
    # if yes, print an apporipriate message
    if u_id in channel["member"]:
        return {}
    
    # if no errors are raised,
    # append a user to the member list
    channel["member"].append(u_id)
    return {}

def channel_leave(token, channel_id):
    # check if the token is valid
    # if not, raise ValueError
    # if yes, get u_id from token
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    
    # check if the channel is valid
    # if not, raise ValueError
    # if yes, get the channel from channel_id
    check_channel_is_valid(channel_id)
    channel = DATA["channellist"][channel_id]
    
    # check if the user is in channel
    # if no, print an apporipirate message and pass
    if u_id not in channel['member']:
        return {}
    
    # otherwise, remove the user from channel
    channel["member"].remove(u_id)
    if u_id in channel['owner']:
        channel['owner'].remove(u_id)
    return {}

def standup_start(token, channel_id,length):
    # check if the channel_id is valid
    # if not, raise a ValueError
    check_channel_is_valid(channel_id)
    channel = DATA["channellist"][channel_id]
    
    u_id = getUserFromToken(token)
    user = DATA['userlist'][u_id]
    # check if the user is in the channel
    # if no, print an apporipriate message
    if u_id not in channel["member"] and not user_is_admin(u_id):
        raise AccessError(f"user {u_id} is not in the channel")
    
    if channel['stand_up'] != {} and channel['stand_up']['timeout'] > datetime.utcnow():
        raise ValueError('An active standup is currently running in this channe')
    # if no error is raised, channel come into the standup period
    # update the standup_finish time
    timeout = datetime.utcnow() + timedelta(seconds=length)
    message_id = message_sendlater(token,channel_id,'',timeout)
    standup = {
        'timeout' : timeout,
        'message_id':message_id['message_id']
    }
    channel['stand_up'] = standup
    timeout = timeout.replace(tzinfo=timezone.utc).timestamp()

    return {'time_finish':timeout}


#-------------------->Haokai Part END<-----------------------------

#-------------------->Jinning Part START<-----------------------------
def message_edit(token, message_id, message):
    checkTokenIsActive(token)
    global DATA
    u_id = getUserFromToken(token)
    old_message = DATA['message_list'][message_id]
    channel = DATA['channellist'][old_message['channel_id']]
    if (u_id != old_message['u_id']) and (u_id not in channel['owner'] and not user_is_admin(u_id)):
        raise AccessError (f'When user with user id {u_id} is not an owner or admin of the channel and not the creater of this message')
    old_message['message'] = message
    if old_message['message'] == "":
        old_message['is_removed'] = True
    return {}

def message_remove(token, message_id):
    checkTokenIsActive(token)
    global DATA
    u_id = getUserFromToken(token)
    message = DATA['message_list'][message_id] 
    if (message['is_removed'] == True):
        raise ValueError (f'Message with message id {message_id} is not exist')       
    channel = DATA['channellist'][message['channel_id']]
    if (u_id != message['u_id']) and (u_id not in channel['owner'] and not user_is_admin(u_id)):
        raise AccessError (f'When user with user id {u_id} is not an owner or admin of the channel and not the creater of this message')
    
    message['is_removed'] = True
    return {}

def message_sendlater(token, channel_id, message, time_sent):
    global DATA
    #print(time_sent)
    checkTokenIsActive(token)
    if type(time_sent) != datetime:
        time_sent = datetime.utcfromtimestamp(time_sent)
    
    # the case channel_id is invalid
    check_channel_is_valid(channel_id)
    # the case message is more than 1000 characters
    if len(message) > 1000:
        raise ValueError('Message is more than 1000 characters')
    # the case the time is in the past    
    if (datetime.utcnow() > time_sent):
        raise ValueError(f'{time_sent} is a time in the past') 
    u_id = getUserFromToken(token)
    dest_channel = DATA['channellist'][channel_id]
    # the case the user is a normal member and is not a member of the channel
    if u_id not in dest_channel['member'] and not user_is_admin(u_id):
        raise AccessError(f'{u_id} is not join the channel  {channel_id}')           
    #assume its unread at first, and not pinned, and the message is hiden as not sent
    react = {
        'react_id' : 1,
        'u_ids' : []
    }
    new_message = {
        'message_id' : len(DATA['message_list']),
        'u_id' : u_id,
        'channel_id' : channel_id,
        'message' : message,
        'time_created' : time_sent,
        'is_unread' : True,
        'reacts' : [react],
        'is_pinned': False,
        'is_removed' : False
    }
    DATA['message_list'].append(new_message)
    return {'message_id':new_message['message_id']}

#-------------------->Jinning Part END<-----------------------------

#-------------------->Yifei Part START<-----------------------------
def message_pin(token, message_id): 
    global DATA 
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    
    pinning_message = DATA['message_list'][message_id]    
    User = DATA['userlist'][u_id]
    
    channel_id = DATA['message_list'][message_id]['channel_id']
    
    check_message_is_valid(message_id)
    dest_channel = DATA['channellist'][channel_id]
    if not user_is_admin(u_id) and u_id not in dest_channel['owner']:
        raise ValueError("The authorised user is not an admin")
    if pinning_message['is_pinned'] == True:
        raise ValueError("already pinnned")  


    pinning_message['is_pinned'] = True
                
    return {}  

def message_unpin(token, message_id): 
    global DATA 
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    
    pinning_message = DATA['message_list'][message_id]    
    User = DATA['userlist'][u_id]
    
    channel_id = DATA['message_list'][message_id]['channel_id']
                  
    check_message_is_valid(message_id)
    dest_channel = DATA['channellist'][channel_id]
    if not user_is_admin(u_id) and u_id not in dest_channel['owner']:
        raise ValueError("The authorised user is not an admin")
    if pinning_message['is_pinned'] == False:
        raise ValueError("haven't been pinnned yet")
    

    pinning_message['is_pinned'] = False
                
    return {}  

def message_react(token, message_id, react_id):
    global DATA 
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)   
    reacting_message = DATA['message_list'][message_id]
    react_list = reacting_message['reacts']
    
    check_message_is_valid(message_id)
    
    if u_id not in DATA['channellist'][reacting_message['channel_id']]['member']:  
        raise ValueError(f"{u_id} is not a member of {channel_id}")
  
    
    if react_id != 1:
        raise ValueError("reaction is not valid")

    for reactions in react_list:   
        #if the react with the user of message is already exist and reacted, raise error      
        if react_id == reactions['react_id'] and u_id in reactions['u_ids']:
            raise ValueError(f"message have been already reacted by the user {u_id}")
        #if the react with the user of message is already exist but is unreacted, make it react
        if react_id == reactions['react_id'] and u_id not in reactions['u_ids']:
            reactions['u_ids'].append(u_id)
            return {}

def message_unreact(token, message_id, react_id):
    global DATA 
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)   
    reacting_message = DATA['message_list'][message_id]
    react_list = reacting_message['reacts']
    
    check_message_is_valid(message_id)
    
    if u_id not in DATA['channellist'][reacting_message['channel_id']]['member']:  
        raise ValueError(f"{u_id} is not a member of {channel_id}")
  
    if react_id != 1:
        raise ValueError("reaction is not valid")

    for reactions in react_list:      
        #if the react with the user of message is already exist and unreacted, raise error           
        if react_id == reactions['react_id'] and u_id not in reactions['u_ids']:
            raise ValueError(f"message have been already unreacted by the user {u_id}")
        #if the react with the user of message is already exist but is reacted, make it unreact
        if react_id == reactions['react_id'] and u_id in reactions['u_ids']:
            reactions['u_ids'].remove(u_id)
            return {}

def search(token, query_str):
    global DATA
    new = []
    checkTokenIsActive(token)
    u_id = getUserFromToken(token)
    user = DATA['userlist'][u_id]
    for message in DATA['message_list']:
        if ((query_str in message['message'] and (u_id in DATA['channellist'][message['channel_id']]['member'] or user['privilege'] != 3))
        and (datetime.utcnow() >= message['time_created'])):
            return_reacts = []
            for react in message['reacts']:
                return_react = {'react_id': react['react_id'], 'u_ids':react['u_ids'], 'is_this_user_reacted' : (u_id in react['u_ids'])}
                return_reacts.append(return_react)

            return_message = {
                'message_id' : message['message_id'],
                'u_id' :  message['u_id'],
                'message' : message['message'],
                'time_created' : message['time_created'].replace(tzinfo=timezone.utc).timestamp(),
                'reacts' : return_reacts,
                'is_pinned': message['is_pinned']
            }
            new.append(return_message)
    new = sorted(new, key = lambda i: i['time_created'], reverse= True)
    return {'messages' : new}

def users_list(token):
    global DATA
    checkTokenIsActive(token)
    output = []
    for user in DATA['userlist']:
        new = {'u_id' : user['u_id']}
        new.update(user_profile(token,user['u_id']))
        output.append(new)
    return {'users': output}

#-------------------->Yifei Part END<-----------------------------
#-------------------->self test in local<-----------------------------
#no need to look
if __name__ == '__main__':
    token1 = auth_register("591193117@qq.com",'123456','jnning', 'liu')
    token2 = auth_register("59119117@qq.com",'123456','haowei', 'lou')
    '''
    user_profile_upload_photo(token1['token'],
    'https://mumsofcoffsharbour.com.au/wp-content/uploads/2019/01/Active-Kids-Vouchers-min.jpg',0,0,400,400)
    print(user_profile(token1['token'],0))
    print(base_url)
    '''
    channel_create(token2['token'],'jinning',True)
    channel_invite(token2['token'],0,0)
    print(channel_detail(token2['token'],0))
    print(channels_list(token1['token']))
    #print(DATA)