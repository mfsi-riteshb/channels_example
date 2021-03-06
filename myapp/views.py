# -*- coding: utf-8 -*-

from datetime import datetime

from django.shortcuts import render
from django.views import View
from django.shortcuts import render, render_to_response
from django.views.generic import ListView
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.views.generic import UpdateView

from .models import Room, Screen
from .forms import RoomForm, RoomScreenForm


def custom_login(request):
    """Handle Custom login.

    Args:
        request: instance of Request object

    Returns:
        if user is authenticated return room_list page
        else redirect to login
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('rooms_list'))
    else:
        return login(request)


class HomeView(View):
    """Get the home page."""

    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        """Handle get request.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Returns:
            if user is authetnticated redirect to room
            else return rendered response of template 'home.html'
        """
        if request.user.is_authenticated:
            return redirect('/rooms')
        return render(request, self.template_name)


class RoomView(View):
    """Get/Post Room.

    GET - Get List of room
    POST - Creation of room
    Redirect to Login if  not authenticated.
    """

    template_name = 'rooms_list.html'
    form = RoomForm

    def get(self, request, *args, **kwargs):
        """Handle GET request.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Returns:
            if user is authenticated
                return rendered 'room_list.html' with user and form object
            else
                Redirect to login
        """
        if request.user.is_authenticated:
            rooms = Room.objects.all()
            return render(
                request, self.template_name,
                {'rooms': rooms, 'user': self.request.user, 'form': self.form}
            )
        else:
            return redirect('/login')

    def post(self, request, *args, **kwargs):
        """Handle POST requests.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Returns:
            if user is authenticated
                if form valid
                    save form and redirect to /rooms
                else
                    return render(request, 'screen.html', {'form': form})
            else
                redirect to login
        """
        if request.user.is_authenticated:
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                room = form.save(commit=False)
                room.user = request.user
                room.created_at = datetime.now()
                room.save()
                return redirect('/rooms', foo='bar')
            return render_to_response('', {'form': form})
        else:
            return redirect('/login')


class RoomDetailView(View):
    """GET - Detail of the room."""

    template_name = 'room_detail.html'

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        method = self.request.POST.get('_method', '').lower()
        if method == 'put':
            return self.put(request, *args, **kwargs)
        if method == 'delete':
            return self.delete(*args, **kwargs)
        return super(RoomDetailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Handle GET Request.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Return:
            if user is authenticated
                return rendered 'room_detail.html' with following data
                    -- Room object
                    -- is_owner boolean
                    -- screens
                    -- current_screen
                    -- total_screen
            else:
                redirect to login page

        Raises:
        Room.DoesNotExist:
            if room is not yet active OR room does not exist
        """
        if request.user.is_authenticated:
            try:
                room = Room.objects.get(id=self.kwargs.get('pk', None))
                screens = room.screens.all()
            except Room.DoesNotExist:
                raise Http404("Room does not exist")
            if not room.is_active and room.user != request.user:
                return render(request, self.template_name, {'room': None})
            return render(
                request,
                self.template_name,
                {
                    'room': room,
                    'is_owner': room.user == request.user,
                    'screens': screens,
                    'current_screen': room.current_screen,
                    'total_screens': room.screens.count(),
                    'number_of_slides': list(range(room.number_of_slides))
                }
            )
        else:
            return redirect('/login')

    def put(self, request, *args, **kwargs):
        number_of_slides = int(request.POST['number_of_slides'])
        try:
            room = Room.objects.get(id=self.kwargs.get('pk', None))
            room.number_of_slides += number_of_slides
            room.save()
        except Room.DoesNotExist:
            raise Http404("Room does not exist")

        return HttpResponseRedirect(reverse('rooms_detail', args=[room.id]))


class ScreenView(View):
    """Handle screen GET/POST request."""

    template_name = 'screen.html'
    form = RoomScreenForm

    def get(self, request, *args, **kwargs):
        """Handle GET requests.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Return:
            rendered 'screen.html' template with user and form object
            and screens queryset

        Raises:
        Room.DoesNotExist:
            if room.user != request.user OR room does not exist
        """
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
        """Handle POST requests.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Return:
            if user authenticated
                if form is valid
                    Redirect to rooms_detail
                else
                    Return rendered 'screen.html' with form object
            else
                Redirect to login
        """
        if request.user.is_authenticated:
            room_id = self.kwargs.get('pk', None)
            try:
                room = Room.objects.get(id=room_id, user=request.user)
            except Room.DoesNotExist:
                return Http404("Room Does Not Exist")
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                screen = form.save(commit=False)
                screen.room = room
                screen.save()
                return HttpResponseRedirect(reverse('rooms_detail', args=[room.id]))

            else:
                return render(request, 'screen.html', {'form': form})
        else:
            return redirect('/login')


class ScreenViewDetail(View):

    template_name = 'screen.html'
    form = RoomScreenForm

    def get(self, request, *args, **kwargs):
        """Handle GET requests.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Return:
            if user authenticated
                if form valid
                    redirect to rooms_detail
                else
                    return rendered 'screen.html' with form object
            else
                redirect to login

        """
        if request.user.is_authenticated:
            room_id = self.kwargs.get('pk', None)
            try:
                Room.objects.get(id=room_id, user=request.user)
                try:
                    screen = Screen.objects.get(id=self.kwargs.get('screen_id', None))
                except Screen.DoesNotExist:
                    raise Http404("Screen does not exist")
            except Room.DoesNotExist:
                raise Http404("Room does not exist")
            form = RoomScreenForm(instance=screen)
            return render(
                request, self.template_name,
                {'user': self.request.user, 'form': form}
            )
        else:
            return redirect('/login')

    def post(self, request, *args, **kwargs):
        """Handle PUT requests.

        Args:
            request: instance of Request object
            *args: non-keyworded, variable-length argument list
            **kwargs: keyworded, variable-length argument list

        Return:
            if user authenticated
                if form valid
                    redirect to rooms_detail
                else
                    return rendered 'screen.html' with form object
            else
                redirect to login
        """
        if request.user.is_authenticated:
            room_id = self.kwargs['pk']
            try:
                room = Room.objects.get(pk=room_id, user=request.user)
                try:
                    screen = Screen.objects.get(pk=self.kwargs.get('screen_id', None))
                    form = RoomScreenForm(request.POST, instance=screen)
                    if form.is_valid():
                        form.save()
                        return HttpResponseRedirect(
                            reverse('rooms_detail', args=[room.id])
                        )
                    else:
                        return render(request, 'screen.html', {'form': form})

                except Screen.DoesNotExist:
                    return Http404("Screen Does not exist")
            except Room.DoesNotExist:
                return Http404("Room Does not exist")
        else:
            return redirect('/login')
