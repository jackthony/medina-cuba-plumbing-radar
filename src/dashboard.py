from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.storage.duckdb import top_accounts, top_signals, top_signals_for_source


def serve(db_path: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            rows = top_signals(db_path, 50, 0)
            accounts = top_accounts(db_path, 15, 70)
            frisco_rows = top_signals_for_source(db_path, "frisco_active_building_permits", 15, 60)
            cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}<small>{2}</small></td><td>{3}</td><td>{4}</td><td>${5:,.0f}</td><td>{6}</td><td><a target='_blank' href='{7}'>ver fuente</a></td></tr>".format(
                    r[0], html.escape(str(r[1])), html.escape(str(r[12] or "")), html.escape(str(r[3])),
                    html.escape(str(r[4] or "")), float(r[5] or 0), html.escape(str(r[6] or r[7] or "—")), html.escape(str(r[11]))
                ) for r in rows
            )
            account_cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}</td><td>{2}</td><td>${3:,.0f}</td><td>{4}</td><td><a target='_blank' href='{5}'>evidencia</a></td></tr>".format(
                    html.escape(str(r[0])), r[1], r[2], float(r[3] or 0), html.escape(str(r[4] or "")), html.escape(str(r[7]))
                ) for r in accounts
            )
            frisco_cards = "".join(
                "<tr><td><b>{0}</b></td><td>{1}<small>{2}</small></td><td>{3}</td><td>{4}</td><td>{5:,.0f} ft²</td><td><a target='_blank' href='{6}'>ver permiso</a></td></tr>".format(
                    r[0], html.escape(str(r[1])), html.escape(str(r[12] or "")), html.escape(str(r[3])),
                    html.escape(str(r[4] or "")), float(r[14] or 0), html.escape(str(r[11]))
                ) for r in frisco_rows
            )
            body = """<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>DFW Project Radar</title>
<style>body{{font-family:Inter,system-ui;margin:0;background:#07111f;color:#eaf2ff}}header{{padding:34px 5%;background:linear-gradient(120deg,#0d2845,#126f80)}}h1{{margin:12px 0 0;font-size:32px}}p{{color:#b8c8dc;line-height:1.55}}.kpi{{display:inline-block;background:#18a6a6;color:white;padding:9px 14px;border-radius:99px}}main{{padding:24px 5%;overflow:auto}}.story{{display:grid;grid-template-columns:repeat(4,minmax(170px,1fr));gap:12px;margin:18px 0 30px}}.step{{background:#10263a;border:1px solid #24445e;border-radius:12px;padding:16px}}.step b{{display:block;color:#70e2db;margin-bottom:7px}}.explain{{background:#16334a;border-left:4px solid #70e2db;padding:12px 18px;border-radius:8px;margin-bottom:24px}}table{{width:100%;border-collapse:collapse;background:#0e1d2e;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:13px;border-bottom:1px solid #23364b;vertical-align:top}}th{{color:#78d8d4;font-size:12px;text-transform:uppercase}}small{{display:block;color:#8ea3b8;margin-top:5px}}a{{color:#70e2db}}@media(max-width:800px){{.story{{grid-template-columns:1fr}}}}</style>
<header><div class='kpi'>{count} oportunidades priorizadas</div> <div class='kpi'>{account_count} empresas objetivo</div><h1>¿Dónde debería buscar Medina Cuba su próximo proyecto?</h1><p>El radar convierte permisos públicos de Fort Worth y Frisco en una lista sencilla de proyectos y empresas que vale la pena investigar primero.</p></header><main><div class='story'><div class='step'><b>1 · Encontramos</b>Permisos públicos de construcción nuevos o activos.</div><div class='step'><b>2 · Entendemos</b>Tipo de proyecto, dirección, tamaño y empresa cuando está disponible.</div><div class='step'><b>3 · Priorizamos</b>Un score de 0 a 100 ordena las señales más relevantes para plumbing.</div><div class='step'><b>4 · Actuamos</b>Verificar empresa, buscar decision maker y solicitar estimate o bid.</div></div><div class='explain'><b>Cómo explicarlo:</b> esto no garantiza un contrato. Reduce cientos de permisos a una lista corta para que el equipo comercial investigue las mejores señales antes que la competencia.</div><h2>Empresas con múltiples proyectos activos</h2><p>Una empresa con varios permisos puede representar una relación comercial de mayor valor que un proyecto aislado.</p><table><thead><tr><th>Empresa objetivo</th><th>Permisos</th><th>Score máx.</th><th>Valor acumulado</th><th>Último permiso</th><th>Fuente</th></tr></thead><tbody>{account_cards}</tbody></table><h2>Frisco · proyectos activos destacados</h2><p>Frisco publica proyecto, dirección y tamaño, pero normalmente no identifica builder o valor. Estos registros requieren investigación.</p><table><thead><tr><th>Score</th><th>Proyecto</th><th>Dirección</th><th>Tipo</th><th>Fecha</th><th>Tamaño</th><th>Fuente</th></tr></thead><tbody>{frisco_cards}</tbody></table><h2>Proyectos priorizados</h2><table><thead><tr><th>Score</th><th>Proyecto</th><th>Tipo</th><th>Fecha</th><th>Valor</th><th>Builder / Owner</th><th>Evidencia</th></tr></thead><tbody>{cards}</tbody></table></main></html>""".format(count=len(rows), account_count=len(accounts), account_cards=account_cards, frisco_cards=frisco_cards, cards=cards)
            encoded = body.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(encoded))); self.end_headers(); self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:
            return

    print("Radar local: http://{0}:{1}".format(host, port), flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
