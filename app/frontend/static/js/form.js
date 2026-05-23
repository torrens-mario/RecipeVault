const form = document.getElementById('recipeForm');
const isEditing = typeof window.EDIT_RECIPE_ID !== 'undefined' && window.EDIT_RECIPE_ID;

// ── Star rating ────────────────────────────────────────────────────────────────

function setStars(val) {
  document.getElementById('ratingHidden').value = val;
  document.querySelectorAll('.star-btn').forEach(s => {
    s.classList.toggle('active', Number(s.dataset.val) <= val);
  });
}

document.querySelectorAll('.star-btn').forEach(btn => {
  btn.addEventListener('click', () => setStars(Number(btn.dataset.val)));
  btn.addEventListener('mouseenter', () => {
    document.querySelectorAll('.star-btn').forEach(s => {
      s.classList.toggle('hover', Number(s.dataset.val) <= Number(btn.dataset.val));
    });
  });
  btn.addEventListener('mouseleave', () => {
    document.querySelectorAll('.star-btn').forEach(s => s.classList.remove('hover'));
  });
});

// ── Prefill ────────────────────────────────────────────────────────────────────

async function prefillForm() {
  if (!isEditing) return;
  const r = await api.getRecipe(window.EDIT_RECIPE_ID);
  form.elements.title.value = r.title || '';
  form.elements.description.value = r.description || '';
  form.elements.category.value = r.category || 'General';
  form.elements.servings.value = r.servings || 2;
  form.elements.difficulty.value = r.difficulty || 'Media';
  form.elements.prep_time.value = r.prep_time || 0;
  form.elements.cook_time.value = r.cook_time || 0;
  form.elements.notes.value = r.notes || '';
  form.elements.ingredients.value = (r.ingredients || []).map(i => `${i.amount} ${i.name}`).join('\n');
  form.elements.steps.value = (r.steps || []).join('\n');
  form.elements.tags.value = (r.tags || []).join(', ');
  setStars(r.rating || 0);
}

// ── Submit ─────────────────────────────────────────────────────────────────────

form?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const payload = {
    title: String(fd.get('title') || '').trim(),
    description: String(fd.get('description') || '').trim(),
    category: String(fd.get('category') || 'General').trim(),
    servings: Number(fd.get('servings') || 2),
    difficulty: String(fd.get('difficulty') || 'Media'),
    prep_time: Number(fd.get('prep_time') || 0),
    cook_time: Number(fd.get('cook_time') || 0),
    rating: Number(fd.get('rating') || 0),
    notes: String(fd.get('notes') || '').trim(),
    ingredients: String(fd.get('ingredients') || '').split('\n').map(line => line.trim()).filter(Boolean).map(line => {
      const parts = line.split(' ');
      if (parts.length >= 3) return { amount: `${parts[0]} ${parts[1]}`, name: parts.slice(2).join(' ') };
      if (parts.length === 2) return { amount: parts[0], name: parts[1] };
      return { amount: '', name: line };
    }),
    steps: String(fd.get('steps') || '').split('\n').map(s => s.trim()).filter(Boolean),
    tags: String(fd.get('tags') || '').split(',').map(t => t.trim()).filter(Boolean),
    favorite: false,
    image: ''
  };

  if (isEditing) {
    await api.updateRecipe(window.EDIT_RECIPE_ID, payload);
    showToast('Receta actualizada correctamente');
    window.location.href = `/recipes/${window.EDIT_RECIPE_ID}`;
  } else {
    const created = await api.createRecipe(payload);
    showToast('Receta creada correctamente');
    window.location.href = `/recipes/${created.id}`;
  }
});

prefillForm();
