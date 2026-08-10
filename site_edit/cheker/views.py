from django.shortcuts import render
from django.http import HttpResponse

from .forms import CheckSite
from .cheker import check_site


# Create your views here.

def index(request):
    errors = None
    score = None
    summary = None
    page_note = None
    fixed_site = None
    if request.method == "GET":
        form = CheckSite()

    elif request.method == "POST":
        form = CheckSite(request.POST)

        if form.is_valid():
            url = form.cleaned_data["url"]

            result = check_site(url)
            score = result["score"]
            errors = result["errors"]
            summary = result["summary"]
            page_note = result["page_note"]
            fixed_site = result["fixed_site"]
    return render(request, "cheker/index.html", {"form": form, "errors":errors, "score":score, "summary": summary,"page_note": page_note, "fixed_site":fixed_site})

def postSite(request):
    url = request.POST.get("url")
    return HttpResponse(url)