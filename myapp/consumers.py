from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http  
from channels.sessions import channel_session
from .models import Room


@channel_session_user_from_http
def ws_connect(message):
    prefix, pk = message['path'].strip('/').split('/')
    if prefix != 'room':
        return
    try:
        room = Room.objects.get(id=int(pk))

        if message.user == room.user:
            room.is_active = True
        else:
            room.number_of_current_user += 1
        room.save()
    except:
        return
    Group('Room-' + pk).add(message.reply_channel)
    message.channel_session['room'] = room.id
    message.reply_channel.send({"accept": True})


@channel_session_user
def ws_receive(message):
    try:
        pk = message.channel_session['room']
        room = Room.objects.get(id=pk)
        total_screens = room.screens.all().count()

        if room.user == message.user:
            if message.content['text'] == 'next':
                if room.current_screen + 1 <= total_screens - 1:
                    room.current_screen += 1
                else:
                    room.current_screen = 0
                room.save()

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
    Group('Room-' + str(pk)).send({'text': str(room.current_screen)})


@channel_session_user
def ws_disconnect(message):
    pk = message.channel_session['room']
    room = Room.objects.get(id=pk)
    if message.user == room.user:
        room.is_active = False
        room.number_of_current_user = 0
        room.save()
    else:
        room.number_of_current_user -= 1;
        room.save()
