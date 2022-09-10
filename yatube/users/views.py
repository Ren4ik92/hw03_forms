from django.template.context_processors import request
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm
from django.shortcuts import render


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/logged_out.html'


def logg_out(request):
    template = 'users/logged_out.html'
    return render(request, template)
