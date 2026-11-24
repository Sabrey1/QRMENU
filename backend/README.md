# QR Menu backend

Install and start the API from this directory:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Configure MySQL in `.env` using `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD`. Set `SECRET_KEY` to a random secret of at least 32 characters. Keep it private and stable across restarts; changing it invalidates existing tokens. `ACCESS_TOKEN_EXPIRE_MINUTES` defaults to 60.

### Aiven for MySQL

1. In your Aiven service's **Overview → Connection information**, get the host, port, database, username and password, and download the project's **CA Certificate**. Aiven uses a service-specific port; use the value shown in the console rather than assuming 3306.
2. Store the downloaded certificate at `backend/certs/aiven-ca.pem`, or use another path. The `backend/certs/` folder is ignored by Git and excluded from the Docker image.
3. In the existing `backend/.env`, keep your database credentials and set `DB_SSL_ENABLED=true` and `DB_SSL_CA_FILE=certs/aiven-ca.pem`. Relative certificate paths are resolved from the backend directory. See `.env.example` for a complete example; do not overwrite an existing `.env` containing credentials.
4. From the backend directory, run `.\.venv\Scripts\python.exe test_connection.py`. This runs a read-only connection check using the same SQLAlchemy engine as the API and Alembic. Restart the API after changing `.env`.

Alternatively, after saving the CA certificate, run `.\.venv\Scripts\python.exe configure_aiven.py` from the backend directory. The guided setup asks for the individual Aiven values locally, hides the password while you type, saves them in `.env`, and checks the connection. It preserves an existing `SECRET_KEY` and generates one only if missing.

TLS verifies both the server certificate and hostname. For Render, set `DB_SSL_ENABLED=true` and provide the CA certificate contents as `DB_SSL_CA_PEM` in Render's environment settings instead of using a local file. Set **either** `DB_SSL_CA_FILE` or `DB_SSL_CA_PEM`, not both. The CA file and credentials are not deployed automatically. Aiven rotates project CAs; update the configured certificate when Aiven notifies you.

Visit http://127.0.0.1:8000/docs for request and response formats. A typical flow is:

1. Register with `POST /v1/api/auth/register` using JSON such as `{"name":"Sabrey","email":"owner@example.com","password":"password123"}`. Registration creates a shop with the same name and makes the account its owner. The response includes `tenant.slug` and `tenant.menu_url`, for example `https://sabrey.sabrey.xyz`. Duplicate shop names receive a suffix such as `sabrey-2`. The default currency is `KHR`; supply an optional `currency_code` such as `USD` to choose another. Then log in with `POST /v1/api/auth/login` using the same email and password.
2. Send the returned token as `Authorization: Bearer <access_token>` on management requests. In the API docs, use the **Authorize** button and enter the token.
3. Use the tenant returned by registration, or create an additional tenant with `POST /v1/api/tenants`. If `slug` is omitted, it is generated from the shop name and made unique (for example, `My Cafe` becomes `my-cafe` or `my-cafe-2`). A name with no Latin letters or digits gets a generated `shop-...` slug; provide a custom slug if you prefer another address.
4. Add categories and menu items under `/v1/api/tenants/{tenant_id}/categories` and `/v1/api/tenants/{tenant_id}/menu-items`. Their create request bodies include the same `tenant_id` as the URL.
5. View the published menu at `GET /v1/api/public/menus/{slug}` (for example, `http://127.0.0.1:8000/v1/api/public/menus/shop`). No login is needed. Only active categories and active, available items appear. An unpublished or unknown shop returns 404.

Tenant owners can manage existing registered users as `admin` or `member` under `/v1/api/tenants/{tenant_id}/members`. Owners and admins can manage categories and items; members can read them. A tenant owner cannot be removed or changed through these routes.

Tenants have a `display_template` field, defaulting to `default_template`. Owners and admins can set it when creating a tenant or update it using `PATCH /v1/api/tenants/{tenant_id}` with `{"display_template":"cosmetic_template"}`. It accepts 1–100 lowercase letters, digits, or underscores. The frontend supports `default_template`, `cosmetic_template`, and `cambodia_template` and falls back to `default_template` for unknown names. Additional templates must be registered in the frontend before they can be displayed.

All endpoints are available under `/v1/api`. The older `/api` URLs remain available for existing clients but are hidden from the API documentation. Future versions can use a separate prefix such as `/v2/api`; no v2 endpoints exist yet.

The version 1 route files live in `app/api/v1/routers/`, and `app/api/v1/router.py` collects them. To add version 2, create `app/api/v2/` with its own routers and register its router in `main.py` with `prefix="/v2"`. Models, schemas, and services currently live in shared `app/models`, `app/schemas`, and `app/services` folders. If v2 needs different behavior or response formats, give it separate services or schemas so changes do not accidentally affect v1.

## Shop subdomains

Registration creates the first shop and returns its `menu_url`. The owner can create additional shops after logging in. The public menu API is available at `GET /v1/api/public/menu` on the shop's hostname and at `GET /v1/api/public/menus/{slug}`. A shop must be published to be visible. On local Vite, use `http://localhost:5173/?shop=sabrey` with the actual slug; customers should use the HTTPS `menu_url`, never a localhost address.

An authenticated shop member can request `GET /v1/api/tenants/{tenant_id}/qr-code` for an SVG QR code containing that tenant's `menu_url`. In the frontend, sign in under Settings and use **Show menu QR code** to display or download it. The URL is usable by customers only after hosting and wildcard DNS are configured.

## Shop banners

Owners and admins can add banner image URLs using `POST /v1/api/tenants/{tenant_id}/banners` with a bearer token and a JSON body such as `{"image_url":"https://example.com/banner.jpg","alt_text":"Shop promotion","sort_order":0,"is_active":true}`. Tenant members can list banners with `GET` at the same address; owners and admins can update or delete one with `PATCH` or `DELETE /v1/api/tenants/{tenant_id}/banners/{banner_id}`. Only active banners are included in the public menu, sorted by `sort_order` then ID. The table stores image URLs, not image files; upload hosting must be configured separately.

Custom slugs must be 1–63 lowercase ASCII letters, numbers or hyphens, start and end with a letter or number, and not use a reserved name such as `www` or `api`. Changing a slug changes the shop's URL. Older tenants with no slug or a slug that is not a valid subdomain need to update their slug before they have a `menu_url`.

For the addresses to work on the internet, deploy the frontend and API to an origin reachable by Cloudflare, create a wildcard DNS record for `*.sabrey.xyz` pointing to that origin, and configure the origin to accept wildcard hostnames and preserve the original `Host` header. Set `SERVE_FRONTEND=true` to serve the built frontend and API together; without it, the FastAPI root returns JSON. The repository does not configure DNS, hosting, or certificates. See `DEPLOYMENT.md` at the project root for the Render test setup and Cloudflare domain steps.

The unique-slug migration requires existing duplicate non-null slugs to be resolved first. Before running `alembic upgrade head` on an existing database, check with `SELECT slug, COUNT(*) FROM tenants WHERE slug IS NOT NULL GROUP BY slug HAVING COUNT(*) > 1;`. Resolve any duplicates intentionally; the migration will fail instead of changing existing addresses.

Run the isolated API tests without connecting to MySQL:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Rate limits

Each client IP can make 120 API requests per minute, including public menus. Login is also limited to 10 attempts per minute and registration to 5 attempts per hour. Both successful and unsuccessful requests count, and `/api` and `/v1/api` share the same limits. Exceeding a limit returns HTTP 429 with a `Retry-After` header in seconds. Change the limits in `.env` with `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_LOGIN_PER_MINUTE`, and `RATE_LIMIT_REGISTER_PER_HOUR` (positive integers); restart the API after changing them.

The default `RATE_LIMIT_STORAGE_URL=memory://` stores counters in one server process and loses them on restart. For multiple workers or servers, configure a shared Redis instance, for example `RATE_LIMIT_STORAGE_URL=redis://127.0.0.1:6379/0` (or `rediss://` for TLS). All instances must use the same Redis database. If storage is unavailable, protected requests return 503 rather than silently disabling the limiter. Per-IP limits can affect people sharing a network and do not prevent distributed attacks; use Cloudflare WAF rate-limiting rules as an additional layer.

The limiter uses the client IP supplied by the ASGI server; it does not read forwarded headers itself. When using a reverse proxy, configure Uvicorn's `--forwarded-allow-ips` to trust only your actual proxy IPs, and ensure the proxy replaces client-supplied forwarding headers with verified addresses. Restrict direct access to the origin. Without correctly configured trusted proxies, many users may share one limit; trusting arbitrary clients permits IP spoofing.

Authentication also needs deployment-specific protections such as HTTPS and a password recovery process.
