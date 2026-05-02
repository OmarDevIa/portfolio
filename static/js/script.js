window.initGoogleTranslate = () => {
    if (!window.google || !window.google.translate) return;
    new window.google.translate.TranslateElement(
        {
            pageLanguage: 'fr',
            includedLanguages: 'fr,en,ar,it,tr',
            autoDisplay: false,
        },
        'google_translate_element'
    );
};

document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('siteHeader');
    const navToggle = document.getElementById('navToggle');
    const mainNav = document.getElementById('mainNav');
    const themeToggle = document.getElementById('themeToggle');
    const backToTop = document.getElementById('backToTop');
    const footerYear = document.getElementById('footerYear');
    const translateToggle = document.getElementById('translateToggle');
    const translatePanel = document.getElementById('translatePanel');

    if (footerYear) footerYear.textContent = new Date().getFullYear();

    // Lazy loading fade-in
    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', () => img.classList.add('loaded'));
        }
    });

    // Intersection Observer pour reveals modernes
    const revealItems = document.querySelectorAll('.reveal, .animate-up, .animate-fadein');
    if (revealItems.length) {
        const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReduced) {
            revealItems.forEach(el => el.classList.add('is-visible'));
        } else {
            const obs = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        obs.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
            revealItems.forEach(el => obs.observe(el));
        }
    }

    // Nav toggle mobile
    if (navToggle && mainNav) {
        navToggle.addEventListener('click', () => mainNav.classList.toggle('open'));
    }

    // Theme
    const applyTheme = (theme) => {
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('portfolio-theme', theme);
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'night' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        }
    };
    if (themeToggle) {
        applyTheme(localStorage.getItem('portfolio-theme') || 'night');
        themeToggle.addEventListener('click', () => {
            applyTheme(document.body.getAttribute('data-theme') === 'night' ? 'day' : 'night');
        });
    }

    // Scroll
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        if (header) header.classList.toggle('scrolled', y > 20);
        if (backToTop) backToTop.classList.toggle('visible', y > 400);
    }, { passive: true });

    // Project filter
    const filterBtns = document.querySelectorAll('.project-filter li');
    if (filterBtns.length) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.dataset.filter;
                document.querySelectorAll('.project-item').forEach(item => {
                    item.classList.toggle('is-hidden', filter !== 'all' && item.dataset.category !== filter);
                });
            });
        });
    }

    // Hero slider
    const heroSlider = document.getElementById('heroSlider');
    if (heroSlider) {
        const slides = Array.from(heroSlider.querySelectorAll('.hero-slide'));
        const dots = Array.from(heroSlider.querySelectorAll('.hero-dot'));
        if (slides.length > 0) {
            let index = 0;
            const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            const show = (next) => {
                index = (next + slides.length) % slides.length;
                slides.forEach((slide, i) => slide.classList.toggle('is-active', i === index));
                dots.forEach((dot, i) => dot.classList.toggle('is-active', i === index));
            };

            show(index);
            dots.forEach((dot) => {
                dot.addEventListener('click', () => show(Number(dot.dataset.index || 0)));
            });

            if (!prefersReduced && slides.length > 1) {
                window.setInterval(() => show(index + 1), 6000);
            }
        }
    }

    // Async form helper
    const wireForm = (formId, alertId) => {
        const form = document.getElementById(formId);
        const alertBox = document.getElementById(alertId);
        if (!form || !alertBox) return;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                const res = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'application/json' },
                    body: new FormData(form),
                });
                const data = await res.json();
                alertBox.classList.remove('d-none', 'success', 'error');
                if (res.ok) {
                    alertBox.classList.add('success');
                    alertBox.textContent = data.message;
                    form.reset();
                } else {
                    alertBox.classList.add('error');
                    alertBox.textContent = Object.values(data.errors || {}).flat().join(' ');
                }
            } catch {
                alertBox.classList.remove('d-none', 'success');
                alertBox.classList.add('error');
                alertBox.textContent = 'Erreur réseau. Réessayez.';
            }
        });
    };

    wireForm('contactForm', 'formAlert');
    wireForm('testimonialForm', 'testiAlert');

    const setLanguage = (lang) => {
        const select = document.querySelector('#google_translate_element select');
        if (!select) return;
        select.value = lang;
        select.dispatchEvent(new Event('change'));
    };

    if (translateToggle && translatePanel) {
        translateToggle.addEventListener('click', () => {
            const isOpen = translatePanel.classList.toggle('is-open');
            translateToggle.setAttribute('aria-expanded', String(isOpen));
            translatePanel.setAttribute('aria-hidden', String(!isOpen));
        });
        document.querySelectorAll('[data-lang]').forEach((button) => {
            button.addEventListener('click', () => {
                const lang = button.getAttribute('data-lang');
                if (lang) setLanguage(lang);
                translatePanel.classList.remove('is-open');
                translateToggle.setAttribute('aria-expanded', 'false');
                translatePanel.setAttribute('aria-hidden', 'true');
            });
        });
        document.addEventListener('click', (event) => {
            if (!translatePanel.contains(event.target) && !translateToggle.contains(event.target)) {
                translatePanel.classList.remove('is-open');
                translateToggle.setAttribute('aria-expanded', 'false');
                translatePanel.setAttribute('aria-hidden', 'true');
            }
        });
    }
});
