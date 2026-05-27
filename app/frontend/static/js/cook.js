(function () {
  function bind() {
    const btn = document.getElementById('cookBtn');
    const output = document.getElementById('cookResult');
    if (!btn || !output || btn.dataset.bound) return;
    btn.dataset.bound = '1';

    btn.addEventListener('click', async () => {
      btn.disabled = true;
      output.textContent = 'Cocinando la receta y actualizando inventario...';
      try {
        const res = await api.cookRecipe(window.RECIPE_ID);
        if (res.success) {
          const low = (res.low_stock || []).map(i => `${i.name} (${i.quantity} ${i.unit})`).join(', ');
          output.textContent = low
            ? `Inventario actualizado. Atención: stock bajo en ${low}.`
            : 'Inventario actualizado correctamente.';
          if (window.refreshInventoryView) window.refreshInventoryView();
          showToast(low ? 'Inventario actualizado con avisos de stock bajo' : 'Inventario actualizado');
        } else {
          const missing = (res.missing || [])
            .map(m => `${m.required} ${m.unit} ${m.name} (disponible: ${m.available})`)
            .join('; ');
          output.textContent = 'No hay stock suficiente para cocinar esta receta. Faltan: ' + missing;
          showToast('Faltan ingredientes en el inventario');
        }
      } catch (err) {
        console.error(err);
        output.textContent = 'Ha ocurrido un error al cocinar la receta.';
        showToast('Error al cocinar la receta');
      } finally {
        btn.disabled = false;
      }
    });
  }

  let attempts = 0;
  const interval = setInterval(() => {
    bind();
    const btn = document.getElementById('cookBtn');
    if (btn || ++attempts >= 20) clearInterval(interval);
  }, 200);
})();
