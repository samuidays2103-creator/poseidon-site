// === Sticky Header (debounced) ===
const header = document.getElementById('header');
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      header.classList.toggle('header--scrolled', window.scrollY > 10);
      ticking = false;
    });
    ticking = true;
  }
});

// === Mobile Navigation (iOS Safari safe) ===
const hamburger = document.getElementById('hamburger');
const nav = document.getElementById('nav');

function closeMenu() {
  nav.classList.remove('open');
  hamburger.classList.remove('active');
  header.classList.remove('header--menu-open');
  hamburger.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

hamburger.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('open');
  hamburger.classList.toggle('active', isOpen);
  header.classList.toggle('header--menu-open', isOpen);
  hamburger.setAttribute('aria-expanded', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
});

nav.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', closeMenu);
});

document.addEventListener('click', (e) => {
  if (nav.classList.contains('open') &&
      !nav.contains(e.target) && !hamburger.contains(e.target)) {
    closeMenu();
  }
});

// === Language Switching ===
const langToggle = document.getElementById('langToggle');
let currentLang = localStorage.getItem('poseidon-lang') || 'ru';

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('poseidon-lang', lang);
  langToggle.textContent = lang === 'ru' ? 'EN' : 'RU';
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-ru][data-en]').forEach(el => {
    const text = el.getAttribute(`data-${lang}`);
    if (text) {
      // Use innerHTML only for elements with HTML content (like <br>, <strong>)
      if (text.includes('<')) {
        el.innerHTML = text;
      } else {
        el.textContent = text;
      }
    }
  });
}

langToggle.addEventListener('click', () => {
  applyLang(currentLang === 'ru' ? 'en' : 'ru');
});

// Apply saved language on load
if (currentLang !== 'ru') applyLang(currentLang);

// === Scroll Fade-in Animation ===
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// === Smooth scroll for anchor links ===
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});
