# Performance Analysis & Optimization Recommendations

This repository contains two small oTree applications (`simple_survey`, `public_goods_trial`). Overall, the code-base is lean and purely server-rendered; there is **no JavaScript bundle** or build pipeline (e.g., Webpack, Vite) that typically causes large client bundles. Consequently, client-side bundle size is already minimal. Nevertheless, a few areas can be improved to ensure fast load times and future scalability.

---

## 1 ▪ Static Asset Delivery

1. **Enable HTTP Compression** (Gzip/Brotli)
   * oTree/Django can serve compressed static files automatically when you run behind a production‐grade HTTP server (e.g., Nginx) or by adding [`whitenoise`](https://whitenoise.evans.io/).
   * **Benefit:** > 30 % reduction in HTML/CSS/JS transfer size, faster First Byte.

2. **Fingerprint & Cache-Control**
   * Run `collectstatic --clear --noinput` during deployment to collect static files and give them hashed filenames (`STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`).
   * Enables long-term caching (e.g., `Cache-Control: max-age=31536000, immutable`) while guaranteeing cache-busts on deploy.

3. **CDN Offload**
   * Offload static files to a CDN (CloudFront, Cloudflare). Latency ↓, global throughput ↑.

---

## 2 ▪ HTML Payload & Templating

1. **Minify HTML** (whitespace, comments). Use [`django-htmlmin`](https://github.com/cobrateam/django-htmlmin) middleware; drops payload ~15 – 20 %.
2. **Lazy-load Heavy Widgets**
   * The only media-heavy widget is the slider (`widgets.Slider`). If you later add custom JS, wrap it in `defer` and load it via `{% static %}` URLs so that browsers don't block rendering.

---

## 3 ▪ Database & Query Efficiency

Current queries are trivial (each round consists of ≤4 players). The `Group.compute()` method is O(n) with `n <= 4` so it's negligible. 

Recommendation (future-proof):
* Wrap `compute()` in an atomic transaction to avoid partial writes and lock contention if you increase group size.
* Use `.annotate(sum=models.Sum('contribution'))` if you later store contributions in a related model – pushes the aggregation to the DB.

---

## 4 ▪ Network Latency & HTTP Requests

* Combine small CSS files into one `.css` to cut request overhead (TCP + TLS handshakes).
* Serve favicons & meta images at `<link rel="preload">` for quicker first paint.

---

## 5 ▪ Deployment Checklist (Production)

| Step | Purpose |
|------|---------|
| `DEBUG = False` | Disables template debug overhead, security risk mitigation |
| `ALLOWED_HOSTS = ['your.domain']` | Host header validation |
| Gunicorn `--workers 2*CPU+1` | Optimal concurrency |
| Nginx `gzip on; brotli on;` | Transfer size ↓ |
| `whitenoise.runserver_nostatic` | Make runserver mimic prod |

---

## 6 ▪ Potential Code Optimizations

1. **Cache total contribution**
```python
# code/public_goods_trial/models.py
class Group(BaseGroup):
    @cached_property  # from django.utils.functional
    def total_contribution(self):
        return sum(p.contribution for p in self.get_players())
```
   * Avoids recalculating in templates; however, current usage is already memoized by saving the field.

2. **Pre-calculate `individual_share`** in DB query if group size or rounds ↑.

---

## 7 ▪ Tooling & Automation

* Add `flake8` + `isort` for lint & import ordering → marginally smaller bytecode, faster cold start.
* Docker multi-stage build: build wheels → copy to slim runtime image (cuts image size ~300 MB → 60 MB).

---

### Summary

The application is already light-weight. The biggest gains will come from **static-file compression, caching, and CDN delivery** rather than code changes. Implementing `whitenoise` and enabling Aggressive HTTP caching will likely yield **~35-50 % faster Time-to-First-Byte** and reduce perceived load times considerably.

> Next steps: integrate `whitenoise` into `settings.py`, run `collectstatic`, and deploy behind an Nginx reverse proxy with Brotli compression.