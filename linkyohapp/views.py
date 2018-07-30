from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Gig, Profile, Location, State, Category, SubCategory
from .forms import GigForm
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str
from json import dumps


# Create your views here.


def load_locations(request):
    state_id = request.GET.get('state')
    locations = Location.objects.filter(local__state__id=state_id).order_by('local')
    return render(request, 'location_dropdown_list_options.html', {'locations': locations})


def load_categories(request):
    categories = Category.objects.all()
    return render(request, 'category_dropdown_list_options.html', {'categories': categories})


def load_sub_categories(request):
    category_id = request.GET.get('category')
    sub_categories = SubCategory.objects.filter(category_id=category_id)
    return render(request, 'sub_category_dropdown_list_options.html', {'sub_categories': sub_categories})


def home(request):
    gigs = Gig.objects.filter(status=True).order_by("-create_time")

    page = request.GET.get('page', 1)

    paginator = Paginator(gigs, 6)

    try:
        gigs = paginator.page(page)
    except PageNotAnInteger:
        gigs = paginator.page(1)
    except EmptyPage:
        gigs = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {"gigs": gigs})


def gig_detail(request, id):
    try:
        gig = Gig.objects.get(id=id)
    except Gig.DoesNotExist:
        return redirect('/')
    return render(request, 'gig_detail.html', {"gig": gig})


@login_required(login_url='/')
def create_gig(request):
    error = ''
    states = State.objects.all()
    if request.method == "POST":
        gig_form = GigForm(request.POST, request.FILES)
        if gig_form.is_valid():
            gig = gig_form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('my_gigs')
        else:
            error = "Data is not valid"
    gig_form = GigForm()
    return render(request, 'create_gig.html', {"error": error, "states": states})


@login_required(login_url='/')
def edit_gig(request, id):
    try:
        gig = Gig.objects.get(id=id, user=request.user)
        error = ''
        if request.method == "POST":
            gig_form = GigForm(request.POST, request.FILES, instance=gig)
            if gig_form.is_valid():
                gig.save()
                return redirect('my_gigs')
            else:
                error = "Data is not Valid"
        return render(request, 'edit_gig.html', {"gig": gig, "error": error})
    except Gig.DoesNotExist:
        return redirect('/')


@login_required(login_url='/')
def my_gigs(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'my_gigs.html', {"gigs": gigs})


@login_required(login_url='/')
def profile(request, username):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        profile.about = request.POST['about']
        profile.slogan = request.POST['slogan']
        profile.save()
    else:
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return redirect('/')

    gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'profile.html', {"profile": profile, "gigs": gigs})
