from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Gig, Profile, Location, State, Category, SubCategory, Review
from .forms import GigForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


# Create your views here.

def load_states(request):
    states = State.objects.all()
    return render(request, 'state_dropdown_list_options.html', {'states': states})


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


def load_menu_categories(request):
    categories = Category.objects.all()
    return render(request, 'category_menu_list_options.html', {'categories': categories})


def category_listings(request, id):
    category = Category.objects.get(pk=id)
    gigs = Gig.objects.filter(status=True, category_id=id).order_by("-create_time")

    page = request.GET.get('page', 1)

    paginator = Paginator(gigs, 6)

    try:
        gigs = paginator.page(page)
    except PageNotAnInteger:
        gigs = paginator.page(1)
    except EmptyPage:
        gigs = paginator.page(paginator.num_pages)

    return render(request, 'categories.html', {"gigs": gigs, "category": category})


def sub_category_listings(request, id):
    sub_category = SubCategory.objects.get(pk=id)
    gigs = Gig.objects.filter(status=True, sub_category_id=id).order_by("-create_time")

    page = request.GET.get('page', 1)

    paginator = Paginator(gigs, 6)

    try:
        gigs = paginator.page(page)
    except PageNotAnInteger:
        gigs = paginator.page(1)
    except EmptyPage:
        gigs = paginator.page(paginator.num_pages)

    return render(request, 'sub_categories.html', {"gigs": gigs, "sub_category": sub_category})


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
    if request.method == 'POST' and \
            request.user.is_authenticated and \
            'content' in request.POST and \
            request.POST['content'].strip() != '':

        # Review.objects.create(content=request.POST['content'],gig_id=id,user=request.user)
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = Review.objects.create(
                user=request.user,
                gig_id=id,
                content=form.cleaned_data.get('content')
            )

    try:
        gig = Gig.objects.get(id=id)
        is_liked = False
        if gig.likes.filter(id=request.user.id).exists():
            is_liked = True
    except Gig.DoesNotExist:
        return redirect('/')

    if request.user.is_authenticated:

        reviewForm = ReviewForm()
        show_post_review = reviewForm
    else:
        # show_post_review = Purchase.objects.filter(gig=gig,buyer=request.user).count() > 0
        show_post_review = False

    reviews = Review.objects.filter(gig=gig)

    return render(request, 'gig_detail.html',
                  {"gig": gig, "reviews": reviews, "show_post_review": show_post_review, 'is_liked': is_liked ,  'total_likes': gig.total_likes(),})


def like_gig(request):
    # post = get_object_or_404(Post, id=request.POST.get('post_id'))
    gig = get_object_or_404(Gig, id=request.POST.get('id'))
    is_liked = False
    if gig.likes.filter(id=request.user.id).exists():
        gig.likes.remove(request.user)
        is_liked = False
    else:
        gig.likes.add(request.user)
        is_liked = True
    context = {
        'gig': gig,
        'is_liked': is_liked,
        'total_likes': gig.total_likes(),
    }
    if request.is_ajax():
        html = render_to_string('like_section.html', context, request=request)
        return JsonResponse({'form': html})


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
        # gig_form = Gig.objects.get(id=id, user=request.user)  instance=gig_form)
        gig_form =GigForm(instance=Gig.objects.get(pk=id))
        error = ''
        if request.method == "POST":
            gig_form = GigForm(request.POST, request.FILES, instance=Gig.objects.get(pk=id))
            if gig_form.is_valid():
                gig_form.save()
                return redirect('my_gigs')
            else:
                error = "Data is not Valid"
        return render(request, 'edit_gig.html', {"gig": gig_form, "error": error})
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


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')

#.filter(title__contains=request.GET['title'])\
def search(request):
    gigs = Gig.objects.filter(Q(title__icontains=request.GET['param']) |
                              Q(category__category__icontains=request.GET['param']) |
                              Q(sub_category__subcategory__icontains=request.GET['param']) |
                              Q(state__state__icontains=request.GET['param']) |
                              Q(location__local__local__icontains=request.GET['param']))
    return render(request, 'home.html', {"gigs": gigs})
