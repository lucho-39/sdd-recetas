# 03-deployment.md — Llevar Recetario IA a tu server con dominio gratis

## Topología (por qué es así)

```
visitante ──https──▶ Caddy (:80/:443, TLS automático)
                        ├─ app.DOMINIO ──▶ frontend:3000 (preview server)
                        └─ admin.DOMINIO ─▶ admin:3001 (preview server)
                                              │  /api, /uploads, /socket.io
                                              ▼ (mismo origen, sin CORS)
                                           backend:8000 ──▶ postgres:5432

(Puertos de contenedor. En el host van bindeados solo a loopback para
convivir con otros stacks: 13000/13001/18000/15432. Ver Firewall abajo.)
```

Cada SvelteKit ya proxea `/api`, `/uploads` y `/socket.io` al backend desde
su preview server (ver `vite.config.ts` de cada app). Caddy entonces solo
reparte por host y termina TLS. El frontend **nunca** habla con el backend por
otro host: no hay CORS cross-site y la cookie de refresh (`Secure`,
`SameSite=Lax`, path `/api/v1/auth/refresh`) viaja same-origin. Si rompés
esto (API en tercer host), hay que reabrir CORS, cookies y OAuth: no lo hagas.

## Dominio gratis (DuckDNS, ~10 min)

1. Entrá a https://www.duckdns.org con tu cuenta (Google/GitHub/etc.).
2. Creá **dos** subdominios: `tu-app` y `tu-app-admin` → `tu-app.duckdns.org`,
   `tu-app-admin.duckdns.org` (elegí tus nombres).
3. Apuntá ambos con un registro **A** a la IP pública de tu server.
4. Si la IP de tu server es dinámica, agregá el cron que sugiere DuckDNS
   (token en la misma página) para actualizarla.

Alternativas válidas: cualquier DNS con A/AAAA a tu IP (No-IP, Afraid.org,
dominio propio). Lo único que Caddy necesita es que ambos nombres resuelvan
a tu server con los puertos 80/443 alcanzables.

## Preparar el server (~15 min)

Requiere: Linux x86_64 con IP pública, Podman + `podman-compose`, git, `ufw`.

```bash
# 1. Firewall: solo entran SSH, HTTP y HTTPS. Los puertos de host
#    (13000/13001/18000/15432) encima van bindeados solo a 127.0.0.1 en el
#    compose: doble barrera, solo Caddy habla con los contenedores, y de
#    eso depende que el rate limiting por X-Forwarded-For sea confiable.
sudo ufw allow 22,80,443/tcp
sudo ufw enable

# 2. Clonar y configurar (NUNCA commitees el .env real)
git clone https://github.com/lucho-39/sdd-recetas.git
cd sdd-recetas
cp .env.production.example .env
# Editá .env: secretos (openssl rand -hex 32), dominios y SMTP si tenés

# 3. Caddy como reverse proxy del host (TLS automático vía Let's Encrypt)
sudo apt install -y caddy
sudo cp Caddyfile /etc/caddy/Caddyfile
# systemctl restart NO hereda el env del comando que lo invoca: los dominios
# van en un drop-in de systemd (sobrevive reboots y restarts).
sudo mkdir -p /etc/systemd/system/caddy.service.d
printf '[Service]\nEnvironment=APP_DOMAIN=tu-app.duckdns.org\nEnvironment=ADMIN_DOMAIN=tu-app-admin.duckdns.org\n' | \
  sudo tee /etc/systemd/system/caddy.service.d/domains.conf
sudo systemctl daemon-reload
sudo systemctl restart caddy

# 4. Levantar la app (el primer arranque compila los frontends: 2-5 min,
#    los healthchecks marcan el ritmo, tené paciencia)
podman-compose up --build -d
podman-compose ps   # backend healthy → frontend/admin healthy
```

## Primera vez en vivo (checklist)

- [ ] `https://tu-app.duckdns.org` carga (candado válido).
- [ ] `https://tu-app-admin.duckdns.org/admin/login` carga.
- [ ] Login admin con `ADMIN_INITIAL_USER`/`ADMIN_INITIAL_PASSWORD` → el
      sistema **exige** cambiar la contraseña en el primer login.
- [ ] Crear una cuenta de usuario, loguearse, recargar: la sesión sobrevive
      (refresh por cookie `Secure`).
- [ ] `/api/v1/health` responde `{"status":"healthy"}` (vía Caddy o directo).
- [ ] `ENVIRONMENT=production`: sin `/docs`, sin echo SQL, cookies `Secure`.

## Operación

```bash
podman-compose logs -f backend      # logs
podman-compose restart backend      # tras cambiar solo código backend
podman exec recetario-postgres pg_dump -U recetario recetario > backup.sql
# Actualizar: git pull && podman-compose up --build -d
```

Backups: el volumen de postgres vive en el host; programá el `pg_dump` en
cron y guardalo fuera del server. Uploads en `./.data/uploads`: incluilo.

## Mostrarlo desde GitHub

1. En el repo → **About** (⚙️ arriba a la derecha) → campo **Website**: pegá
   `https://tu-app.duckdns.org`. Sumá topics (`recetas`, `sveltekit`,
   `fastapi`) para que sea encontrable.
2. La sección "Demo en vivo" del README ya apunta a los dominios de ejemplo:
   reemplazalos por los tuyos cuando existan.

## Límites conocidos (no son bugs)

- Un solo nodo, deploy manual (`git pull` + rebuild): sin CD ni réplicas.
- Los bind mounts del compose son estilo-dev; en prod solo aportan
  reconstrucción con env nuevo, a costo de un arranque lento.
- Rate limiting cuenta por IP vista tras `X-Forwarded-For` (lo pone Caddy):
  válido solo con los puertos internos cerrados (ver firewall arriba).
- `DEBUG`/`ENVIRONMENT=development` en prod reabre `/docs` y el echo SQL:
  jamás uses el `.env.example` de desarrollo en el server.
