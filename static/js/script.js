document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('siteHeader');
    const navToggle = document.getElementById('navToggle');
    const mainNav = document.getElementById('mainNav');
    const themeToggle = document.getElementById('themeToggle');
    const backToTop = document.getElementById('backToTop');
    const footerYear = document.getElementById('footerYear');

    if (footerYear) footerYear.textContent = new Date().getFullYear();

    // Lazy loading fade-in
    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        if (img.complete) {
            img.classList.add('loaded');
        } else {
            img.addEventListener('load', () => img.classList.add('loaded'));
        }
    });

    // Intersection Observer pour animate-up
    const animItems = document.querySelectorAll('.animate-up');
    if (animItems.length) {
        const obs = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.style.animationPlayState = 'running';
                    obs.unobserve(e.target);
                }
            });
        }, { threshold: 0.1 });
        animItems.forEach(el => {
            el.style.animationPlayState = 'paused';
            obs.observe(el);
        });
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
        applyTheme(localStorage.getItem('portfolio-theme') || 'day');
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
});
