
from datetime import datetime

from django.shortcuts import render
from django.views import View
from django.shortcuts import render, render_to_response
from django.views.generic import ListView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from .models import Room
from .forms import RoomForm, RoomScreenForm
# Create your views here.


class HomeView(View):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class RoomView(View):
    template_name = 'rooms_list.html'
    form = RoomForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            rooms = Room.objects.all()
            return render(
                request, self.template_name,
                {'rooms': rooms, 'user': self.request.user, 'form': self.form}
            )
        else:
            return redirect('/login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                room = form.save(commit=False)
                room.user = request.user
                room.created_at = datetime.now()
                room.save()
                return redirect('/rooms', foo='bar')
            return render_to_response('/rooms', {'form': form})
        else:
            return redirect(request, '/login')


class RoomDetailView(View):
    template_name = 'room_detail.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                room = Room.objects.get(id=self.kwargs.get('pk', None))
                screens = room.screens.all()
            except Room.DoesNotExist:
                raise Http404("Room does not exist")
            if not room.is_active and room.user != request.user:
                raise Http404("Room is not yet active")
            return render(
                request,
                self.template_name,
                {
                    'room': room,
                    'is_owner': room.user == request.user,
                    'screens': screens,
                    'current_screen': room.current_screen,
                    'total_screens': room.screens.count() - 1
                }
            )
        else:
            return redirect('/login')


class ScreenView(View):
    template_name = 'screen.html'
    form = RoomScreenForm

    def get(self, request, *args, **kwargs):
        try:
            room = Room.objects.get(id=self.kwargs.get('pk', None))
            if room.user != request.user:
                raise Room.DoesNotExist
            screen = room.screens.all()
        except Room.DoesNotExist:
            return HttpResponseRedirect(reverse('rooms_list'))
        form = RoomScreenForm
        return render(
            request, self.template_name,
            {'screens': screen, 'user': self.request.user, 'form': form}
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            room_id = self.kwargs['pk']
            try:
                room = Room.objects.get(pk=room_id)
            except Room.DoesNotExist:
                return Http404("Room Does Not Exist")
            form = self.form(request.POST)
            if form.is_valid():
                screen = form.save(commit=False)
                screen.room = room
                screen.save()
                return HttpResponseRedirect(reverse('rooms_detail', args=[room.id]))

            else:
                return render_to_response('/rooms', {'form': form})
        else:
            return redirect('/login')
