# Sabrey landing page

A Vue 3 and Vite landing page for the Sabrey digital menu. The menu preview uses example products; it is not connected to shop data.

## Run locally

```powershell
cd landing_page
npm install
npm run dev
```

Open the local URL printed by Vite. The login links point to `http://localhost:5173/login` during local development. Start the separate menu frontend on that address, or set `VITE_MENU_APP_URL` in a `.env` file in this directory:

```text
VITE_MENU_APP_URL=http://localhost:5173
```

Restart Vite after changing the value. The production default is `https://emenu.sabrey.xyz`; set the variable for a different menu application URL before building.

## Add your own images or videos

Place files in `public/media/` and edit the entries in `src/content.js`. For example:

```js
story: { type: 'image', src: '/media/your-shop.jpg', alt: 'Our café' },
menuBanner: { type: 'video', src: '/media/your-menu.mp4', alt: 'Our menu' },
```

You can also use an absolute public URL. The story area, menu banner, and four example product images each have their own entry. Set `type` to `placeholder` to restore a placeholder. Videos have playback controls and do not play automatically. Change the example product names, descriptions and prices in `src/App.vue`.

Run `npm run build` to create the production files in `dist`.

## Contact link

The Contact section starts with an example Telegram link. In `src/content.js`, change `contactTelegram.url` to your own link (for example, `https://t.me/yourname`) and set `isExample` to `false`.
