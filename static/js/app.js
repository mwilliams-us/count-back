// Menu overlay open/close
const menuBtn = document.getElementById('menu-btn');
const overlay = document.getElementById('menu-overlay');

menuBtn?.addEventListener('click', () => overlay.classList.remove('hidden'));
overlay?.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.add('hidden');
});