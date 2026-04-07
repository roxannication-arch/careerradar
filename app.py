#!/usr/bin/env python3
import sqlite3, os
from pathlib import Path
from flask import Flask, jsonify, request, Response

DB_PATH = Path(__file__).resolve().parent / "radar.db"
app = Flask(__name__)



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
  <div style="display:flex;align-items:center;gap:12px;"><button onclick="refresh()" id="rbtn" style="padding:6px 14px;border-radius:8px;border:1px solid #ddd;background:white;font-size:0.78rem;color:#555;cursor:pointer;">🔄 Обновить</button><div class="live"><div class="dot"></div>в сети</div></div>
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
async function refresh(){
  const btn=document.getElementById('rbtn');
  btn.textContent='⏳ Загружаю...';btn.disabled=true;
  try{
    const r=await fetch('/api/refresh',{method:'POST'});
    const d=await r.json();
    btn.textContent='✅ '+d.message;
    setTimeout(()=>{btn.textContent='🔄 Обновить';btn.disabled=false;location.reload();},2000);
  }catch(e){btn.textContent='❌ Ошибка';btn.disabled=false;}
}
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
    import base64
    data = base64.b64decode('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')
    return Response(data, mimetype='image/png')

@app.route('/api/data')
def api_data():
    conn = get_db()
    try:
        articles = conn.execute("SELECT title, url, source, published_date, category FROM articles ORDER BY COALESCE(published_date,'') DESC").fetchall()
        insights = conn.execute("SELECT created_at, content, article_count FROM insights ORDER BY created_at DESC LIMIT 20").fetchall()
        return jsonify({"articles":[dict(a) for a in articles],"insights":[dict(i) for i in insights]})
    finally:
        conn.close()

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    try:
        from collector import collect, init_db
        from analyzer import analyze
        init_db()
        new_articles = collect()
        new_insights = analyze()
        return jsonify({"message": f"+{new_articles} статей, +{new_insights} инсайтов", "ok": True})
    except Exception as e:
        return jsonify({"message": f"Ошибка: {e}", "ok": False})

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
