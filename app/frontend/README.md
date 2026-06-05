# RecipeVault — Frontend (`app/frontend/`)

Interfaz de usuario construida con **HTML, CSS y JavaScript vanilla**. Las páginas se renderizan en el servidor con **Jinja2** y el JS del cliente se comunica con la API REST del backend.

---

## Estructura de archivos

```
frontend/
├── templates/              # Páginas HTML renderizadas por Jinja2 en el servidor
│   ├── base.html           # Layout base: topbar, nav, scripts comunes
│   ├── index.html          # Listado de recetas con filtros y búsqueda
│   ├── recipe-detail.html  # Detalle de una receta
│   ├── recipe-form.html    # Formulario crear/editar receta
│   ├── inventory.html      # Gestión del inventario de ingredientes
│   ├── shopping-list.html  # Lista de la compra automática
│   ├── shared-recipe.html  # Vista pública de receta (sin login)
│   ├── login.html          # Página de inicio de sesión
│   └── register.html       # Página de registro
└── static/
    ├── css/
    │   └── style.css       # Todos los estilos de la aplicación
    └── js/
        ├── api.js          # Cliente HTTP: wrapper de fetch con autenticación
        ├── app.js          # Lógica del listado de recetas (filtros, orden, render)
        ├── detail.js       # Lógica del detalle de receta
        ├── form.js         # Lógica del formulario crear/editar receta
        ├── inventory.js    # Lógica de la página de inventario
        ├── shopping-list.js# Lógica de la lista de la compra
        ├── cook.js         # Botón "Cocinar" en el detalle de receta
        ├── shared-recipe.js# Carga y renderiza la vista pública (sin auth)
        ├── auth.js         # Gestión del token JWT en localStorage
        ├── utils.js        # Utilidades: esc(), showToast(), iconForIngredient()
        └── nav-badge.js    # Badge numérico en el icono de la lista de la compra
```

---

## Templates (Jinja2)

### `base.html`
Layout compartido por todas las páginas autenticadas. Incluye:
- **Topbar** con el logo y la navegación principal (Mis recetas, Inventario, Lista de la compra, Nueva receta, usuario/logout).
- **Badge de compra** (`#shoppingBadge`): número de alertas de stock bajo + ingredientes que faltan, actualizado por `nav-badge.js` en cada carga.
- **Scripts base** que se cargan en todas las páginas: `auth.js`, `api.js`, `utils.js` y `nav-badge.js`. Cada página puede añadir sus propios scripts con el bloque `{% block scripts %}`.
- La variable `active_page` pasada desde el backend controla qué enlace del nav tiene la clase `active`.

### `login.html` y `register.html`
Páginas independientes con su propio HTML mínimo. El JS está inline: llaman directamente a `/api/auth/login` o `/api/auth/register`, guardan el token en `localStorage` y redirigen a `/`.

### `index.html`
Extiende `base.html`. Renderiza el esqueleto de la página. El contenido de las tarjetas de recetas lo genera `app.js` en el cliente.

### `recipe-detail.html`
Extiende `base.html`. Pasa `window.RECIPE_ID` al cliente y carga `detail.js` y `cook.js`. El contenido completo lo genera `detail.js`.

### `recipe-form.html`
Extiende `base.html`. Si la variable `edit_recipe_id` está definida, el template inyecta `window.EDIT_RECIPE_ID` y `form.js` precarga los datos de la receta para editar.

### `inventory.html`
Extiende `base.html`. Contiene el HTML estático de la tabla y los tres modales (añadir, editar, confirmar borrado). `inventory.js` gestiona toda la interactividad.

### `shopping-list.html`
Extiende `base.html`. Tres contenedores vacíos que `shopping-list.js` rellena con los datos de la API.

### `shared-recipe.html`
Página independiente. Accesible sin login. `shared-recipe.js` carga la receta desde `/api/shared/{id}` y la renderiza.

---

## JavaScript

### `auth.js`
Gestiona la sesión del usuario en el cliente:

- `getToken()` / `getUsername()` — leen de `localStorage`.
- `logout()` — borra `token`, `username` y `user_id` de `localStorage` y redirige a `/login`.
- `requireAuth()` — comprueba si hay token; si no, redirige a `/login`. Se llama al cargar cada página protegida.
- `initNav()` — escribe el nombre del usuario en el elemento `#navUser` del topbar.

### `api.js`
Wrapper de `fetch` con autenticación automática. Expone el objeto global `api` con métodos para cada recurso:

- `_authHeaders()` — añade `Authorization: Bearer <token>` a todas las peticiones.
- `_fetch()` — intercepta respuestas 401 (token expirado): borra la sesión y redirige a `/login` automáticamente.
- Métodos disponibles: `listRecipes`, `getRecipe`, `createRecipe`, `updateRecipe`, `deleteRecipe`, `toggleFavorite`, `togglePlan`, `togglePublic`, `cookRecipe`, `listInventory`, `lowStockItems`, `shoppingList`, `createInventoryItem`, `updateInventoryItem`, `deleteInventoryItem`.

### `app.js`
Lógica de la página principal (`/`):

- `loadRecipes()` — llama a `api.listRecipes()` con el texto de búsqueda actual y almacena el resultado en `window.__recipes`.
- `applyFilters()` — filtra el array por categoría, dificultad, favoritas y planificadas. Los filtros de categoría y dificultad son selects; los de favoritas y planificadas son botones toggle con `data-active`.
- `sortRecipes()` — ordena por nombre, favoritas, número de ingredientes, planificadas o valoración.
- `renderRecipes()` — genera el HTML de las tarjetas y lo inyecta en `#recipes`. Usa `esc()` para sanear todos los datos antes de insertarlos en el DOM.
- `populateCategoryFilter()` — construye dinámicamente las opciones del select de categoría a partir de las recetas cargadas.
- La búsqueda tiene un debounce de 200ms para no llamar a la API en cada pulsación de teclado.

### `detail.js`
Lógica del detalle de receta:

- Carga la receta con `api.getRecipe(window.RECIPE_ID)` y renderiza todo el HTML en `#detail`.
- Botones: favorito, plan, visibilidad pública/privada, copiar enlace compartible, eliminar (con modal de confirmación), editar (enlace), cambiar imagen (upload).
- **Subida de imagen:** valida tipo y tamaño en el cliente antes de enviar, luego hace un `fetch` a `/api/recipes/{id}/image` con `FormData`. Actualiza la imagen en la página sin recargar.
- Modal de confirmación para borrar: evita borrados accidentales.

### `form.js`
Lógica del formulario de crear/editar receta:

- **Prefill:** si `window.EDIT_RECIPE_ID` está definido, carga la receta con `api.getRecipe()` y rellena todos los campos del formulario.
- **Estrellas de valoración:** sistema de selección interactiva con hover. El valor se guarda en un `<input type="hidden">`.
- **Parseo de ingredientes:** cada línea del textarea se parsea como `CANTIDAD UNIDAD NOMBRE` (ej. `200 g Pasta`). Si solo hay dos palabras, la primera es la cantidad y la segunda el nombre.
- **Envío:** crea o actualiza la receta y redirige al detalle.

### `inventory.js`
Lógica de la página de inventario:

- `loadInventory()` — carga el inventario y los items de stock bajo en paralelo con `Promise.all`. Mantiene un `Set` de IDs en stock bajo para aplicar estilos sin lógica de comparación en el cliente.
- `renderTable()` — filtra por la búsqueda local (sin llamada a la API) y renderiza la tabla.
- `renderLowStockItems()` — muestra el panel de avisos de stock bajo sobre la tabla.
- Tres modales: añadir ingrediente, editar ingrediente, confirmar borrado. Se abren/cierran con clases CSS y atributo `aria-hidden`.
- Cierre de modales con Escape o clic en el backdrop.

### `shopping-list.js`
Carga `/api/shopping-list` y rellena tres secciones:
- **Stock bajo:** ingredientes por debajo del umbral mínimo.
- **Recetas planificadas:** recetas marcadas como "quiero cocinarla".
- **Ingredientes que faltan:** lo que falta en el inventario para cocinar las recetas planificadas.

### `cook.js`
Botón "Cocinar" en el detalle de receta. Llama a `api.cookRecipe()` y muestra el resultado: éxito con posibles avisos de stock bajo, o lista de ingredientes que faltan. Usa un polling con `setInterval` para enlazarse al botón `#cookBtn` aunque el DOM se cargue después que el script.

### `shared-recipe.js`
Versión simplificada de `detail.js` para la vista pública. No usa `api.js` (no hay autenticación); hace un `fetch` directo a `/api/shared/{id}`. Si la receta es privada o no existe, muestra un mensaje de error.

### `utils.js`
Funciones de utilidad globales disponibles en todas las páginas:

- `esc(s)` — escapa HTML (`&`, `<`, `>`, `"`) para prevenir XSS. Se usa en todos los sitios donde se insertan datos de usuario en el DOM.
- `showToast(message)` — muestra una notificación flotante en la esquina inferior derecha que desaparece a los 2,5 segundos.
- `iconForIngredient(name)` — devuelve un emoji representativo del ingrediente buscando por nombre en un diccionario de ~50 entradas.

### `nav-badge.js`
IIFE que se ejecuta en todas las páginas (cargado en `base.html`). Llama a `api.shoppingList()` y actualiza el badge `#shoppingBadge` con el total de alertas (stock bajo + ingredientes que faltan). Si el total es 0, oculta el badge.

---

## Flujo de autenticación en el cliente

```
Usuario abre la app
       │
       ▼
¿Hay token en localStorage?
  No → redirige a /login
  Sí → initNav() muestra el username en el topbar
       │
       ▼
Cada llamada a api.js añade Authorization: Bearer <token>
       │
       ▼
Si el servidor devuelve 401 (token expirado)
  → _fetch() borra el token y redirige a /login automáticamente
```

---

## Estilos (`style.css`)

Un único archivo CSS con ~300 líneas. No usa ningún framework. Los bloques principales son:

| Selector / bloque | Qué define |
|---|---|
| `.topbar` | Barra de navegación fija con blur |
| `.card` / `.recipe-card` | Tarjetas de recetas con sombra y bordes redondeados |
| `.btn.primary` / `.btn.secondary` | Botones de acción con hover |
| `.modal-backdrop` / `.modal-card` | Sistema de modales accesibles |
| `.inventory-table` | Tabla del inventario con estilos responsive |
| `.difficulty-badge` | Badge de dificultad con colores: verde (Fácil), amarillo (Media), rojo (Difícil) |
| `.star-display` / `.star-btn` | Estrellas de valoración (visualización y selector interactivo) |
| `.toast` | Notificación flotante con transición de opacidad |
| `.auth-card` | Tarjeta centrada para login y registro |
| `@media (max-width: 720px)` | Adaptaciones para móvil: tabla de inventario en modo bloque, nav con solo iconos |