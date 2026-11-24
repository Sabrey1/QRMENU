# Sabrey menu frontend

The default template displays a published shop menu from the backend. It supports category navigation, item search, prices, images, and loading and error states.

The language selector switches the interface between English and Khmer and remembers the selection in the browser. Edit `src/locals/en.json` or `src/locals/km.json` to change interface translations. Shop, category, and item names come from the API and are displayed as entered; translating them requires multilingual menu data in the backend.

Frontend API requests are centralized in `src/services/api-services.js`. It provides helpers for public menus, registration, login, tenant listing, template updates, and QR codes; `apiRequest` supports other endpoints. `VITE_API_ORIGIN` optionally points requests to a separately hosted backend; otherwise requests use the same-origin `/v1/api` path.

Open Settings to select Light, Dark, or System appearance. System follows the device setting, and the selection is saved in the browser for all templates.

`src/view/Home/home.vue` loads the public menu and selects a component using its `display_template` field. Available values are `default_template`, `cosmetic_template`, and `cambodia_template`. Register additional templates in the `templates` map in that file. Templates receive `menu`, `loading`, `error`, `needsShop`, and `isLocal` props and can emit `retry`, `choose-shop`, and `open-shop` (with a slug). Unknown or missing template names fall back to `default_template`.

To change a shop's template, open the header settings, choose Settings, sign in as the shop owner or admin, select a template, and save. The choice is stored on the tenant and shown to all visitors. The sign-in token stays in memory for the current page session; a reload requires signing in again. Sign-in requires HTTPS except on localhost.

After signing in under Settings, use **Show menu QR code** to display or download the shop's QR code. It encodes the tenant's public `https://<slug>.sabrey.xyz` URL; the public hostname must be deployed and configured before customers can use it.

## Admin pages

Sign in at `/login` or open `/admin/banner` to reach the admin panel. The sidebar contains read-only lists for banners, categories, menu items, shops, and shop members, plus the signed-in account profile. Select a shop in the top bar to change the data shown in shop-specific lists. The members endpoint is available only to shop owners; the API does not provide a list of all users.

The admin access token is kept in session storage for the current browser tab and is validated with the API when the session is restored. Signing out clears it. For static hosting, configure SPA fallback to `index.html` for `/login` and `/admin/*`; the optional FastAPI frontend hosting handles these paths itself.

## Run locally

Start the backend (see the backend README). Set `API_PROXY_TARGET` in `frontend/.env` to its origin, for example `http://127.0.0.1:8000`. You can copy `.env.example` to `.env` if you do not have one. Restart Vite after changing the value, then in this directory run:

```powershell
npm install
npm run dev
```

Open the URL printed by Vite, for example `http://localhost:5173/`, and enter the slug of an existing published shop when prompted. You can also open it directly with a slug, for example `http://localhost:5173/?shop=my-cafe`. Vite forwards `/v1/api` requests to `API_PROXY_TARGET`. If the variable is missing, the development proxy is disabled.

To find your slug, sign in and call `GET /v1/api/tenants` with your bearer token; use the `slug` from the shop response. To check its public menu directly, open `http://127.0.0.1:8000/v1/api/public/menus/my-cafe` with your actual slug. `/v1/api/public/menu` instead uses the request hostname and therefore needs a shop hostname such as `my-cafe.sabrey.xyz`; it returns 404 on `localhost` or `127.0.0.1`.

## Deploy

Run `npm run build` and serve `dist` for `*.sabrey.xyz`. Set `VITE_API_ORIGIN` to the Render API origin in the hosting provider's **build environment**, then rebuild and redeploy. On Cloudflare Workers Builds, use Settings > Build > Build variables and secrets; on Cloudflare Pages, use Settings > Environment variables. Vite embeds this value in the browser bundle, so it is public and must not contain credentials. `API_PROXY_TARGET` only configures the Vite development server. With a separate API origin, the frontend derives the shop slug from its `*.sabrey.xyz` hostname and requests `/v1/api/public/menus/<slug>` from FastAPI. A `?shop=<slug>` query selects a shop explicitly, for example `https://emenu.sabrey.xyz/?shop=sabrey`. The backend must allow the frontend origin through CORS. Without `VITE_API_ORIGIN`, configure a same-origin reverse proxy to forward `/v1/api/` to FastAPI while preserving the original `Host` header. Cloudflare wildcard DNS, frontend hosting and HTTPS must also be configured; building the frontend does not configure them.
