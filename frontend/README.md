# Sabrey menu frontend

The default template displays a published shop menu from the backend. It supports category navigation, item search, prices, images, and loading and error states.

The language selector switches the interface between English and Khmer and remembers the selection in the browser. Edit `src/locals/en.json` or `src/locals/km.json` to change interface translations. Shop, category, and item names come from the API and are displayed as entered; translating them requires multilingual menu data in the backend.

Open Settings to select Light, Dark, or System appearance. System follows the device setting, and the selection is saved in the browser for all templates.

`src/view/Home/home.vue` loads the public menu and selects a component using its `display_template` field. Available values are `default_template`, `cosmetic_template`, and `cambodia_template`. Register additional templates in the `templates` map in that file. Templates receive `menu`, `loading`, `error`, `needsShop`, and `isLocal` props and can emit `retry`, `choose-shop`, and `open-shop` (with a slug). Unknown or missing template names fall back to `default_template`.

To change a shop's template, open the header settings, choose Settings, sign in as the shop owner or admin, select a template, and save. The choice is stored on the tenant and shown to all visitors. The sign-in token stays in memory for the current page session; a reload requires signing in again. Sign-in requires HTTPS except on localhost.

After signing in under Settings, use **Show menu QR code** to display or download the shop's QR code. It encodes the tenant's public `https://<slug>.sabrey.xyz` URL; the public hostname must be deployed and configured before customers can use it.

## Run locally

Start the backend on `127.0.0.1:8000` (see the backend README), then in this directory run:

```powershell
npm install
npm run dev
```

Open the URL printed by Vite, for example `http://localhost:5173/`, and enter the slug of an existing published shop when prompted. You can also open it directly with a slug, for example `http://localhost:5173/?shop=my-cafe`. Vite forwards `/v1/api` requests to the local backend.

To find your slug, sign in and call `GET /v1/api/tenants` with your bearer token; use the `slug` from the shop response. To check its public menu directly, open `http://127.0.0.1:8000/v1/api/public/menus/my-cafe` with your actual slug. `/v1/api/public/menu` instead uses the request hostname and therefore needs a shop hostname such as `my-cafe.sabrey.xyz`; it returns 404 on `localhost` or `127.0.0.1`.

## Deploy

Run `npm run build` and serve `dist` for `*.sabrey.xyz`. On each shop hostname, the frontend requests `/v1/api/public/menu` on that same hostname. Configure the web server or reverse proxy to send `/v1/api/` requests to FastAPI and preserve the original `Host` header. Serve the frontend for `/` and its static assets. Cloudflare wildcard DNS, hosting and HTTPS must also be configured; building the frontend does not configure them.
