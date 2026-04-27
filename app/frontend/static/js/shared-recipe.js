(async () => {
  const container = document.getElementById('detail');
  if (!container) return;
  const r = await api.getRecipe(window.RECIPE_ID);
  container.innerHTML = `
    <article class="card">
      <div class="tag" style="width:max-content;">Receta compartida</div>
      <h1 style="font-size:1.5rem;">${r.title}</h1>
      <p class="muted">${r.category} · ${r.servings} raciones</p>
      <p>${r.description || ''}</p>
      <h3 style="margin-top:14px;">Ingredientes</h3>
      <ul style="margin-left:18px;margin-top:6px;">${r.ingredients.map(i => `<li>${i.amount || ''} ${i.name}</li>`).join('')}</ul>
      <h3 style="margin-top:14px;">Pasos</h3>
      <ol style="margin-left:18px;margin-top:6px;">${r.steps.map(s => `<li>${s}</li>`).join('')}</ol>
    </article>`;
})();
