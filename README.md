# Catálogo de Renovables — Chile (lookalikes)

Catálogo HTML de generadoras de energía solar y eólica en Chile que son **similares a
nuestros clientes actuales** (lookalikes) y están sujetas a PMU/PDC/EDAG por el Coordinador
Eléctrico Nacional. Ángulo CONECTA: vender PMU, PDC, EDAG y SCADA (SUPCON ECS-700 +
NovaTech Orion) a generadoras que aún no son clientes o tienen potencial de expansión.

## Estructura
- `index.html` — grid de tarjetas; cada tarjeta enlaza a su ficha.
- `ficha_<generadora>.html` — ficha con 6 secciones: Quién es · Qué hace · Proyectos (parques) ·
  Team de Compras (chips mailto/tel/LinkedIn, rol CT/D/A/R/I/C) · Contacto corporativo · Ángulo CONECTA.
- `research/*.json` — datos crudos con fuentes verificables (origen de las fichas).
- `build/generate.py` — regenera index + fichas desde los JSON.

## Clasificación
- **CLIENTE FINAL** — generadora que compra PMU + PDC + EDAG + SCADA.

## Reglas de datos
- Nada se inventa: sin fuente pública verificable → campo vacío ("no verificado").
- Cada dato cita su URL de fuente (formato "↳ url").
- Prioridad a jefes de área (Team de Compras: CT/D/A/R/I/C).

## Rebuild
```bash
python3 build/generate.py
```
