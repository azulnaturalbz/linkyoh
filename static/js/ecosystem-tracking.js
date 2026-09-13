(function () {
    'use strict';
    document.addEventListener('click', function (event) {
        var link = event.target.closest && event.target.closest('a[data-track]');
        if (!link || !window.rybbit || typeof window.rybbit.event !== 'function') return;
        var url = new URL(link.href, window.location.origin);
        if (url.searchParams.get('utm_medium') !== 'ecosystem') return;
        try {
            window.rybbit.event(link.dataset.track, {
                source: 'linkyoh',
                placement: url.searchParams.get('utm_campaign')
            });
        } catch (error) {
            // Analytics must never interrupt navigation.
        }
    });
}());
