(async () => {
  const container = document.getElementById('detail');
  if (!container) return;

  let r;
  try {
    const res = await fetch(`/api/shared/${window.RECIPE_ID}`);
    if (!res.ok) {
      container.innerHTML = '<p class="muted">Receta no encontrada o no está disponible públicamente.</p>';
      return;
    }
    r = await res.json();
  } catch {
    container.innerHTML = '<p class="muted">No se ha podido cargar la receta. Comprueba tu conexión.</p>';
    return;
  }

  function renderStars(rating) {
    return [1,2,3,4,5].map(i =>
      `<span class="star-display ${i <= rating ? 'active' : ''}">★</span>`
    ).join('');
  }

  function difficultyClass(d) {
    if (d === 'Fácil') return 'facil';
    if (d === 'Difícil') return 'dificil';
    return 'media';
  }

  const timeInfo = [];
  if (r.prep_time > 0) timeInfo.push(`⏱ ${r.prep_time} min prep`);
  if (r.cook_time > 0) timeInfo.push(`🍳 ${r.cook_time} min cocción`);

  container.innerHTML = `
    <article class="card detail-card">
      <div class="tag" style="width:max-content;margin-bottom:10px;">Receta compartida</div>
      ${r.image ? `<img class="detail-photo" src="${esc(r.image)}" alt="Imagen de ${esc(r.title)}" loading="lazy" width="1200" height="800" onerror="this.onerror=null;this.style.display='none'">` : ''}
      <h1 style="font-size:1.5rem;margin-bottom:4px;">${esc(r.title)}</h1>
      <div class="detail-meta">
        <span class="muted">${esc(r.category)} · ${r.servings} raciones</span>
        <span class="difficulty-badge difficulty-${difficultyClass(r.difficulty)}">${esc(r.difficulty || 'Media')}</span>
        ${r.rating > 0 ? `<span class="star-row">${renderStars(r.rating)}</span>` : ''}
      </div>
      ${timeInfo.length ? `<p class="time-info muted">${timeInfo.join(' · ')}</p>` : ''}
      <p style="margin-top:8px;">${esc(r.description || '')}</p>
      <h3 style="margin-top:14px;">Ingredientes</h3>
      <ul style="margin-left:18px;margin-top:6px;">
        ${r.ingredients.map(i => `<li>${esc(i.amount || '')} ${esc(i.name)}</li>`).join('')}
      </ul>
      <h3 style="margin-top:14px;">Pasos</h3>
      <ol style="margin-left:18px;margin-top:6px;">
        ${r.steps.map(s => `<li>${esc(s)}</li>`).join('')}
      </ol>
      ${r.notes ? `<h3 style="margin-top:14px;">Notas</h3><p style="margin-top:6px;font-style:italic;color:#7a5a46;">${esc(r.notes)}</p>` : ''}
      <div style="margin-top:20px;display:flex;gap:8px;flex-wrap:wrap;">
        <a class="btn primary" href="/register">Crear mi cuenta gratis</a>
        <a class="btn secondary" href="/">Ver más recetas</a>
      </div>
    </article>`;
})();
