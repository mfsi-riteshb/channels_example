
import json

from channels import Group
from channels.auth import (
    channel_session_user,
    channel_session_user_from_http
)

from .models import Room, RoomActiveUser, RoomMessage


@channel_session_user_from_http
def ws_connect(message):
    """Connect user through web sockets.

    When user connect to room which he owns then make the room active,
    else increase the number of current_user.
    And make entry in room_active_user table.

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
        try:
            RoomActiveUser.objects.create(user=message.user, room=room)
        except Exception:
            pass
        room.save()
    except:
        return

    Group('Room-' + room_id).add(message.reply_channel)

    # create list of all the current active users adn sent it through socket
    active_users = []
    for active_user in RoomActiveUser.objects.all():
        active_users.append(str(active_user.user))

    Group('Room-' + str(room_id)).send({
        "text": "user_joined:-" + json.dumps({
            "text": active_users
        })
    })

    # send message as who is the new joinee.
    Group('Room-' + str(room_id)).send({
        "text": 'joined:-{} has joined'.format(message.user)
    })

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
        -- Brodcast current screen of the the room for which request came.
        -- Or broadcast data came from frontend.
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
            elif message.content['text'].split(':-')[0] == 'message':
                RoomMessage.objects.create(
                    user=message.user,
                    room=room,
                    message=message.content['text'].split(':-')[1]
                )
                message_str = str(message.user) + ":" + str(message.content['text'].split(':-')[1])
                message_str = "message:-" + message_str
                Group('Room-' + str(room_id)).send(
                    {'text': message_str}
                )
            else:
                Group('Room-' + str(room_id)).send(
                    {'text': str(message.content['text'])}
                )
        else:
            return
    except Room.DoesNotExist:
        return
    Group('Room-' + str(room_id)).send(
        {'text': message.content['text'] + ":-" + str(room.current_screen)}
    )


@channel_session_user
def ws_disconnect(message):
    """Disconnect the user.

    Once the user disconnect, if he owns the room make the room inactive
    or if user doesn't owns the room reduce number_of_current user.
    and send current active user's list

    Args:
        message: Channel Message object.

    Return:
        Broadcast current active user and message for user leaving room.
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

    try:
        RoomActiveUser.objects.get(user=message.user, room=room).delete()
    except RoomActiveUser.DoesNotExist:
        pass

    active_users = []

    for active_user in RoomActiveUser.objects.all():
        active_users.append(str(active_user.user))

    Group('Room-' + str(room_id)).send({
        "text": "user_joined:-" + json.dumps({
            "text": active_users
        })
    })

    # send message as who is the new joinee.
    Group('Room-' + str(room_id)).send({
        "text": 'left:-{} has left the room'.format(message.user)
    })
