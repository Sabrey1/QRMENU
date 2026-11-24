// Use type: 'image' or 'video' and a public URL or a path under /public.
export const media = {
  menuBanner: { type: 'placeholder', src: '', alt: 'Menu banner' },
  story: { type: 'placeholder', src: '', alt: 'Your business' },
  morningToast: { type: 'placeholder', src: '', alt: 'Morning toast' },
  icedLatte: { type: 'placeholder', src: '', alt: 'Iced latte' },
  berryBowl: { type: 'placeholder', src: '', alt: 'Berry bowl' },
  citrusSoda: { type: 'placeholder', src: '', alt: 'Citrus soda' },
}

// Set VITE_MENU_APP_URL in .env when the menu application uses a different origin.
export const menuAppUrl = (import.meta.env.VITE_MENU_APP_URL || (import.meta.env.DEV ? 'http://localhost:5173' : 'https://emenu.sabrey.xyz')).replace(/\/$/, '')

// Replace the example URL with your Telegram link and set isExample to false.
export const contactTelegram = { url: 'https://t.me/your_telegram_username', isExample: true }
