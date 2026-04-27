const form = document.getElementById('recipeForm');
function showToast(message){ let t=document.querySelector('.toast'); if(!t){t=document.createElement('div');t.className='toast';document.body.appendChild(t);} t.textContent=message; t.classList.add('show'); setTimeout(()=>t.classList.remove('show'),2500); }
form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const payload = {
    title: String(fd.get('title') || '').trim(),
    description: String(fd.get('description') || '').trim(),
    category: String(fd.get('category') || 'General').trim(),
    servings: Number(fd.get('servings') || 2),
    ingredients: String(fd.get('ingredients') || '').split('
').map(line => line.trim()).filter(Boolean).map(line => {
      const parts = line.split(' ');
      if(parts.length >= 3){ return { amount: `${parts[0]} ${parts[1]}`, name: parts.slice(2).join(' ') }; }
      if(parts.length === 2){ return { amount: parts[0], name: parts[1] }; }
      return { amount: '', name: line };
    }),
    steps: String(fd.get('steps') || '').split('
').map(s => s.trim()).filter(Boolean),
    tags: String(fd.get('tags') || '').split(',').map(t => t.trim()).filter(Boolean),
    favorite: false,
    image: ''
  };
  const created = await api.createRecipe(payload);
  showToast('Receta creada correctamente');
  window.location.href = `/recipes/${created.id}`;
});
