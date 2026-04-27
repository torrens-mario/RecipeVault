(async function(){
  try {
    if (typeof api === 'undefined' || !api.shoppingList) return;
    const data = await api.shoppingList();
    const totalAlerts = (data.low_stock?.length || 0) + (data.missing_for_planned?.length || 0);
    document.querySelectorAll('#shoppingBadge').forEach(badge => {
      badge.textContent = totalAlerts;
      badge.style.display = totalAlerts ? 'inline-flex' : 'none';
    });
  } catch (e) {
    console.error('No se pudo actualizar el badge de compra', e);
  }
})();
