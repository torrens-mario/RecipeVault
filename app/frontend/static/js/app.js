const grid = document.getElementById('recipes');
const search = document.getElementById('search');
const sortSelect = document.getElementById('sortSelect');
const filterCategory = document.getElementById('filterCategory');
const filterDifficulty = document.getElementById('filterDifficulty');
const filterFavs = document.getElementById('filterFavs');
const filterPlan = document.getElementById('filterPlan');

function sortRecipes(items) {
  const mode = sortSelect?.value || 'alphabetical';
  const sorted = [...items];
  if (mode === 'alphabetical') sorted.sort((a, b) => a.title.localeCompare(b.title, 'es'));
  if (mode === 'favorites') sorted.sort((a, b) => Number(b.favorite) - Number(a.favorite) || a.title.localeCompare(b.title, 'es'));
  if (mode === 'ingredients') sorted.sort((a, b) => (b.ingredients?.length || 0) - (a.ingredients?.length || 0));
  if (mode === 'planned') sorted.sort((a, b) => Number(b.planned_to_cook) - Number(a.planned_to_cook) || a.title.localeCompare(b.title, 'es'));
  if (mode === 'rating') sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0) || a.title.localeCompare(b.title, 'es'));
  return sorted;
}

function applyFilters(items) {
  let result = items;
  const cat = filterCategory?.value || '';
  const diff = filterDifficulty?.value || '';
  const onlyFavs = filterFavs?.dataset.active === 'true';
  const onlyPlan = filterPlan?.dataset.active === 'true';
  if (cat) result = result.filter(r => r.category === cat);
  if (diff) result = result.filter(r => r.difficulty === diff);
  if (onlyFavs) result = result.filter(r => r.favorite);
  if (onlyPlan) result = result.filter(r => r.planned_to_cook);
  return result;
}

function renderStars(rating) {
  if (!rating) return '';
  return [1,2,3,4,5].map(i =>
    `<span class="star-display ${i <= rating ? 'active' : ''}">★</span>`
  ).join('');
}

function renderRecipes(items) {
  if (!grid) return;
  const filtered = applyFilters(items);
  const sorted = sortRecipes(filtered);
  if (!sorted.length) {
    grid.innerHTML = '<p class="muted">No hay recetas con estos filtros.</p>';
    return;
  }
  grid.innerHTML = sorted.map(r => `
    <article class="card recipe-card">
      <img class="recipe-photo" src="${esc(r.image || '')}" alt="Imagen de ${esc(r.title)}" loading="lazy" width="1200" height="800" onerror="this.onerror=null;this.style.display='none'">
      <div class="recipe-card-body">
        <div class="recipe-card-head">
          <h3>${esc(r.title)} ${r.is_public === false ? '<span class="private-badge" title="Receta privada">🔒</span>' : ''}</h3>
          <button class="favorite-btn ${r.favorite ? 'active' : ''}" data-favorite="${r.id}" aria-label="Marcar como favorita">❤</button>
        </div>
        <div class="recipe-card-meta">
          <span class="muted">${esc(r.category)} · ${r.servings} raciones</span>
          <span class="difficulty-badge difficulty-${r.difficulty === 'Fácil' ? 'facil' : r.difficulty === 'Difícil' ? 'dificil' : 'media'}">${esc(r.difficulty || 'Media')}</span>
        </div>
        ${r.rating > 0 ? `<div class="star-row" style="margin-top:4px;">${renderStars(r.rating)}</div>` : ''}
        ${(r.prep_time > 0 || r.cook_time > 0) ? `<p class="muted time-info">${[r.prep_time > 0 ? '⏱ ' + r.prep_time + ' min' : '', r.cook_time > 0 ? '🍳 ' + r.cook_time + ' min' : ''].filter(Boolean).join(' · ')}</p>` : ''}
        <p>${esc(r.description || '')}</p>
        <div class="card-tags">
          ${(r.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join('')}
          ${r.planned_to_cook ? '<span class="tag tag-plan">Quiero cocinarla</span>' : ''}
        </div>
        <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
          <a class="btn secondary" href="/recipes/${r.id}">Ver detalle</a>
          <button class="btn ${r.planned_to_cook ? 'secondary' : 'primary'}" data-plan="${r.id}">
            ${r.planned_to_cook ? 'Quitar de plan' : 'Quiero cocinarla'}
          </button>
        </div>
      </div>
    </article>`).join('');
}

function populateCategoryFilter(items) {
  if (!filterCategory) return;
  const cats = [...new Set(items.map(r => r.category).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
  const current = filterCategory.value;
  filterCategory.innerHTML = '<option value="">Todas las categorías</option>' +
    cats.map(c => `<option value="${esc(c)}" ${c === current ? 'selected' : ''}>${esc(c)}</option>`).join('');
}

async function loadRecipes() {
  if (!grid) return;
  const q = search?.value.trim() || '';
  const items = await api.listRecipes(q);
  window.__recipes = items;
  populateCategoryFilter(items);
  renderRecipes(items);
}

function toggleFilterBtn(btn) {
  const active = btn.dataset.active === 'true';
  btn.dataset.active = active ? 'false' : 'true';
  btn.classList.toggle('active', !active);
  renderRecipes(window.__recipes || []);
}

search?.addEventListener('input', () => {
  clearTimeout(window.__searchTimer);
  window.__searchTimer = setTimeout(loadRecipes, 200);
});

sortSelect?.addEventListener('change', () => renderRecipes(window.__recipes || []));
filterCategory?.addEventListener('change', () => renderRecipes(window.__recipes || []));
filterDifficulty?.addEventListener('change', () => renderRecipes(window.__recipes || []));
filterFavs?.addEventListener('click', () => toggleFilterBtn(filterFavs));
filterPlan?.addEventListener('click', () => toggleFilterBtn(filterPlan));

grid?.addEventListener('click', async (e) => {
  const fav = e.target.closest('[data-favorite]');
  const plan = e.target.closest('[data-plan]');
  if (fav) {
    try { await api.toggleFavorite(Number(fav.dataset.favorite)); await loadRecipes(); }
    catch { showToast('Error al actualizar favorito'); }
  }
  if (plan) {
    try { await api.togglePlan(Number(plan.dataset.plan)); await loadRecipes(); }
    catch { showToast('Error al actualizar plan'); }
  }
});

loadRecipes();
