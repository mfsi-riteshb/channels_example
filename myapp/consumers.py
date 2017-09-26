
from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http  
from channels.sessions import channel_session

from .models import Room


@channel_session_user_from_http
def ws_connect(message):
    """Connect user through web sockets.

    When user connect to room which he owns then make the room active,
    else increase the number of current_user.

    Args:
        message: Channels Message object.

    Returns:
        Successfull connection.
    """
    prefix, room_id = message['path'].strip('/').split('/')
    if prefix != 'room':
        return
    try:
        room = Room.objects.get(id=int(room_id))
        if message.user == room.user:
            room.is_active = True
        else:
            room.number_of_current_user += 1
        room.save()
    except:
        return
    Group('Room-' + room_id).add(message.reply_channel)
    message.channel_session['room'] = room.id
    message.reply_channel.send({"accept": True})


@channel_session_user
def ws_receive(message):
    """Receive message from connected user.

    Receive message from connected user and check if room belong to user,
    if yes then perform increase/decrease in current screen and return it.
    else return nothing.

    Args:
        message: Channels Message object

    Return:
        current screen of the the room for which request came.
    """
    try:
        room_id = message.channel_session['room']
        room = Room.objects.get(id=room_id)
        total_screens = room.screens.all().count()

        # Check if room belongs to user and increase the current_screen number
        # if next signal came from owner else if previous signal comes from
        # user then decrease the current_screen number.
        # return current screen

        # we are doing (total_screen -1) as index of screen starts from 0
        if room.user == message.user:

            # if message is next we increase the current screen if value of
            # current screen is less than the total_screen value, else
            # we make current screen 0
            if message.content['text'] == 'next':
                if room.current_screen + 1 <= total_screens - 1:
                    room.current_screen += 1
                else:
                    room.current_screen = 0
                room.save()

            # if message is previous we decrease the current screen if value of
            # current screen is more than the 0 , else
            # we make current screen as value of total_screen-1
            elif message.content['text'] == 'previous':
                if room.current_screen - 1 >= 0:
                    room.current_screen -= 1
                else:
                    room.current_screen = total_screens - 1
                room.save()
            else:
                return
        else:
            return
    except Room.DoesNotExist:
        return
    Group('Room-' + str(room_id)).send({'text': str(room.current_screen)})


@channel_session_user
def ws_disconnect(message):
    """Disconnect the user.

    Once the user disconnect, if he owns the room make the room inactive
    or if user doesn't owns the room reduce number_of_current user.

    Args:
        message: Channel Message object.

    Return:
        No return
    """
    room_id = message.channel_session['room']
    room = Room.objects.get(id=room_id)
    if message.user == room.user:
        room.is_active = False
        room.number_of_current_user = 0
        room.save()
    else:
        room.number_of_current_user -= 1
        room.save()
