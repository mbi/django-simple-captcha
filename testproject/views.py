from django.template import RequestContext
from django.http import HttpResponseRedirect
from forms import CaptchaForm
from django.shortcuts import render_to_response


def home(request):
    if request.POST:
        form = CaptchaForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(request.path + '?ok')
    else:
        form = CaptchaForm()

    return render_to_response('home.html', dict(
        form=form
    ), context_instance=RequestContext(request))
