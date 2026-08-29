from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.storage.duckdb import radar_summary, source_coverage, top_accounts, top_signals, top_signals_for_source


SOURCE_LABELS = {
    "fort_worth_arcgis_permits": "Fort Worth",
    "frisco_active_building_permits": "Frisco",
}


def serve(db_path: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            rows = top_signals(db_path, 50, 0)
            accounts = top_accounts(db_path, 15, 70)
            frisco_rows = top_signals_for_source(db_path, "frisco_active_building_permits", 15, 60)
            signal_count, source_count, single_family_count = radar_summary(db_path)
            coverage = source_coverage(db_path)

            cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}<small>{2}</small></td><td>{3}</td><td>{4}</td><td>${5:,.0f}</td><td>{6}</td><td><a target='_blank' rel='noopener' href='{7}'>ver evidencia</a></td></tr>".format(
                    r[0], html.escape(str(r[1])), html.escape(str(r[12] or "")), html.escape(str(r[3])),
                    html.escape(str(r[4] or "")), float(r[5] or 0), html.escape(str(r[6] or r[7] or "—")), html.escape(str(r[11]))
                ) for r in rows
            )
            account_cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}</td><td>{2}</td><td>${3:,.0f}</td><td>{4}</td><td><a target='_blank' rel='noopener' href='{5}'>evidencia</a></td></tr>".format(
                    html.escape(str(r[0])), r[1], r[2], float(r[3] or 0), html.escape(str(r[4] or "")), html.escape(str(r[7]))
                ) for r in accounts
            )
            frisco_cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}<small>{2}</small></td><td>{3}</td><td>{4}</td><td>{5:,.0f} ft²</td><td><a target='_blank' rel='noopener' href='{6}'>ver evidencia</a></td></tr>".format(
                    r[0], html.escape(str(r[1])), html.escape(str(r[12] or "")), html.escape(str(r[3])),
                    html.escape(str(r[4] or "")), float(r[14] or 0), html.escape(str(r[11]))
                ) for r in frisco_rows
            )
            coverage_cards = "".join(
                "<div class='coverage'><b>{0}</b><span>{1:,} señales</span><small>Fechas observadas: {2} → {3}</small></div>".format(
                    html.escape(SOURCE_LABELS.get(str(source), str(source))), int(count),
                    html.escape(str(first_date or "sin fecha")), html.escape(str(last_date or "sin fecha"))
                ) for source, count, first_date, last_date in coverage
            )

            body = """<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Radar Comercial MCP</title>
<style>
:root{{--navy:#07111f;--panel:#0e1d2e;--panel2:#10263a;--line:#24445e;--aqua:#70e2db;--blue:#7fc8ff;--text:#eaf2ff;--muted:#adc0d5;--green:#66d19e;--amber:#ffca6a}}
*{{box-sizing:border-box}}body{{font-family:Inter,ui-sans-serif,system-ui;margin:0;background:var(--navy);color:var(--text)}}
header{{padding:38px 5% 30px;background:linear-gradient(120deg,#0d2845,#126f80)}}h1{{margin:12px 0 8px;font-size:clamp(30px,5vw,48px);line-height:1.05;max-width:900px}}h2{{margin-top:36px}}p{{color:var(--muted);line-height:1.55;max-width:1000px}}main{{padding:24px 5% 50px;overflow:auto}}a{{color:var(--aqua)}}
.kpis,.story,.capacity,.scores,.coverage-grid{{display:grid;gap:12px}}.kpis{{grid-template-columns:repeat(4,minmax(150px,1fr));margin-top:22px}}.kpi{{background:rgba(7,17,31,.45);border:1px solid rgba(255,255,255,.18);padding:16px;border-radius:14px}}.kpi b{{display:block;font-size:26px}}.kpi span{{color:#d6e6f5;font-size:13px}}
.headline{{font-size:18px;color:#e8fbff}}.story{{grid-template-columns:repeat(4,minmax(170px,1fr));margin:18px 0 30px}}.step,.score,.coverage{{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:16px}}.step b,.coverage b{{display:block;color:var(--aqua);margin-bottom:7px}}.step small,.coverage small{{display:block;color:#8ea3b8;margin-top:7px}}
.capacity{{grid-template-columns:repeat(3,1fr);margin:14px 0 8px}}.band{{padding:18px;border-radius:14px;background:var(--panel);border:1px solid var(--line)}}.band strong{{display:block;font-size:20px;margin-bottom:6px}}.ideal{{border-color:var(--green)}}.ideal strong{{color:var(--green)}}.secondary{{border-color:var(--amber)}}.secondary strong{{color:var(--amber)}}
.scores{{grid-template-columns:1fr 1fr;margin:18px 0}}.score strong{{font-size:18px;color:var(--blue)}}.status{{display:inline-block;margin-top:10px;padding:5px 9px;border-radius:99px;background:#173b4b;color:var(--aqua);font-size:12px}}.pending{{background:#43351d;color:var(--amber)}}
.coverage-grid{{grid-template-columns:repeat(2,1fr);margin:12px 0 24px}}.coverage span{{display:block;font-size:20px}}
.explain,.warning{{padding:14px 18px;border-radius:9px;margin:18px 0}}.explain{{background:#16334a;border-left:4px solid var(--aqua)}}.warning{{background:#332b1a;border-left:4px solid var(--amber);color:#ffe5ad}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:13px;border-bottom:1px solid #23364b;vertical-align:top}}th{{color:#78d8d4;font-size:12px;text-transform:uppercase}}td small{{display:block;color:#8ea3b8;margin-top:5px}}
@media(max-width:900px){{.kpis,.story{{grid-template-columns:repeat(2,1fr)}}.capacity,.scores,.coverage-grid{{grid-template-columns:1fr}}}}@media(max-width:560px){{.kpis,.story{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div class='headline'>Medina Cuba Plumbing · Inteligencia comercial DFW</div><h1>Detectar desarrollos antes de buscar contactos</h1><p>El radar transforma permisos municipales en señales priorizadas. El objetivo comercial es encontrar builders y desarrollos compatibles con la capacidad actual de MCP.</p>
<div class='kpis'><div class='kpi'><b>{signal_count:,}</b><span>señales municipales almacenadas</span></div><div class='kpi'><b>{source_count}</b><span>fuentes públicas activas</span></div><div class='kpi'><b>{single_family_count:,}</b><span>permisos nuevos unifamiliares observados</span></div><div class='kpi'><b>{opportunity_count}</b><span>oportunidades visibles para investigar</span></div></div></header>
<main>
<h2>El enfoque comercial acordado</h2><div class='capacity'><div class='band'><strong>&lt; 300 viviendas/año</strong>Prioridad menor por escala, salvo una razón estratégica.</div><div class='band ideal'><strong>300–600 viviendas/año</strong>Encaje ideal con la capacidad actual del personal de MCP.</div><div class='band secondary'><strong>&gt; 600 viviendas/año</strong>No se descarta: prioridad secundaria o entrada por fases.</div></div>
<div class='warning'><b>Importante:</b> el radar todavía no afirma producción anual. Primero mide actividad observada; la cifra de viviendas/año se valida agrupando permisos, desarrollo, subdivision, builder y evidencia de lotes.</div>
<h2>Dos decisiones diferentes</h2><div class='scores'><div class='score'><strong>Opportunity Score</strong><p>¿La señal parece atractiva por ubicación, tipo, recencia, tamaño y relevancia para plumbing?</p><span class='status'>Disponible hoy</span></div><div class='score'><strong>Company Confidence</strong><p>¿Estamos seguros de la empresa, su rol en el proyecto y de quién puede contratar el plumbing?</p><span class='status pending'>Siguiente validación</span></div></div>
<h2>Cómo se convierte en negocio</h2><div class='story'><div class='step'><b>1 · Detectar</b>Permisos y proyectos públicos.<small>Radar MCP</small></div><div class='step'><b>2 · Calificar</b>Escala, desarrollo, empresa y evidencia.<small>Radar + revisión</small></div><div class='step'><b>3 · Encontrar</b>Responsable de compras, estimación o construcción.<small>Apollo</small></div><div class='step'><b>4 · Convertir</b>Conversación → reunión → bid → contrato.<small>Embudo comercial</small></div></div>
<h2>Cobertura observada</h2><div class='coverage-grid'>{coverage_cards}</div>
<div class='explain'><b>Cómo explicarlo:</b> no presentamos estos permisos como contratos disponibles. Los usamos para reducir cientos de registros a una lista corta de empresas y desarrollos que merecen validación comercial.</div>
<h2>Empresas con actividad reciente</h2><p>El número representa permisos observados en la ventana disponible, no viviendas anuales confirmadas.</p><table><thead><tr><th>Empresa detectada</th><th>Permisos observados</th><th>Score máx.</th><th>Valor registrado</th><th>Última señal</th><th>Fuente</th></tr></thead><tbody>{account_cards}</tbody></table>
<h2>Frisco · proyectos activos destacados</h2><p>Frisco publica proyecto, dirección y tamaño, pero normalmente no identifica builder o valor. Requieren investigación adicional.</p><table><thead><tr><th>Score</th><th>Proyecto</th><th>Tipo</th><th>Fecha</th><th>Tamaño</th><th>Fuente</th></tr></thead><tbody>{frisco_cards}</tbody></table>
<h2>Proyectos priorizados</h2><table><thead><tr><th>Score</th><th>Proyecto</th><th>Tipo</th><th>Fecha</th><th>Valor</th><th>Builder / Owner</th><th>Evidencia</th></tr></thead><tbody>{cards}</tbody></table>
</main></body></html>""".format(
                signal_count=int(signal_count or 0), source_count=int(source_count or 0),
                single_family_count=int(single_family_count or 0), opportunity_count=len(rows),
                coverage_cards=coverage_cards, account_cards=account_cards, frisco_cards=frisco_cards, cards=cards,
            )
            encoded = body.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:
            return

    print("Radar local: http://{0}:{1}".format(host, port), flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
