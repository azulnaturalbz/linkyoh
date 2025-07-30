/**
 * Ad Tracking JavaScript
 * 
 * This script handles tracking ad impressions and clicks.
 * It ensures that impressions are only counted when ads are actually visible.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Intersection Observer to detect when ads are visible
    if ('IntersectionObserver' in window) {
        const adObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Ad is visible, record impression if not already recorded
                    const adContainer = entry.target;
                    if (!adContainer.dataset.impressionRecorded) {
                        recordImpression(adContainer);
                        adContainer.dataset.impressionRecorded = 'true';
                        
                        // Stop observing this ad after impression is recorded
                        observer.unobserve(adContainer);
                    }
                }
            });
        }, {
            root: null, // viewport
            threshold: 0.5 // 50% of the ad must be visible
        });
        
        // Observe all ad containers
        document.querySelectorAll('.ad-container, .ad-card, .sponsored-ad').forEach(ad => {
            adObserver.observe(ad);
        });
    } else {
        // Fallback for browsers that don't support Intersection Observer
        // Just record impressions for all ads immediately
        document.querySelectorAll('.ad-container, .ad-card, .sponsored-ad').forEach(ad => {
            if (!ad.dataset.impressionRecorded) {
                recordImpression(ad);
                ad.dataset.impressionRecorded = 'true';
            }
        });
    }
    
    // Add click tracking to all ad links
    document.querySelectorAll('.ad-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // The actual redirect will be handled by the href
            // This is just for additional tracking if needed
            const adContainer = link.closest('.ad-container, .ad-card, .sponsored-ad');
            if (adContainer) {
                recordClick(adContainer);
            }
        });
    });
});

/**
 * Record an ad impression
 * @param {HTMLElement} adContainer - The ad container element
 */
function recordImpression(adContainer) {
    const adId = adContainer.dataset.adId;
    const impressionId = adContainer.dataset.impressionId;
    
    if (adId && impressionId) {
        // Log impression for analytics
        console.log(`Ad impression recorded: ${adId}, Impression ID: ${impressionId}`);
        
        // You could send additional data to the server here if needed
        // For example, to record viewability metrics or time spent viewing the ad
    }
}

/**
 * Record an ad click
 * @param {HTMLElement} adContainer - The ad container element
 */
function recordClick(adContainer) {
    const adId = adContainer.dataset.adId;
    
    if (adId) {
        // Log click for analytics
        console.log(`Ad click recorded: ${adId}`);
        
        // You could send additional data to the server here if needed
        // For example, to record click coordinates or time since impression
    }
}