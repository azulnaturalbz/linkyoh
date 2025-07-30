/**
 * Stats Tracking JavaScript
 * 
 * This script handles tracking various events like clicks, shares, and favorites.
 * It sends tracking data to the server via AJAX.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add click tracking to all contact buttons
    document.querySelectorAll('.contact-button, .phone-button, .whatsapp-button, .email-button').forEach(button => {
        button.addEventListener('click', function(e) {
            const gigId = this.dataset.gigId;
            const contactType = this.dataset.contactType || this.className.split(' ')[0];
            
            if (gigId) {
                trackEvent('contact_click', 'gig', gigId, { contact_type: contactType });
            }
        });
    });
    
    // Add click tracking to all share buttons
    document.querySelectorAll('.share-button, .facebook-share, .twitter-share, .whatsapp-share').forEach(button => {
        button.addEventListener('click', function(e) {
            const objectType = this.dataset.objectType;
            const objectId = this.dataset.objectId;
            const platform = this.dataset.platform || this.className.split(' ')[0];
            
            if (objectType && objectId) {
                trackEvent('share', objectType, objectId, { platform: platform });
            }
        });
    });
    
    // Add click tracking to all favorite/like buttons
    document.querySelectorAll('.favorite-button, .like-button').forEach(button => {
        button.addEventListener('click', function(e) {
            const gigId = this.dataset.gigId;
            
            if (gigId) {
                trackEvent('favorite', 'gig', gigId);
            }
        });
    });
});

/**
 * Track an event by sending it to the server
 * @param {string} eventType - The type of event (e.g., 'contact_click', 'share', 'favorite')
 * @param {string} objectType - The type of object (e.g., 'gig', 'category', 'subcategory')
 * @param {string} objectId - The ID of the object
 * @param {Object} metadata - Additional metadata for the event
 */
function trackEvent(eventType, objectType, objectId, metadata = {}) {
    // Create form data for the request
    const formData = new FormData();
    formData.append('event_type', eventType);
    formData.append('object_type', objectType);
    formData.append('object_id', objectId);
    
    // Add metadata if provided
    if (Object.keys(metadata).length > 0) {
        formData.append('metadata', JSON.stringify(metadata));
    }
    
    // Get CSRF token
    const csrfToken = getCsrfToken();
    
    // Send the tracking data to the server
    fetch('/track-event/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            console.error('Error tracking event:', response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Event tracked successfully:', data);
    })
    .catch(error => {
        console.error('Error tracking event:', error);
    });
}

/**
 * Get the CSRF token from the cookie
 * @returns {string} The CSRF token
 */
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}