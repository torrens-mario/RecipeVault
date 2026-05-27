(async () => {
  const low = document.getElementById('lowStockList');
  const planned = document.getElementById('plannedRecipesList');
  const missing = document.getElementById('missingIngredientsList');

  const loadingMsg = '<p class="muted">Cargando...</p>';
  if (low) low.innerHTML = loadingMsg;
  if (planned) planned.innerHTML = loadingMsg;
  if (missing) missing.innerHTML = loadingMsg;

  let data;
  try {
    data = await api.shoppingList();
  } catch {
    const msg = '<p class="muted">No se ha podido cargar la lista. Inténtalo de nuevo.</p>';
    if (low) low.innerHTML = msg;
    if (planned) planned.innerHTML = '';
    if (missing) missing.innerHTML = '';
    return;
  }

  if (!data) {
    const msg = '<p class="muted">No se ha podido cargar la lista. Inténtalo de nuevo.</p>';
    if (low) low.innerHTML = msg;
    if (planned) planned.innerHTML = '';
    if (missing) missing.innerHTML = '';
    return;
  }

  low.innerHTML = data.low_stock.length
    ? data.low_stock.map(i => `
        <div class="shopping-item shopping-item-rich">
          <div class="ingredient-photo">${iconForIngredient(i.name)}</div>
          <div>
            <strong>${esc(i.name)}</strong>
            <span class="muted">Te quedan ${i.quantity} ${esc(i.unit)}. Aviso mínimo: ${i.low_stock_threshold} ${esc(i.low_stock_unit || i.unit)}</span>
          </div>
        </div>`).join('')
    : '<p class="muted">No hay ingredientes en aviso de mínimos.</p>';

  planned.innerHTML = data.planned_recipes.length
    ? data.planned_recipes.map(r => `
        <div class="shopping-item shopping-item-rich">
          ${r.image ? `<img class="shopping-thumb" src="${esc(r.image)}" alt="Imagen de ${esc(r.title)}" loading="lazy" width="240" height="160" onerror="this.onerror=null;this.style.display='none'">` : ''}
          <div>
            <strong>${esc(r.title)}</strong>
            <span class="muted">${r.ingredients.length} ingredientes · ${r.servings} raciones</span>
          </div>
        </div>`).join('')
    : '<p class="muted">No has marcado ninguna receta con quiero cocinarla.</p>';

  missing.innerHTML = data.missing_for_planned.length
    ? data.missing_for_planned.map(i => `
        <div class="shopping-item shopping-item-rich">
          <div class="ingredient-photo">${iconForIngredient(i.name)}</div>
          <div>
            <strong>${esc(i.name)}</strong>
            <span class="muted">Faltan ${i.required} ${esc(i.unit)} para ${esc(i.recipe)}. Disponible: ${i.available}</span>
          </div>
        </div>`).join('')
    : '<p class="muted">Con tu inventario actual no te falta nada para las recetas planificadas.</p>';
})();
