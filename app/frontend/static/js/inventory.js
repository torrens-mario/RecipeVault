const tbody = document.getElementById('inventoryBody');
const form = document.getElementById('inventoryForm');
const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editInventoryForm');
const closeEditModalBtn = document.getElementById('closeEditModal');
const cancelEditModalBtn = document.getElementById('cancelEditModal');
const ICONS = {huevos:'🥚', huevo:'🥚', patata:'🥔', pasta:'🍝', sal:'🧂', pesto:'🌿', tomate:'🍅', queso:'🧀', leche:'🥛', pan:'🍞'};
function iconForIngredient(name){ const key = String(name || '').toLowerCase(); return ICONS[key] || '◻️'; }
function showToast(message){ let t=document.querySelector('.toast'); if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t);} t.textContent=message; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2500); }
function openEditModal(item){
  editForm.elements.id.value = item.id;
  editForm.elements.name.value = item.name;
  editForm.elements.quantity.value = item.quantity;
  editForm.elements.unit.value = item.unit;
  const thresholdValue = String(item.low_stock_threshold ?? 5);
  const thresholdSelect = editForm.elements.low_stock_threshold;
  if ([...thresholdSelect.options].some(o => o.value === thresholdValue)) { thresholdSelect.value = thresholdValue; } else { thresholdSelect.value = '5'; }
  editForm.elements.low_stock_unit.value = item.low_stock_unit || item.unit;
  editModal.classList.add('open');
  editModal.setAttribute('aria-hidden', 'false');
}
function closeEditModal(){
  editModal.classList.remove('open');
  editModal.setAttribute('aria-hidden', 'true');
}
closeEditModalBtn?.addEventListener('click', closeEditModal);
cancelEditModalBtn?.addEventListener('click', closeEditModal);
editModal?.addEventListener('click', (e) => { if (e.target === editModal) closeEditModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && editModal.classList.contains('open')) closeEditModal(); });
async function renderLowStock(){ const list = await api.lowStockItems(); let panel = document.getElementById('lowStockPanel'); if(!panel){ panel = document.createElement('div'); panel.id='lowStockPanel'; panel.className='low-stock-panel'; document.querySelector('.container').insertBefore(panel, document.querySelector('section')); } if(!list.length){ panel.innerHTML=''; return; } panel.innerHTML = list.map(i => `<div class="low-stock-card"><strong>${i.name}</strong><br><span class="muted">Quedan ${i.quantity} ${i.unit}. Conviene comprar antes de quedarte sin.</span></div>`).join(''); }
async function loadInventory(){ if (!tbody) return; const items = await api.listInventory(); window.__inventoryItems = items; tbody.innerHTML = items.map(i => `
  <tr>
    <td><div class="inventory-name"><div class="ingredient-photo">${iconForIngredient(i.name)}</div><div><strong>${i.name}</strong>${i.quantity <= (i.low_stock_threshold || 0) ? '<div class="low-stock-badge">Stock bajo</div>' : ''}</div></div></td>
    <td>${i.quantity}</td><td>${i.unit}</td><td>${i.low_stock_threshold ?? 5} ${i.low_stock_unit || i.unit}</td>
    <td style="text-align:right;"><button class="btn secondary" data-edit="${i.id}">Editar</button> <button class="btn secondary" data-del="${i.id}">Borrar</button></td>
  </tr>`).join(''); renderLowStock(); }
form?.addEventListener('submit', async (e) => { e.preventDefault(); const fd = new FormData(form); const payload = { name: fd.get('name'), quantity: Number(fd.get('quantity')||0), unit: fd.get('unit'), low_stock_threshold: Number(fd.get('low_stock_threshold')||5) }; await api.createInventoryItem(payload); form.reset(); showToast('Ingrediente añadido'); loadInventory(); });
editForm?.addEventListener('submit', async (e) => { e.preventDefault(); const fd = new FormData(editForm); const id = Number(fd.get('id')); const payload = { name: fd.get('name'), quantity: Number(fd.get('quantity')||0), unit: fd.get('unit'), low_stock_threshold: Number(fd.get('low_stock_threshold')||5) }; await api.updateInventoryItem(id, payload); closeEditModal(); showToast('Ingrediente actualizado'); loadInventory(); });
tbody?.addEventListener('click', async (e) => { const btn = e.target.closest('button'); if(!btn) return; const id = Number(btn.dataset.edit || btn.dataset.del); if(btn.dataset.del){ if(confirm('¿Borrar este ingrediente del inventario?')){ await api.deleteInventoryItem(id); showToast('Ingrediente eliminado'); loadInventory(); } } if(btn.dataset.edit){ const item = (window.__inventoryItems || []).find(x => x.id === id); if(item) openEditModal(item); } });
window.refreshInventoryView = loadInventory;
loadInventory();
