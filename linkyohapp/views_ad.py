from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_GET
from django.contrib.auth.models import AnonymousUser

from .models_ad import Advertisement, AdClick

@require_GET
def ad_click(request, slug):
    """
    Handle ad clicks:
    1. Record the click
    2. Redirect to the destination URL
    """
    # Get the ad
    ad = get_object_or_404(Advertisement, slug=slug, status='active')
    
    # Get the placement from the referrer or query parameter
    placement_id = request.GET.get('placement')
    if placement_id:
        try:
            placement = ad.placements.get(id=placement_id)
        except:
            placement = ad.placements.first()
    else:
        placement = ad.placements.first()
    
    if not placement:
        raise Http404("Ad placement not found")
    
    # Get user info
    user = request.user if hasattr(request, 'user') else None
    session_id = request.session.session_key or ''
    ip_address = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Record the click
    click = AdClick.objects.create(
        ad=ad,
        placement=placement,
        user=None if isinstance(user, AnonymousUser) else user,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    # Update counters
    ad.total_clicks += 1
    ad.save(update_fields=['total_clicks'])
    
    # Get the assignment for this placement
    try:
        assignment = ad.adplacementassignment_set.get(placement=placement)
        assignment.clicks += 1
        assignment.save(update_fields=['clicks'])
    except:
        pass
    
    # Redirect to the destination URL
    return HttpResponseRedirect(ad.destination_url)