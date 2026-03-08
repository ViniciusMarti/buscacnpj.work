// GTM Events Tracker
document.addEventListener("DOMContentLoaded", function() {
    // 1. Scroll percentage every 10%
    let scrollMarks = new Set();
    let isMobile = window.innerWidth <= 768 ? 'Mobile' : 'Desktop';
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.scrollY || document.documentElement.scrollTop;
        let docHeight = Math.max(
            document.body.scrollHeight, document.documentElement.scrollHeight,
            document.body.offsetHeight, document.documentElement.offsetHeight,
            document.body.clientHeight, document.documentElement.clientHeight
        ) - document.documentElement.clientHeight;
        
        if (docHeight <= 0) return;

        let scrollPercent = Math.round((scrollTop / docHeight) * 100);
        let roundedPercent = Math.floor(scrollPercent / 10) * 10;
        
        if (roundedPercent > 0 && roundedPercent <= 100 && !scrollMarks.has(roundedPercent)) {
            scrollMarks.add(roundedPercent);
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                'event': 'scroll_depth',
                'scroll_percentage': roundedPercent,
                'device_type': isMobile
            });
        }
    });

    // 2. Cambly Ad Complete View (when ad becomes 90% visible)
    let camblyAd = document.querySelector('.promo-banner') || document.querySelector('.cambly-banner-card');
    if (camblyAd) {
        if ('IntersectionObserver' in window) {
            let adObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && entry.intersectionRatio >= 0.9) {
                        if (!camblyAd.dataset.viewed) {
                            camblyAd.dataset.viewed = "true";
                            window.dataLayer = window.dataLayer || [];
                            window.dataLayer.push({
                                'event': 'cambly_ad_view_complete'
                            });
                        }
                    }
                });
            }, { threshold: [0.9] });
            adObserver.observe(camblyAd);
        } else {
            // Fallback for older browsers
            camblyAd.dataset.viewed = "true";
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                'event': 'cambly_ad_view_complete'
            });
        }
    }

    // 3. Clicked on Cambly Ad
    let camblyLinks = document.querySelectorAll('.promo-cta, .cambly-cta, a[href*="cambly.com"]');
    camblyLinks.forEach(link => {
        link.addEventListener('click', function() {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                'event': 'cambly_ad_click'
            });
        });
    });

    // 4. Left page in less than 5 seconds
    let startTime = Date.now();
    window.addEventListener('beforeunload', function() {
        let timeSpent = Date.now() - startTime;
        if (timeSpent < 5000) {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                'event': 'bounce_fast',
                'time_on_page_ms': timeSpent
            });
        }
    });

    // 5. Copied text/number from page
    document.addEventListener('copy', function() {
        let copiedText = window.getSelection().toString();
        if (copiedText.trim().length > 0) {
            let justNumbers = copiedText.replace(/\D/g, '');
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                'event': 'text_copied',
                'text_length': copiedText.length,
                'is_number': justNumbers.length > 3,
                'is_cnpj': justNumbers.length === 14
            });
        }
    });
});
