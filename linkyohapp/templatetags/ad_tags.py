import random
from django import template
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AnonymousUser

from ..models_ad import AdPlacement, Advertisement, AdPlacementAssignment, AdImpression

register = template.Library()

@register.simple_tag(takes_context=True)
def display_ad(context, placement_name):
    """
    Display an advertisement in the specified placement.
    
    Usage:
    {% load ad_tags %}
    {% display_ad 'home_hero' %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Get the placement
    try:
        placement = AdPlacement.objects.get(name=placement_name, is_active=True)
    except AdPlacement.DoesNotExist:
        return ''
    
    # Get active ads for this placement
    now = timezone.now()
    ad_assignments = AdPlacementAssignment.objects.filter(
        placement=placement,
        ad__status='active',
        ad__start_date__lte=now
    ).select_related('ad').order_by('-priority')
    
    # Filter ads that have an end date in the future or no end date
    ad_assignments = [
        a for a in ad_assignments 
        if a.ad.end_date is None or a.ad.end_date >= now
    ]
    
    # Filter ads that haven't reached their max impressions
    ad_assignments = [
        a for a in ad_assignments 
        if a.ad.max_impressions is None or a.ad.total_impressions < a.ad.max_impressions
    ]
    
    # Get the current user
    user = request.user if hasattr(request, 'user') else None
    
    # Apply targeting filters if available
    if hasattr(context, 'category'):
        category = context.get('category')
        if category:
            ad_assignments = [
                a for a in ad_assignments 
                if not a.ad.target_categories.exists() or a.ad.target_categories.filter(id=category.id).exists()
            ]
    
    if hasattr(context, 'district'):
        district = context.get('district')
        if district:
            ad_assignments = [
                a for a in ad_assignments 
                if not a.ad.target_districts.exists() or a.ad.target_districts.filter(id=district.id).exists()
            ]
    
    # If no ads are available, return empty string
    if not ad_assignments:
        return ''
    
    # Select ads based on priority
    # Group ads by priority
    priority_groups = {}
    for assignment in ad_assignments:
        priority = assignment.priority
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(assignment)
    
    # Get the highest priority group
    highest_priority = max(priority_groups.keys())
    highest_priority_ads = priority_groups[highest_priority]
    
    # Randomly select an ad from the highest priority group
    selected_assignment = random.choice(highest_priority_ads)
    ad = selected_assignment.ad
    
    # Record impression
    if not request.session.session_key:
        request.session.save()
    
    session_id = request.session.session_key
    ip_address = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Create impression record
    impression = AdImpression.objects.create(
        ad=ad,
        placement=placement,
        user=None if isinstance(user, AnonymousUser) else user,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    # Update counters
    ad.total_impressions += 1
    ad.save(update_fields=['total_impressions'])
    
    selected_assignment.impressions += 1
    selected_assignment.save(update_fields=['impressions'])
    
    # Render the ad based on its type
    context = {
        'ad': ad,
        'placement': placement,
        'impression_id': impression.id
    }
    
    if ad.ad_type == 'banner':
        return mark_safe(render_to_string('ads/banner_ad.html', context))
    elif ad.ad_type == 'card':
        return mark_safe(render_to_string('ads/card_ad.html', context))
    elif ad.ad_type == 'text':
        return mark_safe(render_to_string('ads/text_ad.html', context))
    elif ad.ad_type == 'sponsored':
        return mark_safe(render_to_string('ads/sponsored_ad.html', context))
    else:
        # Default rendering
        return mark_safe(render_to_string('ads/default_ad.html', context))