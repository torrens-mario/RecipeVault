// Shared utility functions

const ICONS = {
  huevos: '🥚', huevo: '🥚', patata: '🥔', pasta: '🍝',
  sal: '🧂', pesto: '🌿', tomate: '🍅', queso: '🧀',
  leche: '🥛', pan: '🍞', pollo: '🍗', arroz: '🍚',
  cebolla: '🧅', ajo: '🧄', zanahoria: '🥕', aceite: '🫙'
};

function iconForIngredient(name) {
  const key = String(name || '').toLowerCase();
  return ICONS[key] || '🛒';
}

function showToast(message) {
  let t = document.querySelector('.toast');
  if (!t) {
    t = document.createElement('div');
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = message;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}
