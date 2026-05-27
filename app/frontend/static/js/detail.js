(async () => {
  const container = document.getElementById('detail');
  if (!container) return;

  const r = await api.getRecipe(window.RECIPE_ID);
  const shareUrl = `${window.location.origin}/shared/${r.id}`;

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
      <img class="detail-photo" src="${r.image || ''}" alt="Imagen de ${r.title}" loading="lazy" width="1200" height="800">
      <h1 style="font-size:1.5rem;margin-bottom:4px;">${r.title}</h1>
      <div class="detail-meta">
        <span class="muted">${r.category} · ${r.servings} raciones</span>
        <span class="difficulty-badge difficulty-${difficultyClass(r.difficulty)}">${r.difficulty || 'Media'}</span>
        ${r.rating > 0 ? `<span class="star-row">${renderStars(r.rating)}</span>` : ''}
      </div>
      ${timeInfo.length ? `<p class="time-info muted">${timeInfo.join(' · ')}</p>` : ''}
      <p style="margin-top:8px;">${r.description || ''}</p>
      <h3 style="margin-top:14px;">Ingredientes</h3>
      <ul style="margin-left:18px;margin-top:6px;">
        ${r.ingredients.map(i => `<li>${i.amount || ''} ${i.name}</li>`).join('')}
      </ul>
      <h3 style="margin-top:14px;">Pasos</h3>
      <ol style="margin-left:18px;margin-top:6px;">
        ${r.steps.map(s => `<li>${s}</li>`).join('')}
      </ol>
      ${r.notes ? `<h3 style="margin-top:14px;">Notas</h3><p style="margin-top:6px;font-style:italic;color:#7a5a46;">${r.notes}</p>` : ''}
      <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
        <button class="btn primary" id="cookBtn">Cocinar (actualizar inventario)</button>
        <button class="btn secondary" id="favoriteBtn">${r.favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'}</button>
        <button class="btn ${r.planned_to_cook ? 'secondary' : 'primary'}" id="planBtn">
          ${r.planned_to_cook ? 'Quitar de quiero cocinar' : 'Quiero cocinarla'}
        </button>
        <button class="btn secondary" id="publicBtn">${r.is_public ? '🔓 Hacer privada' : '🔒 Hacer pública'}</button>
        ${r.is_public ? `<button class="btn secondary" id="shareBtn">Copiar enlace</button>` : ''}
        <label class="btn secondary" id="imageUploadLabel" style="cursor:pointer;">
          📷 Cambiar imagen
          <input type="file" id="imageInput" accept="image/jpeg,image/png,image/webp" style="display:none;">
        </label>
        <a class="btn secondary" href="/recipes/${r.id}/edit">Editar receta</a>
        <button class="btn secondary" id="deleteBtn" style="color:#c9435b;border-color:#f2bbc4;">Eliminar receta</button>
      </div>
      <div id="cookResult" class="muted" style="margin-top:10px;"></div>
      ${r.is_public ? `<div class="muted" style="margin-top:6px;word-break:break-all;">Enlace compartible: ${shareUrl}</div>` : '<div class="muted" style="margin-top:6px;">🔒 Esta receta es privada. Solo tú puedes verla.</div>'}
    </article>`;

  document.getElementById('shareBtn')?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      showToast('Enlace copiado al portapapeles');
    } catch (e) {
      alert('No se pudo copiar el enlace. URL: ' + shareUrl);
    }
  });

  document.getElementById('publicBtn')?.addEventListener('click', async () => {
    await api.togglePublic(r.id);
    location.reload();
  });

  document.getElementById('favoriteBtn')?.addEventListener('click', async () => {
    await api.toggleFavorite(r.id);
    location.reload();
  });

  document.getElementById('planBtn')?.addEventListener('click', async () => {
    await api.togglePlan(r.id);
    location.reload();
  });

  document.getElementById('imageInput')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowed = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowed.includes(file.type)) {
      showToast('Solo se permiten imágenes JPEG, PNG o WebP');
      e.target.value = '';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showToast('La imagen es demasiado grande (máximo 5 MB)');
      e.target.value = '';
      return;
    }

    const label = document.getElementById('imageUploadLabel');
    label.style.pointerEvents = 'none';
    label.style.opacity = '0.6';
    label.childNodes[0].textContent = ' Subiendo...';

    try {
      const formData = new FormData();
      formData.append('file', file);
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/recipes/${window.RECIPE_ID}/image`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        showToast(err.detail || 'Error al subir la imagen');
        return;
      }
      const data = await res.json();
      document.querySelector('.detail-photo').src = data.image_url;
      showToast('Imagen actualizada');
    } catch {
      showToast('Error de red al subir la imagen');
    } finally {
      label.style.pointerEvents = '';
      label.style.opacity = '';
      label.childNodes[0].textContent = ' 📷 Cambiar imagen';
      e.target.value = '';
    }
  });

  document.getElementById('deleteBtn')?.addEventListener('click', async () => {
    if (confirm('¿Seguro que quieres eliminar esta receta? Esta acción no se puede deshacer.')) {
      await api.deleteRecipe(r.id);
      showToast('Receta eliminada');
      window.location.href = '/';
    }
  });
})();
