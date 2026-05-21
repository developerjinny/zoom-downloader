#!/usr/bin/env python3
import http.server, threading, subprocess, os, json, webbrowser, re, sys
from datetime import datetime
from urllib.parse import parse_qs

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>Zoom Downloader</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+KR:wght@400;600&display=swap');
  *{box-sizing:border-box;margin:0;padding:0}
  :root{
    --bg:#0c0c0c;--panel:#141414;--border:#252525;
    --accent:#00e5ff;--accent2:#00a3b4;
    --text:#e0e0e0;--muted:#555;
    --success:#00e09e;--error:#ff3d6b;--warn:#ffb300;
  }
  body{background:var(--bg);color:var(--text);font-family:'IBM Plex Sans KR',sans-serif;
       min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:40px 20px}
  .wrap{width:100%;max-width:720px}
  h1{font-size:28px;font-weight:600;letter-spacing:-0.5px;margin-bottom:4px}
  h1 span{color:var(--accent)}
  .sub{color:var(--muted);font-size:13px;margin-bottom:32px}
  .divider{border:none;border-top:1px solid var(--border);margin:20px 0}
  label{display:block;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
  .field{margin-bottom:18px}
  textarea,input[type=text]{
    width:100%;background:var(--panel);color:var(--text);
    border:1px solid var(--border);border-radius:6px;
    padding:10px 14px;font-family:'IBM Plex Mono',monospace;font-size:12px;
    resize:vertical;outline:none;transition:border .2s;
  }
  textarea:focus,input[type=text]:focus{border-color:var(--accent)}
  .row{display:flex;gap:10px}
  .row .field{flex:1}
  .dir-row{display:flex;gap:8px;align-items:center}
  .dir-row input{flex:1}
  .btn{
    background:var(--accent);color:#000;border:none;border-radius:6px;
    padding:12px 24px;font-size:14px;font-weight:600;cursor:pointer;
    font-family:'IBM Plex Sans KR',sans-serif;transition:background .2s;
    width:100%;margin-top:4px;
  }
  .btn:hover{background:var(--accent2)}
  .btn:disabled{background:var(--muted);cursor:not-allowed;color:#888}
  .btn-sm{
    background:var(--panel);color:var(--text);border:1px solid var(--border);
    border-radius:5px;padding:6px 12px;font-size:12px;cursor:pointer;
    white-space:nowrap;transition:background .2s;font-family:inherit;
  }
  .btn-sm:hover{background:var(--border)}
  .progress-bar-wrap{height:4px;background:var(--panel);border-radius:2px;margin:14px 0 6px;overflow:hidden}
  .progress-bar{height:100%;width:0;background:var(--accent);border-radius:2px;transition:width .3s}
  .progress-bar.indeterminate{animation:slide 1.2s infinite;width:30%}
  @keyframes slide{0%{transform:translateX(-100%)}100%{transform:translateX(400%)}}
  .status{font-size:13px;color:var(--muted);margin-bottom:14px;min-height:18px}
  .log-wrap{background:var(--panel);border:1px solid var(--border);border-radius:6px;overflow:hidden}
  .log-header{display:flex;justify-content:space-between;align-items:center;
              padding:10px 14px;border-bottom:1px solid var(--border)}
  .log-header span{font-size:12px;font-weight:600;color:var(--text)}
  #log{font-family:'IBM Plex Mono',monospace;font-size:11px;line-height:1.7;
       padding:12px 14px;height:220px;overflow-y:auto;white-space:pre-wrap;word-break:break-all}
  .info{color:#888}.success{color:var(--success)}.error{color:var(--error)}
  .warn{color:var(--warn)}.accent{color:var(--accent)}
</style>
</head>
<body>
<div class="wrap">
  <h1>⬇ Zoom <span>Downloader</span></h1>
  <p class="sub">Zoom 녹화 영상을 쉽게 다운로드하세요</p>
  <hr class="divider">

  <div class="field">
    <label>🔗 다운로드 URL</label>
    <textarea id="url" rows="3" placeholder="https://ssrweb.zoom.us/replay.../Recording.mp4?..."></textarea>
  </div>

  <div class="field">
    <label>🍪 Cookie</label>
    <textarea id="cookie" rows="4" placeholder="_zm_mtk_guid=...; _zm_page_auth=...; cf_clearance=..."></textarea>
  </div>

  <div class="row">
    <div class="field">
      <label>💾 파일명</label>
      <input type="text" id="fname" value="zoom_recording.mp4">
    </div>
    <div class="field">
      <label>📁 저장 폴더</label>
      <div class="dir-row">
        <input type="text" id="folder" value="">
        <button class="btn-sm" onclick="chooseFolder()">찾기</button>
      </div>
    </div>
  </div>

  <button class="btn" id="dlbtn" onclick="startDownload()">⬇  다운로드 시작</button>

  <div class="progress-bar-wrap"><div class="progress-bar" id="bar"></div></div>
  <div class="status" id="status">대기 중</div>

  <div class="log-wrap">
    <div class="log-header">
      <span>📋 로그</span>
      <button class="btn-sm" onclick="clearLog()">지우기</button>
    </div>
    <div id="log"></div>
  </div>
</div>

<script>
const log = document.getElementById('log');
const bar = document.getElementById('bar');
const status = document.getElementById('status');
const btn = document.getElementById('dlbtn');

// 기본 저장 폴더
fetch('/default_dir').then(r=>r.json()).then(d=>{ document.getElementById('folder').value=d.dir });

function addLog(msg, cls='info'){
  const t=new Date().toTimeString().slice(0,8);
  const el=document.createElement('div');
  el.className=cls; el.textContent=`[${t}] ${msg}`;
  log.appendChild(el); log.scrollTop=log.scrollHeight;
}
function clearLog(){ log.innerHTML=''; }

function chooseFolder(){
  fetch('/choose_folder').then(r=>r.json()).then(d=>{
    if(d.folder) document.getElementById('folder').value=d.folder;
  });
}

function setLoading(on){
  btn.disabled=on;
  btn.textContent=on?'⏳  다운로드 중...':'⬇  다운로드 시작';
  bar.className='progress-bar'+(on?' indeterminate':'');
  if(!on) bar.style.width='0';
}

function startDownload(){
  const url=document.getElementById('url').value.trim();
  const cookie=document.getElementById('cookie').value.trim();
  const fname=document.getElementById('fname').value.trim();
  const folder=document.getElementById('folder').value.trim();
  if(!url||!cookie||!fname||!folder){alert('모든 항목을 입력해주세요.');return;}
  setLoading(true);
  addLog('다운로드 시작...','accent');

  const body=new URLSearchParams({url,cookie,fname,folder});
  fetch('/download',{method:'POST',body}).then(r=>r.json()).then(d=>{
    if(d.ok){
      addLog('✅ 완료! → '+d.path,'success');
      status.textContent='✅ 다운로드 완료!';
      status.style.color='var(--success)';
    } else {
      addLog('❌ 실패: '+d.error,'error');
      status.textContent='❌ 실패';
      status.style.color='var(--error)';
    }
    setLoading(false);
  });

  // 로그 폴링
  const poller=setInterval(()=>{
    fetch('/log_poll').then(r=>r.json()).then(d=>{
      d.lines.forEach(l=>{
        const cls=l.includes('ERROR')||l.includes('error')?'error':
                  l.includes('%')?'accent':
                  l.includes('Destination')||l.includes('100%')?'success':'info';
        addLog(l,cls);
        const m=l.match(/(\d+\.\d+)%/);
        if(m){status.textContent='다운로드 중... '+m[1]+'%';status.style.color='var(--accent)'}
      });
      if(!btn.disabled) clearInterval(poller);
    });
  },500);
}
</script>
</body>
</html>
"""

log_queue = []
log_lock  = threading.Lock()

def push_log(line):
    with log_lock:
        log_queue.append(line)

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == '/':
            self._html(HTML.encode())
        elif self.path == '/default_dir':
            d = os.path.expanduser('~/Downloads')
            self._json({'dir': d})
        elif self.path == '/choose_folder':
            folder = self._osascript_folder()
            self._json({'folder': folder})
        elif self.path == '/log_poll':
            with log_lock:
                lines = list(log_queue)
                log_queue.clear()
            self._json({'lines': lines})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/download':
            length = int(self.headers.get('Content-Length', 0))
            body   = parse_qs(self.rfile.read(length).decode())
            url    = body.get('url',[''])[0]
            cookie = body.get('cookie',[''])[0]
            fname  = body.get('fname',['zoom.mp4'])[0]
            folder = body.get('folder',[''])[0]
            if not fname.endswith('.mp4'):
                fname += '.mp4'
            out = os.path.join(folder, fname)
            ok, err, path = run_download(url, cookie, out)
            self._json({'ok': ok, 'error': err, 'path': path})

    def _html(self, data):
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)

    def _json(self, d):
        data = json.dumps(d, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(data)

    def _osascript_folder(self):
        try:
            r = subprocess.run(
                ['osascript','-e',
                 'POSIX path of (choose folder with prompt "저장 폴더 선택")'],
                capture_output=True, text=True, timeout=30)
            return r.stdout.strip().rstrip('/')
        except:
            return os.path.expanduser('~/Downloads')

def find_tool():
    candidates = [
        '/opt/homebrew/bin/yt-dlp',
        '/usr/local/bin/yt-dlp',
        '/opt/homebrew/bin/youtube-dl',
        '/usr/local/bin/youtube-dl',
        'yt-dlp',
        'youtube-dl',
    ]
    for c in candidates:
        try:
            subprocess.run([c, '--version'], capture_output=True, check=True)
            return c
        except:
            continue
    return None

def run_download(url, cookie, out):
    tool = find_tool()
    if not tool:
        msg = 'yt-dlp를 찾을 수 없습니다. 터미널에서 brew install yt-dlp 실행 후 재시도하세요.'
        push_log(msg)
        return False, msg, ''
    cmd = [tool, '-o', out, '--referer', 'https://zoom.us/',
           '--add-header', f'cookie: {cookie}', url]
    push_log(f'실행: {tool}')
    push_log(f'저장: {out}')
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            line = line.rstrip()
            if line: push_log(line)
        proc.wait()
        if proc.returncode == 0:
            return True, '', out
        else:
            return False, f'exit code {proc.returncode}', ''
    except FileNotFoundError:
        msg = f'{tool} 을 찾을 수 없습니다. brew install yt-dlp 실행 필요'
        push_log(msg)
        return False, msg, ''
    except Exception as e:
        push_log(str(e))
        return False, str(e), ''

def main():
    port = 18765
    server = http.server.HTTPServer(('127.0.0.1', port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    webbrowser.open(f'http://127.0.0.1:{port}')
    print(f'Zoom Downloader 실행 중: http://127.0.0.1:{port}')
    try:
        t.join()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == '__main__':
    main()
