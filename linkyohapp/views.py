from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import credentials
import json
import re

from .auth_views import CustomPasswordResetConfirmView, CustomPasswordResetCompleteView

# Helper function to get client IP address
def _get_client_ip(request):
    """Get the client IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address

from .models import (
    Gig, Profile, Location, District, Category, SubCategory, Review, 
    GigImage, GigContact, GigServiceArea, Stats, GigClaimRequest,
    Conversation, Message, MessageFile
)
from .forms import (
    GigForm, ReviewForm, ContactForm, UserRegistrationForm, ProfileForm,
    GigImageFormSet, GigContactFormSet, GigServiceAreaFormSet, GigClaimRequestForm,
    ConversationForm, MessageForm, MessageFileForm
)


# Create your views here.

def load_districts(request, did=None):
    """HTMX view to load districts"""
    districts = District.objects.all()

    # Try to get selected_district from standard parameter or URL parameter
    selected_district = request.GET.get('district') or did

    # If not found, look for parameters with formset prefixes
    if not selected_district:
        for key in request.GET.keys():
            if ('district' in key) and request.GET.get(key):
                selected_district = request.GET.get(key)
                break

    return render(request, 'district_dropdown_list_options.html', {
        'districts': districts, 
        'selected_district': selected_district
    })


def load_locations(request, did=None, lid=None):
    """HTMX view to load locations based on selected district"""
    # Try to get district_id from standard parameter or URL parameter
    district_id = request.GET.get('district') or did

    # If not found, look for parameters with formset prefixes
    if not district_id:
        for key in request.GET.keys():
            if ('district' in key) and request.GET.get(key):
                district_id = request.GET.get(key)
                break

    # Try to get selected_location from standard parameter or URL parameter
    selected_location = request.GET.get('location') or lid

    # If not found, look for parameters with formset prefixes
    if not selected_location:
        for key in request.GET.keys():
            if ('location' in key) and request.GET.get(key):
                selected_location = request.GET.get(key)
                break

    locations = []
    if district_id:
        locations = Location.objects.filter(local__local_district=district_id).order_by('local')

    return render(request, 'location_dropdown_list_options.html', {
        'locations': locations,
        'selected_location': selected_location
    })

def ajax_load_locations(request):
    """HTMX view to load locations based on selected district"""
    # Try to get district_id from standard parameter
    district_id = request.GET.get('district', '')

    # If not found, look for parameters with formset prefixes
    if not district_id:
        for key in request.GET.keys():
            if ('district' in key) and request.GET.get(key):
                district_id = request.GET.get(key)
                break

    # Try to get selected_location from standard parameter
    selected_location = request.GET.get('location', None)

    # If not found, look for parameters with formset prefixes
    if not selected_location:
        for key in request.GET.keys():
            if ('location' in key) and request.GET.get(key):
                selected_location = request.GET.get(key)
                break

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

    # Try to get selected_cat from standard parameter or URL parameter
    selected_cat = request.GET.get('category') or catid

    # If not found, look for parameters with formset prefixes
    if not selected_cat:
        for key in request.GET.keys():
            if ('category' in key) and ('sub_category' not in key) and request.GET.get(key):
                selected_cat = request.GET.get(key)
                break

    return render(request, 'category_dropdown_list_options.html', {
        'categories': categories, 
        'selected_cat': selected_cat
    })


def load_sub_categories(request, catid=None, subcatid=None):
    """HTMX view to load subcategories based on selected category"""
    # Try to get category_id from standard parameter or URL parameter
    category_id = request.GET.get('category') or catid

    # If not found, look for parameters with formset prefixes
    if not category_id:
        for key in request.GET.keys():
            if ('category' in key) and ('sub_category' not in key) and request.GET.get(key):
                category_id = request.GET.get(key)
                break

    # Try to get selected_subcategory from standard parameter or URL parameter
    selected_subcategory = request.GET.get('subcategory') or subcatid

    # If not found, look for parameters with formset prefixes
    if not selected_subcategory:
        for key in request.GET.keys():
            if ('sub_category' in key) and request.GET.get(key):
                selected_subcategory = request.GET.get(key)
                break

    sub_categories = []
    if category_id:
        sub_categories = SubCategory.objects.filter(category_id=category_id)

    return render(request, 'sub_category_dropdown_list_options.html', {
        'sub_categories': sub_categories,
        'selected_subcategory': selected_subcategory
    })

def ajax_load_subcategories(request):
    """HTMX view to load subcategories based on selected category"""
    # Try to get category_id from standard parameter
    category_id = request.GET.get('category', '')

    # If not found, look for parameters with formset prefixes
    if not category_id:
        for key in request.GET.keys():
            if ('category' in key) and ('sub_category' not in key) and request.GET.get(key):
                category_id = request.GET.get(key)
                break

    # Try to get selected_subcategory from standard parameter
    selected_subcategory = request.GET.get('subcategory', None)

    # If not found, look for parameters with formset prefixes
    if not selected_subcategory:
        for key in request.GET.keys():
            if ('sub_category' in key) and request.GET.get(key):
                selected_subcategory = request.GET.get(key)
                break

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
                Q(location__local__local_name__icontains=search_query) |
                Q(service_areas__district__district_name__icontains=search_query) |
                Q(service_areas__location__local__local_name__icontains=search_query)
            )

        # Apply subcategory filter if provided
        if subcategory_id:
            base_query &= Q(sub_category_id=subcategory_id)

        # Apply district filter if provided
        if district_id:
            base_query &= (Q(district_id=district_id) | Q(service_areas__district_id=district_id))

        # Apply location filter if provided
        if location_id:
            base_query &= (Q(location_id=location_id) | Q(service_areas__location_id=location_id))

        # Optimize query by prefetching related objects
        return Gig.objects.filter(base_query).select_related(
            'user', 'category', 'sub_category', 'district', 'location', 'user__profile'
        ).prefetch_related('service_areas').distinct().order_by(
            "-featured", "-featured_in_category", "-create_time"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cache the category to avoid additional query
        if not hasattr(self, '_category'):
            self._category = Category.objects.get(pk=self.kwargs['id'])
        context['category'] = self._category

        # Track the category view
        self._track_category_view(self._category)

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

        # Add flag to show featured badges
        context['show_featured'] = True

        return context

    def _track_category_view(self, category):
        """Track a view event for this category"""
        # Get the user if authenticated
        user = self.request.user if self.request.user.is_authenticated else None

        # Get the client IP address
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')

        # Get the user agent
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # Track the view
        Stats.track_view(category, user=user, ip_address=ip_address, user_agent=user_agent)

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
        # Get search parameters
        search_query = self.request.GET.get('param', '')
        district_id = self.request.GET.get('district', '')
        location_id = self.request.GET.get('location', '')

        # Start with base query - always show active gigs in this subcategory
        base_query = Q(status=True, sub_category_id=self.kwargs['id'])

        # Add text search if provided
        if search_query:
            base_query &= (
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(district__district_name__icontains=search_query) |
                Q(location__local__local_name__icontains=search_query) |
                Q(service_areas__district__district_name__icontains=search_query) |
                Q(service_areas__location__local__local_name__icontains=search_query)
            )

        # Apply district filter if provided
        if district_id:
            base_query &= (Q(district_id=district_id) | Q(service_areas__district_id=district_id))

        # Apply location filter if provided
        if location_id:
            base_query &= (Q(location_id=location_id) | Q(service_areas__location_id=location_id))

        # Optimize query by prefetching related objects
        return Gig.objects.filter(base_query).select_related(
            'user', 'category', 'sub_category', 'district', 'location', 'user__profile'
        ).prefetch_related('service_areas').distinct().order_by(
            "-featured", "-featured_in_subcategory", "-create_time"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Cache the subcategory to avoid additional query
        if not hasattr(self, '_sub_category'):
            self._sub_category = SubCategory.objects.select_related('category').get(pk=self.kwargs['id'])
        context['sub_category'] = self._sub_category

        # Track the subcategory view
        self._track_subcategory_view(self._sub_category)

        # Add search parameters to context
        context['search_query'] = self.request.GET.get('param', '')
        context['selected_district'] = self.request.GET.get('district', '')
        context['selected_location'] = self.request.GET.get('location', '')

        # Check if any filters are applied
        context['has_filters'] = bool(
            context['selected_district'] or 
            context['selected_location']
        )
        context['has_search'] = bool(context['search_query'])

        # Get total count of results
        context['total_count'] = self.get_queryset().count()

        # Add flag to show featured badges
        context['show_featured'] = True

        return context

    def _track_subcategory_view(self, subcategory):
        """Track a view event for this subcategory"""
        # Get the user if authenticated
        user = self.request.user if self.request.user.is_authenticated else None

        # Get the client IP address
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')

        # Get the user agent
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # Track the view
        Stats.track_view(subcategory, user=user, ip_address=ip_address, user_agent=user_agent)

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
            'user', 'category', 'sub_category', 'user__profile'
        ).order_by("-featured", "-create_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add popular categories (those with the most gigs)
        categories_with_count = Category.objects.annotate(
            gig_count=Count('gig')
        ).order_by('-gig_count')
        context['popular_categories'] = categories_with_count[:6]

        # Add featured gigs (using the featured flag)
        featured_gigs = Gig.objects.filter(status=True, featured=True).select_related(
            'user', 'category', 'sub_category', 'user__profile'
        ).order_by('-create_time')[:3]
        context['featured_gigs'] = featured_gigs

        # Add recent reviews
        recent_reviews = Review.objects.select_related(
            'user', 'gig', 'rating', 'user__profile'
        ).order_by('-create_time')[:3]
        context['recent_reviews'] = recent_reviews

        # Add flag to show featured badges
        context['show_featured'] = True

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

        # Track the gig view
        self._track_gig_view(gig)

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
        context['service_areas'] = gig.get_all_service_areas()

        # Add related gigs (same category, excluding this one)
        context['related_gigs'] = Gig.objects.filter(
            category=gig.category, 
            status=True
        ).exclude(
            id=gig.id
        ).select_related(
            'category', 'sub_category'
        ).order_by('-create_time')[:5]

        # Check if this gig was created by an admin/staff user
        is_admin_created = gig.user.is_staff
        context['is_admin_created'] = is_admin_created

        # Check if the current user can claim this gig
        can_claim = False
        has_pending_claim = False

        if is_admin_created and self.request.user.is_authenticated and self.request.user != gig.user:
            # Check if user already has a pending claim for this gig
            has_pending_claim = GigClaimRequest.objects.filter(
                gig=gig,
                user=self.request.user,
                status='pending'
            ).exists()

            # User can claim if they don't have a pending claim
            can_claim = not has_pending_claim

        context['can_claim'] = can_claim
        context['has_pending_claim'] = has_pending_claim

        return context

    def _track_gig_view(self, gig):
        """Track a view event for this gig"""
        # Get the user if authenticated
        user = self.request.user if self.request.user.is_authenticated else None

        # Get the client IP address
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')

        # Get the user agent
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')

        # Track the view
        Stats.track_view(gig, user=user, ip_address=ip_address, user_agent=user_agent)

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
            context['image_formset'] = GigImageFormSet(self.request.POST, self.request.FILES, prefix='images')
            context['contact_formset'] = GigContactFormSet(self.request.POST, prefix='contacts')
            context['service_area_formset'] = GigServiceAreaFormSet(self.request.POST, prefix='service_areas')
        else:
            context['image_formset'] = GigImageFormSet(prefix='images')
            context['contact_formset'] = GigContactFormSet(prefix='contacts')
            context['service_area_formset'] = GigServiceAreaFormSet(prefix='service_areas')

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        contact_formset = context['contact_formset']
        service_area_formset = context['service_area_formset']

        # Check if all formsets are valid before proceeding
        if not image_formset.is_valid():
            # Aggregate image formset errors for user feedback
            errors = []
            for idx, f in enumerate(image_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Image #{idx} {field}: {err}")
            errors.extend(image_formset.non_form_errors())
            messages.error(self.request, _("Image errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        if not contact_formset.is_valid():
            # Aggregate contact formset errors
            errors = []
            for idx, f in enumerate(contact_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Contact #{idx} {field}: {err}")
            errors.extend(contact_formset.non_form_errors())
            messages.error(self.request, _("Contact errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        if not service_area_formset.is_valid():
            # Aggregate service area formset errors
            errors = []
            for idx, f in enumerate(service_area_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Service Area #{idx} {field}: {err}")
            errors.extend(service_area_formset.non_form_errors())
            messages.error(self.request, _("Service area errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                form.instance.user = self.request.user
                self.object = form.save()

                # Discard any new image forms with no file
                for f in image_formset.forms:
                    if not f.cleaned_data.get('image') and not f.cleaned_data.get('id'):
                        f.cleaned_data['DELETE'] = True

                # Discard any new contact forms with no phone number
                for f in contact_formset.forms:
                    if not f.cleaned_data.get('phone_number') and not f.cleaned_data.get('id'):
                        f.cleaned_data['DELETE'] = True

                image_formset.instance = self.object
                image_formset.save()

                contact_formset.instance = self.object
                contact_formset.save()

                service_area_formset.instance = self.object
                # Ignore completely blank service area forms (e.g. when the user clicked
                # "add" several times but did not fill every extra row). A form is
                # considered blank when both the district and location are missing and
                # it is a brand-new entry (no primary key yet).
                for f in service_area_formset.forms:
                    if (
                        not f.cleaned_data.get('district')
                        and not f.cleaned_data.get('location')
                        and not f.cleaned_data.get('id')
                    ):
                        f.cleaned_data['DELETE'] = True

                service_area_formset.save()

            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred while saving your gig: {str(e)}")
            return self.form_invalid(form)

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/login/')
def create_gig(request):
    view = CreateGigView.as_view()
    return view(request)


class EditGigView(LoginRequiredMixin, UpdateView):
    model = Gig
    form_class = GigForm
    template_name = 'edit_gig.html'
    success_url = reverse_lazy('my_gigs')
    pk_url_kwarg = 'id'
    login_url = '/login/'

    def get_queryset(self):
        # Ensure users can only edit their own gigs
        return Gig.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gig = self.get_object()

        if self.request.POST:
            context['image_formset'] = GigImageFormSet(
                self.request.POST, self.request.FILES, instance=gig, prefix='images'
            )
            context['contact_formset'] = GigContactFormSet(
                self.request.POST, instance=gig, prefix='contacts'
            )
            context['service_area_formset'] = GigServiceAreaFormSet(
                self.request.POST, instance=gig, prefix='service_areas'
            )
        else:
            context['image_formset'] = GigImageFormSet(instance=gig, prefix='images')
            context['contact_formset'] = GigContactFormSet(instance=gig, prefix='contacts')
            context['service_area_formset'] = GigServiceAreaFormSet(instance=gig, prefix='service_areas')

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        contact_formset = context['contact_formset']
        service_area_formset = context['service_area_formset']

        # Check if all formsets are valid before proceeding
        if not image_formset.is_valid():
            errors = []
            for idx, f in enumerate(image_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Image #{idx} {field}: {err}")
            errors.extend(image_formset.non_form_errors())
            messages.error(self.request, _("Image errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        if not contact_formset.is_valid():
            errors = []
            for idx, f in enumerate(contact_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Contact #{idx} {field}: {err}")
            errors.extend(contact_formset.non_form_errors())
            messages.error(self.request, _("Contact errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        if not service_area_formset.is_valid():
            errors = []
            for idx, f in enumerate(service_area_formset.forms, start=1):
                for field, field_errors in f.errors.items():
                    for err in field_errors:
                        errors.append(f"Service Area #{idx} {field}: {err}")
            errors.extend(service_area_formset.non_form_errors())
            messages.error(self.request, _("Service area errors: %s") % "; ".join(errors))
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self.object = form.save()

                # Discard any updated image forms with no file for new entries
                for f in image_formset.forms:
                    if not f.cleaned_data.get('image') and not f.cleaned_data.get('id'):
                        f.cleaned_data['DELETE'] = True

                # Discard any updated contact forms with no phone number for new entries
                for f in contact_formset.forms:
                    if not f.cleaned_data.get('phone_number') and not f.cleaned_data.get('id'):
                        f.cleaned_data['DELETE'] = True

                image_formset.instance = self.object
                image_formset.save()

                contact_formset.instance = self.object
                contact_formset.save()

                service_area_formset.instance = self.object

                # Ignore completely blank service area forms that the user added but did
                # not fill out.
                for f in service_area_formset.forms:
                    if (
                        not f.cleaned_data.get('district')
                        and not f.cleaned_data.get('location')
                        and not f.cleaned_data.get('id')
                    ):
                        f.cleaned_data['DELETE'] = True

                service_area_formset.save()

            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred while saving your gig: {str(e)}")
            return self.form_invalid(form)

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/login/')
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
    login_url = '/login/'

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

        # Add total views for user's gigs
        context['total_views'] = Stats.get_total_views_for_user_gigs(self.request.user)

        # Add total views for all active gigs (for admins)
        if self.request.user.is_staff:
            context['all_active_gigs_views'] = Stats.get_total_views_for_active_gigs()

        # Add view counts for each gig
        gig_views = {}
        for gig in context['gigs']:
            gig_views[gig.id] = Stats.get_views_for_gig(gig)
        context['gig_views'] = gig_views

        return context

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/login/')
def my_gigs(request):
    view = MyGigsView.as_view()
    return view(request)


def profile(request, pid):
    # Check if user is authenticated
    is_authenticated = request.user.is_authenticated

    # Check if viewing own profile or someone else's
    is_own_profile = is_authenticated and str(request.user.id) == str(pid)

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
    all_gigs_count = Gig.objects.filter(user=profile.user, status=True).count()

    if is_authenticated:
        # Show all gigs to authenticated users
        gigs = Gig.objects.filter(user=profile.user, status=True).select_related(
            'category', 'sub_category', 'user__profile'
        )
        has_more_gigs = False
    else:
        # Show only a limited number of gigs to unauthenticated users
        limit = 3  # Limit to 3 gigs for unauthenticated users
        gigs = Gig.objects.filter(user=profile.user, status=True).select_related(
            'category', 'sub_category', 'user__profile'
        )[:limit]
        has_more_gigs = all_gigs_count > limit

    # Get districts for the district dropdown
    districts = District.objects.all()

    context = {
        "profile": profile,
        "gigs": gigs,
        "form": form,
        "is_own_profile": is_own_profile,
        "districts": districts,
        "is_authenticated": is_authenticated,
        "has_more_gigs": has_more_gigs,
        "all_gigs_count": all_gigs_count,
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


def help_center(request):
    """
    View function for the help center landing page.
    This page serves as a central hub for all help topics and guides.
    """
    return render(request, 'help_center.html')


def help_add_gig(request):
    """
    View function for the help page that explains how to add a gig.
    This page provides detailed guidance on creating gigs, explaining form fields,
    and offering tips for success.

    Note: If the gig form structure changes, this help page should be updated accordingly.
    """
    return render(request, 'help_add_gig.html')


def help_search(request):
    """
    View function for the help page that explains how to use the search functionality.
    This page provides guidance on using search filters and finding services.
    """
    return render(request, 'help_search.html')


def help_profile(request):
    """
    View function for the help page that explains how to manage your profile.
    This page provides guidance on updating profile information, adding a profile picture, etc.
    """
    return render(request, 'help_profile.html')


def help_dashboard(request):
    """
    View function for the help page that explains how to use the dashboard/my gigs page.
    This page provides guidance on managing gigs, viewing metrics, etc.
    """
    return render(request, 'help_dashboard.html')


def help_metrics(request):
    """
    View function for the help page that explains how to interpret metrics and analytics.
    This page provides guidance on understanding view counts, likes, etc.
    """
    return render(request, 'help_metrics.html')


def help_faq(request):
    """
    View function for the frequently asked questions page.
    This page provides answers to common questions about using Linkyoh.
    """
    return render(request, 'help_faq.html')


def thanks(request):
    return render(request, 'thanks.html')


class GigClaimRequestView(LoginRequiredMixin, FormView):
    """
    View for users to submit a claim request for a gig that was created by an admin.
    """
    template_name = 'claim_gig.html'
    form_class = GigClaimRequestForm

    def dispatch(self, request, *args, **kwargs):
        # Get the gig
        self.gig = get_object_or_404(Gig, id=self.kwargs['gig_id'])

        # Check if this gig was created by an admin/staff user
        if not self.gig.user.is_staff:
            messages.error(request, "This gig cannot be claimed as it was not created by an administrator.")
            return redirect('gig_detail', id=self.gig.id)

        # Check if the user already has a pending claim for this gig
        if GigClaimRequest.objects.filter(gig=self.gig, user=request.user, status='pending').exists():
            messages.info(request, "You already have a pending claim request for this gig.")
            return redirect('gig_detail', id=self.gig.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gig'] = self.gig
        return context

    def form_valid(self, form):
        # Create the claim request but don't save it yet
        claim_request = form.save(commit=False)

        # Set the gig and user
        claim_request.gig = self.gig
        claim_request.user = self.request.user

        # Save the claim request
        claim_request.save()

        # Show success message
        messages.success(self.request, 
                        "Your claim request has been submitted successfully. "
                        "An administrator will review your request and you will be notified of the decision.")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('gig_detail', kwargs={'id': self.gig.id})


# Function-based view wrapper for backward compatibility
@login_required
def claim_gig(request, gig_id):
    view = GigClaimRequestView.as_view()
    return view(request, gig_id=gig_id)


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

    # Track the search event
    _track_search_event(request, search_query, {
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'district_id': district_id,
        'location_id': location_id,
        'min_price': min_price,
        'max_price': max_price
    })

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
            Q(location__local__local_name__icontains=search_query) |
            Q(service_areas__district__district_name__icontains=search_query) |
            Q(service_areas__location__local__local_name__icontains=search_query)
        )

    # Apply category filter if provided
    if category_id:
        base_query &= Q(category_id=category_id)

    # Apply subcategory filter if provided
    if subcategory_id:
        base_query &= Q(sub_category_id=subcategory_id)

    # Apply district filter if provided
    if district_id:
        base_query &= (Q(district_id=district_id) | Q(service_areas__district_id=district_id))

    # Apply location filter if provided
    if location_id:
        base_query &= (Q(location_id=location_id) | Q(service_areas__location_id=location_id))

    # Apply price range filters if provided, but always include "Call for pricing" gigs (price=-1)
    if min_price:
        try:
            min_price_value = int(min_price)
            # Include gigs with price >= min_price OR price = -1 (call for pricing)
            base_query &= (Q(price__gte=min_price_value) | Q(price=-1))
        except ValueError:
            # Invalid min_price, ignore this filter
            min_price = ''

    if max_price:
        try:
            max_price_value = int(max_price)
            # Include gigs with price <= max_price OR price = -1 (call for pricing)
            base_query &= (Q(price__lte=max_price_value) | Q(price=-1))
        except ValueError:
            # Invalid max_price, ignore this filter
            max_price = ''

    # Execute the query
    gigs = Gig.objects.filter(base_query).select_related(
        'user', 'category', 'sub_category', 'district', 'location', 'user__profile'
    ).prefetch_related('service_areas').distinct().order_by(
        "-featured", "-create_time"
    )

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
        "total_count": total_count,
        "show_featured": True
    }

    return render(request, 'search_results.html', context)


@login_required(login_url='/login/')
@require_POST
def toggle_qr_code(request):
    """HTMX endpoint to toggle the QR code preference without a full page reload"""
    profile = get_object_or_404(Profile, user=request.user)

    # Toggle the show_qr_code field
    profile.show_qr_code = not profile.show_qr_code
    profile.save(update_fields=['show_qr_code'])

    # Return a simple response with the new state
    return HttpResponse(
        f'<div hx-swap-oob="true" id="qr-toggle-status">'
        f'QR Code is now {"enabled" if profile.show_qr_code else "disabled"}'
        f'</div>'
    )


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Store form data in session for later use after verification
            request.session['registration_data'] = {
                'username': user_form.cleaned_data['username'],
                'first_name': user_form.cleaned_data['first_name'],
                'last_name': user_form.cleaned_data['last_name'],
                'email': user_form.cleaned_data['email'],
                'password': user_form.cleaned_data['password'],
                'phone_number': str(user_form.cleaned_data['phone_number']),
            }

            # Check if phone verification is enabled
            if credentials.PHONE_VERIFICATION_ENABLED:
                # Send verification code
                phone_number = user_form.cleaned_data['phone_number']
                method = request.POST.get('verification_method', 'sms')  # Default to SMS

                from .phone_utils import create_verification
                verification, code, success = create_verification(phone_number, method)

                if success:
                    # Redirect to verification page
                    return redirect('verify_phone')
                else:
                    # If sending verification failed, show error
                    messages.error(request, "Failed to send verification code. Please try again.")
            else:
                # If verification is disabled, proceed with registration
                return complete_registration(request)
    else:
        user_form = UserRegistrationForm()

    return render(request, 'account/register.html', context={
        'user_form': user_form,
        'phone_verification_enabled': credentials.PHONE_VERIFICATION_ENABLED,
    })


def complete_registration(request):
    """Complete the registration process after phone verification or if verification is disabled"""
    registration_data = request.session.get('registration_data')

    if not registration_data:
        messages.error(request, "Registration data not found. Please try again.")
        return redirect('register')

    # Create the user
    new_user = User.objects.create_user(
        username=registration_data['username'],
        email=registration_data['email'],
        password=registration_data['password'],
        first_name=registration_data['first_name'],
        last_name=registration_data['last_name']
    )

    # Create the profile with phone number
    profile = Profile(
        user_id=new_user.id,
        phone_number=registration_data['phone_number']
    )
    profile.save()

    # Clear the session data
    if 'registration_data' in request.session:
        del request.session['registration_data']
    if 'phone_verified' in request.session:
        del request.session['phone_verified']

    # Send welcome email
    from .email_utils import send_welcome_email
    send_welcome_email(new_user, request)

    return render(request, 'account/register_done.html', context={'new_user': new_user})


def verify_phone(request):
    """Handle phone verification"""
    # Check if there's registration data in the session
    if 'registration_data' not in request.session:
        messages.error(request, "No registration in progress. Please start over.")
        return redirect('register')

    phone_number = request.session['registration_data']['phone_number']

    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')

        if not verification_code:
            return render(request, 'account/verify_phone.html', {
                'phone_number': phone_number,
                'method': request.session.get('verification_method', 'sms'),
                'error': 'Please enter the verification code.'
            })

        from .phone_utils import verify_code
        if verify_code(phone_number, verification_code):
            # Mark phone as verified in session
            request.session['phone_verified'] = True
            # Complete registration
            return complete_registration(request)
        else:
            return render(request, 'account/verify_phone.html', {
                'phone_number': phone_number,
                'method': request.session.get('verification_method', 'sms'),
                'error': 'Invalid or expired verification code. Please try again.'
            })

    # GET request - show verification form
    return render(request, 'account/verify_phone.html', {
        'phone_number': phone_number,
        'method': request.session.get('verification_method', 'sms')
    })


def resend_code(request):
    """HTMX endpoint to resend verification code"""
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    # Check if there's registration data in the session
    if 'registration_data' not in request.session:
        return render(request, 'account/resend_code_response.html', {
            'success': False,
            'method': 'sms'
        })

    phone_number = request.session['registration_data']['phone_number']
    method = request.POST.get('method', 'sms')

    # Store the verification method in session
    request.session['verification_method'] = method

    from .phone_utils import create_verification
    verification, code, success = create_verification(phone_number, method)

    return render(request, 'account/resend_code_response.html', {
        'success': success,
        'method': method
    })


def _track_search_event(request, query, filters):
    """Track a search event with query and filters"""
    # Get the user if authenticated
    user = request.user if request.user.is_authenticated else None

    # Get the client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Track the search
    Stats.track_search(user=user, ip_address=ip_address, query=query, filters=filters)


@require_POST
def track_event(request):
    """API endpoint for tracking events via AJAX"""
    # Get the event data from the request
    event_type = request.POST.get('event_type')
    object_type = request.POST.get('object_type')
    object_id = request.POST.get('object_id')
    metadata = request.POST.get('metadata', {})

    # Validate required fields
    if not all([event_type, object_type, object_id]):
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

    # Get the user if authenticated
    user = request.user if request.user.is_authenticated else None

    # Get the client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    # Get the user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Track the event based on object type
    try:
        if object_type == 'gig':
            gig = get_object_or_404(Gig, id=object_id)

            if event_type == 'contact_click':
                contact_type = metadata.get('contact_type')
                Stats.track_contact_click(gig, user=user, ip_address=ip_address, contact_type=contact_type)
            elif event_type == 'share':
                platform = metadata.get('platform')
                Stats.track_share(gig, user=user, platform=platform)
            elif event_type == 'favorite':
                Stats.track_favorite(gig, user=user, ip_address=ip_address)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid event type'}, status=400)

        elif object_type == 'category':
            category = get_object_or_404(Category, id=object_id)

            if event_type == 'share':
                platform = metadata.get('platform')
                Stats.track_share(category, user=user, platform=platform)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid event type for category'}, status=400)

        elif object_type == 'subcategory':
            subcategory = get_object_or_404(SubCategory, id=object_id)

            if event_type == 'share':
                platform = metadata.get('platform')
                Stats.track_share(subcategory, user=user, platform=platform)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid event type for subcategory'}, status=400)

        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid object type'}, status=400)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Messaging System Views

class ConversationListView(LoginRequiredMixin, ListView):
    """
    View for listing all conversations for the current user.
    """
    model = Conversation
    template_name = 'messaging/conversation_list.html'
    context_object_name = 'conversations'
    paginate_by = 20

    def get_queryset(self):
        """Get all conversations for the current user that haven't been deleted by them"""
        return Conversation.get_conversations_for_user(self.request.user).select_related(
            'initiator', 'recipient', 'gig', 'initiator__profile', 'recipient__profile'
        ).prefetch_related('messages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add unread message count
        context['unread_count'] = Message.get_unread_count_for_user(self.request.user)

        # Add conversations with last message and other participant info
        conversations_with_details = []
        for conversation in context['conversations']:
            last_message = conversation.get_last_message()
            other_participant = conversation.get_other_participant(self.request.user)

            # Skip if there's no last message (shouldn't happen in practice)
            if not last_message:
                continue

            conversations_with_details.append({
                'conversation': conversation,
                'last_message': last_message,
                'other_participant': other_participant,
                'unread': last_message.sender != self.request.user and not last_message.is_read,
                'profile': getattr(other_participant, 'profile', None),
            })

        context['conversations_with_details'] = conversations_with_details
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying a single conversation with all its messages.
    """
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'

    def get_queryset(self):
        """Only allow access to conversations the user is part of"""
        return Conversation.objects.filter(
            (Q(initiator=self.request.user) & Q(deleted_by_initiator=False)) |
            (Q(recipient=self.request.user) & Q(deleted_by_recipient=False))
        ).select_related('initiator', 'recipient', 'gig', 'initiator__profile', 'recipient__profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.get_object()

        # Get all messages for this conversation
        messages = conversation.messages.select_related('sender', 'sender__profile').prefetch_related(
            'files', 'mentioned_gigs'
        ).order_by('created_at')

        # Mark unread messages as read if the current user is the recipient
        unread_messages = messages.exclude(
            sender=self.request.user
        ).filter(
            is_read=False
        )
        for message in unread_messages:
            message.mark_as_read()

        # Add the message form for replying
        context['message_form'] = MessageForm(conversation=conversation, sender=self.request.user)
        context['file_form'] = MessageFileForm()
        context['messages'] = messages
        context['other_participant'] = conversation.get_other_participant(self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        """Handle message submission from the conversation detail page"""
        conversation = self.get_object()
        message_form = MessageForm(request.POST, conversation=conversation, sender=request.user)

        if message_form.is_valid():
            message = message_form.save()

            # Track message sent metrics
            Stats.track_message_sent(
                message=message,
                user=request.user,
                ip_address=_get_client_ip(request)
            )

            # Handle file uploads if any
            files = request.FILES.getlist('file')
            for file in files:
                file_form = MessageFileForm({'file': file})
                if file_form.is_valid():
                    message_file = file_form.save(commit=False)
                    message_file.message = message
                    message_file.save()

                    # Track file shared metrics
                    Stats.track_file_shared(
                        message_file=message_file,
                        user=request.user,
                        ip_address=_get_client_ip(request)
                    )

            # Process any gig mentions in the message content
            self._process_gig_mentions(message)

            # Fetch the message again to ensure we have all related data
            message = Message.objects.select_related('sender', 'sender__profile').prefetch_related(
                'files', 'mentioned_gigs'
            ).get(pk=message.pk)

            # If this is an HTMX request, return just the new message
            if request.headers.get('HX-Request'):
                return render(request, 'messaging/partials/message.html', {
                    'message': message,
                    'user': request.user,
                })

            # Otherwise redirect back to the conversation
            return redirect('conversation_detail', pk=conversation.pk)

        # If form is invalid, re-render the page with the form errors
        return self.get(request, *args, **kwargs)

    def _process_gig_mentions(self, message):
        """Process @gig mentions in the message content"""
        # Regular expression to find @gig mentions
        # Format: @gig[gig_id]
        mention_pattern = r'@gig\[(\d+)\]'

        # Find all mentions in the message content
        mentions = re.findall(mention_pattern, message.content)

        # Add mentioned gigs to the message
        for gig_id in mentions:
            try:
                gig = Gig.objects.get(id=gig_id)
                message.mentioned_gigs.add(gig)

                # Track gig mention metrics
                Stats.track_gig_mentioned(
                    message=message,
                    gig=gig,
                    user=self.request.user,
                    ip_address=_get_client_ip(self.request)
                )
            except Gig.DoesNotExist:
                # Skip if the gig doesn't exist
                pass


class CreateConversationView(LoginRequiredMixin, CreateView):
    """
    View for starting a new conversation with another user.
    """
    model = Conversation
    form_class = ConversationForm
    template_name = 'messaging/create_conversation.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initiator'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        # Set recipient from URL parameter if provided
        recipient_id = self.kwargs.get('recipient_id')
        if recipient_id:
            try:
                initial['recipient'] = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                pass

        # Set gig from URL parameter if provided
        gig_id = self.kwargs.get('gig_id')
        if gig_id:
            try:
                initial['gig'] = Gig.objects.get(id=gig_id)
            except Gig.DoesNotExist:
                pass

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add recipient and gig details to context if available
        recipient_id = self.kwargs.get('recipient_id')
        if recipient_id:
            try:
                recipient = User.objects.select_related('profile').get(id=recipient_id)
                context['recipient'] = recipient
            except User.DoesNotExist:
                pass

        gig_id = self.kwargs.get('gig_id')
        if gig_id:
            try:
                gig = Gig.objects.get(id=gig_id)
                context['gig'] = gig
            except Gig.DoesNotExist:
                pass

        return context

    def get_success_url(self):
        return reverse('conversation_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Track metrics when a conversation is started"""
        response = super().form_valid(form)

        # Track the conversation started event
        Stats.track_conversation_started(
            conversation=self.object,
            user=self.request.user,
            ip_address=_get_client_ip(self.request)
        )

        return response


@login_required
def start_conversation(request, recipient_id=None, gig_id=None):
    """
    View for starting a new conversation from a user profile or gig detail page.
    This is a wrapper around CreateConversationView for easier URL configuration.
    """
    view = CreateConversationView.as_view()
    return view(request, recipient_id=recipient_id, gig_id=gig_id)


@login_required
def delete_conversation(request, pk):
    """
    View for "deleting" (hiding) a conversation for the current user.
    """
    conversation = get_object_or_404(Conversation, pk=pk)

    # Check if the user is a participant in this conversation
    if not conversation.is_participant(request.user):
        messages.error(request, _("You don't have permission to delete this conversation."))
        return redirect('conversation_list')

    # Mark the conversation as deleted for this user
    conversation.mark_as_deleted(request.user)

    messages.success(request, _("Conversation deleted successfully."))
    return redirect('conversation_list')


@login_required
@require_POST
def send_message(request, conversation_id):
    """
    HTMX endpoint for sending a message in a conversation.
    """
    conversation = get_object_or_404(
        Conversation.objects.filter(
            (Q(initiator=request.user) & Q(deleted_by_initiator=False)) |
            (Q(recipient=request.user) & Q(deleted_by_recipient=False))
        ),
        pk=conversation_id
    )

    # Process the message form
    form = MessageForm(request.POST, conversation=conversation, sender=request.user)

    if form.is_valid():
        message = form.save()

        # Process any gig mentions in the message content
        mention_pattern = r'@gig\[(\d+)\]'
        mentions = re.findall(mention_pattern, message.content)

        for gig_id in mentions:
            try:
                gig = Gig.objects.get(id=gig_id)
                message.mentioned_gigs.add(gig)

                # Track gig mention metrics
                Stats.track_gig_mentioned(
                    message=message,
                    gig=gig,
                    user=request.user,
                    ip_address=_get_client_ip(request)
                )
            except Gig.DoesNotExist:
                pass

        # Track message sent metrics
        Stats.track_message_sent(
            message=message,
            user=request.user,
            ip_address=_get_client_ip(request)
        )

        # Fetch the message again to ensure we have all related data
        message = Message.objects.select_related('sender', 'sender__profile').prefetch_related(
            'files', 'mentioned_gigs'
        ).get(pk=message.pk)

        # Return the new message HTML
        return render(request, 'messaging/partials/message.html', {
            'message': message,
            'user': request.user,
        })

    # Return form errors
    return JsonResponse({'errors': form.errors}, status=400)


@login_required
@require_POST
def upload_message_file(request, conversation_id):
    """
    HTMX endpoint for uploading a file in a conversation.
    """
    conversation = get_object_or_404(
        Conversation.objects.filter(
            (Q(initiator=request.user) & Q(deleted_by_initiator=False)) |
            (Q(recipient=request.user) & Q(deleted_by_recipient=False))
        ),
        pk=conversation_id
    )

    # First create a message to attach the file to
    message_form = MessageForm({
        'content': request.POST.get('content', _('Shared a file'))
    }, conversation=conversation, sender=request.user)

    if message_form.is_valid():
        message = message_form.save()

        # Track message sent metrics
        Stats.track_message_sent(
            message=message,
            user=request.user,
            ip_address=_get_client_ip(request)
        )

        # Process the file upload
        file = request.FILES.get('file')
        if file:
            file_form = MessageFileForm({'file': file})
            if file_form.is_valid():
                message_file = file_form.save(commit=False)
                message_file.message = message
                message_file.save()

                # Track file shared metrics
                Stats.track_file_shared(
                    message_file=message_file,
                    user=request.user,
                    ip_address=_get_client_ip(request)
                )

                # Fetch the message again to ensure we have all related data
                message = Message.objects.select_related('sender', 'sender__profile').prefetch_related(
                    'files', 'mentioned_gigs'
                ).get(pk=message.pk)

                # Return the new message HTML
                return render(request, 'messaging/partials/message.html', {
                    'message': message,
                    'user': request.user,
                })

    # Return form errors
    errors = {}
    if not message_form.is_valid():
        errors.update(message_form.errors)

    return JsonResponse({'errors': errors}, status=400)


@login_required
@require_http_methods(["GET"])
def search_gigs_for_mention(request):
    """
    HTMX endpoint for searching gigs to mention in a message.
    Used for the @mention functionality.
    """
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    # Search for gigs matching the query
    gigs = Gig.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    ).filter(status=True)[:10]

    results = [{
        'id': gig.id,
        'title': gig.title,
        'photo_url': gig.get_photo_url(),
        'category': gig.category.category,
        'mention_text': f'@gig[{gig.id}]'
    } for gig in gigs]

    return JsonResponse({'results': results})


@login_required
def messages_index(request):
    """
    View for the messages index page.
    This is a wrapper around ConversationListView for easier URL configuration.
    """
    view = ConversationListView.as_view()
    return view(request)


@login_required
def conversation_detail(request, pk):
    """
    View for the conversation detail page.
    This is a wrapper around ConversationDetailView for easier URL configuration.
    """
    view = ConversationDetailView.as_view()
    return view(request, pk=pk)
