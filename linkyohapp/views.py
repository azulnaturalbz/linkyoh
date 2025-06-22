from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from six import print_

from .models import Gig, Profile, Location, District, Category, SubCategory, Review, GigImage, GigContact, GigServiceArea
from .forms import (
    GigForm, ReviewForm, ContactForm, UserRegistrationForm, ProfileForm,
    GigImageFormSet, GigContactFormSet, GigServiceAreaFormSet
)


# Create your views here.

def load_districts(request, did=None):
    """HTMX view to load districts"""
    districts = District.objects.all()
    selected_district = request.GET.get('district') or did

    return render(request, 'district_dropdown_list_options.html', {
        'districts': districts, 
        'selected_district': selected_district
    })


def load_locations(request, did=None, lid=None):
    """HTMX view to load locations based on selected district"""
    district_id = request.GET.get('district') or did
    selected_location = request.GET.get('location') or lid

    locations = []
    if district_id:
        locations = Location.objects.filter(local__local_district=district_id).order_by('local')

    return render(request, 'location_dropdown_list_options.html', {
        'locations': locations,
        'selected_location': selected_location
    })

def ajax_load_locations(request):
    """HTMX view to load locations based on selected district"""
    district_id = request.GET.get('district', '')
    selected_location = request.GET.get('location', None)
    locations = []

    if district_id:
        locations = Location.objects.filter(local__local_district=district_id).order_by('local')

    return render(request, 'ajax_location_options.html', {
        'locations': locations,
        'selected_location': selected_location
    })


def load_categories(request, catid=None):
    """HTMX view to load categories"""
    categories = Category.objects.all()
    selected_cat = request.GET.get('category') or catid

    return render(request, 'category_dropdown_list_options.html', {
        'categories': categories, 
        'selected_cat': selected_cat
    })


def load_sub_categories(request, catid=None, subcatid=None):
    """HTMX view to load subcategories based on selected category"""
    category_id = request.GET.get('category') or catid
    selected_subcategory = request.GET.get('subcategory') or subcatid

    sub_categories = []
    if category_id:
        sub_categories = SubCategory.objects.filter(category_id=category_id)

    return render(request, 'sub_category_dropdown_list_options.html', {
        'sub_categories': sub_categories,
        'selected_subcategory': selected_subcategory
    })

def ajax_load_subcategories(request):
    """HTMX view to load subcategories based on selected category"""
    category_id = request.GET.get('category', '')
    selected_subcategory = request.GET.get('subcategory', None)
    subcategories = []

    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id)

    return render(request, 'ajax_subcategory_options.html', {
        'subcategories': subcategories,
        'selected_subcategory': selected_subcategory
    })


def load_menu_categories(request):
    categories = Category.objects.all()
    return render(request, 'category_menu_list_options.html', {'categories': categories})


class CategoryListView(ListView):
    model = Gig
    template_name = 'categories.html'
    context_object_name = 'gigs'
    paginate_by = 6

    def get_queryset(self):
        # Get search parameters
        search_query = self.request.GET.get('param', '')
        subcategory_id = self.request.GET.get('subcategory', '')
        district_id = self.request.GET.get('district', '')
        location_id = self.request.GET.get('location', '')

        # Start with base query - always show active gigs in this category
        base_query = Q(status=True, category_id=self.kwargs['id'])

        # Add text search if provided
        if search_query:
            base_query &= (
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sub_category__subcategory__icontains=search_query) |
                Q(district__district_name__icontains=search_query) |
                Q(location__local__local_name__icontains=search_query)
            )

        # Apply subcategory filter if provided
        if subcategory_id:
            base_query &= Q(sub_category_id=subcategory_id)

        # Apply district filter if provided
        if district_id:
            base_query &= Q(district_id=district_id)

        # Apply location filter if provided
        if location_id:
            base_query &= Q(location_id=location_id)

        # Optimize query by prefetching related objects
        return Gig.objects.filter(base_query).select_related(
            'user', 'category', 'sub_category', 'district', 'location', 'user__profile'
        ).order_by("-create_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cache the category to avoid additional query
        if not hasattr(self, '_category'):
            self._category = Category.objects.get(pk=self.kwargs['id'])
        context['category'] = self._category

        # Add search parameters to context
        context['search_query'] = self.request.GET.get('param', '')
        context['selected_subcategory'] = self.request.GET.get('subcategory', '')
        context['selected_district'] = self.request.GET.get('district', '')
        context['selected_location'] = self.request.GET.get('location', '')

        # Check if any filters are applied
        context['has_filters'] = bool(
            context['selected_subcategory'] or 
            context['selected_district'] or 
            context['selected_location']
        )
        context['has_search'] = bool(context['search_query'])

        # Get total count of results
        context['total_count'] = self.get_queryset().count()

        return context

# Keep the function-based view as a wrapper for backward compatibility
def category_listings(request, id):
    view = CategoryListView.as_view()
    return view(request, id=id)


class SubCategoryListView(ListView):
    model = Gig
    template_name = 'sub_categories.html'
    context_object_name = 'gigs'
    paginate_by = 6

    def get_queryset(self):
        # Optimize query by prefetching related objects
        return Gig.objects.filter(status=True, sub_category_id=self.kwargs['id']).select_related(
            'user', 'category', 'sub_category'
        ).order_by("-create_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cache the subcategory to avoid additional query
        if not hasattr(self, '_sub_category'):
            self._sub_category = SubCategory.objects.select_related('category').get(pk=self.kwargs['id'])
        context['sub_category'] = self._sub_category
        return context

# Keep the function-based view as a wrapper for backward compatibility
def sub_category_listings(request, id):
    view = SubCategoryListView.as_view()
    return view(request, id=id)


class HomeView(ListView):
    model = Gig
    template_name = 'home.html'
    context_object_name = 'gigs'
    paginate_by = 6

    def get_queryset(self):
        # Optimize query by prefetching related objects
        return Gig.objects.filter(status=True).select_related(
            'user', 'category', 'sub_category'
        ).order_by("-create_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add popular categories (those with the most gigs)
        categories_with_count = Category.objects.annotate(
            gig_count=Count('gig')
        ).order_by('-gig_count')
        context['popular_categories'] = categories_with_count[:6]

        # Add featured gigs (those with the most likes)
        featured_gigs = Gig.objects.filter(status=True).select_related(
            'user', 'category', 'sub_category', 'user__profile'
        ).prefetch_related('likes').annotate(
            like_count=Count('likes')
        ).order_by('-like_count')[:3]
        context['featured_gigs'] = featured_gigs

        # Add recent reviews
        recent_reviews = Review.objects.select_related(
            'user', 'gig', 'rating', 'user__profile'
        ).order_by('-create_time')[:3]
        context['recent_reviews'] = recent_reviews

        return context

# Keep the function-based view as a wrapper for backward compatibility
def home(request):
    view = HomeView.as_view()
    return view(request)


class GigDetailView(DetailView):
    model = Gig
    template_name = 'gig_detail.html'
    context_object_name = 'gig'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        # Optimize query by prefetching related objects
        return Gig.objects.select_related(
            'user', 'category', 'sub_category', 'district', 'location', 
            'user__profile'  # Add profile to reduce queries
        ).prefetch_related('likes', 'images', 'contacts', 'service_areas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gig = self.get_object()

        # Check if user has liked the gig
        is_liked = False
        if self.request.user.is_authenticated and gig.likes.filter(id=self.request.user.id).exists():
            is_liked = True

        # Add review form if user is authenticated
        if self.request.user.is_authenticated:
            context['show_post_review'] = ReviewForm()
        else:
            context['show_post_review'] = False

        # Get reviews for this gig with related user and rating
        context['reviews'] = Review.objects.filter(gig=gig).select_related('user', 'rating', 'user__profile')
        context['is_liked'] = is_liked
        context['total_likes'] = gig.total_likes()

        # Add additional images, contacts, and service areas
        context['additional_images'] = gig.images.all().order_by('order', 'created')
        context['contacts'] = gig.contacts.all().order_by('order', 'id')
        context['service_areas'] = gig.service_areas.all().order_by('order', 'id')

        # Add related gigs (same category, excluding this one)
        context['related_gigs'] = Gig.objects.filter(
            category=gig.category, 
            status=True
        ).exclude(
            id=gig.id
        ).select_related(
            'category', 'sub_category'
        ).order_by('-create_time')[:5]

        return context

    def post(self, request, *args, **kwargs):
        # Handle review submission
        if request.user.is_authenticated and 'content' in request.POST and request.POST['content'].strip() != '':
            form = ReviewForm(request.POST)
            if form.is_valid():
                gig = self.get_object()
                Review.objects.create(
                    user=request.user,
                    gig=gig,
                    rating=form.cleaned_data.get('rating'),
                    content=form.cleaned_data.get('content')
                )

        # Redirect to the same page to avoid form resubmission
        return self.get(request, *args, **kwargs)

# Keep the function-based view as a wrapper for backward compatibility
def gig_detail(request, id):
    view = GigDetailView.as_view()
    return view(request, id=id)


def like_gig(request):
    """Handle like/unlike actions for gigs with htmx support"""
    # Get the gig ID from the request (either POST data or JSON)
    gig_id = request.POST.get('id')

    # Get the gig or return 404
    gig = get_object_or_404(Gig, id=gig_id)

    # Toggle the like status
    is_liked = False
    if gig.likes.filter(id=request.user.id).exists():
        gig.likes.remove(request.user)
        is_liked = False
    else:
        gig.likes.add(request.user)
        is_liked = True

    # Prepare the context for the template
    context = {
        'gig': gig,
        'is_liked': is_liked,
        'total_likes': gig.total_likes(),
    }

    # Return the updated like section HTML for htmx to swap in
    return render(request, 'like_section.html', context)


class CreateGigView(LoginRequiredMixin, CreateView):
    model = Gig
    form_class = GigForm
    template_name = 'create_gig.html'
    success_url = reverse_lazy('my_gigs')
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['image_formset'] = GigImageFormSet(self.request.POST, self.request.FILES)
            context['contact_formset'] = GigContactFormSet(self.request.POST)
            context['service_area_formset'] = GigServiceAreaFormSet(self.request.POST)
        else:
            context['image_formset'] = GigImageFormSet()
            context['contact_formset'] = GigContactFormSet()
            context['service_area_formset'] = GigServiceAreaFormSet()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        contact_formset = context['contact_formset']
        service_area_formset = context['service_area_formset']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()

            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()

            if contact_formset.is_valid():
                contact_formset.instance = self.object
                contact_formset.save()

            if service_area_formset.is_valid():
                service_area_formset.instance = self.object
                service_area_formset.save()

        return super().form_valid(form)

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/')
def create_gig(request):
    view = CreateGigView.as_view()
    return view(request)


class EditGigView(LoginRequiredMixin, UpdateView):
    model = Gig
    form_class = GigForm
    template_name = 'edit_gig.html'
    success_url = reverse_lazy('my_gigs')
    pk_url_kwarg = 'id'
    login_url = '/'

    def get_queryset(self):
        # Ensure users can only edit their own gigs
        return Gig.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gig = self.get_object()

        if self.request.POST:
            context['image_formset'] = GigImageFormSet(
                self.request.POST, self.request.FILES, instance=gig
            )
            context['contact_formset'] = GigContactFormSet(
                self.request.POST, instance=gig
            )
            context['service_area_formset'] = GigServiceAreaFormSet(
                self.request.POST, instance=gig
            )
        else:
            context['image_formset'] = GigImageFormSet(instance=gig)
            context['contact_formset'] = GigContactFormSet(instance=gig)
            context['service_area_formset'] = GigServiceAreaFormSet(instance=gig)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        contact_formset = context['contact_formset']
        service_area_formset = context['service_area_formset']

        with transaction.atomic():
            self.object = form.save()

            if image_formset.is_valid():
                image_formset.instance = self.object
                image_formset.save()
            else:
                return self.form_invalid(form)

            if contact_formset.is_valid():
                contact_formset.instance = self.object
                contact_formset.save()
            else:
                return self.form_invalid(form)

            if service_area_formset.is_valid():
                service_area_formset.instance = self.object
                service_area_formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/')
def edit_gig(request, id):
    try:
        # Verify the gig exists and belongs to the user
        gig = Gig.objects.get(id=id, user=request.user)
        view = EditGigView.as_view()
        return view(request, id=id)
    except Gig.DoesNotExist:
        return redirect('/')


class MyGigsView(LoginRequiredMixin, ListView):
    model = Gig
    template_name = 'my_gigs.html'
    context_object_name = 'gigs'
    login_url = '/'

    def get_queryset(self):
        # Optimize query by prefetching related objects and likes
        return Gig.objects.filter(user=self.request.user).select_related(
            'category', 'sub_category', 'district', 'location'
        ).prefetch_related('likes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add count of active gigs
        context['active_gigs_count'] = Gig.objects.filter(user=self.request.user, status=True).count()
        # Add total likes across all user's gigs
        total_likes = 0
        for gig in context['gigs']:
            total_likes += gig.total_likes()
        context['total_likes'] = total_likes
        return context

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/')
def my_gigs(request):
    view = MyGigsView.as_view()
    return view(request)


@login_required(login_url='/')
def profile(request, pid):
    # Check if viewing own profile or someone else's
    is_own_profile = str(request.user.id) == str(pid)

    try:
        profile = Profile.objects.select_related('user', 'district', 'location').get(user_id=pid)
    except Profile.DoesNotExist:
        return redirect('/')

    # If it's the user's own profile and they're submitting the form
    if is_own_profile and request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Add a success message
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile', pid=request.user.id)
    # If it's the user's own profile, show the form
    elif is_own_profile:
        form = ProfileForm(instance=profile)
    else:
        form = None

    # Get the user's gigs
    gigs = Gig.objects.filter(user=profile.user, status=True).select_related(
        'category', 'sub_category', 'user__profile'
    )

    # Get districts for the district dropdown
    districts = District.objects.all()

    context = {
        "profile": profile,
        "gigs": gigs,
        "form": form,
        "is_own_profile": is_own_profile,
        "districts": districts,
    }

    return render(request, 'profile.html', context)


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
    """
    Advanced search view that can be visited with or without parameters.
    Provides extensive filtering options and intuitive UI.
    """
    # Get search parameters
    search_query = request.GET.get('param', '')
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')
    district_id = request.GET.get('district', '')
    location_id = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    # Start with base query - always show active gigs
    base_query = Q(status=True)

    # Add text search if provided
    if search_query:
        base_query &= (
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__category__icontains=search_query) |
            Q(sub_category__subcategory__icontains=search_query) |
            Q(district__district_name__icontains=search_query) |
            Q(location__local__local_name__icontains=search_query)
        )

    # Apply category filter if provided
    if category_id:
        base_query &= Q(category_id=category_id)

    # Apply subcategory filter if provided
    if subcategory_id:
        base_query &= Q(sub_category_id=subcategory_id)

    # Apply district filter if provided
    if district_id:
        base_query &= Q(district_id=district_id)

    # Apply location filter if provided
    if location_id:
        base_query &= Q(location_id=location_id)

    # Apply price range filters if provided
    if min_price:
        try:
            min_price_value = int(min_price)
            base_query &= Q(price__gte=min_price_value)
        except ValueError:
            # Invalid min_price, ignore this filter
            min_price = ''

    if max_price:
        try:
            max_price_value = int(max_price)
            base_query &= Q(price__lte=max_price_value)
        except ValueError:
            # Invalid max_price, ignore this filter
            max_price = ''

    # Execute the query
    gigs = Gig.objects.filter(base_query).select_related(
        'user', 'category', 'sub_category', 'district', 'location', 'user__profile'
    ).order_by("-create_time")

    # Get total count before pagination
    total_count = gigs.count()

    # Paginate results
    paginator = Paginator(gigs, 9)  # Show 9 gigs per page
    page = request.GET.get('page')
    try:
        gigs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        gigs = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        gigs = paginator.page(paginator.num_pages)

    # Check if any filters are applied
    has_filters = bool(category_id or subcategory_id or district_id or location_id or min_price or max_price)
    has_search = bool(search_query)

    # Prepare context
    context = {
        "gigs": gigs,
        "search_query": search_query,
        "selected_category": category_id,
        "selected_subcategory": subcategory_id,
        "selected_district": district_id,
        "selected_location": location_id,
        "min_price": min_price,
        "max_price": max_price,
        "has_filters": has_filters,
        "has_search": has_search,
        "total_count": total_count
    }

    return render(request, 'search_results.html', context)


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            profile = Profile(user_id=new_user.id)
            profile.save()
            return render(request, 'account/register_done.html', context={'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', context={'user_form': user_form})
