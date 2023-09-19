from forms import CaptchaForm  # CustomCaptchaForm

from django.http import HttpResponseRedirect
from django.shortcuts import render


def home(request):
    if request.POST:
        form = CaptchaForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(request.path + "?ok")
    else:
        form = CaptchaForm()

    return render(request, "home.html", {"form": form})
