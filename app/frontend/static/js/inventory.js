const tbody = document.getElementById('inventoryBody');
const invSearch = document.getElementById('invSearch');
const invCount = document.getElementById('invCount');
const invEmpty = document.getElementById('invEmpty');

// ── Add modal ──────────────────────────────────────────────────────────────────

const addModal = document.getElementById('addModal');
const addForm = document.getElementById('inventoryForm');

function openAddModal() {
  addForm.reset();
  addModal.classList.add('open');
  addModal.setAttribute('aria-hidden', 'false');
  document.getElementById('addName').focus();
}
function closeAddModal() {
  addModal.classList.remove('open');
  addModal.setAttribute('aria-hidden', 'true');
}

document.getElementById('openAddModal')?.addEventListener('click', openAddModal);
document.getElementById('closeAddModal')?.addEventListener('click', closeAddModal);
document.getElementById('cancelAddModal')?.addEventListener('click', closeAddModal);
addModal?.addEventListener('click', (e) => { if (e.target === addModal) closeAddModal(); });

// ── Edit modal ─────────────────────────────────────────────────────────────────

const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editInventoryForm');

function openEditModal(item) {
  editForm.elements.id.value = item.id;
  editForm.elements.name.value = item.name;
  editForm.elements.quantity.value = item.quantity;
  editForm.elements.unit.value = item.unit;
  editForm.elements.low_stock_threshold.value = item.low_stock_threshold ?? 5;
  editForm.elements.low_stock_unit.value = item.low_stock_unit || item.unit;
  editModal.classList.add('open');
  editModal.setAttribute('aria-hidden', 'false');
}
function closeEditModal() {
  editModal.classList.remove('open');
  editModal.setAttribute('aria-hidden', 'true');
}

document.getElementById('closeEditModal')?.addEventListener('click', closeEditModal);
document.getElementById('cancelEditModal')?.addEventListener('click', closeEditModal);
editModal?.addEventListener('click', (e) => { if (e.target === editModal) closeEditModal(); });

// ── Low stock panel ────────────────────────────────────────────────────────────

async function renderLowStock() {
  const list = await api.lowStockItems();
  let panel = document.getElementById('lowStockPanel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'lowStockPanel';
    panel.className = 'low-stock-panel';
    document.querySelector('.container').insertBefore(panel, document.querySelector('.inv-toolbar'));
  }
  if (!list.length) { panel.innerHTML = ''; return; }
  panel.innerHTML = `<div style="width:100%;margin-bottom:4px;font-weight:600;font-size:.9rem;color:#8a5200;">⚠️ Stock bajo</div>` +
    list.map(i => `
      <div class="low-stock-card">
        <strong>${iconForIngredient(i.name)} ${i.name}</strong>
        <div class="muted" style="font-size:.82rem;margin-top:2px;">Quedan ${i.quantity} ${i.unit}</div>
      </div>`).join('');
}

// ── Render table ───────────────────────────────────────────────────────────────

function isLow(item) {
  return item.quantity <= (item.low_stock_threshold || 0);
}

function renderTable(items) {
  const q = (invSearch?.value || '').toLowerCase().trim();
  const filtered = q ? items.filter(i => i.name.toLowerCase().includes(q)) : items;

  if (invCount) invCount.textContent = `${filtered.length} ingrediente${filtered.length !== 1 ? 's' : ''}`;

  if (!filtered.length) {
    tbody.innerHTML = '';
    if (invEmpty) invEmpty.style.display = '';
    return;
  }
  if (invEmpty) invEmpty.style.display = 'none';

  tbody.innerHTML = filtered.map(i => `
    <tr class="${isLow(i) ? 'inv-row-low' : ''}">
      <td>
        <div class="inventory-name">
          <div class="ingredient-photo">${iconForIngredient(i.name)}</div>
          <div>
            <strong>${i.name}</strong>
            ${isLow(i) ? '<div class="low-stock-badge">⚠ Stock bajo</div>' : ''}
          </div>
        </div>
      </td>
      <td>
        <span class="inv-qty ${isLow(i) ? 'inv-qty-low' : ''}">${i.quantity} ${i.unit}</span>
      </td>
      <td class="muted" style="font-size:.85rem;">${i.low_stock_threshold ?? 5} ${i.low_stock_unit || i.unit}</td>
      <td style="text-align:right;white-space:nowrap;">
        <button class="btn secondary" style="padding:6px 12px;font-size:.85rem;" data-edit="${i.id}">Editar</button>
        <button class="btn secondary" style="padding:6px 12px;font-size:.85rem;color:#c9435b;border-color:#f2bbc4;" data-del="${i.id}">Borrar</button>
      </td>
    </tr>`).join('');
}

async function loadInventory() {
  if (!tbody) return;
  const items = await api.listInventory();
  window.__inventoryItems = items;
  renderTable(items);
  renderLowStock();
}

// ── Events ─────────────────────────────────────────────────────────────────────

invSearch?.addEventListener('input', () => renderTable(window.__inventoryItems || []));

addForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = addForm.querySelector('[type="submit"]');
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Añadiendo...';
  const fd = new FormData(addForm);
  const payload = {
    name: fd.get('name'),
    quantity: Number(fd.get('quantity') || 0),
    unit: fd.get('unit'),
    low_stock_threshold: Number(fd.get('low_stock_threshold') || 5),
    low_stock_unit: fd.get('low_stock_unit') || fd.get('unit'),
  };
  try {
    await api.createInventoryItem(payload);
    closeAddModal();
    showToast('Ingrediente añadido');
    loadInventory();
  } catch {
    showToast('Error al añadir el ingrediente. Inténtalo de nuevo.');
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
});

editForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = editForm.querySelector('[type="submit"]');
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Guardando...';
  const fd = new FormData(editForm);
  const id = Number(fd.get('id'));
  const payload = {
    name: fd.get('name'),
    quantity: Number(fd.get('quantity') || 0),
    unit: fd.get('unit'),
    low_stock_threshold: Number(fd.get('low_stock_threshold') || 5),
    low_stock_unit: fd.get('low_stock_unit') || fd.get('unit'),
  };
  try {
    await api.updateInventoryItem(id, payload);
    closeEditModal();
    showToast('Ingrediente actualizado');
    loadInventory();
  } catch {
    showToast('Error al actualizar el ingrediente. Inténtalo de nuevo.');
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
});

const deleteItemModal = document.getElementById('confirmDeleteItemModal');
let _pendingDeleteId = null;

function openConfirmDeleteItem(id) {
  _pendingDeleteId = id;
  deleteItemModal.classList.add('open');
  deleteItemModal.setAttribute('aria-hidden', 'false');
}
function closeConfirmDeleteItem() {
  _pendingDeleteId = null;
  deleteItemModal.classList.remove('open');
  deleteItemModal.setAttribute('aria-hidden', 'true');
}

document.getElementById('confirmDeleteItemClose')?.addEventListener('click', closeConfirmDeleteItem);
document.getElementById('confirmDeleteItemCancel')?.addEventListener('click', closeConfirmDeleteItem);
deleteItemModal?.addEventListener('click', (e) => { if (e.target === deleteItemModal) closeConfirmDeleteItem(); });
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { closeAddModal(); closeEditModal(); closeConfirmDeleteItem(); }
});

document.getElementById('confirmDeleteItemOk')?.addEventListener('click', async () => {
  const id = _pendingDeleteId;
  closeConfirmDeleteItem();
  try {
    await api.deleteInventoryItem(id);
    showToast('Ingrediente eliminado');
    loadInventory();
  } catch {
    showToast('Error al eliminar el ingrediente');
  }
});

tbody?.addEventListener('click', async (e) => {
  const btn = e.target.closest('button');
  if (!btn) return;
  const id = Number(btn.dataset.edit || btn.dataset.del);
  if (btn.dataset.del) openConfirmDeleteItem(id);
  if (btn.dataset.edit) {
    const item = (window.__inventoryItems || []).find(x => x.id === id);
    if (item) openEditModal(item);
  }
});

window.refreshInventoryView = loadInventory;
loadInventory();
