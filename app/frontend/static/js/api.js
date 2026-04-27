const api = {
  async listRecipes(q=''){ const url = q ? `/api/recipes?q=${encodeURIComponent(q)}` : '/api/recipes'; return fetch(url).then(r => r.json()); },
  async getRecipe(id){ return fetch(`/api/recipes/${id}`).then(r => r.json()); },
  async createRecipe(payload){ return fetch('/api/recipes', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r => r.json()); },
  async toggleFavorite(id){ return fetch(`/api/recipes/${id}/favorite`, {method:'POST'}).then(r => r.json()); },
  async togglePlan(id){ return fetch(`/api/recipes/${id}/plan`, {method:'POST'}).then(r => r.json()); },
  async listInventory(){ return fetch('/api/inventory').then(r => r.json()); },
  async lowStockItems(){ return fetch('/api/inventory/low-stock').then(r => r.json()); },
  async shoppingList(){ return fetch('/api/shopping-list').then(r => r.json()); },
  async createInventoryItem(payload){ return fetch('/api/inventory', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r => r.json()); },
  async updateInventoryItem(id, payload){ return fetch(`/api/inventory/${id}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)}).then(r => r.json()); },
  async deleteInventoryItem(id){ return fetch(`/api/inventory/${id}`, {method:'DELETE'}); },
  async cookRecipe(id){ return fetch(`/api/recipes/${id}/cook`, {method:'POST'}).then(r => r.json()); }
};
