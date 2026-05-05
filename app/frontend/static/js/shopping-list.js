(async () => {
  const low = document.getElementById('lowStockList');
  const planned = document.getElementById('plannedRecipesList');
  const missing = document.getElementById('missingIngredientsList');

  const data = await api.shoppingList();

  low.innerHTML = data.low_stock.length
    ? data.low_stock.map(i => `
        <div class="shopping-item shopping-item-rich">
          <div class="ingredient-photo">${iconForIngredient(i.name)}</div>
          <div>
            <strong>${i.name}</strong>
            <span class="muted">Te quedan ${i.quantity} ${i.unit}. Aviso mínimo: ${i.low_stock_threshold} ${i.low_stock_unit || i.unit}</span>
          </div>
        </div>`).join('')
    : '<p class="muted">No hay ingredientes en aviso de mínimos.</p>';

  planned.innerHTML = data.planned_recipes.length
    ? data.planned_recipes.map(r => `
        <div class="shopping-item shopping-item-rich">
          <img class="shopping-thumb" src="${r.image || ''}" alt="Imagen de ${r.title}" loading="lazy" width="240" height="160">
          <div>
            <strong>${r.title}</strong>
            <span class="muted">${r.ingredients.length} ingredientes · ${r.servings} raciones</span>
          </div>
        </div>`).join('')
    : '<p class="muted">No has marcado ninguna receta con quiero cocinarla.</p>';

  missing.innerHTML = data.missing_for_planned.length
    ? data.missing_for_planned.map(i => `
        <div class="shopping-item shopping-item-rich">
          <div class="ingredient-photo">${iconForIngredient(i.name)}</div>
          <div>
            <strong>${i.name}</strong>
            <span class="muted">Faltan ${i.required} ${i.unit} para ${i.recipe}. Disponible: ${i.available}</span>
          </div>
        </div>`).join('')
    : '<p class="muted">Con tu inventario actual no te falta nada para las recetas planificadas.</p>';
})();
