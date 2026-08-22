from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.storage.duckdb import top_accounts, top_signals


def serve(db_path: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            rows = top_signals(db_path, 50, 0)
            accounts = top_accounts(db_path, 15, 70)
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
            body = """<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>DFW Project Radar</title>
<style>body{{font-family:Inter,system-ui;margin:0;background:#07111f;color:#eaf2ff}}header{{padding:34px 5%;background:linear-gradient(120deg,#0d2845,#126f80)}}h1{{margin:0;font-size:32px}}p{{color:#b8c8dc}}.kpi{{display:inline-block;background:#18a6a6;color:white;padding:9px 14px;border-radius:99px}}main{{padding:24px 5%;overflow:auto}}table{{width:100%;border-collapse:collapse;background:#0e1d2e;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:13px;border-bottom:1px solid #23364b;vertical-align:top}}th{{color:#78d8d4;font-size:12px;text-transform:uppercase}}small{{display:block;color:#8ea3b8;margin-top:5px}}a{{color:#70e2db}}</style>
<header><div class='kpi'>{count} oportunidades priorizadas</div> <div class='kpi'>{account_count} empresas objetivo</div><h1>Medina Cuba Plumbing · DFW Project Radar</h1><p>Permisos públicos reales de Fort Worth → señal → score → builder/developer → oportunidad comercial.</p></header><main><h2>Empresas con múltiples proyectos activos</h2><table><thead><tr><th>Empresa objetivo</th><th>Permisos</th><th>Score máx.</th><th>Valor acumulado</th><th>Último permiso</th><th>Fuente</th></tr></thead><tbody>{account_cards}</tbody></table><h2>Proyectos priorizados</h2><table><thead><tr><th>Score</th><th>Proyecto</th><th>Tipo</th><th>Fecha</th><th>Valor</th><th>Builder / Owner</th><th>Evidencia</th></tr></thead><tbody>{cards}</tbody></table></main></html>""".format(count=len(rows), account_count=len(accounts), account_cards=account_cards, cards=cards)
            encoded = body.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(encoded))); self.end_headers(); self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:
            return

    print("Radar local: http://{0}:{1}".format(host, port), flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
