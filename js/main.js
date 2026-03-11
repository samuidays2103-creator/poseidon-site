// === Sticky Header ===
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('header--scrolled', window.scrollY > 10);
});

// === Mobile Navigation ===
const hamburger = document.getElementById('hamburger');
const nav = document.getElementById('nav');

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  nav.classList.toggle('open');
  document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
});

// Close mobile nav on link click
nav.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('active');
    nav.classList.remove('open');
    document.body.style.overflow = '';
  });
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
    if (text) el.innerHTML = text;
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
