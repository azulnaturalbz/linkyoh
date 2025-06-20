from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Gig, Profile, Location, District, Category, SubCategory, Review
from .forms import GigForm, ReviewForm, ContactForm, UserRegistrationForm


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


class CategoryListView(ListView):
    model = Gig
    template_name = 'categories.html'
    context_object_name = 'gigs'
    paginate_by = 6

    def get_queryset(self):
        # Optimize query by prefetching related objects
        return Gig.objects.filter(status=True, category_id=self.kwargs['id']).select_related(
            'user', 'category', 'sub_category'
        ).order_by("-create_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Cache the category to avoid additional query
        if not hasattr(self, '_category'):
            self._category = Category.objects.get(pk=self.kwargs['id'])
        context['category'] = self._category
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
            'user', 'category', 'sub_category', 'district', 'location'
        ).prefetch_related('likes')

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
        context['reviews'] = Review.objects.filter(gig=gig).select_related('user', 'rating')
        context['is_liked'] = is_liked
        context['total_likes'] = gig.total_likes()

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

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['districts'] = District.objects.all()
        return context

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
        context['districts'] = District.objects.all()
        context['locations'] = Location.objects.filter(local__local_district=gig.district_id)
        context['categories'] = Category.objects.all()
        context['sub_categories'] = SubCategory.objects.filter(category_id=gig.category_id)
        return context

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
        return Gig.objects.filter(user=self.request.user)

# Keep the function-based view as a wrapper for backward compatibility
@login_required(login_url='/')
def my_gigs(request):
    view = MyGigsView.as_view()
    return view(request)


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
