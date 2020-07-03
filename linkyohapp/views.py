from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from .models import Gig, Profile, Location, District, Category, SubCategory, Review,Contact
from .forms import GigForm, ReviewForm, ContactForm

import credentials


# Create your views here.

def load_districts(request, did=None):
    if did is not None:
        selected_district = did
        districts = District.objects.all()
        return render(request, 'district_dropdown_list_options.html', {'districts': districts, 'selected_state': selected_district})
    else:
        districts = District.objects.all()
        return render(request, 'district_dropdown_list_options.html', {'districts': districts})


def load_locations(request, did=None, lid=None):
    if did is None and lid is None:
        district_id = request.GET.get('district')
        locations = Location.objects.filter(local__local_district=district_id).order_by('local')
        return render(request, 'location_dropdown_list_options.html', {'locations': locations})

    else:
        district_id = request.GET.get('district')
        locations = Location.objects.filter(local__local_district=district_id).order_by('local')
        return render(request, 'location_dropdown_list_options.html', {'locations': locations})


def load_categories(request, catid=None):
    if catid is not None:
        selected_cat = catid
        categories = Category.objects.all()
        return render(request, 'category_dropdown_list_options.html', {'categories': categories, 'selected_cat': catid})
    else:
        categories = Category.objects.all()
        return render(request, 'category_dropdown_list_options.html', {'categories': categories})


def load_sub_categories(request, catid=None, subcatid=None):
    if catid is None and subcatid is None:
        category_id = request.GET.get('category')
        sub_categories = SubCategory.objects.filter(category_id=category_id)
        return render(request, 'sub_category_dropdown_list_options.html',
                      {'sub_categories': sub_categories})
    else:
        category_id = request.GET.get('category')
        sub_categories = SubCategory.objects.filter(category_id=category_id)
        return render(request, 'sub_category_dropdown_list_options.html',
                      {'sub_categories': sub_categories})


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
                rating=form.cleaned_data.get('rating'),
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
                  {"gig": gig, "reviews": reviews, "show_post_review": show_post_review, 'is_liked': is_liked,
                   'total_likes': gig.total_likes(), })


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
    districts = District.objects.all()
    if request.method == "POST":
        gig_form = GigForm(request.POST, request.FILES)
        if gig_form.is_valid():
            gig = gig_form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('my_gigs')
        else:
            error = "Please check data, only png, jpg, jpeg and gif. Max size 24mb"
    gig_form = GigForm()
    return render(request, 'create_gig.html', {"error": error, "districts": districts})


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
        categories = Category.objects.all()
        sub_categories = SubCategory.objects.filter(category_id=gig.category_id)
        districts = District.objects.all()
        locations = Location.objects.filter(local__local_district=gig.district_id)
        return render(request, 'edit_gig.html',
                      {"gig": gig, "error": error,
                       'districts': districts,
                       'locations': locations,
                       'categories': categories,
                       'sub_categories': sub_categories})
    except Gig.DoesNotExist:
        return redirect('/')


@login_required(login_url='/')
def my_gigs(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'my_gigs.html', {"gigs": gigs})


@login_required(login_url='/')
def profile(request, pid):
    if request.method == 'POST':
        profile = Profile.objects.get(user_id=request.user.id)
        profile.about = request.POST['about']
        profile.slogan = request.POST['slogan']
        profile.save()
    else:
        try:
            profile = Profile.objects.get(user_id=pid)
        except Profile.DoesNotExist:
            return redirect('/')

    gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'profile.html', {"profile": profile, "gigs": gigs})


def contact(request):
    error = ''
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(thanks)
        else:
            error = "Please check the contact form once more, something doesn't look right."
    return render(request, 'contact.html', {'form': form})


def about(request):
    return render(request, 'about.html')


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')


def thanks(request):
    return render(request, 'thanks.html')


def search(request):
    gigs = Gig.objects.filter(
        Q(title__icontains=request.GET['param']) |
        Q(category__category__icontains=request.GET['param']) |
        Q(sub_category__subcategory__icontains=request.GET['param']) |
        Q(district__district_name__icontains=request.GET['param']) |
        Q(location__local__local_name__icontains=request.GET['param']), status=True).order_by("-create_time")
    return render(request, 'home.html', {"gigs": gigs})
