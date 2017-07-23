from django.views.generic import View
from django.http import HttpResponse


class Status(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse('<b id="status">logged-in as {u.username}</b>'.format(u=request.user))
        else:
            return HttpResponse('<b id="status">not logged-in</b>')
