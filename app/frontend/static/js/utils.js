// Shared utility functions

const ICONS = {
  huevos: '🥚', huevo: '🥚', patata: '🥔', patatas: '🥔',
  pasta: '🍝', sal: '🧂', pesto: '🌿', tomate: '🍅',
  queso: '🧀', leche: '🥛', pan: '🍞', pollo: '🍗',
  arroz: '🍚', cebolla: '🧅', ajo: '🧄', zanahoria: '🥕',
  aceite: '🫙', harina: '🌾', azúcar: '🍬', azucar: '🍬',
  mantequilla: '🧈', nata: '🥛', limón: '🍋', limon: '🍋',
  naranja: '🍊', manzana: '🍎', plátano: '🍌', platano: '🍌',
  carne: '🥩', ternera: '🥩', cerdo: '🥩', cordero: '🥩',
  pescado: '🐟', salmón: '🐟', salmon: '🐟', atún: '🐟', atun: '🐟',
  gambas: '🦐', marisco: '🦐', mejillones: '🦪',
  pimiento: '🫑', pepino: '🥒', lechuga: '🥬', espinaca: '🥬',
  brócoli: '🥦', brocoli: '🥦', berenjena: '🍆', calabacín: '🥒',
  maíz: '🌽', maiz: '🌽', aguacate: '🥑', champiñón: '🍄',
  chocolate: '🍫', miel: '🍯', vinagre: '🫙', vino: '🍷',
  cerveza: '🍺', agua: '💧', zumo: '🍹', café: '☕', cafe: '☕',
  pimienta: '🌶️', orégano: '🌿', oregano: '🌿', romero: '🌿',
  levadura: '🫙', bicarbonato: '🫙', aceitunas: '🫒',
  panceta: '🥓', jamón: '🍖', jamon: '🍖',
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
