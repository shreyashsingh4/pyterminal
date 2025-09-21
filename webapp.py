# webapp.py
from pathlib import Path
import shlex

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from utils import Sandbox
from shell import Shell
from nl_parser import parse_nl

# ---------------- App + Shell ----------------
app = FastAPI(title="PyTerminal (Web)")
ROOT = Path(__file__).parent.resolve()

sb = Sandbox(ROOT)          # sandboxed to project root
sh = Shell(sb)


# ---------------- Request model (for Swagger input box) ----------------
class RunReq(BaseModel):
    cmd: str


# ---------------- Routes ----------------
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)

@app.get("/whoami")
def whoami():
    return {"cwd": sb.pwd()}

@app.post("/run")
def run(body: RunReq):
    line = (body.cmd or "").strip()
    try:
        # NL mode
        if line.startswith("nl "):
            plans = parse_nl(line[3:])
            if not plans:
                return {"cwd": sb.pwd(), "output": "", "error": "Could not parse that into commands."}
            outputs = []
            for p in plans:
                # parse_nl typically returns tokenized commands (list[str])
                out = sh.run(p) or ""
                outputs.append(f"# {p!r}\n{out}")
            return {"cwd": sb.pwd(), "output": "\n".join(outputs)}

        # Regular shell mode
        args = shlex.split(line) if line else []
        out = sh.run(args)
        return {"cwd": sb.pwd(), "output": out or "", "error": ""}
    except SystemExit:
        return {"cwd": sb.pwd(), "output": "Goodbye!", "error": ""}
    except Exception as e:
        return {"cwd": sb.pwd(), "output": "", "error": f"Error: {e}"}


# ---------------- HTML (UI) ----------------
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>PyTerminal · Web</title>
  <style>
    :root{
      --bg:#0b1220; --panel:#111a2b; --panel2:#0f1828; --text:#e6edf3; --muted:#9db0c9;
      --accent:#6ee7ff; --accent2:#8b5cf6; --border:#1e293b; --chip:#152238;
      --ok:#22c55e; --err:#ef4444;
    }
    *{box-sizing:border-box}
    body{margin:0;background:#0b1220;color:var(--text);font:14px/1.45 ui-monospace,Menlo,Consolas,monospace}
    .wrap{max-width:900px;margin:40px auto;padding:0 16px}
    .card{
      background:linear-gradient(180deg,var(--panel) 0%,var(--panel2) 100%);
      border:1px solid var(--border); border-radius:14px; box-shadow:0 12px 30px rgba(0,0,0,.4);
      overflow:hidden;
    }
    .head{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid var(--border);}
    .title{font-weight:700;color:var(--accent)}
    .badge{display:inline-flex;gap:6px;align-items:center;padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:var(--chip);color:var(--muted);font-size:12px;margin-left:8px}
    .dot{width:6px;height:6px;border-radius:50%;background:var(--ok)}
    #out{height:380px;padding:14px 16px;white-space:pre-wrap;overflow:auto;background:#0b1220;}
    .controls{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
    #cmd{flex:1;background:#0b1220;border:1px solid var(--border);border-radius:10px;padding:10px;color:var(--text)}
    button{background:#14233b;border:1px solid var(--border);color:var(--text);padding:8px 12px;border-radius:10px;cursor:pointer}
    button:hover{background:#0f1c32}
    .chips{padding:0 16px 14px;display:flex;gap:8px;flex-wrap:wrap}
    .chip{border:1px dashed var(--border);background:transparent;color:var(--muted);padding:6px 10px;border-radius:999px;cursor:pointer}
    .system{color:var(--muted)} .err{color:var(--err)}
    footer{color:var(--muted);font-size:12px;text-align:center;padding:10px}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="head">
        <div class="title">PyTerminal <span class="system">· Web</span></div>
        <div><span class="badge"><span class="dot"></span>Sandboxed</span></div>
      </div>

      <div id="out"></div>

      <div class="controls">
        <input id="cmd" placeholder="Type a command (e.g., ls · pwd · ps · cpu · mem · nl create a folder test)" />
        <button onclick="runCmd()">Run ⚡</button>
        <button onclick="clearOut()">Clear 🧹</button>
      </div>

      <div class="chips">
        <button class="chip" onclick="setCmd('help')">help</button>
        <button class="chip" onclick="setCmd('ls')">ls</button>
        <button class="chip" onclick="setCmd('pwd')">pwd</button>
        <button class="chip" onclick="setCmd('mkdir demo')">mkdir demo</button>
        <button class="chip" onclick="setCmd('cd demo')">cd demo</button>
        <button class="chip" onclick="setCmd('ps')">ps</button>
        <button class="chip" onclick="setCmd('cpu')">cpu</button>
        <button class="chip" onclick="setCmd('mem')">mem</button>
        <button class="chip" onclick="setCmd('nl create a folder sample and then go to sample')">nl create…</button>
      </div>
    </div>
    <footer>PyTerminal © 2025</footer>
  </div>

  <script>
    function appendOut(text, cls="") {
      const out = document.getElementById("out");
      const div = document.createElement("div");
      if (cls) div.classList.add(cls);
      div.textContent = String(text || "").replace(/\\r\\n/g, "\\n");
      out.appendChild(div);
      out.scrollTop = out.scrollHeight;
    }

    function clearOut() {
      document.getElementById("out").innerHTML = "";
    }

    function setCmd(text) {
      const el = document.getElementById("cmd");
      el.value = text; el.focus();
    }

    async function runCmd() {
      const el = document.getElementById("cmd");
      const cmd = (el.value || "").trim();
      if (!cmd) return;

      appendOut("$ " + cmd, "system");

      try {
        const res = await fetch("/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ cmd })
        });

        // Read raw response, then try JSON; fall back to raw (HTML error etc.)
        const raw = await res.text();
        let data = null;

        try {
          data = JSON.parse(raw);
        } catch {
          appendOut(`HTTP ${res.status} • non-JSON response:`, "err");
          appendOut(raw, "err");
          el.value = "";
          return;
        }

        if (data.cwd)    appendOut("[cwd] " + data.cwd, "system");
        if (data.output) appendOut(data.output);
        if (data.error)  appendOut(data.error, "err");
        if (!data.output && !data.error) appendOut("(no output)");
      } catch (e) {
        appendOut("Fetch failed: " + e, "err");
        console.error(e);
      }

      el.value = "";
    }

    // Enter to run
    document.getElementById("cmd").addEventListener("keydown", function(e){
      if (e.key === "Enter") runCmd();
    });

    // Greet
    appendOut("Welcome to PyTerminal Web. Type 'help' to see commands.", "system");
  </script>
</body>
</html>
"""
