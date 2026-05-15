function getToken() { return localStorage.getItem('token'); }
function getUsername() { return localStorage.getItem('username'); }

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('user_id');
  window.location.href = '/login';
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/login';
    return false;
  }
  return true;
}

function initNav() {
  if (!requireAuth()) return;
  const el = document.getElementById('navUser');
  if (el) el.textContent = getUsername() || '';
}

document.addEventListener('DOMContentLoaded', initNav);
