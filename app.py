#!/usr/bin/env python3
import sqlite3, os
from pathlib import Path
from flask import Flask, jsonify, request, Response

DB_PATH = Path(__file__).resolve().parent / "radar.db"
app = Flask(__name__)

ICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="115" fill="#f0f0eb"/>
  <circle cx="256" cy="256" r="55" fill="none" stroke="#1a1a1a" stroke-width="20"/>
  <circle cx="256" cy="256" r="110" fill="none" stroke="#1a1a1a" stroke-width="12" stroke-opacity="0.35"/>
  <circle cx="256" cy="256" r="168" fill="none" stroke="#1a1a1a" stroke-width="7" stroke-opacity="0.15"/>
  <circle cx="256" cy="256" r="11" fill="#27ae60"/>
  <line x1="256" y1="201" x2="256" y2="148" stroke="#27ae60" stroke-width="7" stroke-linecap="round"/>
  <line x1="256" y1="201" x2="300" y2="232" stroke="#27ae60" stroke-width="5" stroke-linecap="round" stroke-opacity="0.6"/>
</svg>'''

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Career Radar">
<link rel="apple-touch-icon" href="/icon">
<link rel="icon" href="/icon" type="image/svg+xml">
<title>Career Radar</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f0;color:#1a1a1a;}
.topbar{background:white;border-bottom:1px solid #eee;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;}
.topbar h1{font-size:1.1rem;font-weight:600;}
.topbar p{font-size:0.72rem;color:#999;margin-top:1px;}
.live{display:flex;align-items:center;gap:5px;font-size:0.78rem;color:#27ae60;font-weight:500;}
.dot{width:7px;height:7px;border-radius:50%;background:#27ae60;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.wrap{max-width:1200px;margin:0 auto;padding:20px 16px;}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;}
@media(max-width:600px){.stats{grid-template-columns:repeat(2,1fr);}}
.stat{background:white;border-radius:12px;padding:14px 16px;border:1px solid #eee;}
.stat-label{font-size:0.68rem;color:#aaa;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px;}
.stat-val{font-size:2rem;font-weight:700;line-height:1;}
.red{color:#c0392b;}.blue{color:#2471a3;}.purple{color:#7d3c98;}
.pattern{background:white;border-radius:12px;border:1px solid #eee;padding:18px 20px;margin-bottom:20px;}
.pattern-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.pattern-tag{font-size:0.68rem;font-weight:600;color:#aaa;text-transform:uppercase;letter-spacing:.07em;}
.pattern-date{font-size:0.72rem;color:#bbb;}
.pattern-title{font-size:1rem;font-weight:600;margin-bottom:8px;color:#1a1a1a;}
.pattern-body{font-size:0.88rem;line-height:1.65;color:#333;margin-bottom:12px;}
.pattern-vывод{background:#f0f7ff;border-left:3px solid #2471a3;padding:10px 14px;border-radius:0 8px 8px 0;font-size:0.84rem;color:#444;line-height:1.55;margin-bottom:14px;}
.btns{display:flex;gap:8px;flex-wrap:wrap;}
.btn{padding:7px 16px;border-radius:8px;border:1px solid #ddd;background:white;font-size:0.8rem;color:#333;cursor:pointer;}
.btn:hover{background:#f5f5f5;}
.btn.dark{background:#1a1a1a;color:white;border-color:#1a1a1a;}
.btn.dark:hover{background:#333;}
.grid{display:grid;grid-template-columns:1fr 300px;gap:16px;}
@media(max-width:768px){.grid{grid-template-columns:1fr;}}
.card{background:white;border-radius:12px;border:1px solid #eee;overflow:hidden;margin-bottom:16px;}
.card-hdr{padding:12px 16px 10px;border-bottom:1px solid #f0f0f0;font-size:0.68rem;font-weight:600;color:#aaa;text-transform:uppercase;letter-spacing:.07em;}
.filters{display:flex;gap:6px;flex-wrap:wrap;padding:10px 14px;border-bottom:1px solid #f0f0f0;}
.fbtn{padding:4px 12px;border-radius:20px;border:1px solid #ddd;background:white;font-size:0.77rem;color:#555;cursor:pointer;}
.fbtn.on{background:#1a1a1a;color:white;border-color:#1a1a1a;}
.ni{padding:11px 14px;border-bottom:1px solid #f5f5f5;display:flex;gap:9px;align-items:flex-start;}
.ni:hover{background:#fafafa;}.ni:last-child{border-bottom:none;}
.badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:500;flex-shrink:0;margin-top:2px;white-space:nowrap;}
.b-layoffs{background:#fde8e8;color:#c0392b;}
.b-hiring{background:#e8f8e8;color:#1e8449;}
.b-hiring_freeze{background:#fef5e7;color:#d35400;}
.b-startup{background:#eaf2ff;color:#1a6fa8;}
.b-visa{background:#f5eef8;color:#7d3c98;}
.b-remote_work{background:#f2f2f2;color:#555;}
.b-tech{background:#e8f4fd;color:#1565c0;}
.b-ai_jobs{background:#e8fdf5;color:#0e6655;}
.nt{font-size:.86rem;font-weight:500;line-height:1.4;margin-bottom:2px;}
.nt a{color:inherit;text-decoration:none;}.nt a:hover{color:#2471a3;}
.nm{font-size:.7rem;color:#bbb;}
.ii{padding:12px 14px;border-bottom:1px solid #f5f5f5;}
.ii:last-child{border-bottom:none;}
.id{font-size:.7rem;color:#bbb;margin-bottom:5px;}
.ib{font-size:.8rem;line-height:1.6;color:#444;}
.ib strong{font-weight:600;color:#222;}
.tr{display:flex;align-items:center;gap:8px;padding:5px 14px;}
.tn{font-size:.76rem;color:#666;width:105px;flex-shrink:0;}
.tb{flex:1;height:5px;background:#f0f0f0;border-radius:3px;overflow:hidden;}
.tf{height:100%;border-radius:3px;}
.tc{font-size:.72rem;color:#bbb;width:26px;text-align:right;}
.more{display:block;width:100%;padding:10px;text-align:center;font-size:.8rem;color:#999;background:#fafafa;border:none;border-top:1px solid #f0f0f0;cursor:pointer;}
.empty{padding:28px 16px;text-align:center;color:#bbb;font-size:.83rem;line-height:1.6;}
.mb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;align-items:center;justify-content:center;}
.mb.open{display:flex;}
.mo{background:white;border-radius:16px;padding:24px;max-width:560px;width:90%;max-height:80vh;overflow-y:auto;}
.mo h3{font-size:1rem;margin-bottom:12px;}
.mo textarea{width:100%;border:1px solid #eee;border-radius:8px;padding:12px;font-size:.85rem;line-height:1.6;resize:vertical;min-height:180px;font-family:inherit;color:#333;}
.ma{display:flex;gap:8px;margin-top:12px;justify-content:flex-end;}
.bc{padding:7px 16px;border-radius:8px;border:1px solid #ddd;background:white;cursor:pointer;font-size:.82rem;}
.bk{padding:7px 16px;border-radius:8px;border:none;background:#1a1a1a;color:white;cursor:pointer;font-size:.82rem;}
</style>
</head>
<body>
<div class="topbar">
  <div><h1>📡 Career Radar</h1><p>Разведка рынка труда США</p></div>
  <div class="live"><div class="dot"></div>в сети</div>
</div>
<div class="wrap">
  <div class="stats">
    <div class="stat"><div class="stat-label">Всего статей</div><div class="stat-val" id="st">—</div></div>
    <div class="stat"><div class="stat-label">Увольнения</div><div class="stat-val red" id="sl">—</div></div>
    <div class="stat"><div class="stat-label">Стартапы</div><div class="stat-val blue" id="ss">—</div></div>
    <div class="stat"><div class="stat-label">Инсайтов</div><div class="stat-val purple" id="si">—</div></div>
  </div>
  <div class="pattern" id="pblock" style="display:none">
    <div class="pattern-top">
      <div class="pattern-tag">AI Insight · Паттерн дня</div>
      <div class="pattern-date" id="pdate"></div>
    </div>
    <div class="pattern-title" id="ptitle"></div>
    <div class="pattern-body" id="pbody"></div>
    <div class="pattern-vывод" id="pvyvod" style="display:none"></div>
    <div class="btns">
      <button class="btn dark" onclick="gen('post')">📱 Telegram-пост</button>
      <button class="btn" onclick="gen('thread')">🧵 Threads-провокация</button>
      <button class="btn" onclick="gen('analysis')">📊 Полный анализ</button>
    </div>
  </div>
  <div class="grid">
    <div>
      <div class="card">
        <div class="card-hdr">Лента новостей</div>
        <div class="filters" id="filters"><button class="fbtn on" data-cat="all" onclick="setF('all')">Все</button></div>
        <div id="nlist"></div>
        <button class="more" id="more" onclick="more()" style="display:none">Загрузить ещё</button>
      </div>
    </div>
    <div>
      <div class="card">
        <div class="card-hdr">Все инсайты</div>
        <div id="ilist"><div class="empty">Нет инсайтов.<br>Запусти python3 analyzer.py</div></div>
      </div>
      <div class="card">
        <div class="card-hdr">Тренды</div>
        <div id="trends" style="padding:8px 0;"></div>
      </div>
    </div>
  </div>
</div>
<div class="mb" id="modal" onclick="if(event.target===this)closeM()">
  <div class="mo">
    <h3 id="mtitle"></h3>
    <textarea id="mtext"></textarea>
    <div class="ma">
      <button class="bc" onclick="closeM()">Закрыть</button>
      <button class="bk" onclick="copyT()">Скопировать</button>
    </div>
  </div>
</div>
<script>
const L={layoffs:'увольнения',hiring:'найм',hiring_freeze:'заморозка найма',startup:'стартапы',visa:'визы',remote_work:'удалёнка',tech:'технологии',ai_jobs:'AI & работа'};
const B={layoffs:'b-layoffs',hiring:'b-hiring',hiring_freeze:'b-hiring_freeze',startup:'b-startup',visa:'b-visa',remote_work:'b-remote_work',tech:'b-tech',ai_jobs:'b-ai_jobs'};
const C={layoffs:'#c0392b',hiring:'#27ae60',hiring_freeze:'#e67e22',startup:'#2471a3',visa:'#8e44ad',remote_work:'#888',tech:'#1565c0',ai_jobs:'#0e6655'};
let all=[],f='all',n=30,ins='';
function ta(d){if(!d)return'';const m=Math.floor((Date.now()-new Date(d))/60000);if(m<60)return m+' мин назад';if(m<1440)return Math.floor(m/60)+' ч назад';return Math.floor(m/1440)+' дн назад';}
function bdg(c){return`<span class="badge ${B[c]||'b-tech'}">${L[c]||c}</span>`;}
function mdToHtml(t){return t.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/## (.+)/g,'<strong>$1</strong>').replace(/\n\n/g,'<br><br>').replace(/\n/g,'<br>');}
function rNews(){
  const fil=f==='all'?all:all.filter(a=>a.category===f);
  document.getElementById('nlist').innerHTML=fil.slice(0,n).map(a=>`<div class="ni">${bdg(a.category)}<div><div class="nt"><a href="${a.url}" target="_blank">${a.title}</a></div><div class="nm">${a.source} · ${ta(a.published_date)}</div></div></div>`).join('');
  document.getElementById('more').style.display=fil.length>n?'block':'none';
}
function setF(c){f=c;n=30;document.querySelectorAll('.fbtn').forEach(b=>b.classList.toggle('on',b.dataset.cat===c));rNews();}
function more(){n+=30;rNews();}
function extractSection(text,heading){const re=new RegExp('##\\s*'+heading+'\\s*\\n([\\s\\S]*?)(?=##|$)');const m=text.match(re);return m?m[1].trim():'';}
function genFromIdea(idx){
  const idea=window['_idea_'+idx]||ins;
  document.getElementById('mtitle').textContent='📱 Пост для Telegram';
  document.getElementById('mtext').value='Генерирую...';
  document.getElementById('modal').classList.add('open');
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:`Напиши пост для Telegram-канала на русском. Длина: 800-1200 символов. Цепляющий первый абзац → детали → вывод или вопрос. Без хэштегов. Тема — рынок труда США.\n\nИдея: ${idea}`})}).then(r=>r.json()).then(d=>{document.getElementById('mtext').value=d.text||'Ошибка';});
}
function genThreadFromIdea(idx){
  const idea=window['_idea_'+idx]||ins;
  document.getElementById('mtitle').textContent='🧵 Провокация для Threads';
  document.getElementById('mtext').value='Генерирую...';
  document.getElementById('modal').classList.add('open');
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:`Напиши провокационный пост для Threads на русском. До 500 символов. Острое мнение о рынке труда США. Без хэштегов. Только текст.\n\nИдея: ${idea}`})}).then(r=>r.json()).then(d=>{document.getElementById('mtext').value=d.text||'Ошибка';});
}
function genIdea(){
  document.getElementById('mtitle').textContent='📱 Пост для Telegram';
  document.getElementById('mtext').value='Генерирую...';
  document.getElementById('modal').classList.add('open');
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:`Напиши пост для Telegram на русском. Длина: 800-1200 символов. Цепляющий первый абзац → детали → вывод. Без хэштегов.\n\nИдея: ${window._idea||ins}`})}).then(r=>r.json()).then(d=>{document.getElementById('mtext').value=d.text||'Ошибка';});
}
function genIdeaThread(){
  document.getElementById('mtitle').textContent='🧵 Провокация для Threads';
  document.getElementById('mtext').value='Генерирую...';
  document.getElementById('modal').classList.add('open');
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:`Напиши провокационный пост для Threads на русском. До 500 символов. Острое мнение о рынке труда США. Без хэштегов. Только текст.\n\nИдея: ${window._idea||ins}`})}).then(r=>r.json()).then(d=>{document.getElementById('mtext').value=d.text||'Ошибка';});
}
function gen(type){
  const T={post:'📱 Пост для Telegram',thread:'🧵 Провокация для Threads',analysis:'📊 Полный анализ'};
  const P={
    post:`Напиши пост для Telegram-канала на русском. Длина: 800-1200 символов. Цепляющий первый абзац → детали → вывод или вопрос. Без хэштегов. Тема — рынок труда США, аудитория — русскоязычные люди которые ищут работу в США.\n\n${ins}`,
    thread:`Напиши провокационный пост для Threads на русском. До 500 символов. Острое мнение или неочевидный факт о рынке труда США. Без хэштегов. Только текст.\n\n${ins}`,
    analysis:`Сделай полный аналитический разбор на русском. Структура: ситуация → причины → последствия → что делать job seekers прямо сейчас.\n\n${ins}`
  };
  document.getElementById('mtitle').textContent=T[type];
  document.getElementById('mtext').value='Генерирую...';
  document.getElementById('modal').classList.add('open');
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:P[type]})}).then(r=>r.json()).then(d=>{document.getElementById('mtext').value=d.text||'Ошибка';});
}
function closeM(){document.getElementById('modal').classList.remove('open');}
function copyT(){navigator.clipboard.writeText(document.getElementById('mtext').value);const b=document.querySelector('.bk');b.textContent='✓ Скопировано';setTimeout(()=>b.textContent='Скопировать',2000);}
async function init(){
  const d=await fetch('/api/data').then(r=>r.json());
  all=d.articles;
  document.getElementById('st').textContent=all.length;
  document.getElementById('sl').textContent=all.filter(a=>a.category==='layoffs').length;
  document.getElementById('ss').textContent=all.filter(a=>a.category==='startup').length;
  document.getElementById('si').textContent=d.insights.length;
  const cats=[...new Set(all.map(a=>a.category))].sort();
  const fc=document.getElementById('filters');
  cats.forEach(c=>{const b=document.createElement('button');b.className='fbtn';b.dataset.cat=c;b.textContent=L[c]||c;b.onclick=()=>setF(c);fc.appendChild(b);});
  rNews();
  if(d.insights.length>0){
    ins=d.insights[0].content;
    const date=(d.insights[0].created_at||'').slice(0,10);
    const pattern=extractSection(ins,'Паттерн дня');
    const vyvod=extractSection(ins,'Стратегический вывод');
    const idea=extractSection(ins,'Идея для контента');
    document.getElementById('pdate').textContent=date;
    document.getElementById('ptitle').textContent='Паттерн дня';
    document.getElementById('pbody').innerHTML=mdToHtml(pattern||ins.replace(/##[^\n]*/g,'').trim().slice(0,400));
    if(vyvod){document.getElementById('pvyvod').innerHTML='→ '+mdToHtml(vyvod.slice(0,300));document.getElementById('pvyvod').style.display='block';}
    if(idea){
      const ideaEl=document.createElement('div');
      ideaEl.style='margin-top:12px;padding:12px 14px;background:#f9f9f6;border-radius:8px;border:1px solid #eee;';
      ideaEl.innerHTML=`<div style="font-size:.68rem;font-weight:600;color:#aaa;text-transform:uppercase;letter-spacing:.07em;margin-bottom:6px;">Идея для контента</div><div style="font-size:.84rem;color:#333;line-height:1.55;margin-bottom:10px;">${mdToHtml(idea)}</div><div class="btns"><button class="btn dark" onclick="genIdea()">📱 Telegram-пост</button><button class="btn" onclick="genIdeaThread()">🧵 Threads-провокация</button></div>`;
      document.getElementById('pblock').appendChild(ideaEl);
      window._idea=idea;
    }
    document.getElementById('pblock').style.display='block';
  }
  const il=document.getElementById('ilist');
  if(d.insights.length===0){il.innerHTML='<div class="empty">Нет инсайтов.<br>Запусти python3 analyzer.py</div>';}
  else{
    il.innerHTML=d.insights.slice(0,8).map((i,idx)=>{
      const date=(i.created_at||'').slice(0,16).replace('T',' ');
      const ideaMatch=i.content.match(/##\s*Идея для контента\s*\n([\s\S]*?)(?=##|$)/);
      const idea=ideaMatch?ideaMatch[1].trim():'';
      const clean=mdToHtml(i.content);
      const ideaBtns=idea?`<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;"><button class="btn dark" style="font-size:.75rem;padding:5px 12px;" onclick="genFromIdea(${idx})">📱 Пост</button><button class="btn" style="font-size:.75rem;padding:5px 12px;" onclick="genThreadFromIdea(${idx})">🧵 Тред</button></div>`:'';
      window['_idea_'+idx]=idea||i.content;
      return`<div class="ii"><div class="id">${date} · ${i.article_count} ст.</div><div class="ib">${clean}</div>${ideaBtns}</div>`;
    }).join('');
  }
  const counts={};all.forEach(a=>{counts[a.category]=(counts[a.category]||0)+1;});
  const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  const mx=sorted[0]?.[1]||1;
  document.getElementById('trends').innerHTML=sorted.map(([c,v])=>`<div class="tr"><div class="tn">${L[c]||c}</div><div class="tb"><div class="tf" style="width:${Math.round(v/mx*100)}%;background:${C[c]||'#888'}"></div></div><div class="tc">${v}</div></div>`).join('');
}
init();
</script>
</body>
</html>"""

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return HTML

@app.route('/icon')
def icon():
    return Response(ICON_SVG, mimetype='image/svg+xml')

@app.route('/api/data')
def api_data():
    conn = get_db()
    try:
        articles = conn.execute("SELECT title, url, source, published_date, category FROM articles ORDER BY COALESCE(published_date,'') DESC").fetchall()
        insights = conn.execute("SELECT created_at, content, article_count FROM insights ORDER BY created_at DESC LIMIT 20").fetchall()
        return jsonify({"articles":[dict(a) for a in articles],"insights":[dict(i) for i in insights]})
    finally:
        conn.close()

@app.route('/api/generate', methods=['POST'])
def api_generate():
    from dotenv import load_dotenv
    load_dotenv(DB_PATH.parent / ".env")
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY",""))
        data = request.json
        msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1024, messages=[{"role":"user","content":data["prompt"]}])
        return jsonify({"text": msg.content[0].text})
    except Exception as e:
        return jsonify({"text": f"Ошибка: {e}"})

if __name__ == '__main__':
    print("🚀 Career Radar: http://localhost:5000")

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port, debug=False)
