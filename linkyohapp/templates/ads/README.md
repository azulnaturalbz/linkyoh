# Linkyoh Advertisement System

This document provides an overview of the advertisement system implemented in the Linkyoh application.

## Overview

The advertisement system allows for displaying ads in various locations throughout the site. It includes:

- A database model for storing advertisements and tracking impressions and clicks
- An admin interface for managing ads
- A template tag system for displaying ads in templates
- A tracking system for recording impressions and clicks

## Database Models

The system uses the following models:

1. **AdPlacement**: Defines where ads can be placed in the application
2. **Advertisement**: The main model for advertisements, with fields for content, targeting, scheduling, and tracking
3. **AdPlacementAssignment**: Associates advertisements with placements and tracks performance for specific placements
4. **AdImpression**: Records individual ad impressions for detailed analytics
5. **AdClick**: Records individual ad clicks for detailed analytics

## Ad Types

The system supports four types of ads:

1. **Banner Ads**: Full-width banner advertisements
2. **Card Ads**: Card-style advertisements that match the existing card design
3. **Text Ads**: Simple text-based advertisements
4. **Sponsored Ads**: Advertisements that look like regular content but are marked as sponsored

## Placing Ads in Templates

To display an ad in a template, use the `display_ad` template tag:

```html
{% load ad_tags %}
{% display_ad 'home_hero' %}
```

The `display_ad` tag takes a placement name as an argument. The available placements are:

- `home_hero`: Home Page - Hero Banner
- `home_featured`: Home Page - Featured Section
- `home_categories`: Home Page - Between Categories
- `home_how_it_works`: Home Page - After How It Works
- `home_reviews`: Home Page - After Reviews
- `home_latest`: Home Page - Within Latest Services
- `home_footer`: Home Page - Before Footer
- `category_top`: Category Page - Top
- `category_bottom`: Category Page - Bottom
- `category_inline`: Category Page - Inline with Results
- `gig_detail_top`: Gig Detail Page - Top
- `gig_detail_bottom`: Gig Detail Page - Bottom
- `gig_detail_sidebar`: Gig Detail Page - Sidebar
- `profile_top`: Profile Page - Top
- `profile_bottom`: Profile Page - Bottom
- `search_top`: Search Results - Top
- `search_inline`: Search Results - Inline with Results
- `search_bottom`: Search Results - Bottom
- `global_header`: Global - Below Header
- `global_footer`: Global - Above Footer

## Creating Advertisements

Advertisements can be created through the admin interface. To create an ad:

1. Go to the admin interface
2. Navigate to "Advertisements" under the "Ad System" section
3. Click "Add Advertisement"
4. Fill in the required fields:
   - Title: The title of the advertisement
   - Advertiser: The user who created the advertisement
   - Ad Type: The type of advertisement (banner, card, text, or sponsored)
   - Content: Either an image or HTML content
   - Destination URL: Where users will be directed when clicking the ad
   - Placements: Where the ad will be displayed
   - Targeting: Categories and districts to target
   - Scheduling: Start and end dates for the ad
   - Budget and Limits: Budget and maximum impressions

## Ad Selection Algorithm

When a template requests an ad for a specific placement, the system:

1. Filters ads by placement, status, and scheduling
2. Applies targeting filters based on the current context (category, district)
3. Groups ads by priority
4. Selects a random ad from the highest priority group

This ensures that ads are displayed based on their priority, with randomization among ads of the same priority.

## Tracking Impressions and Clicks

The system tracks impressions and clicks in two ways:

1. **Server-side**: When an ad is displayed, an impression is recorded in the database. When an ad is clicked, a click is recorded in the database.
2. **Client-side**: The `ad_tracking.js` script uses the Intersection Observer API to ensure that impressions are only counted when ads are actually visible to users.

## Viewing Analytics

Analytics for advertisements can be viewed in the admin interface:

1. Go to the admin interface
2. Navigate to "Advertisements" under the "Ad System" section
3. Click on an advertisement to view its details
4. The "Performance" section shows impressions, clicks, and click-through rate (CTR)

For more detailed analytics, you can view the "Ad Impressions" and "Ad Clicks" sections, which show individual impressions and clicks with user information.

## Implementation Details

The advertisement system is implemented using the following files:

- `models_ad.py`: Database models for the ad system
- `admin_ad.py`: Admin interface for the ad system
- `views_ad.py`: Views for handling ad clicks
- `urls_ad.py`: URL patterns for the ad system
- `templatetags/ad_tags.py`: Template tags for displaying ads
- `templates/ads/`: Templates for rendering different types of ads
- `static/js/ad_tracking.js`: JavaScript for tracking ad impressions and clicks

## Best Practices

1. **Ad Content**: Keep ad content relevant to the site's audience
2. **Ad Placement**: Place ads in locations where they will be seen but not disruptive
3. **Ad Targeting**: Use targeting to show ads to the most relevant users
4. **Ad Rotation**: Use multiple ads in the same placement to avoid ad fatigue
5. **Ad Performance**: Monitor ad performance and adjust as needed