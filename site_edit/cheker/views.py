from django.shortcuts import render
from django.http import HttpResponse

from .forms import CheckSite
from .cheker import check_site


# Create your views here.

def index(request):
    errors = None
    score = None
    if request.method == "GET":
        form = CheckSite()

    elif request.method == "POST":
        form = CheckSite(request.POST)

        if form.is_valid():
            url = form.cleaned_data["url"]

            result = check_site(url)
            score = result["score"]
            errors = result["errors"]
    return render(request, "cheker/index.html", {"form": form, "errors":errors, "score":score,})

def postSite(request):
    url = request.POST.get("url")
    return HttpResponse(url)