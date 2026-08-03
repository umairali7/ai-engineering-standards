"""Local, token-protected workspace for optional human EV scoring.

The browser is only an ergonomic editor for the canonical scoresheet. Final
submission always passes through :func:`rating.ingest_scores`; this module does
not create a second scoring protocol or grant qualification authority.
"""

from __future__ import annotations

import json
import secrets
import threading
import webbrowser
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import workspace


MAX_REQUEST_BYTES = 16 * 1024 * 1024


class ReviewWorkspaceError(Exception):
    pass


class ReviewSession:
    """Own draft and submission operations independently of HTTP transport."""

    def __init__(self, run_id: str):
        workspace.validate_run_id(run_id)
        self.run_id = run_id
        self.run_dir = workspace.run_dir(run_id)
        self.sheet_path = self.run_dir / "scoresheet.json"
        self.draft_path = self.run_dir / "human-review-draft.json"
        if not self.sheet_path.is_file():
            raise ReviewWorkspaceError(
                f"scoresheet not found for {run_id!r}; collect responses first")
        self._lock = threading.Lock()

    def _base_sheet(self) -> dict:
        return workspace.read_json(self.sheet_path)

    def _subject_id(self) -> str | None:
        manifest_path = self.run_dir / "manifest.json"
        if not manifest_path.is_file():
            return None
        manifest = workspace.read_json(manifest_path)
        return ((manifest.get("subject") or {}).get("id")
                or (manifest.get("model") or {}).get("registry_id"))

    def _validate_draft(self, sheet: dict) -> dict:
        if not isinstance(sheet, dict):
            raise ReviewWorkspaceError("review draft must be a JSON object")
        if sheet.get("run_id") != self.run_id:
            raise ReviewWorkspaceError("review draft run_id does not match this run")
        base = self._base_sheet()
        expected = [item.get("response_record") for item in base.get("items", [])]
        actual = [item.get("response_record") for item in sheet.get("items", [])]
        if actual != expected:
            raise ReviewWorkspaceError(
                "review draft must retain every scoresheet item in canonical order")
        # Treat browser input as untrusted. Only review fields are editable;
        # scenario identity, frozen instruments, digests, prompts, and response
        # bindings always come back from the canonical scoresheet.
        canonical = deepcopy(base)
        supplied_rater = sheet.get("rater") or {}
        supplied_conflict = supplied_rater.get("conflict_declaration") or {}
        canonical["rater"] = {
            "id": supplied_rater.get("id"),
            "name": supplied_rater.get("name"),
            "kind": "human",
            "conflict_declaration": {
                "declared": bool(supplied_conflict.get("declared")),
                "has_conflict": supplied_conflict.get("has_conflict"),
                "subject_id": self._subject_id(),
            },
        }
        editable = (
            "scores", "findings", "failure_conditions_observed",
            "grounding_diagnostics", "review_trace")
        for target, supplied in zip(canonical.get("items", []),
                                    sheet.get("items", []), strict=True):
            for field in editable:
                target[field] = deepcopy(supplied.get(field))
        return canonical

    def sheet(self) -> dict:
        if self.draft_path.is_file():
            try:
                return self._validate_draft(workspace.read_json(self.draft_path))
            except (OSError, ValueError, ReviewWorkspaceError):
                # A corrupt/stale draft never replaces the canonical worksheet.
                pass
        return self._base_sheet()

    def document(self) -> dict:
        sheet = deepcopy(self.sheet())
        conflict = sheet["rater"].setdefault("conflict_declaration", {})
        conflict["subject_id"] = self._subject_id()
        for item in sheet.get("items", []):
            response_path = self.run_dir / "responses" / item["response_record"]
            response = workspace.read_json(response_path)
            item["task_prompt"] = (
                (response.get("request") or {}).get("prompt")
                or (response.get("scenario") or {}).get("prompt")
                or "Prompt unavailable for this legacy run."
            )
            item["raw_response"] = response.get("raw_response", "")
            item["area"] = response.get("area")
            item["risk_tier"] = response.get("risk_tier")
        return {
            "kind": "aies-human-review-workspace",
            "schema_version": 1,
            "run_id": self.run_id,
            "human_evaluation": "optional",
            "qualification_authority": "none",
            "draft_path": str(self.draft_path),
            "sheet": sheet,
        }

    def save(self, sheet: dict) -> dict:
        with self._lock:
            valid = self._validate_draft(sheet)
            workspace.write_json(self.draft_path, valid, overwrite=True)
        scored = sum(
            1 for item in valid.get("items", [])
            if all(value is not None for value in (item.get("scores") or {}).values())
        )
        return {"saved": True, "scored_items": scored,
                "total_items": len(valid.get("items", []))}

    def submit(self, sheet: dict, progress_callback=None) -> dict:
        """Admit ratings, aggregate, and refresh every report in one action."""
        from . import engine, evaluation, rating, report

        with self._lock:
            valid = self._validate_draft(sheet)
            workspace.write_json(self.draft_path, valid, overwrite=True)
            written = rating.ingest_scores(
                self.run_id, valid, progress_callback=progress_callback,
                reset_progress_clock=True)
            package = engine.aggregate(self.run_id)
            reports = report.write_reports(self.run_id)
        return {
            "submitted": True,
            "ratings_written": len(written),
            "rating_records": written,
            "engineering_evaluation": evaluation.summarize(self.run_id),
            "evidence_package": package,
            "reports": reports,
            "human_evaluation": (
                "recorded; qualification admission remains governed by rater scope, "
                "calibration, independence, and the explicit formal workflow"),
        }


def _html() -> str:
    """Return a dependency-free review application (works fully offline)."""
    return r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIES Human EV Review</title>
<style>
:root{color-scheme:dark;--bg:#081018;--panel:#101c28;--line:#26394a;--ink:#edf5fb;--muted:#9db0bf;--cyan:#48d7d0;--amber:#ffc65c;--red:#ff7b72;--green:#65d88b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#153047 0,transparent 36%),var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}
header{position:sticky;top:0;z-index:3;display:flex;gap:18px;align-items:center;padding:14px 22px;background:#081018eF;border-bottom:1px solid var(--line);backdrop-filter:blur(10px)}
h1{font-size:18px;margin:0;letter-spacing:.03em}.badge{font-size:12px;padding:3px 8px;border:1px solid var(--cyan);color:var(--cyan);border-radius:999px}.grow{flex:1}.muted{color:var(--muted)}
progress{width:180px;accent-color:var(--cyan)}button,input,textarea,select{font:inherit}button{cursor:pointer;border:1px solid var(--line);border-radius:8px;padding:8px 12px;background:#172636;color:var(--ink)}button:hover{border-color:var(--cyan)}button.primary{background:var(--cyan);color:#042326;border:0;font-weight:750}button.danger{background:#41202a;border-color:var(--red)}
main{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:calc(100vh - 63px)}aside{border-right:1px solid var(--line);padding:16px;position:sticky;top:63px;height:calc(100vh - 63px);overflow:auto}.field{margin:0 0 12px}.field label{display:block;color:var(--muted);font-size:12px;margin-bottom:4px}.field input,.field select,.field textarea{width:100%;background:#0b1620;border:1px solid var(--line);border-radius:7px;color:var(--ink);padding:8px}.task{width:100%;text-align:left;margin:0 0 6px;padding:9px;border-left:3px solid var(--line)}.task.done{border-left-color:var(--green)}.task.active{background:#183246;border-color:var(--cyan)}
article{padding:28px;max-width:1180px;width:100%;margin:auto}.eyebrow{color:var(--cyan);font-size:12px;text-transform:uppercase;letter-spacing:.12em}.card{background:#0e1a25dd;border:1px solid var(--line);border-radius:12px;padding:18px;margin:14px 0}.card h2,.card h3{margin-top:0}.content{white-space:pre-wrap;max-height:320px;overflow:auto;background:#071018;border-radius:8px;padding:14px;border:1px solid #1c2b38}
.ev{display:grid;grid-template-columns:190px 260px minmax(220px,1fr);gap:12px;align-items:start;padding:13px 0;border-top:1px solid var(--line)}.ev:first-of-type{border-top:0}.score{display:flex;gap:5px}.score button{width:42px;padding:7px 0}.score button.selected{background:var(--cyan);color:#042326;border-color:var(--cyan);font-weight:800}.ev textarea{width:100%;min-height:62px;background:#08131d;border:1px solid var(--line);color:var(--ink);border-radius:7px;padding:8px}.anchor{font-size:12px;color:var(--muted);margin-top:6px}.anchors{font-size:11px;color:var(--muted);margin-top:7px}.fail{display:block;padding:5px}.ground-grid{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:10px}.actions{display:flex;gap:9px;align-items:center;position:sticky;bottom:0;background:#081018ee;padding:13px 0}.status{min-height:24px;color:var(--muted)}.error{color:var(--red)}.ok{color:var(--green)}
@media(max-width:850px){main{display:block}aside{position:static;height:auto;border:0;border-bottom:1px solid var(--line)}.ev{grid-template-columns:1fr}.content{max-height:420px}header{flex-wrap:wrap}}
</style></head><body>
<header><h1>AIES · Human EV Review</h1><span class="badge">OPTIONAL</span><span id="run" class="muted"></span><span class="grow"></span><span id="count"></span><progress id="progress" max="1" value="0"></progress></header>
<main><aside>
  <div class="field"><label>Rater name (required to submit)</label><input id="raterName" autocomplete="name"></div>
  <div class="field"><label>Durable rater ID (required only for formal admission)</label><input id="raterId"></div>
  <div class="field"><label>Conflict with assessed subject</label><select id="conflict"><option value="">Not declared</option><option value="false">No conflict</option><option value="true">Conflict declared</option></select></div>
  <div class="field"><label>Filter</label><select id="filter"><option value="all">All items</option><option value="unscored">Unscored</option><option value="low">Has score ≤ 2</option></select></div>
  <div id="tasks"></div>
</aside><article>
  <div class="eyebrow" id="meta"></div><h2 id="title">Loading review workspace…</h2>
  <section class="card"><h3>Scenario prompt</h3><div id="prompt" class="content"></div></section>
  <section class="card"><h3>Subject response</h3><div id="answer" class="content"></div></section>
  <section class="card"><h3>EV ratings <span class="muted">· integer anchors 0–4</span></h3><div id="evs"></div></section>
  <section class="card"><h3>Declared failure conditions observed</h3><div id="failures" class="muted">None declared.</div></section>
  <section class="card"><h3>Optional grounding diagnostic <span class="muted">· informational, never EV7</span></h3>
    <label class="fail"><input type="checkbox" id="groundAssessed"> Grounding was explicitly assessed</label>
    <div class="ground-grid">
      <div class="field"><label>Unsupported assertions</label><input id="gUnsupported" type="number" min="0" value="0"></div>
      <div class="field"><label>Fabricated APIs or entities</label><input id="gFabricated" type="number" min="0" value="0"></div>
      <div class="field"><label>Invalid citations or provenance</label><input id="gCitations" type="number" min="0" value="0"></div>
      <div class="field"><label>False success or test claims</label><input id="gSuccess" type="number" min="0" value="0"></div>
    </div>
    <div class="field"><label>Abstention</label><select id="gAbstention"><option value="">Not applicable / not assessed</option><option value="appropriate">Applicable and appropriate</option><option value="inappropriate">Applicable and inappropriate</option></select></div>
    <div class="field"><label>Notes</label><textarea id="grounding" style="min-height:75px" placeholder="Source-separated evidence for the observations above."></textarea></div>
  </section>
  <div class="actions"><button id="prev">← Previous</button><button id="next">Next →</button><span class="grow"></span><button id="export">Export JSON</button><button class="primary" id="submit">Submit, analyze & refresh reports</button></div>
  <div id="status" class="status">Human review is optional. This workspace cannot grant qualification or deployment authority.</div>
</article></main>
<script>
const token=new URLSearchParams(location.search).get('token');let sheet,items,index=0,timer;
const dims=['EV1','EV2','EV3','EV4','EV5','EV6'];const labels={EV1:'Correctness',EV2:'Completeness',EV3:'Safety & Security',EV4:'Maintainability',EV5:'Efficiency',EV6:'Traceability'};
const $=id=>document.getElementById(id);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,method='GET',body){const r=await fetch(path+'?token='+encodeURIComponent(token),{method,headers:{'Content-Type':'application/json','X-AIES-Review-Token':token},body:body?JSON.stringify(body):undefined});const data=await r.json();if(!r.ok)throw Error(data.error||data.message||r.statusText);return data}
function completed(it){return dims.every(d=>Number.isInteger(it.scores[d]))}function low(it){return dims.some(d=>Number.isInteger(it.scores[d])&&it.scores[d]<=2)}
function syncIdentity(){sheet.rater.name=$('raterName').value.trim()||null;sheet.rater.id=$('raterId').value.trim()||null;const c=$('conflict').value,subject=sheet.rater.conflict_declaration?.subject_id||null;sheet.rater.kind='human';sheet.rater.conflict_declaration={declared:c!=='',has_conflict:c===''?null:c==='true',subject_id:subject}}
function schedule(){syncIdentity();clearTimeout(timer);$('status').textContent='Unsaved changes…';timer=setTimeout(save,500)}
async function save(){try{const r=await api('/api/draft','POST',sheet);$('status').className='status ok';$('status').textContent=`Draft saved · ${r.scored_items}/${r.total_items} completely scored`;renderTasks()}catch(e){$('status').className='status error';$('status').textContent=e.message}}
function instrument(it){return it.reviewer_instrument||{};}function render(){const it=items[index],ins=instrument(it),evaluation=ins.evaluation||{};$('run').textContent=sheet.run_id;$('meta').textContent=[it.area,it.risk_tier,it.scenario_id].filter(Boolean).join(' · ');$('title').textContent=it.task_label;$('prompt').textContent=it.task_prompt;$('answer').textContent=it.raw_response;
 $('raterName').value=sheet.rater.name||'';$('raterId').value=sheet.rater.id||'';const cd=sheet.rater.conflict_declaration||{};$('conflict').value=!cd.declared?'':String(Boolean(cd.has_conflict));
 $('evs').innerHTML=dims.map(d=>{const di=(evaluation.dimensions||{})[d]||{},anchors=di.global_anchors||{},criteria=(di.scenario_criteria||[]).map(esc).join(' · '),anchorText=Object.entries(anchors).map(([n,a])=>`<b>${esc(n)}</b> ${esc(typeof a==='string'?a:JSON.stringify(a))}`).join('<br>');const note=((it.findings||[]).find(f=>f.dimension===d)||{}).finding||'';return `<div class="ev"><div><strong>${d} — ${esc(labels[d])}</strong><div class="anchor">${criteria||esc(di.applicability?.rationale||'Use the global anchors.')}</div><div class="anchors">${anchorText}</div></div><div><div class="score">${[0,1,2,3,4].map(n=>`<button data-d="${d}" data-n="${n}" class="${it.scores[d]===n?'selected':''}">${n}</button>`).join('')}</div><div class="anchor">Select the demonstrated anchor.</div></div><textarea data-note="${d}" placeholder="Evidence finding${Number.isInteger(it.scores[d])&&it.scores[d]<=2?' (required for this low score)':''}">${esc(note)}</textarea></div>`}).join('');
 document.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>{it.scores[b.dataset.d]=Number(b.dataset.n);render();schedule()});document.querySelectorAll('[data-note]').forEach(t=>t.oninput=()=>{const d=t.dataset.note;it.findings=(it.findings||[]).filter(f=>f.dimension!==d);if(t.value.trim())it.findings.push({dimension:d,score:it.scores[d],finding:t.value.trim()});schedule()});
 const failures=(evaluation.failure_conditions||[]);$('failures').innerHTML=failures.length?failures.map((f,n)=>`<label class="fail"><input type="checkbox" data-f="${n}" ${(it.failure_conditions_observed||[]).includes(f)?'checked':''}> ${esc(f)}</label>`).join(''):'None declared.';document.querySelectorAll('[data-f]').forEach(c=>c.onchange=()=>{const f=failures[Number(c.dataset.f)],set=new Set(it.failure_conditions_observed||[]);c.checked?set.add(f):set.delete(f);it.failure_conditions_observed=[...set];schedule()});
 const gd=it.grounding_diagnostics||{};$('groundAssessed').checked=gd.grounding_assessed===true;$('gUnsupported').value=gd.unsupported_assertions||0;$('gFabricated').value=gd.fabricated_apis_or_entities||0;$('gCitations').value=gd.invalid_citations_or_provenance||0;$('gSuccess').value=gd.false_success_or_test_claims||0;$('gAbstention').value=gd.abstention_applicable===true?(gd.appropriate_abstention?'appropriate':'inappropriate'):'';$('grounding').value=(gd.notes||[]).join('\n');['groundAssessed','gUnsupported','gFabricated','gCitations','gSuccess','gAbstention','grounding'].forEach(id=>$(id).oninput=()=>{if(!$('groundAssessed').checked){it.grounding_diagnostics=null}else{const abst=$('gAbstention').value;it.grounding_diagnostics={grounding_assessed:true,unsupported_assertions:Number($('gUnsupported').value||0),fabricated_apis_or_entities:Number($('gFabricated').value||0),invalid_citations_or_provenance:Number($('gCitations').value||0),false_success_or_test_claims:Number($('gSuccess').value||0),abstention_applicable:abst?true:null,appropriate_abstention:abst?abst==='appropriate':null,notes:$('grounding').value.trim()?[$('grounding').value.trim()]:[]}}schedule()});renderTasks()}
function visible(it){const f=$('filter').value;return f==='all'||(f==='unscored'&&!completed(it))||(f==='low'&&low(it))}function renderTasks(){const done=items.filter(completed).length;$('progress').max=items.length;$('progress').value=done;$('count').textContent=`${done}/${items.length} scored`;$('tasks').innerHTML=items.map((it,n)=>visible(it)?`<button class="task ${completed(it)?'done':''} ${n===index?'active':''}" data-i="${n}">${n+1}. ${esc(it.task_label)}</button>`:'').join('');document.querySelectorAll('[data-i]').forEach(b=>b.onclick=()=>{index=Number(b.dataset.i);render()})}
function move(delta){let n=index;do{n=(n+delta+items.length)%items.length}while(n!==index&&!visible(items[n]));index=n;render()}
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('filter').onchange=renderTasks;['raterName','raterId','conflict'].forEach(id=>$(id).oninput=schedule);
$('export').onclick=()=>{syncIdentity();const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(sheet,null,2)],{type:'application/json'}));a.download=sheet.run_id+'-human-scoresheet.json';a.click();URL.revokeObjectURL(a.href)};
$('submit').onclick=async()=>{syncIdentity();if(!confirm('Submit immutable human rating records and refresh all reports?'))return;$('submit').disabled=true;$('status').className='status';$('status').textContent='Validating, recording evidence, analyzing, and generating reports…';try{const r=await api('/api/submit','POST',sheet);$('status').className='status ok';$('status').textContent=`Complete · ${r.ratings_written} immutable ratings recorded · reports refreshed`;$('submit').textContent='Submitted'}catch(e){$('submit').disabled=false;$('status').className='status error';$('status').textContent=e.message}};
document.addEventListener('keydown',e=>{if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName))return;if(e.key==='ArrowRight'||e.key==='j')move(1);if(e.key==='ArrowLeft'||e.key==='k')move(-1)});
api('/api/review').then(d=>{sheet=d.sheet;items=sheet.items;render()}).catch(e=>{$('title').textContent='Could not load review';$('status').className='status error';$('status').textContent=e.message});
</script></body></html>'''


def _handler(session: ReviewSession, token: str, progress_callback=None):
    class Handler(BaseHTTPRequestHandler):
        def _authorized(self) -> bool:
            query = parse_qs(urlparse(self.path).query)
            supplied = self.headers.get("X-AIES-Review-Token") or (
                query.get("token", [""])[0])
            return secrets.compare_digest(supplied, token)

        def _send(self, status: int, body, content_type="application/json"):
            if content_type == "application/json":
                payload = json.dumps(body).encode("utf-8")
            else:
                payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", (
                "default-src 'self'; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'self'; "
                "img-src 'none'; object-src 'none'; frame-ancestors 'none'"))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(payload)

        def _json_body(self) -> dict:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise ReviewWorkspaceError("invalid Content-Length") from exc
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise ReviewWorkspaceError(
                    f"request body must be 1–{MAX_REQUEST_BYTES} bytes")
            try:
                return json.loads(self.rfile.read(length))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ReviewWorkspaceError("request body must be valid JSON") from exc

        def do_GET(self):  # noqa: N802
            if not self._authorized():
                self._send(403, {"error": "invalid or missing review token"})
                return
            path = urlparse(self.path).path
            if path == "/":
                self._send(200, _html(), "text/html")
            elif path == "/api/review":
                self._send(200, session.document())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            if not self._authorized():
                self._send(403, {"error": "invalid or missing review token"})
                return
            try:
                body = self._json_body()
                path = urlparse(self.path).path
                if path == "/api/draft":
                    result = session.save(body)
                elif path == "/api/submit":
                    result = session.submit(body, progress_callback)
                else:
                    self._send(404, {"error": "not found"})
                    return
                self._send(200, result)
            except Exception as exc:  # validator errors are user-facing here
                self._send(400, {"error": str(exc)})

        def log_message(self, *_args):
            return

    return Handler


def serve(run_id: str, *, port: int = 0, launch: bool = True,
          progress_callback=None) -> str:
    """Serve until interrupted; always bind to loopback, never the LAN."""
    session = ReviewSession(run_id)
    token = secrets.token_urlsafe(24)
    server = ThreadingHTTPServer(
        ("127.0.0.1", port), _handler(session, token, progress_callback))
    actual_port = int(server.server_address[1])
    url = f"http://127.0.0.1:{actual_port}/?token={token}"
    print("AIES optional Human EV Review Workspace")
    print(f"  run: {run_id}")
    print(f"  open: {url}")
    print("  security: loopback-only · random session token · no remote access")
    print("  authority: records evidence only; cannot grant qualification")
    print("  stop: Ctrl+C (autosaved draft remains in the run directory)")
    if launch:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return url
