function _authHeaders(extra = {}) {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}`, ...extra } : { ...extra };
}

async function _fetch(url, opts = {}) {
  const res = await fetch(url, opts);
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    window.location.href = '/login';
    return null;
  }
  return res;
}

const api = {
  async listRecipes(q = '') {
    const url = q ? `/api/recipes?q=${encodeURIComponent(q)}` : '/api/recipes';
    const res = await _fetch(url, { headers: _authHeaders() });
    return res ? res.json() : [];
  },

  async getRecipe(id) {
    const res = await _fetch(`/api/recipes/${id}`, { headers: _authHeaders() });
    return res ? res.json() : null;
  },

  async createRecipe(payload) {
    const res = await _fetch('/api/recipes', {
      method: 'POST',
      headers: _authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res || !res.ok) throw new Error('Error al crear la receta');
    return res.json();
  },

  async updateRecipe(id, payload) {
    const res = await _fetch(`/api/recipes/${id}`, {
      method: 'PUT',
      headers: _authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res || !res.ok) throw new Error('Error al actualizar la receta');
    return res.json();
  },

  async uploadRecipeImage(id, file) {
    const form = new FormData();
    form.append('file', file);
    const res = await _fetch(`/api/recipes/${id}/image`, {
      method: 'POST',
      headers: _authHeaders(),
      body: form
    });
    return res ? res.json() : null;
  },

  async toggleFavorite(id) {
    const res = await _fetch(`/api/recipes/${id}/favorite`, { method: 'POST', headers: _authHeaders() });
    if (!res || !res.ok) throw new Error('Error al actualizar favorito');
    return res.json();
  },

  async togglePlan(id) {
    const res = await _fetch(`/api/recipes/${id}/plan`, { method: 'POST', headers: _authHeaders() });
    if (!res || !res.ok) throw new Error('Error al actualizar plan');
    return res.json();
  },

  async deleteRecipe(id) {
    return _fetch(`/api/recipes/${id}`, { method: 'DELETE', headers: _authHeaders() });
  },

  async listInventory() {
    const res = await _fetch('/api/inventory', { headers: _authHeaders() });
    return res ? res.json() : [];
  },

  async lowStockItems() {
    const res = await _fetch('/api/inventory/low-stock', { headers: _authHeaders() });
    return res ? res.json() : [];
  },

  async shoppingList() {
    const res = await _fetch('/api/shopping-list', { headers: _authHeaders() });
    return res ? res.json() : null;
  },

  async createInventoryItem(payload) {
    const res = await _fetch('/api/inventory', {
      method: 'POST',
      headers: _authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res || !res.ok) throw new Error('Error al crear el ingrediente');
    return res.json();
  },

  async updateInventoryItem(id, payload) {
    const res = await _fetch(`/api/inventory/${id}`, {
      method: 'PUT',
      headers: _authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload)
    });
    if (!res || !res.ok) throw new Error('Error al actualizar el ingrediente');
    return res.json();
  },

  async deleteInventoryItem(id) {
    return _fetch(`/api/inventory/${id}`, { method: 'DELETE', headers: _authHeaders() });
  },

  async cookRecipe(id) {
    const res = await _fetch(`/api/recipes/${id}/cook`, { method: 'POST', headers: _authHeaders() });
    return res ? res.json() : null;
  },

  async togglePublic(id) {
    const res = await _fetch(`/api/recipes/${id}/public`, { method: 'POST', headers: _authHeaders() });
    if (!res || !res.ok) throw new Error('Error al cambiar visibilidad');
    return res.json();
  }
};
