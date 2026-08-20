#!/usr/bin/env python3
"""Genera index.html + fichas desde research/*.json.
Design system CONECTA: bg #f8fafc, ink #071324, acento #2563eb, radius 20px,
botones 100px, sin rojo (ámbar #d97706), Inter. Cada dato con fuente '↳ url'.

CONFIG al tope = todo lo que cambia entre un catálogo y otro (título, kicker,
subtítulo, leyenda, footers). Copiar a build/generate.py del repo nuevo y editar
solo el bloque CONFIG.
"""
import json, os, html, re, glob

CONFIG = {
    "titulo": "Catálogo de Renovables — Chile (lookalikes)",  # <title> + h1 del index
    "kicker_index": "Inteligencia comercial · Renovables",
    "sub_index": ("Generadoras de energía solar y eólica en Chile similares a nuestros clientes actuales "
                  "(lookalikes), sujetas a PMU/PDC/EDAG por el Coordinador Eléctrico. Cada ficha trae: "
                  "quién es, portafolio de parques, team de compras y el ángulo CONECTA — con fuente verificable."),
    "kicker_ficha": "Expediente de prospecto · Renovables",
    "ficha_sufijo": "· Renovables",  # sufijo del <title> de cada ficha
    "empresas_label": "Generadoras",
    "footer_index": "CONECTA Ingeniería · Catálogo de renovables (lookalikes) · agosto 2026",
    "footer_ficha": "CONECTA Ingeniería · Catálogo de renovables (lookalikes) · agosto 2026 · Cada dato cita su fuente verificable",
    "leyenda": [  # (clase-dot, texto)
        ("g", "CLIENTE FINAL — generadora que compra PMU + PDC + EDAG + SCADA"),
    ],
}

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.join(BASE, "research")
OUT = BASE

def esc(s):
    if s is None: return ""
    return html.escape(str(s))

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')

CLAS_COLOR = {
    "CANAL": ("tag-verde", "CANAL"),
    "SOCIO": ("tag-azul", "SOCIO"),
    "COMPETIDOR": ("tag-amb", "COMPETIDOR"),
    "CLIENTE FINAL": ("tag-gris", "CLIENTE FINAL"),
}
ROL_COMPRA = {
    "CT": ("tag-azul", "Comprador Técnico"),
    "D": ("tag-verde", "Decisor"),
    "A": ("tag-amb", "Autoridad"),
    "R": ("tag-gris", "Recomendador"),
    "I": ("tag-gris", "Influencia"),
    "C": ("tag-verde", "Coach"),
}

def load_companies():
    comps = []
    for f in sorted(glob.glob(os.path.join(RESEARCH, "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"[skip] {f}: {e}")
            continue
        if not d.get("empresa"):
            continue
        d["slug"] = slugify(d.get("slug") or d["empresa"])
        comps.append(d)
    order = {"CANAL": 0, "SOCIO": 1, "CLIENTE FINAL": 2, "COMPETIDOR": 3}
    comps.sort(key=lambda c: (order.get(c.get("clasificacion", "").strip().upper(), 9), c.get("empresa", "")))
    return comps

def fuente(urls):
    if not urls: return ""
    urls = urls if isinstance(urls, list) else [urls]
    parts = []
    for u in urls:
        u = str(u).strip()
        if not u or u.lower() in ("no verificado", "none", ""):
            continue
        label = u.replace("https://", "").replace("http://", "").rstrip("/")
        if len(label) > 60: label = label[:57] + "…"
        parts.append(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(label)}</a>')
    if not parts: return ""
    return f'<div class="fuente">{" · ".join(parts)}</div>'

def kv_line(label, val):
    if not val or str(val).strip() in ("", "no verificado", "None", "no"):
        return ""
    return f'<div><b>{esc(label)}:</b> {esc(val)}</div>'

def card_index(c):
    slug = c["slug"]
    clas = c.get("clasificacion", "").strip().upper()
    color, label = CLAS_COLOR.get(clas, ("tag-azul", clas or "—"))
    rubro = c.get("rubro", "")
    just = c.get("justificacion_angulo", "")
    qe = c.get("quien_es") or {}
    dot = qe.get("dotacion", "") if isinstance(qe, dict) else ""
    sede = qe.get("sede", "") if isinstance(qe, dict) else ""
    meta_bits = []
    if dot: meta_bits.append(f'<div><b>Dotación:</b> {esc(dot)}</div>')
    if sede: meta_bits.append(f'<div><b>Sede:</b> {esc(sede)}</div>')
    return f'''
    <a class="card ficha-link" href="ficha_{esc(slug)}.html">
      <div class="card-head"><h3>{esc(c["empresa"])}</h3><span class="badge {color}">{esc(label)}</span></div>
      <div class="region">{esc(rubro)}</div>
      <div class="meta">{''.join(meta_bits)}</div>
      <div class="ing">{esc(just)}</div>
    </a>'''

def section_quien(c):
    qe = c.get("quien_es") or {}
    if not isinstance(qe, dict): return ""
    lines = []
    if qe.get("descripcion"): lines.append(f'<div>{esc(qe["descripcion"])}</div>')
    for k, lab in [("fundada", "Fundada"), ("dotacion", "Dotación"), ("facturacion", "Facturación"),
                   ("matriz_grupo", "Matriz / grupo"), ("rut", "RUT"), ("sede", "Sede")]:
        lines.append(kv_line(lab, qe.get(k)))
    if not lines: return ""
    return f'''<div class="card"><div class="kv">{''.join(lines)}</div>{fuente(qe.get("fuentes"))}</div>'''

def section_que_hace(c):
    qh = c.get("que_hace") or {}
    if not isinstance(qh, dict): return ""
    html_ = []
    serv = qh.get("servicios")
    if serv:
        lis = ''.join(f'<li>{esc(s)}</li>' for s in serv if s)
        html_.append(f'<ul class="serv">{lis}</ul>')
    if qh.get("rol_cadena"):
        html_.append(f'<p class="rolc">{esc(qh["rol_cadena"])}</p>')
    if not html_: return ""
    return f'''<div class="card">{''.join(html_)}{fuente(qh.get("fuentes"))}</div>'''

def section_proyectos(c):
    projs = c.get("proyectos") or []
    if not projs: return ""
    rows = ""
    for p in projs:
        if not isinstance(p, dict): continue
        monto = p.get("monto") or ""
        if monto and str(monto).lower() in ("no verificado", ""):
            monto = ""
        rows += (f'<tr><td><b>{esc(p.get("proyecto",""))}</b></td>'
                 f'<td>{esc(p.get("cliente",""))}</td>'
                 f'<td>{esc(p.get("ubicacion",""))}</td>'
                 f'<td>{esc(monto)}</td>'
                 f'<td class="src">{fuente(p.get("fuente"))}</td></tr>')
    return f'''<table><tr><th>Proyecto</th><th>Cliente</th><th>Ubicación</th><th>Monto</th><th>Fuente</th></tr>{rows}</table>'''

def section_tomadores(c):
    ts = c.get("tomadores") or []
    if not ts: return ""
    out = ""
    for t in ts:
        if not isinstance(t, dict) or not t.get("nombre"): continue
        nombre = t["nombre"]; cargo = t.get("cargo", "")
        correo = t.get("correo", ""); tel = t.get("telefono", ""); lk = t.get("linkedin", "")
        fr = t.get("fuente", ""); rc = (t.get("rol_compra") or "").strip().upper()
        chips = ""
        if correo and str(correo).strip() and "@" in str(correo):
            chips += f'<a class="chip mail" href="mailto:{esc(correo)}">{esc(correo.split("@")[0])}@</a>'
        if tel and str(tel).strip():
            chips += f'<a class="chip" href="tel:{esc(tel)}">{esc(tel)}</a>'
        if lk and str(lk).strip() and "http" in str(lk):
            chips += f'<a class="chip" href="{esc(lk)}" target="_blank" rel="noopener">LinkedIn ↗</a>'
        rol_badge = ""
        if rc in ROL_COMPRA:
            color, etiqueta = ROL_COMPRA[rc]
            rol_badge = f'<span class="tag {color}">{esc(rc)} · {esc(etiqueta)}</span>'
        rol_extra = f'<div class="rol">{esc(cargo)} {rol_badge}</div>'
        src_line = fuente(fr) if fr else ""
        out += (f'<div class="contacto"><div><span class="nombre">{esc(nombre)}</span>{rol_extra}</div>'
                f'<div class="cta">{chips}</div></div>{src_line}')
    return f'<div class="card">{out}</div>'

def section_angulo(c):
    clas = c.get("clasificacion", "").strip().upper()
    just = c.get("justificacion_angulo", "")
    color, label = CLAS_COLOR.get(clas, ("tag-azul", clas or "—"))
    if not just: return ""
    return f'''<div class="card oportunidad"><h3>Ángulo CONECTA <span class="tag {color}">{esc(label)}</span></h3>
      <p>{esc(just)}</p></div>'''

def section_contacto(c):
    cc = c.get("contacto_corporativo") or {}
    if not isinstance(cc, dict): return ""
    lines = []
    if cc.get("direccion"): lines.append(kv_line("Dirección", cc["direccion"]))
    if cc.get("telefono"): lines.append(kv_line("Teléfono", cc["telefono"]))
    if cc.get("correo"): lines.append(kv_line("Correo", cc["correo"]))
    if cc.get("web"): lines.append(kv_line("Web", cc["web"]))
    if not lines: return ""
    return f'''<div class="card"><div class="kv">{''.join(lines)}</div>{fuente(cc.get("fuente"))}</div>'''

CSS = """
  :root { --bg:#f8fafc; --ink:#071324; --accent:#2563eb; --accent-soft:#dbeafe;
          --accent-softer:#eff6ff; --green:#059669; --green-soft:#d1fae5;
          --amber:#d97706; --amber-soft:#fef3c7; --muted:#64748b; --border:#e2e8f0;
          --radius-lg:20px; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Inter',-apple-system,sans-serif; background:var(--bg); color:var(--ink);
         line-height:1.55; -webkit-font-smoothing:antialiased; }
  .wrap { max-width:1120px; margin:0 auto; padding:40px 24px 80px; }
  .kicker { display:inline-block; font-size:12px; font-weight:600; letter-spacing:.12em;
            text-transform:uppercase; color:var(--accent); background:var(--accent-softer);
            padding:6px 14px; border-radius:100px; }
  h1 { font-size:32px; font-weight:700; margin-top:14px; letter-spacing:-.02em; }
  .sub { color:var(--muted); font-size:15px; margin-top:6px; max-width:720px; }
  .back { display:inline-flex; align-items:center; gap:6px; font-size:13px; font-weight:600;
          color:var(--accent); text-decoration:none; margin-bottom:22px; }
  .legend { display:flex; gap:10px; margin:24px 0 8px; flex-wrap:wrap; }
  .legend span { display:inline-flex; align-items:center; gap:8px; font-size:13px; font-weight:500;
                 color:var(--muted); background:#fff; border:1px solid var(--border);
                 padding:8px 14px; border-radius:100px; }
  .dot { width:10px; height:10px; border-radius:50%; }
  .dot.c { background:var(--green); } .dot.s { background:var(--accent); } .dot.comp { background:var(--amber); } .dot.g { background:#94a3b8; }
  .section-title { font-size:19px; font-weight:700; margin:30px 0 14px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:14px; }
  .card { background:#fff; border:1px solid var(--border); border-radius:var(--radius-lg);
          padding:20px; box-shadow:0 1px 2px rgba(7,19,36,.04); }
  a.card.ficha-link { text-decoration:none; color:inherit; display:flex; flex-direction:column;
          transition:box-shadow .15s ease, transform .15s ease; }
  a.card.ficha-link:hover { box-shadow:0 8px 24px rgba(7,19,36,.08); transform:translateY(-2px); }
  .card-head { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:4px; }
  .card h3 { font-size:17px; font-weight:700; }
  .badge { font-size:11px; font-weight:700; letter-spacing:.04em; padding:3px 10px;
           border-radius:100px; white-space:nowrap; }
  .region { font-size:12.5px; color:var(--muted); margin-bottom:10px; }
  .meta { font-size:13px; margin-bottom:8px; } .meta div { margin-bottom:3px; } .meta b { color:var(--ink); }
  .ing { font-size:12.5px; color:var(--accent); font-weight:600; }

  .section { margin-top:30px; }
  .section h2 { font-size:19px; font-weight:700; margin-bottom:12px; padding-bottom:8px;
                border-bottom:2px solid var(--accent-soft); }
  .kv { font-size:13.5px; } .kv div { margin-bottom:4px; } .kv b { color:var(--ink); }
  .serv { margin:0 0 8px 18px; font-size:13.5px; } .serv li { margin-bottom:3px; }
  .rolc { font-size:13.5px; color:var(--muted); }
  .fuente { font-size:11.5px; color:var(--muted); margin-top:8px; padding-left:14px; }
  .fuente a { color:var(--accent); text-decoration:none; word-break:break-all; }
  .fuente a:hover { text-decoration:underline; }
  .fuente::before { content:"↳ "; color:var(--accent); }
  table { width:100%; border-collapse:collapse; font-size:12.5px; background:#fff;
          border-radius:var(--radius-lg); overflow:hidden; border:1px solid var(--border); }
  th { background:var(--accent-softer); color:var(--ink); font-weight:700; text-align:left;
       padding:10px 12px; font-size:12px; }
  td { padding:10px 12px; border-top:1px solid var(--border); vertical-align:top; }
  td.src { font-size:11px; color:var(--muted); min-width:140px; }
  td.src .fuente { margin-top:0; padding-left:0; }
  .contacto { display:flex; align-items:center; justify-content:space-between; gap:10px;
              margin-bottom:6px; font-size:13.5px; padding-bottom:8px; border-bottom:1px solid var(--border); }
  .contacto:last-of-type { border-bottom:none; }
  .contacto .nombre { font-weight:700; }
  .rol { font-size:12px; color:var(--muted); }
  .contacto .cta { display:flex; gap:6px; flex-shrink:0; flex-wrap:wrap; }
  .chip { font-size:11px; font-weight:600; padding:4px 10px; border-radius:100px; text-decoration:none;
          background:var(--accent-softer); color:var(--accent); white-space:nowrap; }
  .chip:hover { background:var(--accent-soft); }
  .chip.mail { background:var(--green-soft); color:var(--green); }
  .tag { display:inline-block; font-size:11px; font-weight:700; padding:3px 10px; border-radius:100px; }
  .tag-verde { background:var(--green-soft); color:var(--green); }
  .tag-amb { background:var(--amber-soft); color:var(--amber); }
  .tag-azul { background:var(--accent-softer); color:var(--accent); }
  .tag-gris { background:#e2e8f0; color:#475569; }
  .oportunidad { border-left:4px solid var(--amber); }
  .oportunidad p { font-size:13.5px; color:var(--muted); margin-top:6px; }
  footer { margin-top:40px; color:var(--muted); font-size:12px; text-align:center; }
  .warn { background:var(--amber-soft); border:1px solid var(--amber); color:var(--amber);
          border-radius:12px; padding:10px 14px; font-size:12.5px; margin-top:14px; }
"""

def ficha_page(c):
    slug = c["slug"]
    secs = []
    s1 = section_quien(c)
    s2 = section_que_hace(c)
    s3 = section_proyectos(c)
    s4 = section_tomadores(c)
    s5 = section_angulo(c)
    s6 = section_contacto(c)
    if s1: secs.append('<div class="section"><h2>1 · Quién es</h2>' + s1 + '</div>')
    if s2: secs.append('<div class="section"><h2>2 · Qué hace</h2>' + s2 + '</div>')
    if s3: secs.append('<div class="section"><h2>3 · Proyectos / clientes</h2>' + s3 + '</div>')
    if s4: secs.append('<div class="section"><h2>4 · Team de Compras — tomadores de decisión</h2>' + s4 + '</div>')
    if s6: secs.append('<div class="section"><h2>5 · Contacto corporativo</h2>' + s6 + '</div>')
    if s5: secs.append('<div class="section"><h2>6 · Ángulo CONECTA</h2>' + s5 + '</div>')
    return f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(c["empresa"])} {esc(CONFIG["ficha_sufijo"])}</title><style>{CSS}</style></head>
<body><div class="wrap">
<a class="back" href="index.html">← Volver al catálogo</a>
<header><span class="kicker">{esc(CONFIG["kicker_ficha"])}</span>
<h1>{esc(c["empresa"])}</h1>
<p class="sub">{esc(c.get("rubro",""))}</p></header>
{''.join(secs)}
<footer>{esc(CONFIG["footer_ficha"])}</footer>
</div></body></html>'''

def index_page(comps):
    cards = ''.join(card_index(c) for c in comps)
    leyenda = ''.join(f'<span><i class="dot {cls}"></i>{esc(txt)}</span>' for cls, txt in CONFIG["leyenda"])
    return f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(CONFIG["titulo"])}</title><style>{CSS}</style></head>
<body><div class="wrap">
<header><span class="kicker">{esc(CONFIG["kicker_index"])}</span>
<h1>{esc(CONFIG["titulo"])}</h1>
<p class="sub">{esc(CONFIG["sub_index"])}</p></header>
<div class="legend">{leyenda}</div>
<div class="section-title">{esc(CONFIG["empresas_label"])} ({len(comps)})</div>
<div class="grid">{cards}</div>
<div class="warn">⚠ Datos en investigación con fuente pública verificable. Los contactos marcados "formato inferido" deben confirmarse antes de uso. Nada se inventa: campo sin fuente queda vacío.</div>
<footer>{esc(CONFIG["footer_index"])}</footer>
</div></body></html>'''

def main():
    comps = load_companies()
    if not comps:
        print("No se encontraron JSON en research/. Esperando resultados de subagentes...")
        return
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index_page(comps))
    for c in comps:
        fn = os.path.join(OUT, f'ficha_{c["slug"]}.html')
        open(fn, "w", encoding="utf-8").write(ficha_page(c))
    print(f"OK: index.html + {len(comps)} fichas generadas")

if __name__ == "__main__":
    main()
