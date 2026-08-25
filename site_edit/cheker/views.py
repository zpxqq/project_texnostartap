from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .forms import CheckSite
from .cheker import check_site
from django.shortcuts import get_object_or_404

# Create your views here.
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Site, Check, CheckResult


def index(request):

    if request.method == "POST":

        form = CheckSite(request.POST)

        if form.is_valid():

            url = form.cleaned_data["url"]

            result = check_site(url)

            site, created = Site.objects.get_or_create(user=request.user,url=url,defaults={"name": url})

            check = Check.objects.create(site=site,score=result["score"])

            for error in result["errors"]:
                CheckResult.objects.create(
                    checkk=check,
                    type=error["type"],
                    count=error["count"],
                    total=error["total"],
                    message=error["message"]
                )

            return render(
                request,
                "cheker/result.html",
                {
                    "url": url,
                    "score": result["score"],
                    "errors": result["errors"],
                    "summary": result["summary"],
                    "page_note": result["page_note"],
                    "fixed_site": result["fixed_site"],
                    "site": 'site'
                }
            )


    else:
        form = CheckSite()

    return render(
        request,
        "cheker/index.html",
        {
            "form": form
        }
    )



def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            return render(request,"cheker/register.html",{"error": "Такой пользователь уже существует"})

        user = User.objects.create_user(username=username,email=email,password=password)

        auth_login(request, user)

        return redirect("dashboard")

    return render(request, "cheker/register.html")

def dashboard(request):
    sites = Site.objects.filter(user=request.user)
    return render(request, "cheker/dashboard.html", {"sites": sites})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        return render(request,"cheker/login.html",{"error": "Неверное имя пользователя или пароль"})
    return render(request, "cheker/login.html")


@login_required
def project(request, site_id):

    site = get_object_or_404(Site,id=site_id,user=request.user)
    checks = site.checks.order_by("-checked_at")
    last_check = checks.first()
    return render(
        request,"cheker/project.html",{
            "site": site,
            "checks": checks,
            "last_check": last_check,}
    )