#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pockademy — server.py
HTTP Server, request routing, HTML builder.
แก้ UI/endpoint ที่นี่ไม่กระทบ engine เลย
"""
from engine import *
from engine import _make_ai_for_course, enrollment_preview_curriculum

# ── TTS cache directory ────────────────────────────────────────────
TTS_DIR = DATA_DIR / "tts_cache"
TTS_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# WEB UI HTML v2.0
# ═══════════════════════════════════════════════════════════════════
def build_html() -> str:
    providers_json   = json.dumps(PROVIDERS, ensure_ascii=False)
    mentor_json      = json.dumps(MENTOR_STYLES, ensure_ascii=False)
    levels_json      = json.dumps([[t, n] for t, n in GamificationEngine.LEVELS], ensure_ascii=False)
    badges_json      = json.dumps(GamificationEngine.BADGES, ensure_ascii=False)

    return r"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pockademy 0.1 — Level Up Your Brain</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=DM+Mono:wght@400;500&family=Noto+Sans+Thai:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
/* ═══ ARIA UNIVERSITY v2.0 — Ivory & Ink Academic Dark ═══ */
:root {
  /* ── Gameboy Retro-Future: Royal Purple × Vibrant Orange × Lemon ── */
  --ink:     #0f0520;
  --ink1:    #1a0835;
  --ink2:    #240d48;
  --ink3:    #311460;
  --border:  #5e2d9e;
  --gold:    #ff6b2b;
  --gold2:   #ff8c52;
  --gold3:   #c44a10;
  --ivory:   #f0e6ff;
  --ivory2:  #d4b8f0;
  --muted:   #8b6aad;
  --red:     #ff4757;
  --green:   #2ed573;
  --blue:    #5352ed;
  --purple:  #9b59ff;
  --yellow:  #ffd60a;
  --yellow2: #ffe94d;
  --serif:   'Press Start 2P', 'Noto Sans Thai', monospace;
  --mono:    'DM Mono', 'Press Start 2P', monospace;
  --sans:    'Noto Sans Thai', sans-serif;
  --radius:  16px;
  --pixel-border: 3px;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--ink);
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(155,89,255,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 90% 80%, rgba(255,107,43,0.10) 0%, transparent 50%);
  color: var(--ivory);
  font-family: var(--sans);
  min-height: 100vh;
  overflow-x: hidden;
}
/* Scanline retro overlay */
body::after {
  content: '';
  position: fixed; inset: 0;
  background-image: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.06) 2px,
    rgba(0,0,0,0.06) 4px
  );
  pointer-events: none;
  z-index: 9998;
  opacity: 0.6;
}

/* LAYOUT */
.shell { display: flex; min-height: 100vh; }

/* SIDEBAR */
.sidebar {
  width: 260px; min-width: 260px;
  background: var(--ink1);
  border-right: 2px solid var(--border);
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; bottom: 0;
  overflow-y: auto; z-index: 100;
  box-shadow: 4px 0 24px rgba(155,89,255,0.12);
}
.sidebar-brand {
  padding: 16px 16px 14px;
  border-bottom: 2px solid var(--border);
  background: linear-gradient(160deg, rgba(155,89,255,0.18) 0%, rgba(255,107,43,0.08) 60%, transparent 100%);
  position: relative;
  overflow: hidden;
}
.sidebar-brand::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--purple), var(--gold), var(--yellow), var(--purple));
  background-size: 200% 100%;
  animation: brand-scan 3s linear infinite;
}
@keyframes brand-scan { to { background-position: 200% 0; } }
.brand-logo-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.brand-logo-svg { flex-shrink: 0; filter: drop-shadow(0 0 6px rgba(255,214,10,0.6)); animation: logo-bob 3s ease-in-out infinite; width: 30px !important; height: 30px !important; }
@keyframes logo-bob { 0%,100%{transform:translateY(0) rotate(-2deg)} 50%{transform:translateY(-3px) rotate(2deg)} }
.brand-text-col { flex: 1; min-width: 0; overflow: hidden; }
.brand-name {
  font-family: var(--serif);
  font-size: 11px;
  color: var(--yellow);
  letter-spacing: 1.5px;
  text-shadow: 0 0 14px rgba(255,214,10,0.7), 2px 2px 0 rgba(0,0,0,0.6);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  display: block;
}
.sidebar-brand:hover .brand-name { animation: brand-glitch 0.25s steps(2) forwards; }
@keyframes brand-glitch {
  0%  { text-shadow: 0 0 14px rgba(255,214,10,0.7), 2px 2px 0 #000, -2px 0 rgba(255,71,87,0.6); }
  33% { text-shadow: 0 0 14px rgba(255,214,10,0.7),-2px 2px 0 #000,  2px 0 rgba(83,82,237,0.6); }
  66% { text-shadow: 0 0 14px rgba(255,214,10,0.7), 2px-2px 0 #000, -2px 0 rgba(255,71,87,0.4); }
  100%{ text-shadow: 0 0 14px rgba(255,214,10,0.7), 2px 2px 0 #000; }
}
.brand-sub { font-size: 7px; color: var(--muted); letter-spacing: 2px; margin-top: 3px; text-transform: uppercase; white-space: nowrap; }
.brand-meta-row { display: flex; align-items: center; justify-content: space-between; margin-top: 8px; }
.brand-ver { font-size: 8px; color: var(--gold); font-family: var(--mono); letter-spacing: 1px; }
.brand-online { display: flex; align-items: center; gap: 4px; font-size: 8px; color: var(--green); }
.brand-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px var(--green); animation: dot-blink 1.6s ease-in-out infinite; }
@keyframes dot-blink { 0%,100%{opacity:1;box-shadow:0 0 6px var(--green)} 50%{opacity:0.3;box-shadow:0 0 2px var(--green)} }
.brand-xp-badge { display: inline-flex; align-items: center; gap: 3px; background: rgba(155,89,255,0.2); border: 1px solid rgba(155,89,255,0.5); border-radius: 6px; padding: 2px 7px; font-size: 8px; color: var(--purple); font-family: var(--mono); margin-top: 5px; letter-spacing: 0.5px; }

/* EXP BAR — v2.0 */
.exp-bar-wrap { padding: 10px 16px; border-bottom: 1px solid var(--border); }
.exp-level-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
.exp-level-name { font-size: 11px; color: var(--gold); }
.exp-label { font-size: 10px; color: var(--muted); }
.exp-bar { height: 5px; background: var(--ink3); border-radius: 3px; overflow: hidden; }
.exp-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--purple) 0%, var(--gold) 60%, var(--yellow) 100%);
  border-radius: 3px;
  transition: width 0.6s;
  box-shadow: 0 0 8px rgba(255,107,43,0.5);
}

.sidebar-section { padding: 10px 16px 3px; font-size: 9px; color: var(--muted); letter-spacing: 3px; text-transform: uppercase; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 20px; cursor: pointer;
  color: var(--muted); font-size: 13px;
  border-left: 3px solid transparent;
  transition: all 0.12s;
}
.nav-item:hover {
  color: var(--ivory2);
  background: var(--ink2);
  border-left-color: var(--border);
}
.nav-item.active {
  color: var(--yellow);
  background: linear-gradient(90deg, rgba(155,89,255,0.15), transparent);
  border-left-color: var(--yellow);
  text-shadow: 0 0 8px rgba(255,214,10,0.4);
}
.nav-item .ni { font-size: 16px; width: 22px; text-align: center; }

.course-mini {
  margin: 4px 10px;
  padding: 10px 12px;
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.12s;
  box-shadow: 0 2px 0 rgba(0,0,0,0.3);
}
.course-mini:hover {
  border-color: var(--purple);
  transform: translateX(2px);
}
.course-mini.active-course {
  border-color: var(--yellow);
  background: rgba(255,214,10,0.05);
}
.course-mini-title { font-size: 12px; color: var(--ivory); font-weight: 600; }
.course-mini-sub { font-size: 10px; color: var(--muted); margin-top: 2px; }
.course-mini-prog { height: 3px; background: var(--ink3); border-radius: 2px; margin-top: 5px; overflow: hidden; }
.course-mini-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--purple), var(--gold));
  border-radius: 2px;
  transition: width 0.4s;
  box-shadow: 0 0 4px rgba(255,107,43,0.4);
}

.sidebar-footer { margin-top: auto; padding: 14px 20px; border-top: 1px solid var(--border); }
#timer-display { font-family: var(--mono); font-size: 12px; color: var(--gold); }

/* MAIN */
.main { flex: 1; margin-left: 260px; min-height: 100vh; background: var(--ink); }
.page { display: none; padding: 30px; max-width: 960px; }
.page.active { display: block; }
.page-header { margin-bottom: 24px; }
.page-title {
  font-family: var(--sans);
  font-weight: 700;
  font-size: 24px;
  color: var(--yellow);
  line-height: 1.2;
  margin-bottom: 5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 0 16px rgba(255,214,10,0.3);
}
.page-sub { font-size: 13px; color: var(--muted); }

/* CARDS */
.card {
  background: var(--ink1);
  border: 2px solid var(--border);
  border-radius: 20px;
  padding: 18px;
  margin-bottom: 18px;
  box-shadow: 0 4px 0 rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(155,89,255,0.15);
  transition: transform 0.15s, box-shadow 0.15s;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 0 rgba(0,0,0,0.4), 0 12px 32px rgba(155,89,255,0.15), inset 0 1px 0 rgba(155,89,255,0.2);
}
.card-title {
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 700;
  color: var(--gold2);
  margin-bottom: 12px;
  display: flex; align-items: center; gap: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.g3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.g4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
@media(max-width:800px){ .g2,.g3,.g4{ grid-template-columns:1fr; } }

/* STAT CARDS */
.stat-card {
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 3px 0 rgba(0,0,0,0.5), inset 0 1px 0 rgba(155,89,255,0.12);
}
.stat-val {
  font-family: var(--serif);
  font-size: 22px;
  color: var(--yellow);
  line-height: 1;
  text-shadow: 0 0 12px rgba(255,214,10,0.4);
}
.stat-lbl {
  font-size: 8px;
  color: var(--muted);
  letter-spacing: 2px;
  margin-top: 5px;
  text-transform: uppercase;
}
.prog-wrap { background: var(--ink3); border-radius: 4px; overflow: hidden; height: 6px; border: 1px solid var(--border); }
.prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--purple), var(--gold), var(--yellow));
  transition: width 0.5s;
  border-radius: 3px;
  box-shadow: 0 0 6px rgba(255,107,43,0.4);
}

/* SKILL PATH — v2.0 */
.skill-path { display: flex; flex-direction: column; gap: 0; }
.skill-item { display: flex; align-items: flex-start; gap: 14px; padding: 10px 0; position: relative; }
.skill-item::before { content:''; position:absolute; left:14px; top:36px; bottom:-10px; width:2px; background:var(--border); }
.skill-item:last-child::before { display:none; }
.skill-dot {
  width: 32px; height: 32px;
  border-radius: 8px;
  border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; flex-shrink: 0;
  transition: all 0.2s;
  color: var(--muted);
  margin-top: 2px;
  box-shadow: 0 2px 0 rgba(0,0,0,0.4);
}
.skill-item.done .skill-dot {
  background: var(--purple);
  border-color: var(--purple);
  color: white;
  box-shadow: 0 2px 0 rgba(0,0,0,0.4), 0 0 10px rgba(155,89,255,0.4);
}
.skill-item.active .skill-dot {
  border-color: var(--yellow);
  color: var(--yellow);
  box-shadow: 0 2px 0 rgba(0,0,0,0.4), 0 0 12px rgba(255,214,10,0.4);
}
.skill-item.exam .skill-dot {
  border-color: var(--blue);
  color: #a0a8ff;
  box-shadow: 0 2px 0 rgba(0,0,0,0.4);
}
.skill-info { flex: 1; }
.skill-title { font-size: 13px; color: var(--ivory); }
.skill-sub   { font-size: 11px; color: var(--muted); margin-top: 2px; }

/* DAY GRID */
.day-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 8px; }
.day-cell {
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 14px;
  padding: 10px 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.12s;
  min-height: 72px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.day-cell:hover {
  border-color: var(--purple);
  transform: translateY(-2px);
  box-shadow: 0 5px 0 rgba(0,0,0,0.4);
}
.day-cell.done { border-color: var(--green); }
.day-cell.done .dc-num { color: var(--green); text-shadow: 0 0 6px rgba(46,213,115,0.4); }
.day-cell.exam-day { border-color: var(--blue); }
.day-cell.active-day {
  border-color: var(--yellow);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4), 0 0 16px rgba(255,214,10,0.2);
}
.dc-num {
  font-family: var(--serif);
  font-size: 16px;
  color: var(--muted);
  line-height: 1;
}
.dc-lbl { font-size: 8px; color: var(--muted); margin-top: 4px; line-height: 1.3; word-break: break-word; }

/* CONTENT BOX */
.content-box { background: var(--ink); border: 1px solid var(--border); border-radius: 6px; padding: 14px; font-size: 14px; line-height: 1.9; white-space: pre-wrap; min-height: 80px; max-height: 460px; overflow-y: auto; color: var(--ivory2); }

/* BUTTONS */
.btn {
  background: linear-gradient(180deg, var(--gold2) 0%, var(--gold) 50%, var(--gold3) 100%);
  border: none;
  border-bottom: 4px solid var(--gold3);
  border-right: 2px solid rgba(0,0,0,0.3);
  color: #1a0835;
  font-weight: 700;
  padding: 10px 20px;
  border-radius: 14px;
  cursor: pointer;
  font-family: var(--sans);
  font-size: 12px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  transition: all 0.08s;
  box-shadow: 0 4px 0 var(--gold3), 0 6px 16px rgba(255,107,43,0.25);
  position: relative;
}
.btn:hover {
  filter: brightness(1.08);
  transform: translateY(2px);
  box-shadow: 0 2px 0 var(--gold3), 0 4px 10px rgba(255,107,43,0.2);
}
.btn:active {
  transform: translateY(4px);
  box-shadow: 0 0px 0 var(--gold3);
}
.btn-ghost {
  background: transparent;
  border: 2px solid var(--border);
  border-bottom: 4px solid rgba(0,0,0,0.3);
  color: var(--ivory2);
  box-shadow: 0 4px 0 rgba(0,0,0,0.3);
}
.btn-ghost:hover {
  border-color: var(--purple);
  color: var(--ivory);
}
.btn-red {
  background: linear-gradient(180deg, #ff6b7a, var(--red), #c0202f);
  border-bottom-color: #8b0000;
  color: white;
  box-shadow: 0 4px 0 #8b0000, 0 6px 16px rgba(255,71,87,0.25);
}
.btn-blue {
  background: linear-gradient(180deg, #7c7fff, var(--blue), #2a28cc);
  border-bottom-color: #1a18aa;
  color: white;
  box-shadow: 0 4px 0 #1a18aa, 0 6px 16px rgba(83,82,237,0.25);
}
.btn-purple {
  background: linear-gradient(180deg, #c07eff, var(--purple), #5a20cc);
  border-bottom-color: #3d0f9e;
  color: white;
  box-shadow: 0 4px 0 #3d0f9e, 0 6px 16px rgba(155,89,255,0.3);
}
.btn-sm { padding: 6px 13px; font-size: 11px; border-radius: 10px; }
.btn-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }

/* INPUTS */
input[type="text"], input[type="password"], input[type="file"], select, textarea {
  background: var(--ink2);
  border: 2px solid var(--border);
  color: var(--ivory);
  padding: 9px 13px;
  border-radius: 12px;
  font-family: var(--sans);
  font-size: 13px;
  width: 100%;
  transition: border-color 0.15s, box-shadow 0.15s;
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--purple);
  box-shadow: 0 0 0 3px rgba(155,89,255,0.2);
}
textarea { resize: vertical; min-height: 100px; line-height: 1.7; }
label { font-size: 11px; color: var(--muted); letter-spacing: 1px; display: block; margin-bottom: 5px; margin-top: 12px; }
label:first-child { margin-top: 0; }
input[type="file"]::file-selector-button { background: var(--gold3); color: var(--ink); border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; margin-right: 8px; }
select { cursor: pointer; }

/* TABS */
.tabs { display: flex; gap: 4px; margin-bottom: 14px; border-bottom: 2px solid var(--border); }
.tab {
  padding: 7px 16px; cursor: pointer; font-size: 12px;
  color: var(--muted); border-bottom: 3px solid transparent;
  margin-bottom: -2px; transition: all 0.12s;
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.tab:hover { color: var(--ivory2); background: rgba(155,89,255,0.08); }
.tab.active {
  color: var(--yellow);
  border-bottom-color: var(--yellow);
  background: rgba(255,214,10,0.06);
  text-shadow: 0 0 8px rgba(255,214,10,0.3);
}
.tab-content { display: none; }
.tab-content.active { display: block; }

/* CHAT */
.chat-box { background: var(--ink); border: 1px solid var(--border); border-radius: 6px; padding: 12px; min-height: 260px; max-height: 420px; overflow-y: auto; margin-bottom: 10px; }
.chat-msg {
  padding: 9px 13px; margin: 7px 0;
  border-radius: 14px; font-size: 13px; line-height: 1.7;
}
.chat-user {
  background: rgba(255,107,43,0.12);
  border-left: 3px solid var(--gold);
  border-radius: 14px 14px 4px 14px;
}
.chat-ai {
  background: rgba(155,89,255,0.1);
  border-left: 3px solid var(--purple);
  border-radius: 14px 14px 14px 4px;
}
.chat-sys {
  background: rgba(83,82,237,0.12);
  border-left: 3px solid var(--blue);
  color: #a0a8ff;
  font-size: 11px;
  border-radius: 8px;
}
.chat-row  { display: flex; gap: 8px; }
.chat-row input { flex: 1; }

/* BADGE PILLS */
.badge-pill {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(155,89,255,0.15);
  border: 2px solid var(--yellow);
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--yellow);
  margin: 3px;
  text-transform: uppercase;
  box-shadow: 0 2px 0 rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,214,10,0.15);
}
.badge-locked { opacity: 0.3; filter: grayscale(1); }

/* ENROLLMENT WIZARD */
.wizard-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
.wizard-card {
  background: var(--ink1);
  border: 3px solid var(--border);
  border-radius: 24px;
  padding: 36px;
  max-width: 640px;
  width: 100%;
  box-shadow: 0 8px 0 rgba(0,0,0,0.5), 0 20px 60px rgba(155,89,255,0.2);
}
.wizard-logo {
  font-family: var(--serif);
  font-size: 20px;
  color: var(--yellow);
  text-align: center;
  margin-bottom: 6px;
  text-shadow: 0 0 20px rgba(255,214,10,0.6), 3px 3px 0 rgba(0,0,0,0.5);
  line-height: 1.5;
}
.wizard-tagline {
  text-align: center;
  color: var(--muted);
  font-size: 9px;
  letter-spacing: 2px;
  margin-bottom: 28px;
  text-transform: uppercase;
}
.wizard-step { display: none; }
.wizard-step.active { display: block; }
.wizard-step-title { font-family: var(--serif); font-size: 20px; color: var(--gold2); margin-bottom: 5px; }
.wizard-step-sub { font-size: 13px; color: var(--muted); margin-bottom: 18px; line-height: 1.6; }

/* Assessment choice buttons */
.assess-choice-btn { display:flex; align-items:center; gap:10px; background:var(--surface2); border:1.5px solid var(--border); border-radius:12px; padding:11px 16px; font-size:14px; color:var(--text); cursor:pointer; text-align:left; transition:all 0.15s; font-family:inherit; width:100%; }
.assess-choice-btn:hover { border-color:var(--gold); background:var(--surface3,#252525); }
.assess-choice-btn.selected { border-color:var(--gold); background:rgba(212,175,55,0.12); color:var(--gold2); font-weight:600; }
.assess-choice-emoji { font-size:18px; min-width:26px; text-align:center; }
.assess-choice-btn.assess-choice-small { flex:0 0 auto; width:auto; padding:8px 16px; font-size:13px; border-radius:20px; }


.provider-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 14px 0; }
.provider-card {
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.12s;
  text-align: center;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.provider-card:hover {
  border-color: var(--purple);
  transform: translateY(-2px);
  box-shadow: 0 5px 0 rgba(0,0,0,0.4), 0 8px 16px rgba(155,89,255,0.15);
}
.provider-card.selected {
  border-color: var(--yellow);
  background: var(--ink3);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4), inset 0 0 16px rgba(255,214,10,0.08);
}
.provider-icon { font-size: 22px; margin-bottom: 5px; }
.provider-name { font-size: 13px; font-weight: 600; color: var(--ivory); }
.provider-hint { font-size: 10px; color: var(--muted); margin-top: 2px; }

/* Mentor style grid — v2.0 */
.mentor-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 14px 0; }
.mentor-card {
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.12s;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.mentor-card:hover {
  border-color: var(--gold);
  transform: translateY(-2px);
  box-shadow: 0 5px 0 rgba(0,0,0,0.4), 0 8px 16px rgba(255,107,43,0.15);
}
.mentor-card.selected {
  border-color: var(--yellow);
  background: rgba(255,214,10,0.07);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4), 0 0 20px rgba(255,214,10,0.12);
}
.mentor-icon { font-size: 22px; margin-bottom: 5px; }
.mentor-name { font-size: 13px; font-weight: 600; color: var(--ivory); }
.mentor-desc { font-size: 10px; color: var(--muted); margin-top: 2px; }

.model-option { background: var(--ink2); border: 1px solid var(--border); border-radius: 6px; padding: 9px 13px; margin-bottom: 6px; cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 10px; }
.model-option:hover { border-color: var(--gold3); }
.model-option.selected { border-color: var(--gold); }
.model-radio { width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--border); flex-shrink: 0; transition: all 0.15s; }
.model-option.selected .model-radio { border-color: var(--gold); background: var(--gold); }

.assess-bubble { background: var(--ink2); border: 1px solid var(--border); border-radius: 12px 12px 12px 4px; padding: 12px 16px; font-size: 14px; line-height: 1.7; color: var(--ivory); margin-bottom: 10px; max-width: 85%; white-space: pre-line; }
.assess-bubble.user { background: rgba(200,168,75,0.12); border-color: var(--gold3); border-radius: 12px 12px 4px 12px; margin-left: auto; }

.stepper { display: flex; gap: 0; margin-bottom: 24px; }
.step-item { flex: 1; text-align: center; position: relative; }
.step-item::before { content: ''; position: absolute; top: 13px; left: 50%; right: -50%; height: 1px; background: var(--border); }
.step-item:last-child::before { display: none; }
.step-dot {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: var(--ink2);
  border: 2px solid var(--border);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 9px; color: var(--muted);
  position: relative; z-index: 1;
  transition: all 0.2s;
}
.step-item.done .step-dot {
  background: var(--purple);
  border-color: var(--purple);
  color: white;
  box-shadow: 0 0 8px rgba(155,89,255,0.5);
}
.step-item.active .step-dot {
  border-color: var(--yellow);
  color: var(--yellow);
  box-shadow: 0 0 10px rgba(255,214,10,0.4);
}
.step-lbl { font-size: 8px; color: var(--muted); margin-top: 4px; }

.teacher-tag { display: inline-flex; align-items: center; gap: 8px; background: var(--ink2); border: 1px solid var(--gold3); border-radius: 20px; padding: 5px 13px; margin-bottom: 12px; font-size: 12px; color: var(--gold2); }
.teacher-avatar { width: 26px; height: 26px; border-radius: 50%; background: linear-gradient(135deg, var(--gold3), var(--gold)); display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; color: var(--ink); font-weight: 700; }

/* COURSE MANAGE CARD — v2.0 */
.manage-course-card { background: var(--ink1); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; margin-bottom: 12px; display: flex; align-items: center; gap: 16px; transition: border-color 0.15s; }
.manage-course-card:hover { border-color: var(--gold3); }
.manage-course-info { flex: 1; }
.manage-course-title { font-size: 15px; font-weight: 600; color: var(--ivory); }
.manage-course-sub { font-size: 11px; color: var(--muted); margin-top: 3px; }
.manage-course-actions { display: flex; gap: 8px; flex-shrink: 0; }

/* ACHIEVEMENTS — v2.0 */
.badge-card {
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  text-align: center;
  transition: all 0.15s;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.badge-card.earned {
  border-color: var(--yellow);
  background: rgba(255,214,10,0.07);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4), 0 0 20px rgba(255,214,10,0.15);
}
.badge-card.earned:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 6px 0 rgba(0,0,0,0.4), 0 0 28px rgba(255,214,10,0.2);
}
.badge-icon { font-size: 36px; margin-bottom: 8px; }
.badge-name { font-size: 13px; font-weight: 600; color: var(--ivory); }
.badge-desc { font-size: 11px; color: var(--muted); margin-top: 3px; }
.badge-exp  { font-size: 10px; color: var(--gold); margin-top: 4px; }

/* TOAST */
.toast {
  position: fixed; bottom: 24px; right: 24px; z-index: 10000;
  background: var(--ink1);
  border: 2px solid var(--yellow);
  border-radius: 14px;
  padding: 12px 18px;
  color: var(--yellow);
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 4px 0 rgba(0,0,0,0.5), 0 8px 32px rgba(155,89,255,0.2);
  opacity: 0;
  transform: translateY(16px) scale(0.95);
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
  max-width: 340px;
}
.toast.show { opacity: 1; transform: translateY(0) scale(1); }
.toast.err { border-color: var(--red); color: #ff8080; }
.toast.ok  { border-color: var(--green); color: #80ffb0; }

/* [v2.9.3] Interactive Quiz styles */
.qz-question { background: var(--ink1); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; margin-bottom: 14px; }
.qz-q-text { font-size: 14px; color: var(--ivory); font-weight: 600; margin-bottom: 10px; line-height: 1.5; }
.qz-q-num { font-family: var(--mono); font-size: 11px; color: var(--gold3); margin-bottom: 6px; }
.qz-choices { display: flex; flex-direction: column; gap: 6px; }
.qz-choice {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 14px;
  background: var(--ink2);
  border: 2px solid var(--border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.1s;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.qz-choice:hover {
  border-color: var(--purple);
  background: rgba(155,89,255,0.08);
  transform: translateX(3px);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.qz-choice.selected {
  border-color: var(--yellow);
  background: rgba(255,214,10,0.1);
  box-shadow: 0 3px 0 rgba(0,0,0,0.4), inset 0 0 12px rgba(255,214,10,0.06);
}
.qz-choice.correct  { border-color: var(--green); background: rgba(46,213,115,0.12); }
.qz-choice.wrong    { border-color: var(--red);   background: rgba(255,71,87,0.12); }
.qz-choice-key {
  font-family: var(--serif);
  font-size: 10px;
  color: var(--yellow);
  min-width: 24px;
  font-weight: 700;
  text-shadow: 0 0 6px rgba(255,214,10,0.3);
}
.qz-choice-text { font-size: 13px; color: var(--ivory2); line-height: 1.5; }
.qz-explanation { font-size: 12px; color: var(--muted); margin-top: 8px; padding: 6px 10px; background: rgba(200,168,75,0.06); border-radius: 4px; border-left: 2px solid var(--gold3); display: none; }

/* [v2.9.3] Period sub-lesson indicator */
.period-badge { display: inline-flex; align-items: center; gap: 5px; background: rgba(41,128,185,0.15); border: 1px solid #2980b9; border-radius: 12px; padding: 3px 10px; font-size: 11px; color: #7ab8e0; margin-bottom: 8px; }


/* ═══ BMO GAME BOY CONSOLE — Pixel Art v2 ═══ */
/* chassis — horizontal widescreen GBA style */
.bmo-console {
  background: #5a3080;
  border: 4px solid #000;
  border-bottom: 6px solid #000;
  border-right: 5px solid #000;
  border-radius: 12px 12px 18px 18px;
  padding: 10px 12px 12px;
  margin-bottom: 14px;
  position: relative;
  image-rendering: pixelated;
  box-shadow:
    inset 2px 2px 0 rgba(255,255,255,0.2),
    inset -2px -2px 0 rgba(0,0,0,0.4),
    4px 6px 0 #1a0835,
    6px 8px 0 rgba(0,0,0,0.35);
  user-select: none;
  width: 100%;
}
/* top label stripe — pixel font */
.bmo-console::before {
  content: 'GAME BOY';
  position: absolute;
  top: 6px; left: 10px;
  font-family: 'Press Start 2P', monospace;
  font-size: 6px;
  color: #c8a8f0;
  letter-spacing: 2px;
  opacity: 0.9;
}
/* speaking glow */
.bmo-console.speaking {
  box-shadow:
    inset 2px 2px 0 rgba(255,255,255,0.15),
    inset -2px -2px 0 rgba(0,0,0,0.3),
    4px 6px 0 #1a0835,
    0 0 20px rgba(155,89,255,0.55),
    0 0 40px rgba(155,89,255,0.2);
}
/* ── main body row: D-pad LEFT | screen CENTER | buttons RIGHT ── */
.bmo-body {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 18px;
}
/* ── Left column: D-pad ── */
.bmo-left-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
/* ── Screen center ── */
.bmo-screen-wrap {
  flex: 1;
  min-width: 0;
  background: #000;
  border: 4px solid #000;
  border-radius: 4px;
  padding: 4px;
  box-shadow:
    inset 0 2px 6px rgba(0,0,0,0.9),
    2px 2px 0 rgba(0,0,0,0.4);
  image-rendering: pixelated;
}
.bmo-screen {
  width: 100%;
  aspect-ratio: 16/9;
  background: #c8a070;
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  image-rendering: pixelated;
}
/* pixel scanline overlay */
.bmo-screen::after {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.07) 2px,
    rgba(0,0,0,0.07) 3px
  );
  pointer-events: none;
}
/* screen glow when speaking */
.bmo-console.speaking .bmo-screen {
  box-shadow: 0 0 12px rgba(200,160,240,0.55);
}
/* ── Right column: A/B + speaker ── */
.bmo-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
/* ── D-pad ── */
.bmo-dpad {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
}
/* ── AB buttons area ── */
.bmo-ab {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}
/* ── Bottom strip: name row + speech + controls ── */
.bmo-bottom {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
/* name + style pill row */
.avatar-name-row {
  display: flex; align-items: center; gap: 6px;
}
.avatar-name {
  font-size: 11px; font-weight: 700; color: #ffd60a;
  font-family: 'Press Start 2P', monospace;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  text-shadow: 1px 1px 0 #7a5800, 0 0 8px rgba(255,214,10,0.5);
}
.avatar-style-pill {
  font-size: 10px; color: var(--ivory2);
  background: var(--ink3); border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 8px; flex-shrink: 0;
}
/* speech bubble — integrated into console body */
.avatar-speech-bubble {
  font-size: 12px; line-height: 1.6; color: var(--ivory2);
  background: #0f0620;
  border: 2px solid #3a1a5a;
  border-right: 3px solid #1a0835;
  border-bottom: 3px solid #1a0835;
  border-radius: 4px;
  padding: 7px 10px;
  max-height: 70px;
  overflow: hidden;
}
/* controls row — cleaner, no wave dots */
.avatar-controls {
  display: flex; gap: 6px; align-items: center; flex-wrap: nowrap;
}
/* sound wave dots — hidden by default in new layout */
.avatar-sound-dots {
  display: none;
}
.avatar-sound-dots span {
  width: 3px; border-radius: 0;
  background: var(--gold);
  height: 3px;
  transition: height 0.06s;
}
/* blink animation for eyes — both sync, no delay */
@keyframes bmo-blink {
  0%,88%,100% { transform: scaleY(1); }
  93%          { transform: scaleY(0.06); }
  96%          { transform: scaleY(1); }
}
/* Apply same animation with NO delay so both eyes blink simultaneously */
.bmo-eye   { animation: bmo-blink 4s ease-in-out infinite; }
.bmo-eye-r { animation: bmo-blink 4s ease-in-out infinite; }
/* speaking indicator on screen */
@keyframes avatar-pulse {
  from { filter: brightness(1); }
  to   { filter: brightness(1.15) drop-shadow(0 0 6px rgba(155,89,255,0.8)); }
}
.bmo-console.speaking .bmo-screen svg {
  animation: avatar-pulse 0.3s ease-in-out infinite alternate;
}
/* ═══ INLINE PANEL wrapper (reuse for BMO) ═══ */
.avatar-panel-inline {
  position: relative;
  margin-bottom: 14px;
  animation: card-in 0.3s cubic-bezier(0.22,1,0.36,1) both;
}
.avatar-inline-top { display: contents; }
.avatar-inline-info { display: contents; }
.avatar-stage-sm   { display: contents; }
.avatar-svg-wrap-sm { display: none; }
.avatar-sound-dots-sm { display: none; }
.avatar-speech-bubble-sm { display: none; }
.avatar-controls-sm { display: none; }
/* mobile */
@media(max-width:520px){
  .bmo-dpad   { width: 44px; height: 44px; }
}


.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--purple);
  border-right-color: var(--yellow);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 5px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.sep { border: none; border-top: 1px solid var(--border); margin: 14px 0; }

/* [v2.9] Time-Slot Timeline */
.ts-timeline { transition: all 0.2s; }
.ts-period   { transition: border-color 0.15s; }
.ts-period:hover { filter: brightness(1.08); }
.day-card    { transition: border-color 0.15s; }
.day-card:hover > div:first-child { background: var(--ink2); }

.generating-dots::after { content: ''; animation: dots 1.5s steps(4, end) infinite; }
.preview-badge { background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:6px 12px; font-size:12px; color:var(--gold2); font-family:var(--mono); }
.preview-day { border:1px solid var(--border); border-radius:10px; overflow:hidden; margin-bottom:6px; }
.preview-day-header { display:flex; align-items:center; gap:10px; padding:10px 14px; background:var(--surface2); cursor:pointer; user-select:none; transition:background 0.15s; }
.preview-day-header:hover { background:var(--surface3,#2a2a2a); }
.preview-day-num { font-family:var(--mono); font-size:11px; color:var(--muted); min-width:36px; }
.preview-day-title { font-size:13px; color:var(--text); flex:1; }
.preview-day-arrow { font-size:10px; color:var(--muted); transition:transform 0.2s; }
.preview-day-arrow.open { transform:rotate(90deg); }
.preview-day-topics { display:none; padding:8px 14px 10px 60px; font-size:12px; color:var(--muted); line-height:1.8; border-top:1px solid var(--border); background:var(--surface); }
.preview-day-topics.open { display:block; }
.preview-scroll { max-height:58vh; overflow-y:auto; margin-bottom:14px; padding-right:2px; }
.preview-scroll::-webkit-scrollbar { width:3px; }
.preview-scroll::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
@keyframes dots { 0%,20%{ content:''; } 40%{ content:'.'; } 60%{ content:'..'; } 80%,100%{ content:'...'; } }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--ink1); }
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--purple); }

/* ═══ MOBILE RESPONSIVE — Full Bottom Nav System ═══ */
@media(max-width:768px){
  /* ลบ .sidebar-overlay { display: block !important; } ออก */
  .sidebar-overlay.active { display: block !important; pointer-events: auto !important; }
  .sidebar-overlay:not(.active) { display: none !important; pointer-events: none !important; }
  .sidebar { transform: translateX(-100%); transition: transform 0.28s cubic-bezier(.4,0,.2,1); width: 280px !important; min-width: 280px !important; z-index: 200; box-shadow: 4px 0 24px rgba(0,0,0,0.5); }
  .sidebar.open { transform: translateX(0); }
  .sidebar-overlay { display: none; }
  .sidebar-overlay.active { display: block !important; pointer-events: auto !important; }
.sidebar.open ~ .sidebar-overlay { display: block !important; pointer-events: auto !important; }
.sidebar-overlay.active { display: block !important; pointer-events: auto !important; }
  /* Main takes full width */
  .main { margin-left: 0 !important; padding-bottom: 72px; }
  .page { padding: 14px !important; }
  /* Bottom nav bar */
  .mobile-nav { display: flex !important; }
  /* Grids collapse */
  .g2,.g3,.g4 { grid-template-columns: 1fr !important; }
  /* Wizard full width */
  .wizard-card { padding: 22px 18px; border-radius: 12px; }
  /* Provider/mentor grids stay 2col on mobile — fine */
  /* Content box shorter on mobile */
  .content-box { max-height: 320px; }
  /* Chat box shorter */
  .chat-box { max-height: 300px; }
  /* Page title smaller */
  .page-title { font-size: 22px; }
  /* Day grid bigger cells for touch */
  .day-grid { grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 6px; }
  .day-cell { min-height: 60px; }
  /* Hamburger visible */
  .hamburger { display: flex !important; }
  /* Stat cards 2-col */
  .g4 { grid-template-columns: 1fr 1fr !important; }
  /* btn-row wrap nicely */
  .btn-row { gap: 6px; flex-wrap: wrap; }
  .btn-row .btn { flex: 0 1 auto; min-width: 0; font-size: 11px; padding: 8px 10px; white-space: nowrap; }
  /* Lesson action buttons: 2-column grid on mobile */
  #page-lesson .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  #page-lesson .btn-row .btn { flex: unset; width: 100%; text-align: center; font-size: 12px; padding: 9px 6px; }
  /* Toast bottom-center on mobile (above bottom nav) */
  .toast { bottom: 80px; right: 50%; transform: translateX(50%); font-size: 12px; }
  .toast.show { transform: translateX(50%) translateY(0); }
}

/* ═══ MOBILE UI ELEMENTS ═══ */
.sidebar-overlay {
  display: none;
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 150;
  pointer-events: none;
}
.sidebar-overlay.active {
  pointer-events: auto;
}
.hamburger {
  display: none;
  position: fixed;
  top: 14px; left: 14px;
  z-index: 201;
  background: var(--ink1);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 40px; height: 40px;
  align-items: center; justify-content: center;
  flex-direction: column; gap: 5px;
  cursor: pointer;
}
.hamburger span { display: none; }
.hamburger:hover svg { filter: drop-shadow(0 0 10px rgba(255,214,10,1)) !important; transform: scale(1.1); }
/* Mobile bottom nav bar */
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 64px;
  background: var(--ink1);
  border-top: 3px solid var(--border);
  z-index: 150;
  align-items: stretch;
  box-shadow: 0 -4px 20px rgba(155,89,255,0.15);
}
.mob-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  cursor: pointer;
  color: var(--muted);
  font-size: 10px;
  letter-spacing: 0.3px;
  transition: color 0.15s, background 0.15s;
  border-top: 2px solid transparent;
  padding: 8px 2px;
  -webkit-tap-highlight-color: transparent;
}
.mob-nav-item:hover, .mob-nav-item.active {
  color: var(--yellow);
  border-top-color: var(--yellow);
  background: rgba(255,214,10,0.06);
  text-shadow: 0 0 8px rgba(255,214,10,0.3);
}
.mob-nav-icon { font-size: 18px; line-height: 1; }
.mob-nav-label { font-size: 9px; text-align: center; line-height: 1.2; }
/* Mobile course header bar (shows current course on mobile) */
.mobile-header {
  display: none;
}
@media(max-width:768px){
  .mobile-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px 12px 60px;
    background: var(--ink1);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
    min-height: 56px;
  }
  .mobile-header-title {
    font-family: var(--serif);
    font-size: 14px;
    color: var(--gold);
    font-weight: 700;
    flex: 1;
    min-width: 0;
    overflow: hidden;
    white-space: nowrap;
  }
  .mobile-header-title .marquee-inner {
    display: inline-block;
    white-space: nowrap;
    animation: mh-marquee 12s linear infinite;
    padding-right: 40px;
  }
  @keyframes mh-marquee {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-100%); }
  }
  /* ถ้าข้อความสั้นพอ ไม่ต้องเลื่อน */
  .mobile-header-title.short .marquee-inner { animation: none; }
  .mobile-header-exp {
    font-size: 10px;
    color: var(--muted);
    font-family: var(--mono);
    white-space: nowrap;
    flex-shrink: 0;
  }
}

/* ════════════════════════════════════════════
   POCKADEMY GIMMICK LAYER v1.0
   ════════════════════════════════════════════ */

/* Floating pixel coins */
.pixel-coin {
  position: fixed; pointer-events: none; z-index: 0;
  opacity: 0; user-select: none;
  animation: coin-float linear infinite;
  filter: drop-shadow(0 0 6px rgba(255,214,10,0.7));
}
@keyframes coin-float {
  0%   { transform: translateY(110vh) rotate(0deg);   opacity: 0; }
  5%   { opacity: 0.55; }
  90%  { opacity: 0.35; }
  100% { transform: translateY(-10vh) rotate(720deg); opacity: 0; }
}

/* Glitch effect on brand name */
.brand-name { position: relative; cursor: default; }
.brand-name::before,
.brand-name::after {
  content: attr(data-text);
  position: absolute; inset: 0;
  font-family: inherit; font-size: inherit; font-weight: inherit;
  line-height: inherit; letter-spacing: inherit;
  opacity: 0; pointer-events: none;
}
.brand-name::before {
  color: #ff4757;
  clip-path: polygon(0 30%, 100% 30%, 100% 55%, 0 55%);
  animation: glitch-a 4s infinite;
}
.brand-name::after {
  color: #2ed573;
  clip-path: polygon(0 60%, 100% 60%, 100% 80%, 0 80%);
  animation: glitch-b 4s infinite;
}
@keyframes glitch-a {
  0%,45%,47%,100% { opacity:0; transform:translate(0); }
  46%             { opacity:0.8; transform:translate(-3px,1px) skewX(-5deg); }
}
@keyframes glitch-b {
  0%,45%,47%,100% { opacity:0; transform:translate(0); }
  46%             { opacity:0.6; transform:translate(3px,-1px) skewX(5deg); }
}

/* Scanline on sidebar brand */
.sidebar-brand { position: relative; overflow: hidden; }
.sidebar-brand::after {
  content: ''; position: absolute; inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 3px,
    rgba(0,0,0,0.08) 3px, rgba(0,0,0,0.08) 4px
  );
  pointer-events: none; z-index: 1;
}

/* EXP bar pulse */
.exp-fill { animation: exp-glow 2s ease-in-out infinite alternate; }
@keyframes exp-glow {
  from { box-shadow: 0 0 6px rgba(255,107,43,0.4); }
  to   { box-shadow: 0 0 16px rgba(255,214,10,0.9), 0 0 4px rgba(255,107,43,0.8); }
}

/* Pixel cursor trail */
.cursor-trail {
  position: fixed; pointer-events: none; z-index: 99999;
  width: 6px; height: 6px; border-radius: 1px;
  background: var(--yellow, #ffd60a); opacity: 0;
  transform: translate(-50%, -50%);
  animation: trail-fade 0.5s forwards;
}
@keyframes trail-fade {
  0%   { opacity: 0.9; transform: translate(-50%,-50%) scale(1.2); }
  100% { opacity: 0;   transform: translate(-50%,-50%) scale(0.2); }
}

/* Level-up flash overlay */
#levelup-flash {
  position: fixed; inset: 0; z-index: 99998;
  background: radial-gradient(ellipse at 50% 40%, rgba(255,214,10,0.35) 0%, transparent 70%);
  pointer-events: none; opacity: 0; transition: opacity 0.15s;
}
#levelup-flash.show { opacity: 1; animation: flash-out 0.8s forwards; }
@keyframes flash-out {
  0%  { opacity: 1; } 40% { opacity: 0.6; } 100% { opacity: 0; }
}

/* Blinking cursor on wizard tagline */
.wizard-tagline::after {
  content: ' ▮';
  animation: blink-cursor 0.9s step-end infinite;
  color: var(--yellow, #ffd60a);
}
@keyframes blink-cursor { 50% { opacity: 0; } }

/* Nav active glow */
.nav-item.active {
  box-shadow: inset 3px 0 0 var(--yellow), inset 4px 0 12px rgba(255,214,10,0.15);
}

/* Card entrance animation */
.card { animation: card-in 0.35s cubic-bezier(0.22,1,0.36,1) both; }
@keyframes card-in {
  from { opacity:0; transform: translateY(14px); }
  to   { opacity:1; transform: translateY(0); }
}

/* Skill dot pulse when done */
.skill-item.done .skill-dot { animation: dot-pulse 2s ease-in-out infinite; }
@keyframes dot-pulse {
  0%,100% { box-shadow: 0 2px 0 rgba(0,0,0,0.4), 0 0 10px rgba(155,89,255,0.4); }
  50%     { box-shadow: 0 2px 0 rgba(0,0,0,0.4), 0 0 20px rgba(155,89,255,0.8); }
}

/* Background floating 8-bit icons */
.pixel-bg-icon {
  position: fixed; pointer-events: none; z-index: 0;
  opacity: 0.03; font-size: 80px; user-select: none;
  animation: bg-float ease-in-out infinite alternate; filter: grayscale(1);
}
@keyframes bg-float {
  from { transform: translateY(0) rotate(-3deg); }
  to   { transform: translateY(-18px) rotate(3deg); }
}


/* ═══════════════════════════════════════════════════════
   PIXEL SKILL TREE  (Skill Tree Patch)
   ─ View-toggle buttons
   ─ Skill Tree container + scroll
   ─ Detail popup panel
   ─ SVG node animations (กำหนดใน <defs> ของ SVG แทน)
═══════════════════════════════════════════════════════ */

/* ── View toggle row ── */
.vt-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.vt-btn {
  padding: 8px 18px;
  border: 2px solid var(--border);
  border-bottom: 4px solid rgba(0,0,0,.35);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .4px;
  color: var(--muted);
  cursor: pointer;
  background: var(--ink2);
  font-family: var(--sans);
  transition: all .1s;
  box-shadow: 0 3px 0 rgba(0,0,0,.4);
}
.vt-btn:hover {
  border-color: var(--purple);
  color: var(--ivory2);
  transform: translateY(-1px);
}
.vt-btn.vt-active {
  border-color: var(--yellow);
  color: var(--yellow);
  background: rgba(255,214,10,.07);
  box-shadow: 0 3px 0 rgba(0,0,0,.4), 0 0 14px rgba(255,214,10,.18);
  transform: none;
}

/* ── Skill tree wrapper card ── */
.st-card {
  background: var(--ink1);
  border: 2px solid var(--border);
  border-radius: 20px;
  padding: 14px 10px 10px;
  margin-bottom: 12px;
  box-shadow: 0 4px 0 rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
  overflow: hidden;
}

/* Progress bar above tree */
.st-prog-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 6px;
}
.st-prog-label {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--yellow);
  white-space: nowrap;
}
.st-prog-bar {
  flex: 1;
  height: 6px;
  background: var(--ink3);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.st-prog-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--purple), var(--gold), var(--yellow));
  border-radius: 4px;
  transition: width .6s cubic-bezier(.22,1,.36,1);
  box-shadow: 0 0 6px rgba(255,107,43,.4);
}
.st-prog-pct {
  font-size: 9px;
  color: var(--muted);
  font-family: 'DM Mono', monospace;
  white-space: nowrap;
}

/* SVG scroll container */
.st-svg-scroll {
  overflow-x: hidden;
  overflow-y: auto;
  max-height: 70vh;
  -webkit-overflow-scrolling: touch;
}

/* ── Detail popup ── */
.st-detail {
  background: var(--ink1);
  border: 2px solid var(--yellow);
  border-radius: 18px;
  padding: 16px;
  margin-top: 12px;
  display: none;
  box-shadow: 0 4px 0 rgba(0,0,0,.5), 0 10px 28px rgba(255,214,10,.1);
}
.st-detail.st-open {
  display: block;
  animation: stSlideUp .2s cubic-bezier(.22,1,.36,1);
}
@keyframes stSlideUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.st-detail-day {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.st-detail-title {
  font-size: 17px;
  font-weight: 700;
  color: #f0e6ff;
  margin-bottom: 8px;
  line-height: 1.3;
}
.st-detail-obj {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.65;
  margin-bottom: 8px;
}
.st-detail-meta {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 4px;
}

/* avatar-panel-inline shim → handled in BMO block above */
</style>
</head>
<body>

<!-- ═══ GIMMICK LAYER v1.0 ═══ -->
<div id="levelup-flash"></div>
<div class="pixel-bg-icon" style="top:8%;  left:3%;  animation-duration:7s;  animation-delay:0s">🎮</div>
<div class="pixel-bg-icon" style="top:30%; right:2%; animation-duration:9s;  animation-delay:-3s">🏆</div>
<div class="pixel-bg-icon" style="top:55%; left:1%;  animation-duration:11s; animation-delay:-6s">📖</div>
<div class="pixel-bg-icon" style="top:75%; right:4%; animation-duration:8s;  animation-delay:-2s">⭐</div>
<div class="pixel-bg-icon" style="bottom:5%;left:40%;animation-duration:10s; animation-delay:-4s">🎓</div>

<!-- Mobile overlay -->
<div class="sidebar-overlay" id="sidebar-overlay" onclick="closeSidebar()"></div>

<!-- Hamburger = pixel logo button (mobile only) -->
<div class="hamburger" id="hamburger" onclick="toggleSidebar()" title="เมนู">
  <svg width="28" height="28" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 0 5px rgba(255,214,10,0.7));transition:filter 0.15s,transform 0.15s">
    <rect x="4" y="6" width="28" height="20" rx="2" fill="#1a0835" stroke="#9b59ff" stroke-width="1.5"/>
    <rect x="6" y="8" width="24" height="16" rx="1" fill="#240d48"/>
    <rect x="9"  y="11" width="2" height="8" fill="#ffd60a"/>
    <rect x="11" y="11" width="3" height="2" fill="#ffd60a"/>
    <rect x="11" y="14" width="3" height="2" fill="#ffd60a"/>
    <rect x="14" y="11" width="2" height="5" fill="#ffd60a"/>
    <rect x="21" y="12" width="2" height="2" fill="#ff6b2b"/>
    <rect x="19" y="14" width="2" height="2" fill="#ff6b2b"/>
    <rect x="21" y="14" width="2" height="2" fill="#ff8c52"/>
    <rect x="23" y="14" width="2" height="2" fill="#ff6b2b"/>
    <rect x="21" y="16" width="2" height="2" fill="#ff6b2b"/>
    <rect x="15" y="26" width="6" height="2" fill="#5e2d9e"/>
    <rect x="12" y="28" width="12" height="2" rx="1" fill="#5e2d9e"/>
  </svg>
</div>

<!-- Mobile bottom nav -->
<nav class="mobile-nav" id="mobile-nav">
  <div class="mob-nav-item active" onclick="nav('dashboard')" id="mnav-dashboard">
    <span class="mob-nav-icon">🏠</span>
    <span class="mob-nav-label">หน้าหลัก</span>
  </div>
  <div class="mob-nav-item" onclick="nav('lesson')" id="mnav-lesson">
    <span class="mob-nav-icon">📖</span>
    <span class="mob-nav-label">บทเรียน</span>
  </div>
  <div class="mob-nav-item" onclick="nav('homework')" id="mnav-homework">
    <span class="mob-nav-icon">📝</span>
    <span class="mob-nav-label">ส่งงาน</span>
  </div>
  <div class="mob-nav-item" onclick="nav('chat')" id="mnav-chat">
    <span class="mob-nav-icon">💬</span>
    <span class="mob-nav-label">ถามครู</span>
  </div>
  <div class="mob-nav-item" onclick="nav('curriculum')" id="mnav-curriculum">
    <span class="mob-nav-icon">🗺️</span>
    <span class="mob-nav-label">แผนเรียน</span>
  </div>
</nav>

<!-- Mobile header bar -->
<div class="mobile-header" id="mobile-header">
  <div class="mobile-header-title" id="mobile-header-title">Pockademy</div>
  <div class="mobile-header-exp" id="mobile-header-exp">0 EXP</div>
</div>

<!-- ═══ ENROLLMENT WIZARD ═══ -->
<div id="wizard-view" class="wizard-wrap" style="display:none">
  <div class="wizard-card">
    <div class="wizard-logo">🎮 POCKADEMY</div>
    <div class="wizard-tagline">v0.1 — LEVEL UP YOUR BRAIN</div>

    <div class="stepper" id="stepper">
      <div class="step-item active" id="st-0"><div class="step-dot">1</div><div class="step-lbl">Provider</div></div>
      <div class="step-item"        id="st-1"><div class="step-dot">2</div><div class="step-lbl">Key</div></div>
      <div class="step-item"        id="st-2"><div class="step-dot">3</div><div class="step-lbl">Model</div></div>
      <div class="step-item"        id="st-3"><div class="step-dot">4</div><div class="step-lbl">Mentor</div></div>
      <div class="step-item"        id="st-4"><div class="step-dot">5</div><div class="step-lbl">Subject</div></div>
      <div class="step-item"        id="st-5"><div class="step-dot">6</div><div class="step-lbl">Assess</div></div>
      <div class="step-item"        id="st-6"><div class="step-dot">✓</div><div class="step-lbl">Build</div></div>
    </div>

    <!-- Step 0: Provider -->
    <div class="wizard-step active" id="ws-provider">
      <div class="wizard-step-title">เลือก AI Provider</div>
      <div class="wizard-step-sub">เลือก platform ที่คุณมี API Key<br>Ollama = รันบนเครื่องตัวเองฟรี</div>
      <div class="provider-grid" id="provider-grid"></div>
      <div id="saved-config-hint" style="display:none; margin:10px 0; padding:10px; background:rgba(200,168,75,0.08); border:1px solid var(--gold3); border-radius:6px; font-size:12px; color:var(--gold2)"></div>
      <div class="btn-row">
        <button class="btn" onclick="selectProviderNext()">ถัดไป →</button>
      </div>
    </div>

    <!-- Step 1: API Key -->
    <div class="wizard-step" id="ws-apikey">
      <div class="wizard-step-title">ใส่ API Key</div>
      <div class="wizard-step-sub" id="apikey-hint">API Key ของ provider ที่เลือก</div>
      <label>API Key</label>
      <input type="password" id="api-key-input" placeholder="API Key...">
      <div id="ollama-note" style="display:none; margin-top:10px; font-size:12px; color:var(--muted)">💡 Ollama ไม่ต้องใส่ API Key — กด ถัดไป ได้เลย</div>
      <div id="saved-key-note" style="display:none; margin-top:8px; font-size:11px; color:var(--green)">✅ โหลด API Key ที่บันทึกไว้แล้ว (แก้ไขได้)</div>
      <div class="btn-row">
        <button class="btn btn-ghost btn-sm" onclick="wzBack('ws-provider')">← กลับ</button>
        <button class="btn" onclick="verifyApiKey()">ยืนยัน API Key</button>
      </div>
      <div id="apikey-status" style="margin-top:8px; font-size:12px"></div>
    </div>

    <!-- Step 2: Model -->
    <div class="wizard-step" id="ws-model">
      <div class="wizard-step-title">เลือก AI Model</div>
      <div class="wizard-step-sub">Model นี้จะเป็น "ครู" ตลอดหลักสูตร</div>
      <div id="model-list-wz"></div>
      <div class="btn-row">
        <button class="btn btn-ghost btn-sm" onclick="wzBack('ws-apikey')">← กลับ</button>
        <button class="btn" onclick="wzNext('ws-mentor'); updateStepper(3)">ถัดไป →</button>
      </div>
    </div>

    <!-- Step 3: Mentor Style (NEW v2.0) -->
    <div class="wizard-step" id="ws-mentor">
      <div class="wizard-step-title">เลือกสไตล์ครู</div>
      <div class="wizard-step-sub">บุคลิกของครู AI ที่จะสอนคุณตลอดหลักสูตร</div>
      <div class="mentor-grid" id="mentor-grid"></div>
      <div class="btn-row">
        <button class="btn btn-ghost btn-sm" onclick="wzBack('ws-model')">← กลับ</button>
        <button class="btn" onclick="wzNext('ws-subject'); updateStepper(4)">ถัดไป →</button>
      </div>
    </div>

    <!-- Step 4: Subject + RAG URL -->
    <div class="wizard-step" id="ws-subject">
      <div class="wizard-step-title">อยากเรียนเรื่องอะไร?</div>
      <div class="wizard-step-sub">ยิ่งละเอียดยิ่งดี — เช่น "Python สำหรับวิเคราะห์ข้อมูล", "กีตาร์คลาสสิก"</div>
      <label>หัวข้อ / วิชาที่ต้องการเรียน</label>
      <input type="text" id="subject-input" placeholder="เช่น: การลงทุนในตลาดหุ้น..." oninput="subjectTyping()">
      <label style="margin-top:12px">ชื่อของคุณ</label>
      <input type="text" id="learner-name-input" placeholder="ชื่อ...">
      <!-- RAG URL — v2.0 -->
      <label style="margin-top:14px">🔗 URL อ้างอิง (ไม่บังคับ) <span style="color:var(--muted);font-weight:normal">— AI จะใช้ข้อมูลจาก URL นี้ในการสอน</span></label>
      <input type="text" id="rag-url-input" placeholder="https://... (เว็บ, บทความ, เอกสาร)">
      <div style="font-size:11px; color:var(--muted); margin-top:4px">เช่น Wikipedia, บทความ, หน้าเอกสาร</div>
      <div class="btn-row">
        <button class="btn btn-ghost btn-sm" onclick="wzBack('ws-mentor')">← กลับ</button>
        <button class="btn" id="subject-next-btn" onclick="startAssessment()" disabled>เริ่มประเมินระดับ →</button>
      </div>
    </div>

    <!-- Step 5: Assessment -->
    <div class="wizard-step" id="ws-assessment">
      <div class="wizard-step-title">ประเมินระดับความรู้</div>
      <div class="wizard-step-sub">ตอบ 6 ข้อ เพื่อออกแบบหลักสูตรเฉพาะสำหรับคุณ</div>

      <!-- Progress bar -->
      <div style="margin:12px 0 18px;background:var(--border);border-radius:8px;height:6px;overflow:hidden">
        <div id="assess-progress-bar" style="height:100%;background:var(--gold);border-radius:8px;width:0%;transition:width .4s ease"></div>
      </div>
      <div id="assess-step-label" style="font-size:11px;color:var(--muted);text-align:right;margin-top:-14px;margin-bottom:10px">ข้อ 0 / 6</div>

      <!-- Question card -->
      <div id="assess-question-card" style="background:var(--surface2);border-radius:14px;padding:18px 16px;margin-bottom:16px;min-height:60px">
        <div id="assess-question-text" style="font-size:15px;line-height:1.7;white-space:pre-line;color:var(--text)"></div>
      </div>

      <!-- Choice buttons (choice / choice+reason) -->
      <div id="assess-choices" style="display:none;flex-direction:column;gap:8px"></div>

      <!-- Timeline special UI -->
      <div id="assess-timeline" style="display:none">
        <div style="font-size:12px;color:var(--muted);margin-bottom:6px">จำนวนวัน</div>
        <div id="assess-days-choices" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px"></div>
        <div style="font-size:12px;color:var(--muted);margin-bottom:6px">วันละกี่ชั่วโมง</div>
        <div id="assess-hours-choices" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px"></div>
        <button id="assess-timeline-confirm" class="btn btn-sm" style="margin-top:4px;display:none" onclick="confirmTimeline()">ยืนยัน →</button>
      </div>

      <!-- Reason textarea (choice+reason) — bottom sheet on mobile -->
      <div id="assess-reason-row" style="display:none;position:fixed;bottom:0;left:0;right:0;z-index:999;background:var(--ink,#1a1a1a);border-top:1px solid var(--gold3,#7a6a2a);padding:14px 16px 24px;box-shadow:0 -8px 32px rgba(0,0,0,0.5)">
        <div style="font-size:12px;color:var(--gold2,#c8a832);margin-bottom:8px;font-weight:600">📝 เพิ่มรายละเอียด <span style="color:var(--muted);font-weight:normal">(ไม่บังคับ)</span></div>
        <textarea id="assess-reason-input" rows="2" placeholder="" style="width:100%;box-sizing:border-box;background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:10px 12px;font-size:14px;color:var(--text);resize:none;font-family:inherit" onkeypress="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();submitWithReason(false)}"></textarea>
        <div style="display:flex;gap:8px;margin-top:10px">
          <button class="btn btn-ghost btn-sm" style="flex:1" onclick="submitWithReason(true)">ข้าม →</button>
          <button class="btn btn-sm" style="flex:2" onclick="submitWithReason(false)">✅ ยืนยัน</button>
        </div>
      </div>

      <!-- Fallback text input (type:text) -->
      <div id="assess-text-row" style="display:none">
        <div class="chat-row" style="margin-top:4px">
          <input type="text" id="assess-input" placeholder="ตอบที่นี่..." onkeypress="if(event.key==='Enter')assessAnswerText()">
          <button class="btn btn-sm" onclick="assessAnswerText()">ส่ง</button>
        </div>
      </div>

      <!-- Done row -->
      <div class="btn-row" id="assess-done-row" style="display:none;margin-top:16px">
        <button class="btn" onclick="previewCurriculum()">🔍 ดูแผนหลักสูตรก่อน →</button>
      </div>
    </div>

    <!-- Step 6: Preview -->
    <div class="wizard-step" id="ws-preview">
      <div class="wizard-step-title">แผนหลักสูตรของคุณ</div>
      <div class="wizard-step-sub" id="preview-sub">AI กำลังออกแบบหลักสูตรเฉพาะสำหรับคุณ...</div>
      <div id="preview-loading" style="text-align:center;padding:28px 20px;color:var(--muted);font-size:13px;line-height:2.2">
        <div id="preview-log" style="font-family:var(--mono);font-size:11px"></div>
      </div>
      <div id="preview-content" style="display:none">
        <div id="preview-meta" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px"></div>
        <div style="font-size:11px;color:var(--muted);margin-bottom:8px;font-family:var(--mono)">📅 แผนการเรียนทั้งหมด — แตะเพื่อดูรายละเอียด</div>
        <div id="preview-days" class="preview-scroll"></div>
        <div class="btn-row" style="gap:10px">
          <button class="btn btn-ghost btn-sm" onclick="wzBack('ws-assessment')">← แก้คำตอบ</button>
          <button class="btn" onclick="generateCourse()">✅ ยืนยัน สร้างหลักสูตรเลย!</button>
        </div>
      </div>
    </div>

    <!-- Step 7: Generating -->
    <div class="wizard-step" id="ws-generating">
      <div class="wizard-step-title">สร้างหลักสูตร<span class="generating-dots"></span></div>
      <div class="wizard-step-sub" id="gen-status">ครู AI กำลังออกแบบหลักสูตรเฉพาะสำหรับคุณ</div>
      <div id="gen-log" style="margin-top:14px; font-family:var(--mono); font-size:11px; color:var(--muted); line-height:2.2"></div>
    </div>
  </div>
</div>

<!-- ═══ MAIN APP ═══ -->
<div id="app-view" class="shell" style="display:none">
  <!-- SIDEBAR -->
  <nav class="sidebar" id="sidebar">
    <div class="sidebar-brand">
      <div class="brand-logo-row">
        <svg class="brand-logo-svg" width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="6" width="28" height="20" rx="2" fill="#1a0835" stroke="#9b59ff" stroke-width="1.5"/>
          <rect x="6" y="8" width="24" height="16" rx="1" fill="#240d48"/>
          <rect x="9"  y="11" width="2" height="8" fill="#ffd60a"/>
          <rect x="11" y="11" width="3" height="2" fill="#ffd60a"/>
          <rect x="11" y="14" width="3" height="2" fill="#ffd60a"/>
          <rect x="14" y="11" width="2" height="5" fill="#ffd60a"/>
          <rect x="21" y="12" width="2" height="2" fill="#ff6b2b"/>
          <rect x="19" y="14" width="2" height="2" fill="#ff6b2b"/>
          <rect x="21" y="14" width="2" height="2" fill="#ff8c52"/>
          <rect x="23" y="14" width="2" height="2" fill="#ff6b2b"/>
          <rect x="21" y="16" width="2" height="2" fill="#ff6b2b"/>
          <rect x="15" y="26" width="6" height="2" fill="#5e2d9e"/>
          <rect x="12" y="28" width="12" height="2" rx="1" fill="#5e2d9e"/>
        </svg>
        <div class="brand-text-col">
          <div class="brand-name">POCKADEMY</div>
          <div class="brand-sub">LEVEL UP YOUR BRAIN</div>
        </div>
      </div>
      <div class="brand-meta-row">
        <div class="brand-ver">v0.1 DEMO</div>
        <div class="brand-online"><div class="brand-dot"></div>ONLINE</div>
      </div>
      <div class="brand-xp-badge" id="sidebar-course-name">🎓 ยังไม่มีหลักสูตร</div>
    </div>

    <!-- EXP BAR — v2.0 -->
    <div class="exp-bar-wrap">
      <div class="exp-level-row">
        <span class="exp-level-name" id="sb-level-name">🌱 Seedling</span>
        <span class="exp-label" id="sb-exp-val">0 EXP</span>
      </div>
      <div class="exp-bar"><div class="exp-fill" id="sb-exp-fill" style="width:0%"></div></div>
    </div>

    <div class="sidebar-section">หลักสูตรของฉัน</div>
    <div id="course-list-sidebar"></div>
    <div style="padding:6px 12px">
      <button class="btn btn-ghost btn-sm" style="width:100%" onclick="newCourse()">+ เพิ่มหลักสูตรใหม่</button>
    </div>

    <div class="sidebar-section">เมนู</div>
    <div class="nav-item active" onclick="nav('dashboard')"><span class="ni">🏠</span> Dashboard</div>
    <div class="nav-item" onclick="nav('lesson')"><span class="ni">📖</span> บทเรียน</div>
    <div class="nav-item" onclick="nav('homework')"><span class="ni">📝</span> ส่งงาน</div>
    <div class="nav-item" onclick="nav('chat')"><span class="ni">💬</span> ถามครู</div>
    <div class="nav-item" onclick="nav('curriculum')"><span class="ni">🗺️</span> แผนการเรียน</div>
    <div class="nav-item" onclick="nav('achievements')"><span class="ni">🏆</span> Achievements</div>
    <div class="nav-item" onclick="nav('manage')"><span class="ni">⚙️</span> จัดการหลักสูตร</div>
    <div class="nav-item" onclick="nav('cache')"><span class="ni">🗑️</span> Cache</div>

    <div class="sidebar-footer">
      <div id="timer-display">⏱ 00:00</div>
    </div>
  </nav>

  <!-- MAIN -->
  <main class="main">

    <!-- DASHBOARD -->
    <div id="page-dashboard" class="page active">
      <div class="page-header">
        <div class="page-title" id="db-title">Dashboard</div>
        <div class="page-sub" id="db-sub">ยินดีต้อนรับกลับมา</div>
      </div>

      <div id="teacher-greeting" class="teacher-tag" style="display:none; margin-bottom:18px">
        <div class="teacher-avatar" id="teacher-av">A</div>
        <span id="teacher-greeting-text"></span>
      </div>

      <!-- Stats row -->
      <div class="g4" style="margin-bottom:18px">
        <div class="stat-card">
          <div class="stat-val" id="d-score">0</div>
          <div class="stat-lbl">SCORE</div>
          <div class="prog-wrap" style="margin-top:8px">
            <div class="prog-fill" id="d-prog" style="width:0%"></div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-val" id="d-days">0/0</div>
          <div class="stat-lbl">DAYS DONE</div>
        </div>
        <div class="stat-card">
          <div class="stat-val" id="d-exp">0</div>
          <div class="stat-lbl">EXP</div>
          <div class="prog-wrap" style="margin-top:8px">
            <div class="exp-fill" id="d-exp-prog" style="width:0%"></div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-val" id="d-time">00:00</div>
          <div class="stat-lbl">STUDY TIME</div>
        </div>
      </div>

      <div class="g2">
        <!-- Skill Path — v2.0 -->
        <div class="card">
          <div class="card-title">🛤️ Skill Path</div>
          <div id="skill-path" class="skill-path"></div>
        </div>

        <div>
          <div class="card">
            <div class="card-title">⚡ เริ่มเรียนได้เลย</div>
            <div id="d-today-plan" style="font-size:13px; color:var(--muted); margin-bottom:10px"></div>
            <div class="btn-row">
              <button class="btn" onclick="nav('lesson')">📖 เรียนวันนี้</button>
              <button class="btn btn-ghost" onclick="nav('chat')">💬 ถามครู</button>
            </div>
          </div>
          <div class="card">
            <div class="card-title">📊 คะแนนการบ้าน</div>
            <div id="d-hw-scores" style="font-size:13px; color:var(--muted)">ยังไม่มีคะแนน</div>
          </div>
          <div class="card">
            <div class="card-title">🏅 Badges</div>
            <div id="d-badges" style="font-size:13px; color:var(--muted)">ยังไม่มี Badge</div>
          </div>
        </div>
      </div>
    </div>

    <!-- LESSON -->
    <div id="page-lesson" class="page">
      <div class="page-header">
        <div class="page-title">📖 บทเรียน</div>
        <div class="page-sub" id="lesson-course-info">—</div>
      </div>
      <div class="g2">
        <div>
          <div class="card">
            <div class="card-title">เลือกบทเรียน</div>
            <label>วันที่</label>
            <select id="lesson-day-sel" onchange="onDaySelChange()"></select>
            <!-- [v2.9.3] Sub-lesson (period) selector -->
            <div id="period-sel-wrap" style="display:none; margin-top:10px">
              <label>📌 บทเรียนย่อย (คาบ)</label>
              <select id="lesson-period-sel" onchange="onPeriodSelChange()">
                <option value="0">— ทั้งวัน (ภาพรวม) —</option>
              </select>
              <div id="period-detail-hint" style="font-size:11px;color:var(--muted);margin-top:4px;padding:6px 8px;background:var(--ink2);border-radius:4px;display:none"></div>
            </div>
            <div class="btn-row">
              <button class="btn" onclick="loadLesson()">📖 อ่านบทเรียน</button>
              <button class="btn btn-ghost" id="btn-load-period-lesson" onclick="loadPeriodLesson()" style="display:none">📌 เรียนคาบนี้</button>
              <button class="btn btn-ghost" id="btn-hw-view" onclick="loadHomeworkView()" style="display:none">📝 ดูการบ้าน</button>

              <button class="btn btn-ghost" onclick="openInteractiveQuiz()">🧩 แบบฝึกหัด</button>
              <button class="btn btn-ghost btn-sm" onclick="regenLesson()">🔄 Regen</button>
              <button class="btn btn-purple btn-sm" onclick="generateNotebookLMScript()" title="สร้าง Script สำหรับ Google NotebookLM Podcast">🎙️ NotebookLM</button>

            </div>
          </div>
          <!-- ═══════════════════════════════════════ -->
          <div class="card" id="lesson-meta-card" style="display:none">
            <div class="teacher-tag" id="lesson-teacher-tag">
              <div class="teacher-avatar" id="lesson-av">A</div>
              <span id="lesson-teacher-name">ครู</span>
            </div>
            <div class="card-title" id="lesson-day-title">—</div>
            <div id="lesson-objectives" style="font-size:12px; color:var(--muted); margin-bottom:10px"></div>
            <div class="tabs">
              <div class="tab active" onclick="showTab('les','content')">บทเรียน</div>
              <div class="tab" onclick="showTab('les','hw')">การบ้าน</div>
            </div>

            <!-- ═══ BMO GAME BOY CONSOLE — Pixel Art v2 ═══ -->
            <div id="mentor-avatar-panel" class="bmo-console" style="display:none">

              <!-- Top body row: D-pad LEFT | screen CENTER | A/B RIGHT -->
              <div class="bmo-body">

                <!-- Left: D-pad -->
                <div class="bmo-left-controls">
                  <svg class="bmo-dpad" viewBox="0 0 52 52" width="52" height="52"
                       style="image-rendering:pixelated">
                    <!-- pixel cross shape — solid yellow with black border -->
                    <rect x="17" y="0"  width="18" height="52" rx="0" fill="#000"/>
                    <rect x="0"  y="17" width="52" height="18" rx="0" fill="#000"/>
                    <rect x="18" y="1"  width="16" height="50" rx="0" fill="#ffd60a"/>
                    <rect x="1"  y="18" width="50" height="16" rx="0" fill="#ffd60a"/>
                    <!-- center square -->
                    <rect x="18" y="18" width="16" height="16" rx="0" fill="#ffd60a"/>
                    <!-- arrows (pixel solid triangles) -->
                    <polygon points="26,4 20,14 32,14" fill="#000"/>
                    <polygon points="26,48 20,38 32,38" fill="#000"/>
                    <polygon points="4,26 14,20 14,32" fill="#000"/>
                    <polygon points="48,26 38,20 38,32" fill="#000"/>
                  </svg>
                </div>

                <!-- Center: Screen -->
                <div class="bmo-screen-wrap">
                  <div class="bmo-screen" id="bmo-screen">
                    <svg id="bmo-face-svg" viewBox="0 0 160 90"
                         xmlns="http://www.w3.org/2000/svg"
                         width="100%" height="100%"
                         style="image-rendering:pixelated">
                      <!-- ── Skin-tone background (warm beige, pixel art NPC) ── -->
                      <rect x="0" y="0" width="160" height="90" fill="#F3B5C6"/>
                      <!-- subtle cheek blush -->
                      <rect x="22" y="38" width="18" height="8" rx="0" fill="#c0607a" opacity="0.25"/>
                      <rect x="120" y="38" width="18" height="8" rx="0" fill="#c0607a" opacity="0.25"/>

                      <!-- ── LEFT EYE — pixel art style (small square dot like sprite) ── -->
                      <g class="bmo-eye" style="transform-origin:46px 28px">
                        <!-- eye outer (dark shadow) -->
                        <rect x="36" y="22" width="20" height="14" rx="0" fill="#3d1a0a"/>
                        <!-- eye white -->
                        <rect x="37" y="23" width="18" height="12" rx="0" fill="#f5f0e8"/>
                        <!-- iris/pupil — dark maroon like sprite -->
                        <rect x="40" y="24" width="8" height="8" rx="0" fill="#5a1a1a"/>
                        <!-- pupil center -->
                        <rect x="42" y="25" width="4" height="5" rx="0" fill="#1a0505"/>
                        <!-- eye shine -->
                        <rect x="43" y="25" width="2" height="2" rx="0" fill="white" opacity="0.9"/>
                        <!-- lower lid line -->
                        <rect x="37" y="33" width="18" height="2" rx="0" fill="#3d1a0a"/>
                      </g>

                      <!-- ── RIGHT EYE — pixel art style ── -->
                      <g class="bmo-eye-r" style="transform-origin:114px 28px">
                        <rect x="104" y="22" width="20" height="14" rx="0" fill="#3d1a0a"/>
                        <rect x="105" y="23" width="18" height="12" rx="0" fill="#f5f0e8"/>
                        <rect x="108" y="24" width="8" height="8" rx="0" fill="#5a1a1a"/>
                        <rect x="110" y="25" width="4" height="5" rx="0" fill="#1a0505"/>
                        <rect x="111" y="25" width="2" height="2" rx="0" fill="white" opacity="0.9"/>
                        <rect x="105" y="33" width="18" height="2" rx="0" fill="#3d1a0a"/>
                      </g>

                      <!-- ── NOSE — small pixel dot ── -->
                      <rect x="77" y="46" width="3" height="3" rx="0" fill="#c08060" opacity="0.7"/>
                      <rect x="82" y="46" width="3" height="3" rx="0" fill="#c08060" opacity="0.7"/>

                      <!-- ── MOUTH — sprite image, frame-switched by JS ── -->
                      <!-- mouth area: x=20..140, y=50..85 in 160x90 viewBox -->
                      <image id="bmo-sprite-mouth"
                             x="30" y="48"
                             width="100" height="34"
                             preserveAspectRatio="xMidYMid meet"
                             style="image-rendering:pixelated"/>
                    </svg>
                  </div>
                </div>

                <!-- Right: A/B buttons + speaker -->
                <div class="bmo-controls">
                  <!-- A/B pixel circle buttons — diagonal: B lower-left, A upper-right -->
                  <svg viewBox="0 0 64 56" width="64" height="56"
                       style="image-rendering:pixelated;display:block">
                    <!-- B button (lower left) — green circle -->
                    <rect x="2" y="28" width="26" height="26" rx="13" fill="#000"/>
                    <rect x="4" y="30" width="22" height="22" rx="11" fill="#1a8a3a"/>
                    <rect x="4" y="30" width="22" height="6" rx="0" fill="#2ec860" opacity="0.5"/>
                    <text x="15" y="45" text-anchor="middle"
                          font-family="'Press Start 2P',monospace"
                          font-size="8" fill="white" font-weight="bold">B</text>
                    <!-- A button (upper right) — blue circle -->
                    <rect x="36" y="2" width="26" height="26" rx="13" fill="#000"/>
                    <rect x="38" y="4" width="22" height="22" rx="11" fill="#2255e8"/>
                    <rect x="38" y="4" width="22" height="6" rx="0" fill="#5588ff" opacity="0.5"/>
                    <text x="49" y="19" text-anchor="middle"
                          font-family="'Press Start 2P',monospace"
                          font-size="8" fill="white" font-weight="bold">A</text>
                  </svg>

                  <!-- Speaker grille — 5 diagonal lines bottom-right style -->
                  <svg viewBox="0 0 36 28" width="36" height="28"
                       style="image-rendering:pixelated;display:block;opacity:0.75">
                    <line x1="2"  y1="28" x2="8"  y2="0"  stroke="#000" stroke-width="3" stroke-linecap="square"/>
                    <line x1="9"  y1="28" x2="15" y2="0"  stroke="#000" stroke-width="3" stroke-linecap="square"/>
                    <line x1="16" y1="28" x2="22" y2="0"  stroke="#000" stroke-width="3" stroke-linecap="square"/>
                    <line x1="23" y1="28" x2="29" y2="0"  stroke="#000" stroke-width="3" stroke-linecap="square"/>
                    <line x1="30" y1="28" x2="36" y2="0"  stroke="#000" stroke-width="3" stroke-linecap="square"/>
                    <line x1="2"  y1="28" x2="8"  y2="0"  stroke="#7a50b0" stroke-width="2" stroke-linecap="square"/>
                    <line x1="9"  y1="28" x2="15" y2="0"  stroke="#7a50b0" stroke-width="2" stroke-linecap="square"/>
                    <line x1="16" y1="28" x2="22" y2="0"  stroke="#7a50b0" stroke-width="2" stroke-linecap="square"/>
                    <line x1="23" y1="28" x2="29" y2="0"  stroke="#7a50b0" stroke-width="2" stroke-linecap="square"/>
                    <line x1="30" y1="28" x2="36" y2="0"  stroke="#7a50b0" stroke-width="2" stroke-linecap="square"/>
                  </svg>
                </div>
              </div>

              <!-- Bottom strip: name + select/start + speech + controls -->
              <div class="bmo-bottom">
                <!-- name + style pill + select/start row -->
                <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                  <span class="avatar-name" id="avatar-name">ครู AI</span>
                  <!-- Style pill with white left-arrow -->
                  <span class="avatar-style-pill" id="avatar-style-pill">😂 สายฮา</span>
                  <span style="font-size:11px;color:#fff;font-weight:bold;margin-left:0">←</span>
                  <!-- select/start pixel buttons — triangle (select) + circle (start) -->
                  <div style="display:flex;gap:6px;align-items:center;margin-left:auto">
                    <!-- SELECT — triangle pixel -->
                    <div style="display:flex;flex-direction:column;align-items:center;gap:2px">
                      <svg width="16" height="12" viewBox="0 0 16 12" style="image-rendering:pixelated">
                        <polygon points="8,0 0,12 16,12" fill="#4a2a7a" stroke="#000" stroke-width="1"/>
                      </svg>
                      <span style="font-size:5px;color:#9a70c0;font-family:'Press Start 2P',monospace">SEL</span>
                    </div>
                    <!-- START — circle pixel -->
                    <div style="display:flex;flex-direction:column;align-items:center;gap:2px">
                      <svg width="14" height="14" viewBox="0 0 14 14" style="image-rendering:pixelated">
                        <rect x="0" y="0" width="14" height="14" rx="7" fill="#000"/>
                        <rect x="1" y="1" width="12" height="12" rx="6" fill="#4a2a7a"/>
                      </svg>
                      <span style="font-size:5px;color:#9a70c0;font-family:'Press Start 2P',monospace">STA</span>
                    </div>
                  </div>
                </div>

                <!-- controls row — single unified play button -->
                <div class="avatar-controls">
                  <!-- hidden shim so old JS refs to avatar-play-btn don't error -->
                  <div id="avatar-play-btn" style="display:none"></div>
                  <button class="btn btn-red btn-sm" id="btn-tts-speak"
                    onclick="ttsSmartPlay()"
                    style="font-size:10px;padding:4px 10px;border-radius:4px;min-width:90px">▶ ฟังบทเรียน</button>
                  <select id="avatar-voice-sel"
                    style="font-size:10px;padding:3px 6px;width:auto;border-radius:4px;flex:1;min-width:0">
                    <option value="th-TH-PremwadeeNeural">🎙 Premwadee</option>
                    <option value="th-TH-NiwatNeural">🎙 Niwat</option>
                    <option value="th-TH-AcharaNeural">🎙 Achara</option>
                  </select>
                  <button class="btn btn-ghost btn-sm" onclick="avatarRegen()"
                    style="font-size:10px;padding:4px 8px;border-radius:4px">🔄</button>
                  <input type="checkbox" id="tts-cache-toggle" checked
                         style="accent-color:var(--green);width:14px;height:14px">
                  <label for="tts-cache-toggle"
                         style="font-size:10px;color:var(--muted);cursor:pointer">cache</label>
                  <span id="avatar-status" style="font-size:10px;color:var(--muted)"></span>
                  <!-- wave dots hidden — keep IDs for JS compatibility -->
                  <div id="avatar-sound-dots" style="display:none">
                    <span id="av-dot-0"></span><span id="av-dot-1"></span>
                    <span id="av-dot-2"></span><span id="av-dot-3"></span>
                    <span id="av-dot-4"></span>
                  </div>
                </div>
              </div>

              <!-- hidden shims so old JS refs don't error -->
              <div id="avatar-glow"    style="display:none"></div>
              <div id="avatar-svg-wrap" style="display:none"></div>
            </div>
            <!-- Speech bubble — hidden, kept for JS compat -->
            <div id="avatar-speech-bubble" style="display:none">สวัสดีครับ/ค่ะ พร้อมเรียนกันไหม?</div>
            <!-- ═══════════════════════════════════════ -->

            <div id="les-tab-content" class="tab-content active content-box">เลือกบทเรียนแล้วกด อ่านบทเรียน</div>
            <div id="les-tab-hw"      class="tab-content content-box"></div>
          </div>
            <!-- TTS Audio Player -->
            <div id="tts-player-wrap" style="display:none; margin-top:14px; padding:10px 12px; background:var(--ink2); border:1px solid var(--border); border-radius:8px;">
              <div style="font-size:11px; color:var(--muted); margin-bottom:6px;">🔊 เสียงบทเรียน — หยุด/เล่นต่อ/กรอได้</div>
              <audio id="tts-audio" controls style="width:100%; height:36px; accent-color:var(--gold);"></audio>
              <div style="display:flex; gap:8px; margin-top:8px; align-items:center; flex-wrap:wrap;">
                <select id="tts-voice-sel" style="font-size:11px; padding:4px 8px; width:auto;">
                  <option value="th-TH-PremwadeeNeural">🎙️ Premwadee (หญิง)</option>
                  <option value="th-TH-NiwatNeural">🎙️ Niwat (ชาย)</option>
                  <option value="th-TH-AcharaNeural">🎙️ Achara (หญิง 2)</option>
                </select>
                <button class="btn btn-ghost btn-sm" onclick="ttsRegenerate()" style="font-size:11px;">🔄 สร้างเสียงใหม่</button>
                <span id="tts-status" style="font-size:11px; color:var(--muted);"></span>
              </div>
            </div>
        </div>
        <div>
          <div class="card">
            <div class="card-title">💬 ถามครูเรื่องบทนี้</div>
            <div class="chat-box" id="lesson-chat" style="min-height:300px"></div>
            <div class="chat-row" style="margin-top:8px">
              <input type="text" id="lesson-chat-in" placeholder="ถามคำถามเกี่ยวกับบทนี้..." onkeypress="if(event.key==='Enter')lessonAsk()">
              <button class="btn btn-sm" onclick="lessonAsk()">ส่ง</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- [v2.9.3] INTERACTIVE QUIZ MODAL -->
    <div id="quiz-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:10003;overflow:auto;padding:20px 10px">
      <div style="max-width:780px;margin:0 auto;position:relative">
        <button onclick="closeQuizModal()" style="position:absolute;top:-8px;right:0;background:var(--red);color:white;border:none;border-radius:50%;width:30px;height:30px;font-size:16px;cursor:pointer;z-index:1">✕</button>
        <div class="card" style="margin-top:30px;border-color:var(--gold3)">
          <div class="card-title">🧩 แบบฝึกหัดระหว่างเรียน — <span id="qz-title">—</span></div>
          <div id="qz-topic" style="font-size:12px;color:var(--muted);margin-bottom:14px"></div>
          <div id="qz-loading" style="text-align:center;padding:30px;color:var(--muted)"><span class="spinner"></span> กำลังสร้างแบบฝึกหัด...</div>
          <div id="qz-content" style="display:none">
            <div id="qz-questions"></div>
            <div class="btn-row" style="margin-top:18px">
              <button class="btn" onclick="submitQuiz()">✅ ตรวจคำตอบ</button>
              <button class="btn btn-ghost btn-sm" onclick="regenQuiz()">🔄 สร้างใหม่</button>
              <button class="btn btn-ghost btn-sm" onclick="closeQuizModal()">ปิด</button>
            </div>
            <div id="qz-result" style="display:none;margin-top:16px;padding:14px;border-radius:8px;border:1px solid var(--gold3);background:rgba(200,168,75,0.08)">
              <div id="qz-score-line" style="font-size:18px;font-weight:bold;color:var(--gold);margin-bottom:10px"></div>
              <div id="qz-explanations" style="font-size:13px;line-height:2"></div>
            </div>
          </div>
          <div id="qz-error" style="display:none;color:var(--red);padding:14px"></div>
        </div>
      </div>
    </div>

    <!-- HOMEWORK -->
    <div id="page-homework" class="page">
      <div class="page-header">
        <div class="page-title">📝 ส่งงาน</div>
        <div class="page-sub">ครูจะตรวจตรงกับโจทย์ที่กำหนดไว้</div>
      </div>
      <div class="g2">
        <div>
          <div class="card">
            <label>วันที่</label>
            <select id="hw-day-sel"></select>
            <label>ประเภทงาน</label>
            <select id="hw-type-sel" onchange="hwTypeChange()">
              <option value="practice">Practice / ฝึกทำ</option>
              <option value="reflection">Reflection / สะท้อนความคิด</option>
              <option value="project">Project / โปรเจค</option>
              <option value="essay">Essay / เรียงความ</option>
              <option value="code">Code / โค้ด</option>
              <option value="others">อื่นๆ</option>
            </select>
            <div id="hw-custom-wrap" style="display:none; margin-top:8px">
              <label>ระบุประเภทงาน</label>
              <input type="text" id="hw-custom-in" placeholder="เช่น สรุปบทเรียน...">
            </div>
            <label>หมายเหตุถึงครู (ไม่บังคับ)</label>
            <input type="text" id="hw-note-in" placeholder="บอกครูเพิ่มเติม...">
            <hr class="sep">
            <div class="tabs">
              <div class="tab active" onclick="showTab('hwt','text')">⌨️ พิมพ์</div>
              <div class="tab" onclick="showTab('hwt','file')">📂 ไฟล์</div>
            </div>
            <div id="hwt-tab-text" class="tab-content active">
              <label>เนื้อหางาน</label>
              <textarea id="hw-content" rows="8" placeholder="วางงานที่นี่..."></textarea>
            </div>
            <div id="hwt-tab-file" class="tab-content">
              <label>อัปโหลดไฟล์</label>
              <input type="file" id="hw-file" accept=".txt,.md,.pdf,.jpg,.jpeg,.png,.webp">
            </div>
            <div class="btn-row">
              <button class="btn" onclick="submitHomework()">🤖 ส่งให้ครูตรวจ</button>
            </div>
          </div>
        </div>
        <div>
          <div class="card">
            <div class="card-title">📋 ผลการตรวจ</div>
            <div id="hw-result" class="content-box" style="min-height:340px">ส่งงานเพื่อดูผลการตรวจ...</div>
          </div>
        </div>
      </div>
    </div>

    <!-- CHAT -->
    <div id="page-chat" class="page">
      <div class="page-header">
        <div class="page-title">💬 ถามครู</div>
        <div class="page-sub">ครูรู้ทุกอย่างเกี่ยวกับหลักสูตรและความคืบหน้าของคุณ</div>
      </div>
      <div class="card" style="max-width:720px">
        <div class="teacher-tag" id="chat-teacher-tag" style="display:none">
          <div class="teacher-avatar" id="chat-av">A</div>
          <span id="chat-teacher-name">ครู</span>
        </div>
        <div id="chat-context-bar" class="chat-sys chat-msg" style="margin-bottom:10px; font-size:11px"></div>
        <div class="chat-box" id="main-chat" style="min-height:380px"></div>
        <div class="chat-row" style="margin-top:10px">
          <input type="text" id="chat-in" placeholder="ถามอะไรก็ได้..." onkeypress="if(event.key==='Enter')mainChat()">
          <button class="btn" onclick="mainChat()">ส่ง</button>
        </div>
        <div class="btn-row" style="margin-top:8px">
          <button class="btn btn-ghost btn-sm" onclick="clearMainChat()">🗑 ล้างแชท</button>
        </div>
      </div>
    </div>

    <!-- CURRICULUM MAP -->
    <div id="page-curriculum" class="page">
      <div class="page-header">
        <div class="page-title">🗺️ แผนการเรียน</div>
        <div class="page-sub" id="curr-sub">—</div>
      </div>
      <!-- ── Skill Tree / List toggle ── -->
      <div class="vt-row">
        <button class="vt-btn vt-active" id="vt-tree" onclick="stSwitchView('tree')">🗺 Skill Tree</button>
        <button class="vt-btn" id="vt-list" onclick="stSwitchView('list')">📋 List</button>
      </div>

      <!-- ── Skill Tree view ── -->
      <div id="skill-tree-view">
        <div class="st-card">
          <!-- Progress bar -->
          <div class="st-prog-wrap" id="st-prog-row">
            <div class="st-prog-label" id="st-prog-label">CLEARED 0/0</div>
            <div class="st-prog-bar"><div class="st-prog-fill" id="st-prog-fill" style="width:0%"></div></div>
            <div class="st-prog-pct" id="st-prog-pct">0%</div>
          </div>
          <!-- SVG canvas -->
          <div class="st-svg-scroll" id="skill-tree-container"></div>
        </div>
        <!-- Detail panel -->
        <div id="st-detail-panel" class="st-detail"></div>
      </div>

      <!-- ── List view (hidden by default) ── -->
      <div id="curriculum-list" style="display:none"></div>
      <!-- [FEAT-1c v2.5] Next Phase button for Roadmap -->
      <div id="next-phase-section" style="display:none; margin-top:20px">
        <div class="card" style="max-width:560px; border-color:var(--purple)">
          <div class="card-title">🚀 Roadmap ต่อเนื่อง</div>
          <div id="phase-info" style="font-size:13px;color:var(--muted);margin-bottom:12px"></div>
          <div class="btn-row">
            <button class="btn btn-purple" onclick="generateNextPhase()">✨ สร้าง Phase ถัดไป</button>
            <button class="btn btn-ghost btn-sm" onclick="viewPhaseCertificate()">🏛️ ดูใบรับรอง Phase</button>
          </div>
          <div id="next-phase-result" style="margin-top:10px;font-size:13px;color:var(--green)"></div>
        </div>
      </div>
    </div>

    <!-- ACHIEVEMENTS — v2.0 -->
    <div id="page-achievements" class="page">
      <div class="page-header">
        <div class="page-title">🏆 Achievements</div>
        <div class="page-sub">ความสำเร็จและใบรับรองของคุณ</div>
      </div>
      <!-- Level Card -->
      <div class="card" style="max-width:520px; margin-bottom:20px">
        <div class="card-title">⚡ Level & EXP</div>
        <div style="text-align:center; padding:16px 0">
          <div style="font-size:48px; margin-bottom:8px" id="ach-level-icon">🌱</div>
          <div style="font-family:var(--serif); font-size:24px; color:var(--gold)" id="ach-level-name">Seedling</div>
          <div style="font-size:13px; color:var(--muted); margin-top:4px" id="ach-exp-line">0 EXP</div>
          <div style="margin:14px auto; max-width:300px">
            <div class="prog-wrap" style="height:8px">
              <div class="exp-fill" id="ach-exp-bar" style="width:0%"></div>
            </div>
          </div>
          <div style="font-size:11px; color:var(--muted)" id="ach-next-line">ต้องการอีก 500 EXP เพื่อเลื่อนระดับ</div>
        </div>
      </div>
      <!-- Badges -->
      <div class="card">
        <div class="card-title">🏅 Badges</div>
        <div class="g3" id="badges-grid"></div>
      </div>
      <!-- Certificate -->
      <div class="card">
        <div class="card-title">🎓 ใบรับรอง</div>
        <div id="cert-status" style="font-size:13px; color:var(--muted); margin-bottom:12px">เรียนให้จบหลักสูตรเพื่อรับใบรับรอง</div>
        <div class="btn-row">
          <button class="btn btn-purple" onclick="viewCertificate()">📜 ดูใบรับรอง</button>
        </div>
      </div>
    </div>

    <!-- MANAGE COURSES — v2.0 -->
    <div id="page-manage" class="page">
      <div class="page-header">
        <div class="page-title">⚙️ จัดการหลักสูตร</div>
        <div class="page-sub">เรียนต่อ ดูสถิติ หรือลบหลักสูตร</div>
      </div>
      <div id="manage-list"></div>
      <div class="btn-row">
        <button class="btn" onclick="newCourse()">+ สร้างหลักสูตรใหม่</button>
      </div>
    </div>

    <!-- CACHE -->
    <div id="page-cache" class="page">
      <div class="page-header">
        <div class="page-title">🗑️ จัดการ Cache</div>
        <div class="page-sub">ลบ cache เพื่อ generate บทเรียนใหม่ (คะแนน Day นั้นจะถูกหักคืน)</div>
      </div>
      <div class="g2">
        <div class="card">
          <div class="card-title">Cache ปัจจุบัน</div>
          <div id="cache-list"></div>
          <div class="btn-row">
            <button class="btn btn-red btn-sm" onclick="clearAllCache()">🗑 ล้างทั้งหมด</button>
          </div>
        </div>
        <div class="card">
          <div class="card-title">📊 สถิติ</div>
          <div id="cache-stats" style="font-size:13px; line-height:2.4; color:var(--muted)"></div>
          <div id="score-sync-log" style="margin-top:10px; font-size:12px; color:#e88080"></div>
        </div>
      </div>
    </div>

  </main>
</div>

<!-- TOAST -->
<div class="toast" id="toast"></div>

<!-- Certificate modal -->
<div id="cert-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); z-index:10001; overflow:auto; padding:20px">
  <div style="max-width:720px; margin:0 auto; position:relative">
    <button onclick="closeCert()" style="position:absolute; top:-10px; right:0; background:var(--red); color:white; border:none; border-radius:50%; width:30px; height:30px; font-size:16px; cursor:pointer; z-index:1">✕</button>
    <iframe id="cert-frame" style="width:100%; height:80vh; border:none; border-radius:12px; margin-top:10px"></iframe>
  </div>
</div>

<script>
// ════════════════════════════════════════════════════════
// CONSTANTS (injected from Python)
// ════════════════════════════════════════════════════════
const PROVIDERS_DATA = """ + providers_json + r""";
const MENTOR_STYLES  = """ + mentor_json + r""";
const EXP_LEVELS     = """ + levels_json + r""";
const BADGES_DATA    = """ + badges_json + r""";

// ════════════════════════════════════════════════════════
// STATE
// ════════════════════════════════════════════════════════
const S = {
  enrollId    : null,
  courseId    : null,
  status      : {},
  courses     : [],
  chatHistory : [],      // main chat (in-memory, also persisted server-side)
  lessonChatH : [],
  provider    : null,
  apiKey      : '',
  model       : null,
  mentorStyle : 'friendly',
  ragUrl      : '',
  assessStep  : 0,
  assessDone  : false,
  sessionSec  : 0,
  learnerName : 'คุณ',
};

// ════════════════════════════════════════════════════════
// UTILS
// ════════════════════════════════════════════════════════
function toast(msg, type='', dur=3200) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (type ? ' '+type : '');
  setTimeout(() => el.className = 'toast', dur);
}

async function api(path, method='GET', body=null) {
  const opts = { method, headers: {'Content-Type':'application/json'} };
  if (body) opts.body = JSON.stringify(body);
  try {
    const r = await fetch(path, opts);
    return r.json();
  } catch(e) {
    return { error: e.message };
  }
}

function loading(elId, msg='กำลังโหลด...') {
  const el = document.getElementById(elId);
  if (el) el.innerHTML = `<span class="spinner"></span> ${msg}`;
}

function showTab(group, tab) {
  const pre = group + '-tab-';
  document.querySelectorAll('[id^="'+pre+'"]').forEach(el =>
    el.classList.toggle('active', el.id === pre+tab));
  document.querySelectorAll('.tabs .tab').forEach(t => {
    if (t.getAttribute('onclick')?.includes("'"+group+"'"))
      t.classList.toggle('active', t.getAttribute('onclick').includes("'"+tab+"'"));
  });
}

function appendChat(boxId, msg, role, name='') {
  const box = document.getElementById(boxId);
  if (!box) return;
  const div = document.createElement('div');
  div.className = 'chat-msg chat-' + role;
  const prefix = role==='user' ? (name||'คุณ')+': ' : role==='ai' ? (name||'ครู')+': ' : '';
  div.textContent = prefix + msg;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

// ════════════════════════════════════════════════════════
// TIMER
// ════════════════════════════════════════════════════════
setInterval(() => {
  S.sessionSec++;
  const h = Math.floor(S.sessionSec/3600);
  const m = Math.floor((S.sessionSec%3600)/60);
  const s = S.sessionSec%60;
  const disp = h>0 ? `${h}h ${String(m).padStart(2,'0')}m` : `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  document.getElementById('timer-display').textContent = '⏱ ' + disp;
  if (S.courseId && S.sessionSec % 60 === 0)
    api('/api/study_time', 'POST', {course_id: S.courseId, seconds: 60}).catch(()=>{});
}, 1000);

// ════════════════════════════════════════════════════════
// ENROLLMENT WIZARD
// ════════════════════════════════════════════════════════
function showWizard() {
  document.getElementById('wizard-view').style.display = 'flex';
  document.getElementById('app-view').style.display = 'none';
  buildProviderGrid();
  buildMentorGrid();
  loadSavedConfig();
}

function showApp() {
  document.getElementById('wizard-view').style.display = 'none';
  document.getElementById('app-view').style.display = 'flex';
}

async function loadSavedConfig() {
  const r = await api('/api/config');
  if (r.provider) {
    const hint = document.getElementById('saved-config-hint');
    hint.style.display = 'block';
    hint.textContent = `💾 พบ config บันทึกไว้: ${r.provider} / ${r.model} — คลิกเลือก provider เดิมเพื่อโหลดอัตโนมัติ`;
    // Pre-select saved provider
    S.savedConfig = r;
  }
}

function buildProviderGrid() {
  const grid = document.getElementById('provider-grid');
  const icons = {gemini:'🟦', openai:'🟩', anthropic:'🟧', ollama:'🖥️'};
  grid.innerHTML = Object.entries(PROVIDERS_DATA).map(([k,v]) =>
    `<div class="provider-card" id="pcard-${k}" onclick="selectProvider('${k}')">
      <div class="provider-icon">${icons[k]||'🤖'}</div>
      <div class="provider-name">${v.name}</div>
      <div class="provider-hint">${v.key_hint}</div>
    </div>`
  ).join('');
}

function buildMentorGrid() {
  const grid = document.getElementById('mentor-grid');
  grid.innerHTML = Object.entries(MENTOR_STYLES).map(([k,v], i) =>
    `<div class="mentor-card${i===1?' selected':''}" id="mc-${k}" onclick="selectMentor('${k}')">
      <div class="mentor-icon">${v.emoji}</div>
      <div class="mentor-name">${v.label}</div>
      <div class="mentor-desc">${v.desc}</div>
    </div>`
  ).join('');
  S.mentorStyle = 'friendly';
}

function selectProvider(id) {
  S.provider = id;
  document.querySelectorAll('.provider-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('pcard-'+id)?.classList.add('selected');
  // Auto-fill saved API key for this provider
  if (S.savedConfig?.providers?.[id]?.api_key) {
    document.getElementById('api-key-input').value = S.savedConfig.providers[id].api_key;
    document.getElementById('saved-key-note').style.display = 'block';
  } else {
    document.getElementById('saved-key-note').style.display = 'none';
  }
}

function selectMentor(id) {
  S.mentorStyle = id;
  document.querySelectorAll('.mentor-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('mc-'+id)?.classList.add('selected');
}

function selectProviderNext() {
  if (!S.provider) { toast('เลือก Provider ก่อนนะ', 'err'); return; }
  document.getElementById('ollama-note').style.display = S.provider==='ollama' ? 'block' : 'none';
  document.getElementById('apikey-hint').textContent = `API Key ของ ${PROVIDERS_DATA[S.provider].name} (รูปแบบ: ${PROVIDERS_DATA[S.provider].key_hint})`;
  wzNext('ws-apikey'); updateStepper(1);
}

async function verifyApiKey() {
  const key = document.getElementById('api-key-input').value.trim();
  if (!key && S.provider !== 'ollama') { toast('ใส่ API Key ก่อน', 'err'); return; }
  const statusEl = document.getElementById('apikey-status');
  statusEl.innerHTML = '<span class="spinner"></span> กำลังทดสอบ...';
  const r = await api('/api/verify_key', 'POST', {provider: S.provider, api_key: key, model: null});
  if (r.ok) {
    statusEl.innerHTML = '<span style="color:var(--green)">✅ เชื่อมต่อสำเร็จ!</span>';
    S.apiKey = key;
    buildModelList();
    setTimeout(() => { wzNext('ws-model'); updateStepper(2); }, 800);
  } else {
    statusEl.innerHTML = `<span style="color:var(--red)">❌ ${r.error||'ตรวจสอบ API Key'}</span>`;
    if (S.provider === 'ollama') {
      S.apiKey = '';
      buildModelList();
      setTimeout(() => { wzNext('ws-model'); updateStepper(2); }, 1500);
    }
  }
}

function buildModelList() {
  const models = PROVIDERS_DATA[S.provider]?.models || [];
  const saved  = S.savedConfig?.providers?.[S.provider]?.model;
  const el = document.getElementById('model-list-wz');
  el.innerHTML = models.map(m => {
    const isRec = saved ? m.id === saved : m.recommended;
    return `<div class="model-option${isRec?' selected':''}" id="mo-${m.id.replace(/[^a-z0-9]/gi,'_')}"
       onclick="selectModel('${m.id}')">
      <div class="model-radio${isRec?' selected':''}"></div>
      <div>
        <div style="font-size:13px;color:var(--ivory)">${m.id}</div>
        <div style="font-size:11px;color:var(--muted)">${m.label}</div>
      </div>
    </div>`;
  }).join('');
  const rec = models.find(m => saved ? m.id === saved : m.recommended);
  if (rec) S.model = rec.id;
}

function selectModel(id) {
  S.model = id;
  document.querySelectorAll('.model-option').forEach(el => {
    el.classList.remove('selected');
    el.querySelector('.model-radio')?.classList.remove('selected');
  });
  const safeId = 'mo-' + id.replace(/[^a-z0-9]/gi,'_');
  const el = document.getElementById(safeId);
  if (el) { el.classList.add('selected'); el.querySelector('.model-radio')?.classList.add('selected'); }
}

function subjectTyping() {
  const val = document.getElementById('subject-input').value.trim();
  document.getElementById('subject-next-btn').disabled = val.length < 2;
}

// ════════════════════════════════════════════════════════
// ASSESSMENT — Choice-based UI (refactored)
// ════════════════════════════════════════════════════════

// State for current assessment question
let _assessState = {
  selectedChoice: null,   // value ที่เลือก
  selectedDays: null,
  selectedHours: null,
  qType: null,
};

async function startAssessment() {
  const subject = document.getElementById('subject-input').value.trim();
  const name    = document.getElementById('learner-name-input').value.trim() || 'นักเรียน';
  const ragUrl  = document.getElementById('rag-url-input').value.trim();
  if (!subject) { toast('ใส่หัวข้อก่อน', 'err'); return; }
  S.subject = subject; S.learnerName = name; S.ragUrl = ragUrl;
  wzNext('ws-assessment'); updateStepper(5);

  const r = await api('/api/enrollment/create', 'POST', {
    provider: S.provider, api_key: S.apiKey||'', model: S.model,
    subject, learner_name: name, mentor_style: S.mentorStyle, rag_url: ragUrl
  });
  S.enrollId = r.enroll_id;
  const qr = await api('/api/enrollment/question', 'POST', {enroll_id: S.enrollId});
  renderAssessQuestion(qr);
}

function renderAssessQuestion(qr) {
  if (!qr || qr.done) {
    // All done
    document.getElementById('assess-question-card').style.display = 'none';
    document.getElementById('assess-choices').style.display = 'none';
    document.getElementById('assess-timeline').style.display = 'none';
    document.getElementById('assess-reason-row').style.display = 'none';
    document.getElementById('assess-text-row').style.display = 'none';
    document.getElementById('assess-done-row').style.display = 'flex';
    document.getElementById('assess-question-text').textContent = qr.summary || 'ครบแล้ว! กดดูแผนหลักสูตรได้เลย 🎯';
    document.getElementById('assess-question-card').style.display = 'block';
    document.getElementById('assess-progress-bar').style.width = '100%';
    document.getElementById('assess-step-label').textContent = 'ครบทุกข้อแล้ว! ✅';
    return;
  }

  _assessState = { selectedChoice: null, selectedDays: null, selectedHours: null, qType: qr.q_type };

  // Progress
  const pct = Math.round(((qr.step||0) / (qr.total_steps||6)) * 100);
  document.getElementById('assess-progress-bar').style.width = pct + '%';
  document.getElementById('assess-step-label').textContent = `ข้อ ${(qr.step||0)+1} / ${qr.total_steps||6}`;

  // Question text
  document.getElementById('assess-question-text').textContent = qr.question;
  document.getElementById('assess-question-card').style.display = 'block';

  // Hide all input areas first
  document.getElementById('assess-choices').style.display = 'none';
  document.getElementById('assess-timeline').style.display = 'none';
  document.getElementById('assess-reason-row').style.display = 'none';
  document.getElementById('assess-text-row').style.display = 'none';
  document.getElementById('assess-done-row').style.display = 'none';

  if (qr.q_type === 'choice' || qr.q_type === 'choice+reason') {
    const el = document.getElementById('assess-choices');
    el.innerHTML = '';
    (qr.choices||[]).forEach(ch => {
      const label = ch.label || ch.value;
      const btn = document.createElement('button');
      btn.className = 'assess-choice-btn';
      btn.innerHTML = `<span class="assess-choice-emoji">${ch.emoji||''}</span><span>${label}</span>`;
      btn.onclick = () => selectChoice(btn, ch.value, qr.q_type, qr.reason_placeholder);
      el.appendChild(btn);
    });
    el.style.display = 'flex';
    el.style.flexDirection = 'column';

    if (qr.q_type === 'choice+reason') {
      const ta = document.getElementById('assess-reason-input');
      ta.placeholder = qr.reason_placeholder || 'รายละเอียดเพิ่มเติม (ไม่บังคับ)';
      ta.value = '';
      // reason row shows after choice selected → handled in selectChoice()
    }

  } else if (qr.q_type === 'choice_timeline') {
    const daysEl  = document.getElementById('assess-days-choices');
    const hoursEl = document.getElementById('assess-hours-choices');
    daysEl.innerHTML = '';
    hoursEl.innerHTML = '';
    (qr.days_choices||[]).forEach(ch => {
      const btn = document.createElement('button');
      btn.className = 'assess-choice-btn assess-choice-small';
      btn.textContent = ch.label;
      btn.dataset.value = ch.value;
      btn.onclick = () => selectTimeline(btn, 'days');
      daysEl.appendChild(btn);
    });
    (qr.hours_choices||[]).forEach(ch => {
      const btn = document.createElement('button');
      btn.className = 'assess-choice-btn assess-choice-small';
      btn.textContent = ch.label;
      btn.dataset.value = ch.value;
      btn.onclick = () => selectTimeline(btn, 'hours');
      hoursEl.appendChild(btn);
    });
    document.getElementById('assess-timeline-confirm').style.display = 'none';
    document.getElementById('assess-timeline').style.display = 'block';

  } else {
    // fallback text
    document.getElementById('assess-input').value = '';
    document.getElementById('assess-text-row').style.display = 'block';
    setTimeout(() => document.getElementById('assess-input').focus(), 100);
  }
}

function selectChoice(btn, value, qType, reasonPlaceholder) {
  document.querySelectorAll('#assess-choices .assess-choice-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  _assessState.selectedChoice = value;

  if (qType === 'choice+reason') {
    const ta = document.getElementById('assess-reason-input');
    ta.placeholder = reasonPlaceholder || 'รายละเอียดเพิ่มเติม (ไม่บังคับ)';
    ta.value = '';
    document.getElementById('assess-reason-row').style.display = 'block';
    setTimeout(() => ta.focus(), 80);
  } else {
    submitChoiceAnswer(value);
  }
}

async function submitWithReason(skip = false) {
  if (!_assessState.selectedChoice) { toast('เลือกตัวเลือกก่อนนะครับ', 'err'); return; }
  const reason = skip ? '' : document.getElementById('assess-reason-input').value.trim();
  const answer = reason ? `${_assessState.selectedChoice} — ${reason}` : _assessState.selectedChoice;
  await submitChoiceAnswer(answer);
}

function selectTimeline(btn, group) {
  const parent = btn.parentElement;
  parent.querySelectorAll('.assess-choice-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  if (group === 'days')  _assessState.selectedDays  = btn.dataset.value;
  if (group === 'hours') _assessState.selectedHours = btn.dataset.value;
  if (_assessState.selectedDays && _assessState.selectedHours) {
    document.getElementById('assess-timeline-confirm').style.display = 'block';
  }
}

async function confirmTimeline() {
  if (!_assessState.selectedDays || !_assessState.selectedHours) {
    toast('เลือกจำนวนวันและชั่วโมงด้วยนะครับ', 'err'); return;
  }
  const answer = `${_assessState.selectedDays} วัน วันละ ${_assessState.selectedHours} ชั่วโมง`;
  await submitChoiceAnswer(answer);
}

async function assessAnswerText() {
  const input = document.getElementById('assess-input');
  const answer = input.value.trim();
  if (!answer) return;
  input.value = '';
  await submitChoiceAnswer(answer);
}

async function submitChoiceAnswer(answer) {
  document.getElementById('assess-reason-row').style.display = 'none';
  document.querySelectorAll('#ws-assessment button').forEach(b => b.disabled = true);
  const r = await api('/api/enrollment/answer', 'POST', {enroll_id: S.enrollId, answer});
  document.querySelectorAll('#ws-assessment button').forEach(b => b.disabled = false);
  renderAssessQuestion(r);
}

async function previewCurriculum() {
  wzNext('ws-preview'); updateStepper(6);
  const loadEl    = document.getElementById('preview-loading');
  const contentEl = document.getElementById('preview-content');
  const logEl     = document.getElementById('preview-log');
  loadEl.style.display = 'block';
  contentEl.style.display = 'none';

  // แสดง progress log ขณะรอ
  const steps = [
    '⏳ วิเคราะห์คำตอบของคุณ...',
    '🧑‍🏫 สร้างบุคลิกครู AI...',
    '📐 ออกแบบโครงสร้างหลักสูตร...',
    '📅 จัดลำดับเนื้อหาทุกวัน...',
    '✦ เกือบเสร็จแล้ว...',
  ];
  let si = 0;
  logEl.innerHTML = steps[si++] + '<br>';
  const interval = setInterval(() => {
    if (si < steps.length) logEl.innerHTML += steps[si++] + '<br>';
  }, 3500);

  const r = await api('/api/enrollment/preview', 'POST', {enroll_id: S.enrollId});
  clearInterval(interval);
  loadEl.style.display = 'none';

  if (r.error) {
    document.getElementById('preview-sub').textContent = '❌ ' + r.error;
    loadEl.style.display = 'block';
    logEl.innerHTML += '❌ ' + r.error;
    return;
  }

  // Meta badges
  document.getElementById('preview-meta').innerHTML = [
    `📅 ${r.total_days} วัน`,
    `⏱️ วันละ ${r.hours_per_day} ชม.`,
    `🎯 ระดับ${r.level}`,
  ].map(t => `<span class="preview-badge">${t}</span>`).join('');

  if (r.goal) document.getElementById('preview-sub').textContent = `เป้าหมาย: ${r.goal}`;

  // Day accordion list
  const daysEl = document.getElementById('preview-days');
  daysEl.innerHTML = (r.days||[]).map(d => {
    const topics = d.topics ? d.topics.split(',').map(t => t.trim()).filter(Boolean) : [];
    const topicsHtml = topics.length
      ? topics.map(t => `• ${t}`).join('<br>')
      : '(รายละเอียดจะถูกสร้างเมื่อเริ่มเรียน)';
    return `<div class="preview-day">
      <div class="preview-day-header" onclick="togglePreviewDay(this)">
        <span class="preview-day-num">วัน ${String(d.day).padStart(2,'0')}</span>
        <span class="preview-day-title">${d.title}</span>
        <span class="preview-day-arrow">▶</span>
      </div>
      <div class="preview-day-topics">${topicsHtml}</div>
    </div>`;
  }).join('');

  contentEl.style.display = 'block';
}

function togglePreviewDay(header) {
  const arrow  = header.querySelector('.preview-day-arrow');
  const topics = header.nextElementSibling;
  const isOpen = topics.classList.contains('open');
  // ปิดทุกอัน
  document.querySelectorAll('.preview-day-topics.open').forEach(el => el.classList.remove('open'));
  document.querySelectorAll('.preview-day-arrow.open').forEach(el => el.classList.remove('open'));
  // เปิดอันที่กด (ถ้ายังไม่ได้เปิด)
  if (!isOpen) {
    topics.classList.add('open');
    arrow.classList.add('open');
    header.scrollIntoView({behavior:'smooth', block:'nearest'});
  }
}

async function generateCourse() {
  wzNext('ws-generating'); updateStepper(6);
  const log = document.getElementById('gen-log');
  const statusEl = document.getElementById('gen-status');
  log.innerHTML = '';
  statusEl.textContent = 'ครู AI กำลังออกแบบหลักสูตรเฉพาะสำหรับคุณ';
  // Remove any previous retry button
  document.getElementById('gen-retry-btn')?.remove();

  const steps = [
    '✦ วิเคราะห์ผลการประเมิน...',
    S.ragUrl ? '✦ ดึงข้อมูลจาก URL (RAG)...' : '✦ เตรียมข้อมูล...',
    '✦ สร้างบุคลิกครู ' + (MENTOR_STYLES[S.mentorStyle]?.label||'') + '...',
    '✦ ออกแบบ curriculum...',
    '✦ จัดลำดับเนื้อหา...',
    '✦ บันทึกหลักสูตร + config...',
  ];
  let si = 0;
  const interval = setInterval(() => { if (si < steps.length) { log.innerHTML += steps[si++] + '<br>'; } }, 900);
  const r = await api('/api/enrollment/generate', 'POST', {enroll_id: S.enrollId});
  clearInterval(interval);
  if (r.course_id) {
    log.innerHTML += '✅ สร้างหลักสูตรสำเร็จ!<br>';
    statusEl.textContent = `"${r.title}" พร้อมแล้ว!`;
    S.courseId = r.course_id;
    setTimeout(async () => {
      await loadCourseData(S.courseId);
      showApp(); nav('dashboard');
    }, 1200);
  } else {
    // [BUG-FIX] Session ยังอยู่ (retryable) — แสดงปุ่ม retry ไม่ต้องเริ่มใหม่
    log.innerHTML += '❌ เกิดข้อผิดพลาด<br>';
    statusEl.textContent = '❌ ' + (r.error||'เกิดข้อผิดพลาด');
    const retryBtn = document.createElement('button');
    retryBtn.id = 'gen-retry-btn';
    retryBtn.className = 'btn btn-sm';
    retryBtn.style.marginTop = '14px';
    retryBtn.textContent = '🔄 ลองใหม่อีกครั้ง';
    retryBtn.onclick = generateCourse;
    document.getElementById('gen-log').after(retryBtn);
  }
}

function wzNext(stepId) {
  document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
  document.getElementById(stepId)?.classList.add('active');
}
function wzBack(stepId) { wzNext(stepId); }
function updateStepper(active) {
  for (let i = 0; i <= 6; i++) {
    const el = document.getElementById('st-'+i);
    if (!el) continue;
    el.classList.remove('active','done');
    if (i < active) el.classList.add('done');
    else if (i === active) el.classList.add('active');
  }
}

// ════════════════════════════════════════════════════════
// APP NAVIGATION
// ════════════════════════════════════════════════════════
function nav(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-'+page)?.classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {
    if (n.getAttribute('onclick')?.includes("'"+page+"'")) n.classList.add('active');
  });
  // Sync mobile bottom nav
  document.querySelectorAll('.mob-nav-item').forEach(n => n.classList.remove('active'));
  const mitem = document.getElementById('mnav-'+page);
  if (mitem) mitem.classList.add('active');
  // Close sidebar on mobile after nav
  closeSidebar();
  if (page === 'dashboard')    refreshDashboard();
  if (page === 'lesson')       onEnterLesson();
  if (page === 'homework')     onEnterHomework();
  if (page === 'chat')         onEnterChat();
  if (page === 'curriculum')   onEnterCurriculum();
  if (page === 'achievements') onEnterAchievements();
  if (page === 'manage')       onEnterManage();
  if (page === 'cache')        onEnterCache();
}

// Mobile sidebar toggle
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('active'); // เพิ่มบรรทัดนี้
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('active'); // เพิ่มบรรทัดนี้
}

function newCourse() { showWizard(); }

// ════════════════════════════════════════════════════════
// DATA LOADING
// ════════════════════════════════════════════════════════
async function loadCourseData(courseId) {
  // จำตำแหน่ง Scroll ปัจจุบัน
  const mainView = document.querySelector('.main');
  const scrollPos = mainView ? mainView.scrollTop : 0;

  const r = await api('/api/course/' + courseId);
  if (r.error) { toast('โหลดหลักสูตรไม่ได้: '+r.error, 'err'); return; }
  S.status   = r;
  if(typeof avatarInit==='function') avatarInit(r);
  S.courseId = courseId;
  refreshUI(r);

  // เลื่อนกลับไปตำแหน่งเดิมเนียนๆ
  if (mainView) {
    setTimeout(() => { mainView.scrollTop = scrollPos; }, 10);
  }
}


function refreshUI(d) {
  const t    = d.teacher || {};
  const prog = d.progress || {};
  const ginfo= d.gamification || {};

  // Sidebar
  document.getElementById('sidebar-course-name').textContent = d.title || '—';
  // Update mobile header
  const mhTitle = document.getElementById('mobile-header-title');
  if (mhTitle) {
    const text = d.title || 'Pockademy';
    mhTitle.innerHTML = `<span class="marquee-inner">${text}</span>`;
    // ถ้าข้อความสั้น (<20 ตัว) ไม่ต้องเลื่อน
    mhTitle.classList.toggle('short', text.length < 20);
  }

  // EXP bar in sidebar
  const levelName = ginfo.level_name || '🌱 Seedling';
  document.getElementById('sb-level-name').textContent = levelName;
  document.getElementById('sb-exp-val').textContent    = (ginfo.exp||0) + ' EXP';
  const mhExp = document.getElementById('mobile-header-exp');
  if (mhExp) mhExp.textContent = (ginfo.exp||0) + ' EXP · ' + (ginfo.level_name||'Seedling');
  document.getElementById('sb-exp-fill').style.width   = (ginfo.level_pct||0) + '%';

  // Teacher tags
  const initials = (t.name||'A').charAt(0).toUpperCase();
  ['teacher-av','lesson-av','chat-av'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = initials;
  });
  ['lesson-teacher-name','chat-teacher-name'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = t.name || 'ครู';
  });
  ['chat-teacher-tag'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = 'inline-flex';
  });

  // Dashboard stats
  document.getElementById('db-title').textContent = d.title || 'Dashboard';
  document.getElementById('db-sub').textContent   = `วิชา: ${d.subject} | ระดับ: ${d.level} | ${d.total_days} วัน`;
  document.getElementById('d-score').textContent  = prog.total_score||0;
  document.getElementById('d-days').textContent   = `${prog.days_done||0}/${d.total_days||0}`;
  document.getElementById('d-time').textContent   = prog.study_time||'00:00';
  document.getElementById('d-exp').textContent    = ginfo.exp||0;
  const pct = Math.min(100, (prog.total_score||0) / Math.max(1, d.total_days * 30) * 100);
  document.getElementById('d-prog').style.width     = pct + '%';
  document.getElementById('d-exp-prog').style.width = (ginfo.level_pct||0) + '%';

  // Teacher greeting
  if (t.greeting_phrase) {
    document.getElementById('teacher-greeting').style.display = 'inline-flex';
    document.getElementById('teacher-greeting-text').textContent = `${t.name}: "${t.greeting_phrase}"`;
  }

  // Today plan
  const today = prog.current_day || 1;
  const todayPlan = (d.curriculum||[]).find(p => p.day === today);
  if (todayPlan) {
    document.getElementById('d-today-plan').innerHTML =
      `<strong style="color:var(--gold)">วันที่ ${today}:</strong> ${todayPlan.title}`;
  }

  // Skill path
  buildSkillPath(d);

  // HW scores
  buildHwScores(prog);

  // Badges mini
  buildBadgesMini(ginfo.badges||[]);

  // Selects
  buildDaySelects(d);

  // Lesson info — [v2.9.8] อ่าน subject_name ก่อน (key ใหม่), fallback → subject → 'General Subject'
  const _subjectDisplay = (d.subject_name || d.subject || '').trim() || 'General Subject';
  document.getElementById('lesson-course-info').textContent = `วิชา: ${_subjectDisplay} | ระดับ: ${d.level||''} | ครู: ${t.name||''}`;

  // Chat context
  document.getElementById('chat-context-bar').textContent =
    `บริบท: ${d.subject} | Day ${today}/${d.total_days} | Score ${prog.total_score||0} | ${levelName}`;

  // Curriculum sub
  document.getElementById('curr-sub').textContent = `${d.title} — ${d.total_days} วัน`;

  // Sidebar courses
  loadSidebarCourses();
}


// [v3.0] buildSkillPath — แสดง ???? สำหรับ pending days + auto lazy-load
function buildSkillPath(d) {
  const el   = document.getElementById('skill-path');
  if (!el) return;
  const done = (d.progress?.days_completed)||[];
  const curr = d.progress?.current_day||1;
  const items = (d.curriculum||[]).slice(0, 10);

  el.innerHTML = items.map(p => {
    const isDone    = done.includes(p.day);
    const isActive  = p.day === curr;
    const isExam    = p.is_exam_day;
    const isPending = p._periods_pending === true || (p.periods||[]).length === 0;
    const cls = 'skill-item' + (isDone?' done':'') + (isActive?' active':'') + (isExam?' exam':'');
    const dotIcon = isDone ? '✓' : isExam ? '🎯' : p.day;
    const periods  = p.periods||[];
    const displayTitle = globalCleanDayTitle(p.title, p.day);

    // [v3.0] subList: แสดง ???? สำหรับ pending, คาบจริงสำหรับ expanded
    let subList = '';
    if (isPending) {
      // แสดง skeleton badge — click เพื่อ expand
      subList = `<div style="margin-top:5px">
        <span onclick="event.stopPropagation();lazyExpandDay(${p.day})"
          style="font-size:9px;padding:2px 10px;border-radius:10px;
            background:rgba(200,168,75,0.1);border:1px solid rgba(200,168,75,0.3);
            color:var(--muted);cursor:pointer;display:inline-block"
          title="คลิกเพื่อ generate รายละเอียดคาบเรียน">
          ⏳ กำลังรอ generate คาบเรียน — คลิกเพื่อ load
        </span>
      </div>`;
    } else if (periods.length > 0) {
      subList = `<div style="margin-top:5px;display:flex;flex-wrap:wrap;gap:4px">
        ${periods.map((pp, i) => {
          const n = i + 1;
          const st = periodStyle(pp.type||'');
          const rawName = pp.name || '';
          const shortName = globalCleanPeriod(pp, i);
          const displayShort = shortName.substring(0, 28) + (shortName.length > 28 ? '...' : '');
          const locked = isPeriodLocked(p.day, n);
          const lockStyle = locked
            ? 'background:rgba(80,80,80,0.2);border:1px solid rgba(150,150,150,0.2);color:var(--muted);cursor:not-allowed;opacity:0.6'
            : 'background:' + st.bg + ';border:1px solid ' + st.border + ';color:var(--ivory2);cursor:pointer;transition:filter 0.15s';
          const hoverAttr = locked ? '' : 'onmouseover="this.style.filter=\'brightness(1.2)\'" onmouseout="this.style.filter=\'\'"';
          const lockIcon = locked ? '🔒 ' : '';
          const tipText = locked ? 'ต้องอ่านบทเรียนและผ่านแบบฝึกหัดชั่วโมงก่อนหน้า' : rawName;
          return '<span onclick="event.stopPropagation();loadDayPeriodFromCurr(' + p.day + ',' + n + ')"'
            + ' style="font-size:9px;padding:2px 7px;border-radius:10px;' + lockStyle + '"'
            + ' ' + hoverAttr
            + ' title="' + tipText + '">' + lockIcon + 'ชม.' + n + ': ' + (displayShort||'คาบ '+n) + '</span>';
        }).join('')}
      </div>`;
    }

    return `<div class="${cls}" onclick="nav('lesson');document.getElementById('lesson-day-sel').value=${p.day};onDaySelChange()">
      <div class="skill-dot">${dotIcon}</div>
      <div class="skill-info">
        <div class="skill-title">${displayTitle}</div>
        <div class="skill-sub">${p.objectives||''}</div>
        ${subList}
      </div>
    </div>`;
  }).join('');

  if (d.curriculum?.length > 10) {
    el.innerHTML += `<div style="font-size:11px;color:var(--muted);margin-top:8px;padding-left:44px">...และอีก ${d.curriculum.length-10} บทเรียน — ดูทั้งหมดใน <a href="#" onclick="nav('curriculum');return false" style="color:var(--gold)">แผนการเรียน</a></div>`;
  }

  // [v3.0] Auto lazy-load วันปัจจุบันและวันถัดไป (background)
  autoLazyLoadNearby(d, curr);
}

// [v3.0] Lazy-load เมื่อ user คลิก ???? badge
async function lazyExpandDay(day) {
  if (!S.courseId) return;
  toast(`⏳ กำลัง generate คาบเรียน Day ${day}...`, '', 5000);
  const r = await api('/api/day_detail', 'POST', { course_id: S.courseId, day });
  if (r.ok || r.already_done) {
    toast(`✅ Day ${day} พร้อมแล้ว!`, 'ok');
    await loadCourseData(S.courseId); // refresh UI
  } else {
    toast(`❌ ${r.error || 'Generate ไม่สำเร็จ'}`, 'err');
  }
}

// [v3.0] Auto lazy-load วัน curr และ curr+1 แบบ background (ไม่รอ UI)
async function autoLazyLoadNearby(d, curr) {
  if (!S.courseId) return;
  const daysToLoad = [curr, curr + 1].filter(day => {
    const plan = (d.curriculum||[]).find(p => p.day === day);
    return plan && (plan._periods_pending === true || (plan.periods||[]).length === 0);
  });
  for (const day of daysToLoad) {
    console.log(`[Lazy] Auto-expanding Day ${day}...`);
    const r = await api('/api/day_detail', 'POST', { course_id: S.courseId, day });
    if (r.ok) {
      console.log(`[Lazy] Day ${day} expanded`);
      await loadCourseData(S.courseId);
    }
  }
}


function buildHwScores(prog) {
  const el = document.getElementById('d-hw-scores');
  if (!el) return;
  const scores = prog.homework_scores||{};
  const keys = Object.keys(scores).sort((a,b)=>parseInt(a.split('_')[1])-parseInt(b.split('_')[1]));
  if (!keys.length) { el.textContent='ยังไม่มีคะแนน'; return; }
  el.innerHTML = keys.map(k => {
    const day=k.split('_')[1], sc=scores[k], bar=Math.round(sc/20*100);
    return `<div style="display:flex;align-items:center;gap:8px;margin:4px 0">
      <span style="width:46px;color:var(--muted);font-size:12px">Day ${day}</span>
      <div style="flex:1;background:var(--ink2);border-radius:3px;height:6px">
        <div style="width:${bar}%;height:100%;background:linear-gradient(90deg,var(--gold3),var(--gold));border-radius:3px"></div>
      </div>
      <span style="color:var(--gold);font-size:11px;width:44px">${sc}/20</span>
    </div>`;
  }).join('');
}

function buildBadgesMini(earned) {
  const el = document.getElementById('d-badges');
  if (!el) return;
  if (!earned.length) { el.textContent='ยังไม่มี Badge'; return; }
  el.innerHTML = earned.map(b => {
    const bd = BADGES_DATA[b]||{icon:'🏅',name:b};
    return `<span class="badge-pill">${bd.icon} ${bd.name}</span>`;
  }).join('');
}

// [v2.9.9] globalCleanDayTitle — shared util สำหรับทุก dropdown/selector
// แก้ปัญหา: ชื่อภาษาไทยแสดงผิด เช่น "sssมะ:" หรือติด "Foundations & Core Taxonomy"
function globalCleanDayTitle(raw, dayNum) {
  if (!raw) return `Day ${dayNum}`;
  let t = raw
    // ลบ prefix เลขวัน ทั้งไทยและอังกฤษ
    .replace(/^วันที่\s*\d+\s*[:：]\s*/i, '')
    .replace(/^Day\s*\d+\s*[:：]\s*/i, '')
    // ลบ " — Day X Overview" / " - Day X" ท้าย
    .replace(/\s*[—–\-]\s*Day\s*\d+\s*Overview\s*$/i, '')
    .replace(/\s*[—–\-]\s*Day\s*\d+\s*$/i, '')
    .replace(/\s*\(Day\s*\d+\)\s*$/i, '')
    // ลบ "Day X Overview" ที่เกิดขึ้นกลางหรือต้น string
    .replace(/\bDay\s*\d+\s*Overview\b/gi, '')
    .replace(/\bOverview\b/gi, '')
    // ลบ "Foundations & Core Taxonomy" เมื่อเป็น artifact จาก fallback
    .replace(/^Foundations\s*&\s*Core\s*Taxonomy\s*[:\-]?\s*/i, '')
    // ลบ artifact ขยะ เช่น "sss" นำหน้า, ตัวอักษรสุ่มก่อนภาษาไทย/ตัวอักษรจริง
    .replace(/^[a-z]{1,4}(?=[ก-๙A-Z])/, '')
    // ลบ colon ที่เหลืออยู่ต้นบรรทัด
    .replace(/^[:：\s]+/, '')
    // ลบช่องว่างซ้ำ
    .replace(/\s{2,}/g, ' ')
    .trim();
  return t || `Day ${dayNum}`;
}

// [v2.9.9] globalCleanPeriod — ชื่อคาบย่อย: อ่าน period_title → name → 'Unassigned Topic'
// Priority: ชื่อจริงจาก name/period_title ก่อน — ไม่ใช้ focus มาแทนชื่อ
function globalCleanPeriod(pp, idx) {
  // อ่าน name จริง: period_title (new) → name (legacy)
  const rawName = (pp.period_title || pp.name || '').trim();

  if (!rawName) return 'Unassigned Topic';

  // ถ้ามี prefix "คาบที่ N:" หรือ "ชั่วโมง N:" ให้เอาส่วนหลัง colon เป็น shortName
  // แต่เก็บเลขคาบไว้เพื่อแสดงแบบ "ชั่วโมง N: ชื่อ"
  const periodNumMatch = rawName.match(/^(?:คาบที่|ชั่วโมง)\s*(\d+)\s*[:：]\s*([\s\S]+)/i);
  if (periodNumMatch) {
    const num = periodNumMatch[1];
    const title = periodNumMatch[2].trim();
    // ลบ artifact เพิ่มเติม
    const cleaned = title
      .replace(/^[:：\s]+/, '')
      .replace(/\s{2,}/g, ' ')
      .trim();
    return cleaned || `Topic ${num}`;
  }

  // ไม่มี prefix — return ตามเดิมหลัง clean artifacts
  const cleaned = rawName
    .replace(/^[:：\s]+/, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
  return cleaned || 'Unassigned Topic';
}

function buildDaySelects(d) {
  ['lesson-day-sel','hw-day-sel'].forEach(id => {
    const sel = document.getElementById(id);
    if (!sel) return;
    const curr = d.progress?.current_day||1;
    sel.innerHTML = (d.curriculum||[]).map(p => {
      // [v2.9.5.2] clean title ก่อนแสดงใน dropdown
      const cleanTitle = globalCleanDayTitle(p.title, p.day);
      return `<option value="${p.day}"${p.day===curr?' selected':''}>Day ${p.day}: ${cleanTitle}</option>`;
    }).join('');
  });
  // [v2.9.3] build period selector for current day
  onDaySelChange();
}

// [v2.9.9] เมื่อเปลี่ยน Day — rebuild period selector แบบ "ชั่วโมง X: ชื่อหัวข้อ"
function onDaySelChange() {
  const day = parseInt(document.getElementById('lesson-day-sel')?.value||'0');
  if (!day) return;
  const plan = (S.status.curriculum||[]).find(p => p.day === day)||{};
  const periods = plan.periods||[];
  const wrap = document.getElementById('period-sel-wrap');
  const sel  = document.getElementById('lesson-period-sel');
  const btnP = document.getElementById('btn-load-period-lesson');
  if (!wrap || !sel) return;

  if (periods.length > 0) {
    wrap.style.display = 'block';
    // [v3.1] แสดงสถานะ lock ในแต่ละคาบ
    sel.innerHTML = `<option value="0">— ทั้งวัน (ภาพรวม) —</option>` +
      periods.map((p, i) => {
        const num = i + 1;
        const cleanName = globalCleanPeriod(p, i);
        const shortName = cleanName.length > 45 ? cleanName.substring(0, 43) + '…' : cleanName;
        const locked = isPeriodLocked(day, num);
        const lockIcon = locked ? '🔒 ' : '';
        return `<option value="${num}" ${locked ? 'style="color:var(--muted)"' : ''}>${lockIcon}ชั่วโมง ${num}: ${shortName} [${p.type||''}]</option>`;
      }).join('');
    onPeriodSelChange();
  } else {
    wrap.style.display = 'none';
    if (btnP) btnP.style.display = 'none';
    document.getElementById('period-detail-hint').style.display = 'none';
  }
}

// [v2.9.9] เมื่อเปลี่ยน Period — แสดง hint "ชั่วโมง X: ชื่อหัวข้อ + focus"
function onPeriodSelChange() {
  const day    = parseInt(document.getElementById('lesson-day-sel')?.value||'0');
  const period = parseInt(document.getElementById('lesson-period-sel')?.value||'0');
  const btnP   = document.getElementById('btn-load-period-lesson');
  const hint   = document.getElementById('period-detail-hint');
  if (!day) return;
  const plan    = (S.status.curriculum||[]).find(p => p.day === day)||{};
  const periods = plan.periods||[];

  if (period > 0 && periods[period-1]) {
    const p = periods[period-1];
    const locked = isPeriodLocked(day, period);

    if (hint) {
      hint.style.display = 'block';
      if (locked) {
        // [v3.1] แสดง lock message
        const prevPeriod = period - 1;
        const quizResults = S.status?.progress?.quiz_results || {};
        const prevResult = quizResults[`${day}_${prevPeriod}`];
        const prevScore = prevResult ? `(ครั้งล่าสุด: ${prevResult.score}/${prevResult.total})` : '(ยังไม่เคยทำ)';
        // [v3.2] แสดงสถานะทั้งสองเงื่อนไข
        const periodsRead = S.status?.progress?.periods_read || {};
        const prevRead = (periodsRead[String(day)] || []).includes(prevPeriod);
        const prevQuizPassed = (S.status?.progress?.quiz_results || {})[String(day)+'_'+prevPeriod]?.passed === true;
        hint.innerHTML =
          `<div style="color:var(--red);font-size:13px">🔒 <strong>ชั่วโมง ${period} ถูกล็อค</strong></div>` +
          `<div style="color:var(--muted);font-size:12px;margin-top:4px">ต้องทำครบ 2 ขั้นตอนสำหรับชั่วโมง ${prevPeriod}:</div>` +
          `<div style="font-size:12px;margin-top:4px">${prevRead ? '✅' : '⬜'} อ่านบทเรียนและกดยืนยัน</div>` +
          `<div style="font-size:12px;margin-top:2px">${prevQuizPassed ? '✅' : '⬜'} ทำแบบฝึกหัดผ่าน (≥3/5) ${prevScore}</div>` +
          `<div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">` +
          (!prevRead ? `<button class="btn btn-sm" style="font-size:11px;padding:4px 12px" onclick="document.getElementById('lesson-period-sel').value=${prevPeriod};onPeriodSelChange();loadPeriodLesson()">📖 เรียนคาบ ${prevPeriod}</button>` : '') +
          (!prevQuizPassed && prevRead ? `<button class="btn btn-sm" style="font-size:11px;padding:4px 12px" onclick="document.getElementById('lesson-period-sel').value=${prevPeriod};onPeriodSelChange();openInteractiveQuiz()">📝 ทำแบบฝึกหัดคาบ ${prevPeriod}</button>` : '') +
          `</div>`;
      } else {
        const cleanedName = globalCleanPeriod(p, period-1);
        const focusPart = p.focus
          ? `<div style="color:var(--gold2);font-size:12px;margin-bottom:4px">🎯 <strong>${p.focus}</strong></div>`
          : '';
        const subject = (S.status.subject_name || S.status.subject || '').trim() || 'General Subject';
        // [v2.9.9] แสดงเป็น "ชั่วโมง X: ชื่อหัวข้อ"
        hint.innerHTML =
          `<strong style="color:var(--gold2)">ชั่วโมง ${period}: ${cleanedName}</strong>` +
          `<span style="font-size:10px;color:var(--muted);margin-left:6px">(${subject})</span><br>` +
          `<span style="color:var(--muted)">${p.time_slot||''} · ${p.type||''}</span>` +
          focusPart +
          (p.detail ? `<br><span style="color:var(--ivory2)">${p.detail}</span>` : '');
      }
    }
    // [v3.1] ซ่อนปุ่มเรียนถ้า locked
    if (btnP) {
      btnP.style.display = locked ? 'none' : 'inline-flex';
    }
  } else {
    if (hint) hint.style.display = 'none';
    if (btnP) btnP.style.display = 'none';
  }
  
  // [ใหม่] ตรวจสอบ Activity Gate หากเรียนครบแล้วให้แสดงปุ่มการบ้าน
  const hwBtn = document.getElementById('btn-hw-view');
  if (hwBtn && day) {
    api(`/api/activity_gate?course_id=${S.courseId}&day=${day}&activity=homework`).then(res => {
      hwBtn.style.display = res.enabled ? 'inline-flex' : 'none';
    });
  }
}


async function loadSidebarCourses() {
  const r = await api('/api/courses');
  S.courses = r.courses||[];
  const el = document.getElementById('course-list-sidebar');
  if (!el) return;
  el.innerHTML = S.courses.map(c => `
    <div class="course-mini${c.id===S.courseId?' active-course':''}" onclick="switchCourse('${c.id}')">
      <div class="course-mini-title">${c.title||c.subject}</div>
      <div class="course-mini-sub">${c.days_done}/${c.total_days} วัน · ${c.total_score} pts · ${c.level_name||''}</div>
      <div class="course-mini-prog">
        <div class="course-mini-fill" style="width:${Math.round(c.days_done/Math.max(1,c.total_days)*100)}%"></div>
      </div>
    </div>`).join('')||'<div style="padding:8px 12px;font-size:12px;color:var(--muted)">ยังไม่มีหลักสูตร</div>';
}

async function switchCourse(id) {
  S.courseId=id; S.chatHistory=[]; S.lessonChatH=[];
  await loadCourseData(id); nav('dashboard');
}

async function refreshDashboard() {
  if (!S.courseId) return;
  await loadCourseData(S.courseId);
}

// ════════════════════════════════════════════════════════
// LESSON
// ════════════════════════════════════════════════════════
function onEnterLesson() {}

async function loadLesson() {
  const day = parseInt(document.getElementById('lesson-day-sel').value);
  if (!day) return;
  showLessonMeta(day, 0); showTab('les','content');
  loading('les-tab-content', 'ครูกำลังสอน...');
  const r = await api(`/api/lesson?course_id=${S.courseId}&day=${day}`);
  document.getElementById('les-tab-content').textContent = r.content||r.error||'—';
  toast('✅ โหลดบทเรียน Day '+day);
  await loadCourseData(S.courseId);
  // Load persistent lesson chat
  loadPersistentLessonChat(day);
}

// [v2.9.3] โหลดบทเรียนย่อย (period/sub-lesson)
async function loadPeriodLesson() {
  const day    = parseInt(document.getElementById('lesson-day-sel').value);
  const period = parseInt(document.getElementById('lesson-period-sel').value||'0');
  if (!day || !period) { loadLesson(); return; }

  // [v3.2] ตรวจสอบ Lock Gate — ต้องทั้งอ่านจบและผ่าน Quiz คาบก่อนหน้า
  if (isPeriodLocked(day, period)) {
    const prevPeriod = period - 1;
    const periodsRead = S.status?.progress?.periods_read || {};
    const dayRead = periodsRead[String(day)] || [];
    const prevRead = dayRead.includes(prevPeriod);
    const quizResults = S.status?.progress?.quiz_results || {};
    const prevQuizPassed = quizResults[`${day}_${prevPeriod}`]?.passed === true;

    showLessonMeta(day, period); showTab('les','content');
    const missingHtml = [
      !prevRead   ? `<div style="padding:6px 0;font-size:13px">⬜ 📖 อ่านบทเรียนคาบที่ ${prevPeriod} ให้จบก่อน</div>` : `<div style="padding:6px 0;font-size:13px;color:var(--green)">✅ อ่านคาบที่ ${prevPeriod} จบแล้ว</div>`,
      !prevQuizPassed ? `<div style="padding:6px 0;font-size:13px">⬜ 📝 ทำแบบฝึกหัดคาบที่ ${prevPeriod} ให้ผ่าน (≥3/5)</div>` : `<div style="padding:6px 0;font-size:13px;color:var(--green)">✅ ผ่านแบบฝึกหัดคาบที่ ${prevPeriod} แล้ว</div>`,
    ].join('');
    document.getElementById('les-tab-content').innerHTML =
      `<div style="text-align:center;padding:40px 20px;color:var(--muted)">` +
      `<div style="font-size:48px;margin-bottom:16px">🔒</div>` +
      `<div style="font-size:16px;color:var(--ivory2);margin-bottom:8px"><strong>ชั่วโมง ${period} ถูกล็อคอยู่</strong></div>` +
      `<div style="font-size:13px;margin-bottom:16px;color:var(--muted)">ต้องทำครบทั้งสองขั้นตอนนี้ก่อน:</div>` +
      `<div style="text-align:left;display:inline-block;margin-bottom:20px">${missingHtml}</div><br>` +
      `<button class="btn" onclick="document.getElementById('lesson-period-sel').value=${prevPeriod};onPeriodSelChange();loadPeriodLesson()">📖 กลับไปเรียนคาบ ${prevPeriod}</button>` +
      (prevRead ? ` <button class="btn" style="margin-left:8px" onclick="document.getElementById('lesson-period-sel').value=${prevPeriod};onPeriodSelChange();openInteractiveQuiz()">📝 ทำแบบฝึกหัดคาบ ${prevPeriod}</button>` : '') +
      `</div>`;
    toast(`🔒 ต้องอ่านจบและผ่านแบบฝึกหัดคาบ ${prevPeriod} ก่อน`, 'err');
    return;
  }

  showLessonMeta(day, period); showTab('les','content');
  loading('les-tab-content', `ครูกำลังสอน คาบที่ ${period}...`);
  const r = await api(`/api/period_lesson?course_id=${S.courseId}&day=${day}&period=${period}`);
  
  // [ใหม่] แทรกเนื้อหาพร้อมปุ่มกดยืนยันการอ่านจบ
  const rawContent = r.content || r.error || '—';
  document.getElementById('les-tab-content').innerHTML = `
    <div style="white-space: pre-wrap; font-size: 14px; color: var(--ivory2);">${rawContent}</div>
    <hr class="sep">
    <div style="text-align:center; margin-top: 20px;">
        <button class="btn btn-purple" id="btn-mark-complete" onclick="markManualComplete(${day}, ${period})">✅ ยืนยันว่าอ่านคาบนี้จบแล้ว</button>
    </div>
  `;
  // [v3.2] ไม่ auto-mark เมื่อโหลด — ต้องรอ user กดปุ่ม "อ่านจบแล้ว" เองก่อน
  // การ mark จะเกิดขึ้นผ่าน markManualComplete() เท่านั้น
  // [v2.9.9] อ่าน period_title → name → 'Unassigned Topic' / subject_name → subject → 'General Subject'
  const plan = (S.status.curriculum||[]).find(p => p.day === day)||{};
  const periods = plan.periods||[];
  const periodName = periods[period-1] ? globalCleanPeriod(periods[period-1], period-1) : 'Unassigned Topic';
  const subject = (S.status.subject_name || S.status.subject || '').trim() || 'General Subject';
  toast(`✅ ${subject} · Day ${day} ชั่วโมง ${period}: ${periodName}`);
  loadPersistentLessonChat(day);
}
async function markManualComplete(day, period) {
    const btn = document.getElementById('btn-mark-complete');
    btn.textContent = '⏳ กำลังบันทึก...';
    btn.disabled = true;

    const r = await api('/api/mark_period_read', 'POST', { course_id: S.courseId, day, period });
    if (r.ok) {
        // [v3.2] อัปเดต periods_read ใน memory ทันที
        if (!S.status.progress) S.status.progress = {};
        if (!S.status.progress.periods_read) S.status.progress.periods_read = {};
        if (!S.status.progress.periods_read[String(day)]) S.status.progress.periods_read[String(day)] = [];
        if (!S.status.progress.periods_read[String(day)].includes(period))
            S.status.progress.periods_read[String(day)].push(period);

        // ตรวจว่าผ่าน quiz คาบนี้ด้วยหรือยัง
        const quizResults = S.status?.progress?.quiz_results || {};
        const quizPassed = quizResults[`${day}_${period}`]?.passed === true;

        btn.textContent = '✅ อ่านจบแล้ว!';
        btn.className = 'btn';
        btn.style.background = 'var(--green)';
        btn.disabled = true;

        await loadCourseData(S.courseId);
        onPeriodSelChange();

        if (quizPassed) {
            toast(`🔓 ครบทั้งสองเงื่อนไข! คาบ ${period+1} ปลดล็อกแล้ว`, 'ok');
        } else {
            toast(`✅ อ่านคาบ ${period} จบแล้ว — อย่าลืมทำแบบฝึกหัดด้วยนะ!`, 'ok');
            // แสดงปุ่มทำแบบฝึกหัดต่อ
            const quizHint = document.createElement('div');
            quizHint.style.cssText = 'text-align:center;margin-top:12px';
            quizHint.innerHTML = `<button class="btn btn-purple" onclick="openInteractiveQuiz()">📝 ทำแบบฝึกหัดคาบ ${period} เลย</button>
              <div style="font-size:11px;color:var(--muted);margin-top:6px">ต้องผ่านแบบฝึกหัด (≥3/5) ถึงจะปลดล็อกคาบถัดไป</div>`;
            btn.parentNode.appendChild(quizHint);
        }
    } else {
        toast('เกิดข้อผิดพลาดในการบันทึก', 'err');
        btn.textContent = '❌ ลองใหม่อีกครั้ง';
        btn.disabled = false;
    }
}



async function loadHomeworkView() {
  const day = parseInt(document.getElementById('lesson-day-sel').value);
  if (!day) return;
  showLessonMeta(day, 0); showTab('les','hw');
  loading('les-tab-hw', 'ดึงโจทย์...');
  const r = await api(`/api/homework_view?course_id=${S.courseId}&day=${day}`);
  document.getElementById('les-tab-hw').textContent = r.content||r.error||'—';
}

// ════════════════════════════════════════════════════════
// [TTS v2] อ่านบทเรียนด้วย edge-tts → .mp3 → <audio> tag
// หยุด/เล่นต่อ/กรอหน้า-หลัง ได้ 100% เหมือนฟังเพลง
// ════════════════════════════════════════════════════════
function cleanTextForTTS(text) {
  return text
    // ── 1. Strip Markdown formatting ──
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#{1,6}\s*/g, '')
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/_{1,2}(.*?)_{1,2}/g, '$1')
    // ── 2. Remove ALL emoji / pictographs (Unicode ranges) ──
    .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')   // emoticons, symbols, etc.
    .replace(/[\u{2600}-\u{27BF}]/gu, '')      // misc symbols, dingbats
    .replace(/[\u{2300}-\u{23FF}]/gu, '')      // misc technical
    .replace(/[\u{FE00}-\u{FEFF}]/gu, '')      // variation selectors
    .replace(/[\u{1F3FB}-\u{1F3FF}]/gu, '')    // skin tone modifiers
    .replace(/\u200D/g, '')                    // zero-width joiner
    // ── 3. Clean bullet/list markers ──
    .replace(/^[-+*•]\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    // ── 4. Normalize punctuation for natural pausing ──
    .replace(/:{2,}/g, ':')                    // multiple colons → one
    .replace(/!{2,}/g, '!')
    .replace(/\?{2,}/g, '?')
    .replace(/\.{4,}/g, '...')
    // ── 5. Collapse whitespace / newlines ──
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[^\S\n]+/g, ' ')
    .replace(/\n/g, ' ')                       // newlines → space (TTS reads better)
    .replace(/ {2,}/g, ' ')
    .trim();
}

function _ttsGetAudio() { return document.getElementById('tts-audio'); }
function _ttsGetWrap()  { return document.getElementById('tts-player-wrap'); }
function _ttsGetStatus(){ return document.getElementById('tts-status'); }

function _ttsSetStatus(msg) {
  const el = _ttsGetStatus();
  if (el) el.textContent = msg;
}

// ════════════════════════════════════════════════════════
// ttsSmartPlay — ปุ่มเดียวครบ: สร้าง + เล่น + หยุด + ปากขยับ
// detect เนื้อหาเปลี่ยน → สร้างไฟล์ใหม่อัตโนมัติ
// ════════════════════════════════════════════════════════
const _TTS_STATE = {
  day: null, period: null, contentSig: null,   // signature ของเนื้อหาที่โหลดล่าสุด
};

function _ttsContentSig() {
  // fingerprint สั้นๆ จากเนื้อหาปัจจุบัน (day + period + 80 ตัวอักษรแรก)
  const day    = parseInt(document.getElementById('lesson-day-sel')?.value || '0');
  const period = parseInt(document.getElementById('lesson-period-sel')?.value || '0');
  const el     = document.getElementById('les-tab-content');
  const snip   = (el ? (el.innerText || el.textContent || '') : '').trim().substring(0, 80);
  return `${day}_${period}_${snip}`;
}

function _ttsBtn() { return document.getElementById('btn-tts-speak'); }
function _ttsBtnState(state) {
  const btn = _ttsBtn();
  if (!btn) return;
  const states = {
    idle:     { text: '▶ ฟังบทเรียน', disabled: false },
    loading:  { text: '⏳ กำลังสร้าง...', disabled: true },
    playing:  { text: '⏸ หยุด', disabled: false },
    paused:   { text: '▶ เล่นต่อ', disabled: false },
  };
  const s = states[state] || states.idle;
  btn.textContent = s.text;
  btn.disabled    = s.disabled;
}

async function ttsSmartPlay() {
  const contentEl = document.getElementById('les-tab-content');
  const rawText = contentEl ? (contentEl.innerText || contentEl.textContent || '') : '';
  const isPlaceholder = !rawText
    || rawText.trim() === 'เลือกบทเรียนแล้วกด อ่านบทเรียน'
    || rawText.startsWith('ครูกำลังสอน')
    || rawText.startsWith('กำลังโหลด');
  if (isPlaceholder) { toast('กรุณาโหลดบทเรียนก่อน', 'err'); return; }

  const sig = _ttsContentSig();
  const contentChanged = sig !== _TTS_STATE.contentSig;

  // ── กรณี: กำลังเล่นอยู่ → หยุด ──
  if (AV.speaking && AV.mediaEl && !AV.mediaEl.paused && !contentChanged) {
    AV.mediaEl.pause();
    _avStopAnimation();
    _ttsBtnState('paused');
    return;
  }

  // ── กรณี: หยุดอยู่ + เนื้อหาไม่เปลี่ยน → เล่นต่อ ──
  if (AV.mediaEl && AV.mediaEl.paused && AV.mediaEl.src && !contentChanged) {
    AV.mediaEl.play();
    _avStartAnimation();
    _ttsBtnState('playing');
    AV.mediaEl.onended = () => { _avStopAnimation(); _ttsBtnState('idle'); _avSetStatus(''); };
    return;
  }

  // ── กรณี: เนื้อหาเปลี่ยน หรือยังไม่เคยสร้าง → สร้างใหม่ ──
  if (contentChanged && AV.mediaEl) {
    // ลบ cache ของ day/period เดิมออกก่อน
    const oldDay    = _TTS_STATE.day;
    const oldPeriod = _TTS_STATE.period;
    if (oldDay !== null) {
      await api('/api/tts_cache', 'POST', {
        course_id: S.courseId, day: String(oldDay), period: String(oldPeriod)
      });
    }
    AV.mediaEl.pause(); AV.mediaEl.src = '';
    _avStopAnimation();
  }

  // ── Generate + เล่น ──
  const day    = parseInt(document.getElementById('lesson-day-sel')?.value || '1');
  const period = parseInt(document.getElementById('lesson-period-sel')?.value || '0');
  const voice  = document.getElementById('avatar-voice-sel')?.value
              || document.getElementById('tts-voice-sel')?.value
              || 'th-TH-PremwadeeNeural';
  const text   = cleanTextForTTS(rawText);

  _ttsBtnState('loading');
  _avSetStatus('กำลัง generate...');

  try {
    const r = await api('/api/tts_generate', 'POST', {
      course_id: S.courseId, day, period, text, voice
    });
    if (r.error) { toast('❌ ' + r.error, 'err'); _ttsBtnState('idle'); _avSetStatus(''); return; }

    // สร้าง/ใช้ซ้ำ audio element แบบ avatar (เพื่อให้ lip-sync analyser ทำงาน)
    let audio = document.getElementById('avatar-hidden-audio');
    if (!audio) {
      audio = document.createElement('audio');
      audio.id = 'avatar-hidden-audio';
      audio.crossOrigin = 'anonymous';
      document.body.appendChild(audio);
    }
    audio.src = r.url + '&t=' + Date.now();
    audio.load();
    _avConnectAudio(audio);
    AV.mediaEl = audio;
    audio.onended = () => { _avStopAnimation(); _ttsBtnState('idle'); _avSetStatus(''); };
    audio.play();
    _avStartAnimation();
    _ttsBtnState('playing');
    _avSetStatus(r.cached ? '✅ cache' : '✅ สร้างใหม่');

    // บันทึก signature
    _TTS_STATE.contentSig = sig;
    _TTS_STATE.day    = day;
    _TTS_STATE.period = period;

    // แสดง player bar ด้านล่างด้วย (sync กัน)
    const wrap = _ttsGetWrap();
    const ttsAudio = _ttsGetAudio();
    if (wrap && ttsAudio) {
      ttsAudio.src = r.url + '&t=' + Date.now();
      ttsAudio.load();
      wrap.style.display = 'block';
    }
  } catch(e) {
    toast('❌ ' + e, 'err');
    _ttsBtnState('idle');
    _avSetStatus('');
  }
}

// backward-compat shims — ฟังก์ชันเก่าที่อาจมีการเรียกจากที่อื่น
async function ttsGenerate()   { await ttsSmartPlay(); }
async function ttsRegenerate() {
  // บังคับลบ cache + สร้างใหม่โดย reset signature
  _TTS_STATE.contentSig = null;
  const day    = parseInt(document.getElementById('lesson-day-sel')?.value || '1');
  const period = parseInt(document.getElementById('lesson-period-sel')?.value || '0');
  await api('/api/tts_cache', 'POST', { course_id: S.courseId, day: String(day), period: String(period) });
  if (AV.mediaEl) { AV.mediaEl.pause(); AV.mediaEl.src = ''; }
  _avStopAnimation(); _ttsBtnState('idle');
  await ttsSmartPlay();
}


// [v2.9.3] Interactive Quiz — เปิด modal แบบฝึกหัด
let _quizData = null;
let _quizAnswers = {};

// ── [v3.1] Quiz Gate: ตรวจสอบว่าคาบนี้ต้องผ่าน Quiz คาบก่อนหน้าก่อนหรือไม่ ──
function isPeriodLocked(day, period) {
  // คาบแรกหรือภาพรวมทั้งวัน ไม่ถูกล็อค
  if (!period || period <= 1) return false;

  const prevPeriod = period - 1;

  // [v3.2] เงื่อนไขปลดล็อก: ต้องทั้ง "อ่านจบ" AND "ผ่าน quiz" ของคาบก่อนหน้า
  // 1) เช็คว่าอ่านคาบก่อนหน้าจบแล้วหรือยัง
  const periodsRead = S.status?.progress?.periods_read || {};
  const dayRead = periodsRead[String(day)] || [];
  const prevPeriodRead = dayRead.includes(prevPeriod);

  // 2) เช็คว่าผ่าน quiz คาบก่อนหน้าแล้วหรือยัง
  const quizResults = S.status?.progress?.quiz_results || {};
  const prevKey = `${day}_${prevPeriod}`;
  const prevResult = quizResults[prevKey];
  const prevQuizPassed = prevResult && prevResult.passed === true;

  // ต้องผ่านทั้งสองเงื่อนไขถึงจะปลดล็อก
  return !(prevPeriodRead && prevQuizPassed);
}

// ── [v3.1] Shuffle quiz choices แต่ยัง map เฉลยให้ถูกต้อง ──
function shuffleQuizChoices(questions) {
  return questions.map(q => {
    const entries = Object.entries(q.choices || {});
    // Fisher-Yates shuffle
    for (let i = entries.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [entries[i], entries[j]] = [entries[j], entries[i]];
    }
    // สร้าง mapping ใหม่: A/B/C/D → shuffled values
    const displayKeys = ['A', 'B', 'C', 'D', 'E'];
    const newChoices = {};
    const reverseMap = {}; // originalKey → newDisplayKey
    entries.forEach(([origKey, val], idx) => {
      const newKey = displayKeys[idx] || origKey;
      newChoices[newKey] = val;
      reverseMap[origKey] = newKey;
    });
    // อัปเดต answer ให้ตรงกับ display key ใหม่
    const newAnswer = reverseMap[q.answer] || q.answer;
    return { ...q, choices: newChoices, answer: newAnswer, _shuffled: true };
  });
}

async function openInteractiveQuiz(regenFlag) {
  if (!S.courseId) { toast('เลือกหลักสูตรก่อน', 'err'); return; }
  const day    = parseInt(document.getElementById('lesson-day-sel')?.value||'1');
  const period = parseInt(document.getElementById('lesson-period-sel')?.value||'0');

  // [v3.2] ตรวจว่าคาบนี้ถูกล็อค — ต้องทั้งอ่านจบและผ่าน Quiz คาบก่อนหน้า
  if (isPeriodLocked(day, period)) {
    const prevPeriod = period - 1;
    const periodsRead = S.status?.progress?.periods_read || {};
    const dayRead = periodsRead[String(day)] || [];
    const prevRead = dayRead.includes(prevPeriod);
    const quizResults = S.status?.progress?.quiz_results || {};
    const prevQuizPassed = quizResults[`${day}_${prevPeriod}`]?.passed === true;

    document.getElementById('quiz-modal').style.display = 'block';
    document.getElementById('qz-loading').style.display  = 'none';
    document.getElementById('qz-content').style.display  = 'none';
    document.getElementById('qz-result').style.display   = 'none';
    document.getElementById('qz-error').style.display    = 'block';
    document.getElementById('qz-title').textContent = `แบบฝึกหัด Day ${day} คาบ ${period}`;
    document.getElementById('qz-topic').textContent = '';
    document.getElementById('qz-error').innerHTML =
      `🔒 <strong>ยังเข้าแบบฝึกหัดคาบ ${period} ไม่ได้</strong><br><br>` +
      `${prevRead ? '✅' : '⬜'} อ่านบทเรียนคาบที่ ${prevPeriod} จบแล้ว<br>` +
      `${prevQuizPassed ? '✅' : '⬜'} ผ่านแบบฝึกหัดคาบที่ ${prevPeriod} (≥3/5)<br><br>` +
      `<small style="color:var(--muted)">ต้องครบทั้งสองข้อจึงจะปลดล็อกได้</small>`;
    return;
  }

  _quizAnswers = {};
  _quizData = null;

  // แสดง modal
  document.getElementById('quiz-modal').style.display = 'block';
  document.getElementById('qz-loading').style.display  = 'block';
  document.getElementById('qz-content').style.display  = 'none';
  document.getElementById('qz-error').style.display    = 'none';
  document.getElementById('qz-result').style.display   = 'none';
  document.getElementById('qz-title').textContent = `Day ${day}${period ? ' คาบ '+period : ''}`;
  document.getElementById('qz-topic').textContent = '';

  const regenParam = regenFlag ? '&regen=1' : '';
  const r = await api(`/api/quiz_structured?course_id=${S.courseId}&day=${day}&period=${period}${regenParam}`);

  document.getElementById('qz-loading').style.display = 'none';
  if (r.error || (!r.questions)) {
    document.getElementById('qz-error').style.display = 'block';
    document.getElementById('qz-error').innerHTML = `
        <div style="color:var(--red); text-align:center; padding:20px;">
            <div style="font-size:32px; margin-bottom:10px;">⚠️</div>
            <strong>AI สร้างแบบฝึกหัดไม่สำเร็จ (Timeout/Error)</strong><br>
            <span style="font-size: 12px; color: var(--muted);">${r.error || 'ระบบอาจมีการตอบสนองล่าช้า'}</span><br><br>
            <button class="btn btn-sm" onclick="openInteractiveQuiz(true)">🔄 ลองสร้างใหม่อีกครั้ง (Manual Retry)</button>
        </div>
    `;
    return;
  }

  // [v3.1] Shuffle choices ทุกครั้งที่เปิด (ยกเว้นกด regen — shuffle ใหม่จาก AI แล้ว)
  const shuffledQuestions = shuffleQuizChoices(r.questions);
  _quizData = { ...r, questions: shuffledQuestions };

  document.getElementById('qz-title').textContent = r.title||`แบบฝึกหัด Day ${day}`;
  document.getElementById('qz-topic').textContent = r.topic ? '📚 หัวข้อ: '+r.topic : '';
  document.getElementById('qz-content').style.display = 'block';
  renderQuizQuestions(shuffledQuestions);
}

function renderQuizQuestions(questions) {
  const container = document.getElementById('qz-questions');
  if (!questions || !questions.length) {
    container.innerHTML = '<div style="color:var(--muted);text-align:center;padding:20px">ไม่มีคำถาม</div>';
    return;
  }
  container.innerHTML = questions.map((q, qi) => {
    const choices = q.choices||{};
    const choiceHtml = Object.entries(choices).map(([k, v]) =>
      `<div class="qz-choice" id="qzc-${qi}-${k}" onclick="selectQuizChoice(${qi},'${k}')">
        <span class="qz-choice-key">${k}</span>
        <span class="qz-choice-text">${v}</span>
      </div>`
    ).join('');
    return `<div class="qz-question" id="qzq-${qi}">
      <div class="qz-q-num">ข้อที่ ${q.no||qi+1}</div>
      <div class="qz-q-text">${q.question||''}</div>
      <div class="qz-choices">${choiceHtml}</div>
      <div class="qz-explanation" id="qze-${qi}">${q.explanation||''}</div>
    </div>`;
  }).join('');
}

function selectQuizChoice(qi, key) {
  // deselect previous
  const prev = _quizAnswers[qi];
  if (prev) document.getElementById(`qzc-${qi}-${prev}`)?.classList.remove('selected');
  // select new
  _quizAnswers[qi] = key;
  document.getElementById(`qzc-${qi}-${key}`)?.classList.add('selected');
}

function submitQuiz() {
  if (!_quizData || !_quizData.questions) return;
  const questions = _quizData.questions;
  let correct = 0;
  questions.forEach((q, qi) => {
    const userAns = _quizAnswers[qi];
    const rightAns = q.answer;
    // show all choices
    Object.keys(q.choices||{}).forEach(k => {
      const el = document.getElementById(`qzc-${qi}-${k}`);
      if (!el) return;
      el.classList.remove('selected','correct','wrong');
      if (k === rightAns) el.classList.add('correct');
      else if (k === userAns && userAns !== rightAns) el.classList.add('wrong');
    });
    if (userAns === rightAns) correct++;
    // show explanation
    const expEl = document.getElementById(`qze-${qi}`);
    if (expEl) expEl.style.display = 'block';
  });
  const total  = questions.length;
  const pass   = _quizData.passing_score||3;
  const passed = correct >= pass;
  const resultEl = document.getElementById('qz-result');
  resultEl.style.display = 'block';
  resultEl.style.borderColor = passed ? 'var(--green)' : 'var(--red)';
  resultEl.style.background  = passed ? 'rgba(39,174,96,0.1)' : 'rgba(192,57,43,0.1)';
  document.getElementById('qz-score-line').textContent =
    `${passed ? '🎉' : '📚'} ได้ ${correct}/${total} ข้อ — ${passed ? 'ผ่านแล้ว!' : 'ยังไม่ผ่าน ลองใหม่นะ'}`;
  document.getElementById('qz-explanations').innerHTML =
    questions.map((q, qi) => {
      const ua = _quizAnswers[qi]||'—';
      const ok = ua === q.answer;
      return `<div style="color:${ok?'var(--green)':'var(--red)'}">
        ข้อ ${q.no||qi+1}: คุณตอบ <strong>${ua}</strong> ${ok?'✓ ถูก':'✗ ผิด'} (เฉลย: <strong>${q.answer}</strong>)
      </div>`;
    }).join('');
  // [v3.0] บันทึก quiz result + mark period complete เมื่อผ่าน
  const day    = _quizData.day    || parseInt(document.getElementById('lesson-day-sel')?.value||'1');
  const period = _quizData.period || 0;
  api('/api/save_quiz_result', 'POST', {
    course_id: S.courseId, day, period,
    score: correct, total, passed
  }).then(async sr => {
    // [v3.1] อัปเดต quiz_results ใน memory ทันที
    if (!S.status.progress) S.status.progress = {};
    if (!S.status.progress.quiz_results) S.status.progress.quiz_results = {};
    S.status.progress.quiz_results[`${day}_${period}`] = { passed, score: correct, total };

    // [v3.2] Refresh จาก server เพื่ออัปเดต lock status ทั้งหมด
    if (sr.ok) await loadCourseData(S.courseId);

    if (sr.ok && passed && period > 0) {
      // ตรวจว่า server บอกว่าปลดล็อกได้จริงหรือไม่ (ต้องอ่านจบ + ผ่าน quiz)
      const unlockData = sr.unlock || {};
      const nextPeriod = period + 1;
      const plan = (S.status.curriculum||[]).find(p => p.day === day)||{};
      const totalPeriods = (plan.periods||[]).length;

      if (unlockData.both_conditions_met && nextPeriod <= totalPeriods) {
        // ✅ อ่านจบแล้วและผ่าน quiz → ปลดล็อกคาบถัดไปได้
        toast(`🏆 ผ่านแล้ว! 🔓 ปลดล็อกชั่วโมง ${nextPeriod} แล้ว`, 'ok');
        const resultEl = document.getElementById('qz-result');
        const nextBtn = document.createElement('div');
        nextBtn.style.cssText = 'margin-top:12px;text-align:center';
        nextBtn.innerHTML = `<button class="btn" onclick="closeQuizModal();document.getElementById('lesson-period-sel').value=${nextPeriod};onPeriodSelChange();loadPeriodLesson()">▶ เรียนชั่วโมง ${nextPeriod} ต่อเลย</button>`;
        resultEl.appendChild(nextBtn);
      } else if (unlockData.both_conditions_met && nextPeriod > totalPeriods) {
        // ✅ ผ่านหมดทุกคาบแล้ว
        toast('🏆 ผ่านทุกคาบของวันนี้แล้ว! 🎉', 'ok');
      } else {
        // ✅ ผ่าน quiz แต่ยังไม่ได้อ่านบทเรียนคาบนี้ → แจ้งให้กลับไปอ่านก่อน
        toast(`✅ ผ่าน quiz แล้ว! แต่ต้องกลับไปอ่านบทเรียนคาบ ${period} ให้จบด้วย`, 'ok');
        const resultEl = document.getElementById('qz-result');
        const noteDiv = document.createElement('div');
        noteDiv.style.cssText = 'margin-top:12px;text-align:center;font-size:12px;color:var(--muted)';
        noteDiv.innerHTML = `📖 <strong>ยังไม่ได้อ่านบทเรียนคาบ ${period}</strong><br>กลับไปอ่านให้จบก่อน แล้วคาบ ${nextPeriod} จะปลดล็อกให้อัตโนมัติ<br>
          <button class="btn btn-ghost btn-sm" style="margin-top:8px" onclick="closeQuizModal();document.getElementById('lesson-period-sel').value=${period};onPeriodSelChange();loadPeriodLesson()">📖 กลับไปอ่านคาบ ${period}</button>`;
        resultEl.appendChild(noteDiv);
      }
    } else if (sr.ok && passed) {
      toast('🏆 ทำแบบฝึกหัดผ่าน! ได้ EXP เพิ่ม', 'ok');
    } else if (!passed) {
      toast(`📚 ได้ ${correct}/${total} — ลองใหม่ได้เลย (คำตอบจะสลับใหม่)`, 'err');
    }
  }).catch(() => {
    if (passed) toast('🏆 ทำแบบฝึกหัดผ่าน! ได้ EXP เพิ่ม', 'ok');
  });
}

async function regenQuiz() {
  openInteractiveQuiz(true);
}

function closeQuizModal() {
  document.getElementById('quiz-modal').style.display = 'none';
}

async function regenLesson() {
  const day = parseInt(document.getElementById('lesson-day-sel').value);
  if (!day) return;
  if (!confirm(`Regen บทเรียน Day ${day}?\n⚠️ คะแนน Day ${day} จะถูกหักคืน`)) return;
  showTab('les','content'); loading('les-tab-content', 'กำลัง Regen...');
  const r = await api(`/api/lesson?course_id=${S.courseId}&day=${day}&regen=1`);
  document.getElementById('les-tab-content').textContent = r.content||r.error||'—';
  toast('🔄 Regen Day '+day+' แล้ว');
  await loadCourseData(S.courseId);
}

// [v2.9.9] showLessonMeta — แสดง Day Title + ชั่วโมงย่อยแบบ "ชั่วโมง X: ชื่อหัวข้อ"
//   Level 1 (Main): subject_name → subject → 'General Subject'
//   Level 2 (Sub):  period_title → name → 'Unassigned Topic'
function showLessonMeta(day, period) {
  document.getElementById('lesson-meta-card').style.display = 'block';
  document.getElementById('lesson-teacher-tag').style.display = 'inline-flex';
  const plan = (S.status.curriculum||[]).find(p => p.day === day)||{};

  // Level 1 — ชื่อวิชาหลัก
  const subject = (S.status.subject_name || S.status.subject || '').trim() || 'General Subject';
  const level   = (S.status.level || '').trim();

  // ทำความสะอาด Day title
  const cleanTitle = globalCleanDayTitle(plan.title||'', day);
  let titleText = `Day ${day}: ${cleanTitle}`;

  // แสดงวิชาหลัก (Level 1) + ระดับใต้ title card
  const subjectLine = `<div style="font-size:11px;color:var(--muted);margin-top:2px">`
    + `📚 วิชา: <strong style="color:var(--gold2)">${subject}</strong>`
    + (level ? ` | ระดับ: ${level}` : '')
    + `</div>`;

  let objText = plan.objectives ? '🎯 '+plan.objectives : '';

  // Level 2 (Sub) — แสดงชั่วโมงย่อย: "ชั่วโมง X: ชื่อหัวข้อ"
  if (period > 0) {
    const periods = plan.periods||[];
    if (periods[period-1]) {
      const p = periods[period-1];
      const cleanPeriodName = globalCleanPeriod(p, period-1);
      // [v2.9.9] format: "ชั่วโมง X: ชื่อหัวข้อ"
      titleText = `Day ${day} · ชั่วโมง ${period}: ${cleanPeriodName}`;
      objText   = `<span class="period-badge">📌 ${p.type||''} · ${p.time_slot||''}</span>` +
                  (p.focus ? `<br><span style="font-size:12px;color:var(--gold2)">🎯 ${p.focus}</span>` : '') +
                  (p.detail ? `<br><span style="font-size:12px;color:var(--muted)">${p.detail}</span>` : '');
    }
  }

  document.getElementById('lesson-day-title').textContent = '';
  document.getElementById('lesson-day-title').innerHTML = titleText + subjectLine;
  document.getElementById('lesson-objectives').innerHTML = objText;
}

function loadPersistentLessonChat(day) {
  const hist = S.status?.chat_lesson?.[String(day)]||[];
  const box  = document.getElementById('lesson-chat');
  if (!box || !hist.length) return;
  box.innerHTML = '';
  const tname = S.status.teacher?.name||'ครู';
  hist.slice(-8).forEach(h => {
    appendChat('lesson-chat', h.user, 'user', S.learnerName);
    appendChat('lesson-chat', h.ai,   'ai',   tname);
  });
}

async function lessonAsk() {
  const input = document.getElementById('lesson-chat-in');
  const msg   = input.value.trim();
  if (!msg) return;
  const day   = parseInt(document.getElementById('lesson-day-sel').value)||1;
  const tname = S.status.teacher?.name||'ครู';
  appendChat('lesson-chat', msg, 'user', S.learnerName||'คุณ');
  input.value = '';
  S.lessonChatH.push({user: msg});
  const r = await api('/api/chat', 'POST', {
    course_id: S.courseId, message: msg, day, history: S.lessonChatH.slice(-6), persist_key: String(day)
  });
  const reply = r.reply||r.error||'—';
  appendChat('lesson-chat', reply, 'ai', tname);
  S.lessonChatH[S.lessonChatH.length-1].ai = reply;
}

// ════════════════════════════════════════════════════════
// HOMEWORK
// ════════════════════════════════════════════════════════
function onEnterHomework() {}
function hwTypeChange() {
  document.getElementById('hw-custom-wrap').style.display =
    document.getElementById('hw-type-sel').value==='others' ? 'block' : 'none';
}

async function submitHomework() {
  const day    = parseInt(document.getElementById('hw-day-sel').value);
  const hwType = document.getElementById('hw-type-sel').value;
  const customN= document.getElementById('hw-custom-in').value.trim();
  const note   = document.getElementById('hw-note-in').value.trim();
  if (!day) { toast('เลือกวันก่อน','err'); return; }

  const isFile = document.querySelector('#hwt-tab-file')?.classList.contains('active');
  if (isFile) {
    const fileEl = document.getElementById('hw-file');
    if (!fileEl.files?.[0]) { toast('เลือกไฟล์ก่อน','err'); return; }
    loading('hw-result', 'ครูกำลังตรวจ...');
    const fd = new FormData();
    fd.append('course_id',S.courseId); fd.append('day',day);
    fd.append('hw_type', hwType==='others'?(customN||'อื่นๆ'):hwType);
    fd.append('note',note); fd.append('file',fileEl.files[0]);
    const r = await fetch('/api/homework_file',{method:'POST',body:fd});
    const d = await r.json();
    document.getElementById('hw-result').textContent = d.feedback||d.error;
  } else {
    const content = document.getElementById('hw-content').value.trim();
    if (!content) { toast('ใส่เนื้อหาก่อน','err'); return; }
    loading('hw-result', 'ครูกำลังตรวจ...');
    const r = await api('/api/homework_text','POST',{
      course_id:S.courseId, day, hw_type: hwType==='others'?(customN||'อื่นๆ'):hwType, note, content
    });
    document.getElementById('hw-result').textContent = r.feedback||r.error;
  }
  toast('📬 ส่งงานแล้ว');
  await loadCourseData(S.courseId);
}

// ════════════════════════════════════════════════════════
// CHAT
// ════════════════════════════════════════════════════════
function onEnterChat() {
  const tname = S.status.teacher?.name||'ครู';
  // Load persistent main chat
  const hist = S.status?.chat_main||[];
  if (hist.length && !S.chatHistory.length) {
    const box = document.getElementById('main-chat');
    box.innerHTML = '';
    hist.slice(-8).forEach(h => {
      appendChat('main-chat',h.user,'user',S.learnerName);
      appendChat('main-chat',h.ai,'ai',tname);
    });
    S.chatHistory = hist.slice(-8);
  } else if (!S.chatHistory.length) {
    const phrase = S.status.teacher?.greeting_phrase;
    if (phrase) appendChat('main-chat', phrase, 'ai', tname);
  }
}

async function mainChat() {
  const input = document.getElementById('chat-in');
  const msg   = input.value.trim();
  if (!msg) return;
  const tname = S.status.teacher?.name||'ครู';
  const day   = S.status.progress?.current_day||1;
  appendChat('main-chat', msg, 'user', S.learnerName||'คุณ');
  input.value = '';
  S.chatHistory.push({user: msg});
  const r = await api('/api/chat','POST',{
    course_id:S.courseId, message:msg, day, history:S.chatHistory.slice(-10), persist_key:'main'
  });
  const reply = r.reply||r.error||'—';
  appendChat('main-chat', reply, 'ai', tname);
  S.chatHistory[S.chatHistory.length-1].ai = reply;
}

function clearMainChat() {
  document.getElementById('main-chat').innerHTML = '';
  S.chatHistory = [];
  toast('ล้างแชทแล้ว');
}

// ════════════════════════════════════════════════════════
// CURRICULUM
// ════════════════════════════════════════════════════════
// [v2.9] Time-type styles
const PERIOD_TYPE_STYLE = {
  'ทฤษฎี':              {bg:'rgba(41,128,185,0.15)',  border:'#2980b9', icon:'📖'},
  'สาธิต':              {bg:'rgba(142,68,173,0.15)', border:'#8e44ad', icon:'🎬'},
  'ปฏิบัติ':            {bg:'rgba(39,174,96,0.15)',  border:'#27ae60', icon:'🔧'},
  'Lab/ปฏิบัติขั้นสูง': {bg:'rgba(230,126,34,0.15)', border:'#e67e22', icon:'⚗️'},
  'ทบทวน':              {bg:'rgba(52,73,94,0.25)',    border:'#7f8c8d', icon:'🔁'},
  'สรุปผล':             {bg:'rgba(200,168,75,0.15)', border:'#c8a84b', icon:'📋'},
  'ขั้นสูง':            {bg:'rgba(192,57,43,0.15)',  border:'#c0392b', icon:'🚀'},
};
function periodStyle(type) {
  return PERIOD_TYPE_STYLE[type] || {bg:'rgba(255,255,255,0.05)', border:'var(--border)', icon:'📌'};
}

function buildPeriodsTimeline(periods) {
  if (!periods || !periods.length) return '';
  return `<div class="ts-timeline" style="margin-top:10px;border-left:2px solid var(--border);padding-left:12px">
    ${periods.map((p,i) => {
      const st = periodStyle(p.type||'');
      return `<div class="ts-period" style="margin-bottom:8px;padding:7px 10px;background:${st.bg};border:1px solid ${st.border};border-radius:6px;position:relative">
        <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
          <span style="font-family:var(--mono);font-size:11px;color:${st.border};white-space:nowrap;min-width:120px">${p.time_slot||''}</span>
          <span style="font-size:12px;font-weight:600;color:var(--ivory)">${st.icon} ${p.name||''}</span>
          <span style="font-size:10px;color:var(--muted);margin-left:auto;background:rgba(0,0,0,0.3);padding:1px 6px;border-radius:4px">${p.type||''}</span>
        </div>
        ${p.detail ? `<div style="font-size:11px;color:var(--muted);margin-top:4px;line-height:1.5">${p.detail}</div>` : ''}
      </div>`;
    }).join('')}
  </div>`;
}

function onEnterCurriculum() {
  const curr = S.status.curriculum||[];
  const done = S.status.progress?.days_completed||[];
  const el = document.getElementById('curriculum-list');

  // สร้าง Day cards
  el.innerHTML = curr.map(p => {
    const isDone = done.includes(p.day), isExam = p.is_exam_day;
    const periods = p.periods||[];
    const hasPeriods = periods.length > 0;
    const accentColor = isDone ? 'var(--gold)' : isExam ? 'var(--blue)' : 'var(--border)';

    // [v2.9.3] สร้าง sub-lesson (period) cards
    let periodsHtml = '';
    if (hasPeriods) {
      periodsHtml = `<div style="margin-top:12px">
        <div style="font-size:10px;color:var(--muted);letter-spacing:2px;margin-bottom:8px">📋 บทเรียนย่อย (${periods.length} คาบ)</div>
        ${periods.map((pp, i) => {
          const pn = i + 1;
          const st = periodStyle(pp.type||'');
          const fullName = pp.name || `คาบที่ ${pn}`;
          const subName  = fullName.replace(/^คาบที่\s*\d+\s*:\s*/i, '').trim();
          // [v2.9.4] แสดง focus ชัดเจนบน Dashboard
          const focusLine = pp.focus ? `<div style="font-size:11px;color:var(--gold2);margin-top:3px;font-style:italic">🎯 ${pp.focus}</div>` : '';
          return `<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:6px;padding:8px 10px;background:${st.bg};border:1px solid ${st.border};border-radius:6px">
            <div style="min-width:24px;height:24px;border-radius:50%;background:${st.border};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:var(--ink);flex-shrink:0">${pn}</div>
            <div style="flex:1;min-width:0">
              <div style="font-size:12px;font-weight:600;color:var(--ivory)">${st.icon} ${subName || fullName}</div>
              <div style="font-size:10px;color:var(--muted);margin-top:1px">${pp.time_slot||''} · ${pp.type||''}</div>
              ${focusLine}
              ${pp.detail ? `<div style="font-size:11px;color:var(--ivory2);margin-top:4px;line-height:1.5">${pp.detail}</div>` : ''}
            </div>
            <button class="btn btn-ghost btn-sm" style="flex-shrink:0;font-size:10px;padding:4px 10px" onclick="event.stopPropagation();loadDayPeriodFromCurr(${p.day},${pn})">${isPeriodLocked(p.day, pn) ? '🔒 ล็อค' : '▶ เรียนคาบนี้'}</button>
          </div>`;
        }).join('')}
      </div>`;
    }

    return `<div class="day-card" id="dc-${p.day}" style="background:var(--ink1);border:1px solid var(--border);border-left:4px solid ${accentColor};border-radius:8px;margin-bottom:10px;overflow:hidden">
      <!-- Day header — click to expand -->
      <div onclick="toggleDayCard(${p.day})" style="display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer;user-select:none">
        <div style="font-family:var(--serif);font-size:22px;color:${isDone?'var(--gold)':'var(--muted)'};min-width:36px;text-align:center">${isDone?'✓':p.day}</div>
        <div style="flex:1;min-width:0">
          <div style="font-size:14px;font-weight:600;color:${isDone?'var(--gold2)':'var(--ivory)'};display:flex;align-items:center;gap:6px">
            ${isExam?'<span style="background:rgba(41,128,185,0.3);padding:1px 6px;border-radius:3px;font-size:10px;color:#7fb3d3">EXAM</span>':''}
            Day ${p.day}: ${p.title}
          </div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.topics||''}</div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;flex-shrink:0">
          ${hasPeriods ? `<span style="font-size:10px;color:var(--muted);background:var(--ink2);padding:2px 7px;border-radius:10px">${periods.length} คาบ</span>` : ''}
          <span style="font-size:10px;color:var(--muted)">⭐${p.difficulty||1}</span>
          ${isDone?'<span style="color:var(--gold);font-size:12px">✅</span>':''}
          <span style="color:var(--muted);font-size:12px" id="dc-arr-${p.day}">▾</span>
        </div>
      </div>
      <!-- Expandable detail -->
      <div id="dc-body-${p.day}" style="display:none;padding:0 16px 14px;border-top:1px solid var(--border)">
        <div style="font-size:12px;color:var(--muted);padding-top:10px">🎯 ${p.objectives||''}</div>
        ${periodsHtml}
        ${p.homework_brief ? `<div style="margin-top:10px;padding:8px 10px;background:rgba(200,168,75,0.07);border:1px solid var(--gold3);border-radius:6px;font-size:11px;color:var(--ivory2)">📝 การบ้าน: ${p.homework_brief}</div>` : ''}
        <div style="margin-top:8px;text-align:right;display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap">
          <button class="btn btn-sm btn-ghost" onclick="event.stopPropagation();loadDayFromCurr(${p.day})">📖 เรียนทั้งวัน</button>
          <button class="btn btn-sm btn-ghost" onclick="event.stopPropagation();openQuizFromCurr(${p.day})">🧩 แบบฝึกหัด</button>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleDayCard(day) {
  const body = document.getElementById('dc-body-'+day);
  const arr  = document.getElementById('dc-arr-'+day);
  if (!body) return;
  const open = body.style.display === 'block';
  body.style.display = open ? 'none' : 'block';
  if (arr) arr.textContent = open ? '▾' : '▴';
}

function loadDayFromCurr(day) {
  document.getElementById('lesson-day-sel').value = day;
  // reset period to overview
  const psel = document.getElementById('lesson-period-sel');
  if (psel) psel.value = '0';
  nav('lesson');
  loadLesson();
}

// [v2.9.3] เรียนเฉพาะคาบ จากหน้า Curriculum
function loadDayPeriodFromCurr(day, period) {
  // [v3.1] เช็ค lock ก่อน navigate
  if (isPeriodLocked(day, period)) {
    const prevPeriod = period - 1;
    toast(`🔒 ต้องผ่านแบบฝึกหัดชั่วโมง ${prevPeriod} ก่อน`, 'err');
    // Navigate ไปที่หน้า lesson แล้วเปิด quiz คาบก่อนหน้า
    document.getElementById('lesson-day-sel').value = day;
    onDaySelChange();
    setTimeout(() => {
      const psel = document.getElementById('lesson-period-sel');
      if (psel) psel.value = prevPeriod;
      onPeriodSelChange();
      nav('lesson');
      openInteractiveQuiz();
    }, 80);
    return;
  }
  document.getElementById('lesson-day-sel').value = day;
  onDaySelChange(); // rebuild period sel
  setTimeout(() => {
    const psel = document.getElementById('lesson-period-sel');
    if (psel) psel.value = period;
    onPeriodSelChange();
    nav('lesson');
    loadPeriodLesson();
  }, 80);
}

// [v2.9.3] เปิดแบบฝึกหัดจากหน้า Curriculum
function openQuizFromCurr(day) {
  document.getElementById('lesson-day-sel').value = day;
  const psel = document.getElementById('lesson-period-sel');
  if (psel) psel.value = '0';
  onDaySelChange();
  openInteractiveQuiz();
}

// ════════════════════════════════════════════════════════
// ACHIEVEMENTS — v2.0
// ════════════════════════════════════════════════════════
function onEnterAchievements() {
  const prog = S.status.progress||{};
  const ginfo = S.status.gamification||{};
  const earned = ginfo.badges||[];
  const exp = ginfo.exp||0;
  const next = ginfo.next||500;
  const pct  = ginfo.level_pct||0;

  // Level
  document.getElementById('ach-level-icon').textContent = (ginfo.level_name||'🌱').split(' ')[0];
  document.getElementById('ach-level-name').textContent = ginfo.level_name||'Seedling';
  document.getElementById('ach-exp-line').textContent   = `${exp} EXP · Level ${ginfo.level||1}`;
  document.getElementById('ach-exp-bar').style.width    = pct + '%';
  document.getElementById('ach-next-line').textContent  = `ต้องการอีก ${Math.max(0,next-exp)} EXP เพื่อเลื่อนระดับ`;

  // Badges grid
  const grid = document.getElementById('badges-grid');
  grid.innerHTML = Object.entries(BADGES_DATA).map(([k,b]) => {
    const isEarned = earned.includes(k);
    return `<div class="badge-card${isEarned?' earned':''}">
      <div class="badge-icon"${!isEarned?' style="filter:grayscale(1);opacity:0.3"':''}>${b.icon}</div>
      <div class="badge-name">${b.name}</div>
      <div class="badge-desc">${b.desc}</div>
      <div class="badge-exp">+${b.exp} EXP${isEarned?' · ✅ ได้แล้ว':''}</div>
    </div>`;
  }).join('');

  // Certificate status
  const days_done  = prog.days_done||0;
  const total_days = S.status.total_days||1;
  const certEl = document.getElementById('cert-status');
  certEl.textContent = days_done >= total_days
    ? '🎉 คุณเรียนจบหลักสูตรแล้ว! กดดูใบรับรองด้านล่าง'
    : `เรียนอีก ${total_days - days_done} วัน เพื่อรับใบรับรอง (${days_done}/${total_days})`;
}

async function viewCertificate() {
  const r = await api(`/api/certificate?course_id=${S.courseId}`);
  if (r.html) {
    const frame = document.getElementById('cert-frame');
    const doc = frame.contentDocument || frame.contentWindow.document;
    doc.open(); doc.write(r.html); doc.close();
    document.getElementById('cert-modal').style.display = 'block';
  } else {
    toast(r.error||'ไม่สามารถสร้างใบรับรองได้','err');
  }
}
function closeCert() { document.getElementById('cert-modal').style.display='none'; }

// ════════════════════════════════════════════════════════
// MANAGE COURSES — v2.0
// ════════════════════════════════════════════════════════
async function onEnterManage() {
  const r = await api('/api/courses');
  const courses = r.courses||[];
  const el = document.getElementById('manage-list');
  if (!courses.length) {
    el.innerHTML = '<div class="card" style="text-align:center;color:var(--muted);padding:30px">ยังไม่มีหลักสูตร — กดสร้างหลักสูตรใหม่</div>';
    return;
  }
  el.innerHTML = courses.map(c => `
    <div class="manage-course-card">
      <div style="font-size:28px">${c.mentor_style==='strict'?'🔥':c.mentor_style==='funny'?'🤣':c.mentor_style==='professional'?'💼':'😊'}</div>
      <div class="manage-course-info">
        <div class="manage-course-title">${c.title||c.subject}</div>
        <div class="manage-course-sub">
          ${c.level} · ${c.days_done}/${c.total_days} วัน · ${c.total_score} pts · ${c.level_name||''} · ${c.exp||0} EXP
          ${(c.badges||[]).map(b=>BADGES_DATA[b]?.icon||'').join(' ')}
        </div>
      </div>
      <div class="manage-course-actions">
        <button class="btn btn-sm" onclick="switchCourse('${c.id}');nav('dashboard')">▶ เรียนต่อ</button>
        <button class="btn btn-red btn-sm" onclick="deleteCourse('${c.id}','${(c.title||'').replace(/'/g,"\\'")}')">🗑</button>
      </div>
    </div>`).join('');
}

async function deleteCourse(id, title) {
  if (!confirm(`ลบหลักสูตร "${title}"?\n⚠️ ข้อมูลทั้งหมดจะหายถาวร`)) return;
  const r = await api('/api/course/delete','POST',{course_id:id});
  if (r.ok) {
    toast('ลบหลักสูตรแล้ว','ok');
    if (S.courseId === id) { S.courseId=null; S.status={}; }
    await onEnterManage();
    await loadSidebarCourses();
    if (!S.courseId) showWizard();
  } else {
    toast('ลบไม่ได้: '+(r.error||''),'err');
  }
}

// ════════════════════════════════════════════════════════
// CACHE
// ════════════════════════════════════════════════════════
function onEnterCache() { loadCacheView(); }

async function loadCacheView() {
  if (!S.courseId) return;
  const r = await api(`/api/cache_info?course_id=${S.courseId}`);
  const list  = document.getElementById('cache-list');
  const stats = document.getElementById('cache-stats');
  if (!r.entries?.length) {
    list.innerHTML='<div style="color:var(--muted);font-size:13px;padding:10px">ไม่มี cache</div>';
  } else {
    list.innerHTML = r.entries.map(e => {
      const dayMatch=e.key.match(/(\d+)/); const day=dayMatch?parseInt(dayMatch[1]):null;
      return `<div style="display:flex;justify-content:space-between;align-items:center;padding:9px;margin:5px 0;background:var(--ink2);border-radius:6px;border:1px solid var(--border)">
        <div>
          <div style="font-size:13px;color:var(--ivory)">${e.key}</div>
          <div style="font-size:10px;color:var(--muted)">${e.ts||''}</div>
        </div>
        <button class="btn btn-red btn-sm" onclick="deleteCache('${e.key}',${day||'null'})">✕${day?' Day '+day:''}</button>
      </div>`;
    }).join('');
  }
  stats.innerHTML = `ทั้งหมด: ${r.total_keys} รายการ<br>บทเรียน: ${r.lesson_count} วัน<br>อัปเดต: ${r.last_updated||'—'}`;
}

async function deleteCache(key, day) {
  if (!confirm(`ลบ cache "${key}"?${day?' (หักคะแนน Day '+day+')':''}`)) return;
  const r = await api('/api/cache_delete','POST',{course_id:S.courseId, key, day});
  if (r.score_deducted>0) {
    document.getElementById('score-sync-log').innerHTML = `📉 หักคะแนน Day ${day}: -${r.score_deducted}`;
    toast(`ลบแล้ว — หัก ${r.score_deducted} คะแนน`,'err');
  } else toast('ลบ cache แล้ว');
  await loadCacheView(); await loadCourseData(S.courseId);
}

async function clearAllCache() {
  if (!confirm('⚠️ ล้าง cache ทั้งหมด? คะแนนทุก Day จะถูกหักคืน')) return;
  const r = await api('/api/cache_clear','POST',{course_id:S.courseId});
  const total=Object.values(r.sync||{}).reduce((a,b)=>a+b,0);
  if (total>0) {
    document.getElementById('score-sync-log').innerHTML=`📉 หักรวม -${total} คะแนน`;
    toast(`ล้าง cache แล้ว — หักรวม ${total}`,'err');
  } else toast('ล้าง cache แล้ว');
  await loadCacheView(); await loadCourseData(S.courseId);
}

// ════════════════════════════════════════════════════════
// INIT
// ════════════════════════════════════════════════════════
async function init() {
  const r = await api('/api/courses');
  const courses = r.courses||[];
  if (courses.length > 0) {
    S.courseId = courses[0].id;
    await loadCourseData(S.courseId);
    showApp(); nav('dashboard');
  } else {
    showWizard();
  }
}


// ════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════
// BMO GAME BOY CONSOLE — Lip-Sync Engine v1.0
// Web Audio API AnalyserNode + requestAnimationFrame
// ═══════════════════════════════════════════════════════════

// ── BMO mouth scale levels — 0=fully closed, 1=fully open ──────────────────────
// drives scaleY on #bmo-mouth-g (transform-origin: center of mouth)
const BMO_OPEN_H = {
  rest:   0,
  open_s: 0.25,
  open_m: 0.55,
  open_l: 1.0,
  talk_a: 0.70,
  talk_b: 0.35,
};
// Legacy shims
const BMO_MOUTH_STATES = {};
const BMO_MOUTHS = {};
const BMO_TONGUE_OP = {};

// ── Avatar state ─────────────────────────────────────────────
const AV = {
  style: 'friendly', audioCtx: null, analyser: null,
  source: null, mediaEl: null, rafId: null,
  speaking: false, currentText: '',
};

function _avGetStyle() {
  return (S.status && S.status.mentor_style) ? S.status.mentor_style : (AV.style || 'friendly');
}

const BMO_SPRITE_MOUTHS = {
  rest: "data:image/png;base64,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",
  talk_1: "data:image/png;base64,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",
  talk_2: "data:image/png;base64,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",
  talk_mid: "data:image/png;base64,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",
  o_shape: "data:image/png;base64,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",
  open_wide: "data:image/png;base64,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",
  talk_7: "data:image/png;base64,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",
  talk_8: "data:image/png;base64,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",
};

// ── Sprite mouth frame switcher ────────────────────────────────────────────
// Waveform amplitude 0..1 → ช่องปาก ตามคำอธิบาย lip-sync ภาษาไทย:
//   0%       → rest      (ช่อง 3 — เงียบ / ม,บ,ป)
//   1-25%    → talk_1    (ช่อง 1 — basic talk)
//   26-60%   → สลับ talk_2/7/8 (variation ดูเนียน)
//   61-85%   → open_wide (ช่อง 4 — สระอา/เน้นคำ)
//   86-100%  → scream    (ช่อง 6 — ตะโกน peak)
// + o_shape (ช่อง 5) แทรกก่อนกลับ rest (จัดการใน _bmoPickFrame)

// ── Mouth sprite state (simplified) ────────────────────────────────────────
const _TALK_FRAMES = ['rest', 'talk_1', 'talk_mid', 'open_wide', 'o_shape'];
let _bmoSilenceTimer = null;

function _bmoSetSpriteFrame(key) {
  const el = document.getElementById('bmo-sprite-mouth');
  if (el && BMO_SPRITE_MOUTHS[key]) el.setAttribute('href', BMO_SPRITE_MOUTHS[key]);
}

function _bmoSetMouth(key) { _bmoSetSpriteFrame('talk_2'); }
function _bmoLerpTick()    { }
function _bmoApplyScale(s) { }
function _avRenderSvg(k)   { _bmoSetSpriteFrame('talk_2'); }
function _avBuildSvg()     { return ''; }

function avatarInit(status) {
  const panel = document.getElementById('mentor-avatar-panel');
  if (!panel) return;
  panel.style.display = 'block';
  AV.style = status.mentor_style || 'friendly';
  const tp   = status.teacher_persona || {};
  const name = tp.name || status.teacher_name || 'ครู AI';
  document.getElementById('avatar-name').textContent = name;
  const styleLabels = { strict:'🔥 สายโหด', friendly:'😊 สายใจดี', funny:'🤣 สายฮา', professional:'💼 มือโปร' };
  document.getElementById('avatar-style-pill').textContent = styleLabels[AV.style] || '😊';
  const intro = tp.greeting || tp.intro || (tp.catchphrase ? `"${tp.catchphrase}"` : 'สวัสดีครับ/ค่ะ พร้อมเรียนกันไหม?');
  document.getElementById('avatar-speech-bubble').textContent = intro;
  _bmoSetMouth('rest');
  // Set initial sprite frame
  _bmoSetSpriteFrame('talk_2');
}

function avatarSetContent(text) {
  AV.currentText = text;
  const bubble = document.getElementById('avatar-speech-bubble');
  if (!bubble) return;
  const sentences = text.replace(/#{1,6}\s*/g,'').split(/[.!?。\n]/).filter(s=>s.trim().length>10);
  const preview = sentences.slice(0,2).join(' ').substring(0,120) + (text.length > 120 ? '...' : '');
  bubble.textContent = preview || text.substring(0, 120);
}

// shims — avatarTogglePlay และ avatarRegen ถูกรวมเข้า ttsSmartPlay แล้ว
async function avatarTogglePlay() { await ttsSmartPlay(); }
async function avatarRegen() { await ttsRegenerate(); }

function _avConnectAudio(audioEl) {
  try {
    if (!AV.audioCtx || AV.audioCtx.state === 'closed')
      AV.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (AV.audioCtx.state === 'suspended') AV.audioCtx.resume();
    if (AV.source) { try { AV.source.disconnect(); } catch(_){} }
    AV.analyser = AV.audioCtx.createAnalyser(); AV.analyser.fftSize = 256;
    AV.source   = AV.audioCtx.createMediaElementSource(audioEl);
    AV.source.connect(AV.analyser); AV.analyser.connect(AV.audioCtx.destination);
    _avStartAnimation();
  } catch(e) { _avFallbackAnimation(); }
}

// initBmoLipSync — hook to any MediaStream (mic / remote audio)
function initBmoLipSync(stream) {
  try {
    if (!AV.audioCtx || AV.audioCtx.state === 'closed')
      AV.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (AV.audioCtx.state === 'suspended') AV.audioCtx.resume();
    if (AV.source) { try { AV.source.disconnect(); } catch(_){} }
    AV.analyser = AV.audioCtx.createAnalyser(); AV.analyser.fftSize = 256;
    AV.source   = AV.audioCtx.createMediaStreamSource(stream);
    AV.source.connect(AV.analyser); // NOT to destination (no feedback)
    _avStartAnimation();
  } catch(e) { _avFallbackAnimation(); }
}

function _avStartAnimation() {
  AV.speaking = true;
  document.getElementById('mentor-avatar-panel')?.classList.add('speaking');

  if (!AV.analyser) { _avFallbackAnimation(); return; }

  const buf        = new Uint8Array(AV.analyser.frequencyBinCount);
  const THRESH     = 35;   // สูงขึ้น — กัน background noise ไม่ให้ปากค้าง
  const SILENCE_MS = 200;  // ms เงียบแล้วถึงปิดปาก
  const SWAP_MS    = 120;  // ms ต่ำสุดระหว่างการเปลี่ยน frame (~8fps)
  let lastSwap     = 0;

  if (_bmoSilenceTimer) { clearTimeout(_bmoSilenceTimer); _bmoSilenceTimer = null; }

  function tick() {
    if (!AV.speaking) return;
    AV.rafId = requestAnimationFrame(tick);

    AV.analyser.getByteFrequencyData(buf);

    const binHz = AV.audioCtx.sampleRate / AV.analyser.fftSize;
    const lo    = Math.max(1, Math.floor(80   / binHz));
    const hi    = Math.min(buf.length - 1, Math.floor(4000 / binHz));
    let peak = 0;
    for (let i = lo; i <= hi; i++) if (buf[i] > peak) peak = buf[i];

    const now = performance.now();

    if (peak >= THRESH) {
      // มีเสียง — ยกเลิก silence timer
      if (_bmoSilenceTimer) { clearTimeout(_bmoSilenceTimer); _bmoSilenceTimer = null; }
      // เปลี่ยน frame ได้แค่ทุก SWAP_MS (ไม่สั่น)
      if (now - lastSwap >= SWAP_MS) {
        lastSwap = now;
        const frame = _TALK_FRAMES[Math.floor(Math.random() * _TALK_FRAMES.length)];
        _bmoSetSpriteFrame(frame);
      }
    } else {
      // เงียบ — รอ SILENCE_MS แล้วค่อยปิดปาก
      if (!_bmoSilenceTimer) {
        _bmoSilenceTimer = setTimeout(() => {
          _bmoSilenceTimer = null;
          _bmoSetSpriteFrame('talk_2');
        }, SILENCE_MS);
      }
    }
  }
  tick();
}

// Fallback เมื่อไม่มี analyser
let _fbPhase = 0;
function _avFallbackAnimation() {
  AV.speaking = true;
  document.getElementById('mentor-avatar-panel')?.classList.add('speaking');
  _fbPhase = 0;
  let lastSwap = 0;
  const SWAP_MS = 130;
  function tick() {
    if (!AV.speaking) return;
    AV.rafId = requestAnimationFrame(tick);
    _fbPhase++;
    const now  = performance.now();
    const wave = Math.sin(_fbPhase * 0.07) * 0.6 + Math.sin(_fbPhase * 0.19) * 0.4;
    if (wave > 0 && now - lastSwap >= SWAP_MS) {
      lastSwap = now;
      _bmoSetSpriteFrame(_TALK_FRAMES[Math.floor(Math.random() * _TALK_FRAMES.length)]);
    } else if (wave <= 0) {
      _bmoSetSpriteFrame('talk_2');
    }
  }
  tick();
}

function _avStopAnimation() {
  AV.speaking = false;
  if (AV.rafId) { cancelAnimationFrame(AV.rafId); AV.rafId = null; }
  if (_bmoSilenceTimer) { clearTimeout(_bmoSilenceTimer); _bmoSilenceTimer = null; }
  document.getElementById('mentor-avatar-panel')?.classList.remove('speaking');
  _bmoSetSpriteFrame('talk_2');
  for (let i=0;i<5;i++) { const d=document.getElementById('av-dot-'+i); if(d) d.style.height='3px'; }
}

function _avSetStatus(msg) {
  const el = document.getElementById('avatar-status'); if (el) el.textContent = msg;
}

(function() {
  const _origLoad = window.loadLesson;
  window.loadLesson = async function() {
    await _origLoad.apply(this, arguments);
    setTimeout(() => { const el=document.getElementById('les-tab-content'); if(el) avatarSetContent(el.innerText||el.textContent||''); }, 600);
  };
  const _origPeriod = window.loadPeriodLesson;
  window.loadPeriodLesson = async function() {
    await _origPeriod.apply(this, arguments);
    setTimeout(() => { const el=document.getElementById('les-tab-content'); if(el) avatarSetContent(el.innerText||el.textContent||''); }, 600);
  };
})();


init();

// ══════════════════════════════════════════════════════════
// [FEAT-2 v2.5] NotebookLM Script Generator
// ══════════════════════════════════════════════════════════
async function generateNotebookLMScript() {
  if (!S.courseId) { toast('เลือกหลักสูตรก่อน', 'err'); return; }
  const day = parseInt(document.getElementById('lesson-day-sel')?.value || '1');
  toast('🎙️ กำลังสร้าง NotebookLM Script...', '', 8000);

  // แสดง modal
  let modal = document.getElementById('notebooklm-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'notebooklm-modal';
    modal.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:10002;overflow:auto;padding:20px';
    modal.innerHTML = `
      <div style="max-width:760px;margin:0 auto;position:relative">
        <button onclick="document.getElementById('notebooklm-modal').style.display='none'"
          style="position:absolute;top:-10px;right:0;background:var(--red);color:white;border:none;border-radius:50%;width:30px;height:30px;font-size:16px;cursor:pointer;z-index:1">✕</button>
        <div class="card" style="margin-top:30px;border-color:var(--purple)">
          <div class="card-title">🎙️ NotebookLM Script — Day <span id="nlm-day"></span></div>
          <div style="font-size:12px;color:var(--muted);margin-bottom:12px">
            คัดลอก script ด้านล่าง → วางใน <strong style="color:var(--gold)">Google NotebookLM</strong> → กด Generate Audio Overview
          </div>
          <div id="nlm-content" class="content-box" style="min-height:400px;white-space:pre-wrap;font-size:13px;line-height:1.8">
            <span class="spinner"></span> กำลังสร้าง Script...
          </div>
          <div class="btn-row" style="margin-top:12px">
            <button class="btn btn-purple" onclick="copyNLMScript()">📋 คัดลอก Script</button>
            <button class="btn btn-ghost btn-sm"
              onclick="document.getElementById('notebooklm-modal').style.display='none'">ปิด</button>
          </div>
        </div>
      </div>`;
    document.body.appendChild(modal);
  }
  document.getElementById('nlm-day').textContent = day;
  document.getElementById('nlm-content').innerHTML = '<span class="spinner"></span> กำลังสร้าง Script 7-9 นาที...';
  modal.style.display = 'block';

  const r = await api('/api/notebooklm_script', 'POST', { course_id: S.courseId, day });
  if (r.script && !r.script.startsWith('❌')) {
    document.getElementById('nlm-content').textContent = r.script;
    toast('✅ สร้าง Script เสร็จแล้ว!', 'ok');
  } else {
    document.getElementById('nlm-content').textContent = r.error || r.script || 'เกิดข้อผิดพลาด';
    toast('❌ ' + (r.error || 'ผิดพลาด'), 'err');
  }
}

function copyNLMScript() {
  const text = document.getElementById('nlm-content')?.textContent || '';
  navigator.clipboard.writeText(text).then(() => toast('✅ คัดลอกแล้ว!', 'ok'));
}

// ══════════════════════════════════════════════════════════
// [FEAT-1c v2.5] Next Phase for Roadmap
// ══════════════════════════════════════════════════════════
async function generateNextPhase() {
  if (!S.courseId) { toast('เลือกหลักสูตรก่อน', 'err'); return; }
  const resultEl = document.getElementById('next-phase-result');
  if (resultEl) resultEl.textContent = '⏳ กำลังสร้าง Phase ถัดไป...';
  toast('🚀 AI กำลังออกแบบ Phase ถัดไป...', '', 10000);

  const r = await api('/api/course/next_phase', 'POST', { course_id: S.courseId });
  if (r.ok) {
    const msg = `✅ สร้าง Phase ${r.phase} สำเร็จ! เพิ่มอีก ${r.days_added} วัน (Day ${r.start_day}–${r.end_day}) รวม ${r.new_total_days} วัน`;
    if (resultEl) resultEl.textContent = msg;
    toast(msg, 'ok', 5000);
    await loadCourseData(S.courseId);
    onEnterCurriculum();
  } else {
    const msg = '❌ ' + (r.error || 'ผิดพลาด');
    if (resultEl) resultEl.textContent = msg;
    toast(msg, 'err');
  }
}

async function viewPhaseCertificate() {
  if (!S.courseId) { toast('เลือกหลักสูตรก่อน', 'err'); return; }
  const phase = S.status?.current_phase || 1;
  const r = await api(`/api/certificate/phase?course_id=${S.courseId}&phase=${phase}`);
  if (r.html) {
    const frame = document.getElementById('cert-frame');
    if (frame) {
      frame.srcdoc = r.html;
      document.getElementById('cert-modal').style.display = 'block';
    }
  }
}

// ══════════════════════════════════════════════════════════
// [FEAT-1c v2.5] Patch onEnterCurriculum to show Next Phase btn
// ══════════════════════════════════════════════════════════
const _origOnEnterCurriculum = typeof onEnterCurriculum !== 'undefined' ? onEnterCurriculum : null;
function onEnterCurriculum() {
  if (_origOnEnterCurriculum) _origOnEnterCurriculum();
  // Show Next Phase button if roadmap mode
  const d = S.status || {};
  const nps = document.getElementById('next-phase-section');
  if (nps) {
    const isRoadmap = d.roadmap_mode || (d.learner_profile && d.learner_profile.roadmap_mode);
    nps.style.display = isRoadmap ? 'block' : 'none';
    if (isRoadmap) {
      const phase = d.current_phase || 1;
      const phaseSize = d.phase_size || 30;
      const daysCompleted = d.progress?.days_done || 0;
      const phaseInfo = document.getElementById('phase-info');
      if (phaseInfo) {
        phaseInfo.textContent = `Phase ปัจจุบัน: ${phase} | เรียนมาแล้ว ${daysCompleted} วัน | Phase ขนาด ${phaseSize} วัน`;
      }
    }
  }
}

// ══════════════════════════════════════════════════════════
// [FEAT-1b v2.5] Patch curriculum render to show periods per day
// ══════════════════════════════════════════════════════════
const _origRenderCurriculum = typeof renderCurriculum !== 'undefined' ? renderCurriculum : null;
// Override onEnterCurriculum to also patch curriculum cards with periods
document.addEventListener('DOMContentLoaded', () => {
  // Patch btn-purple style if not exists
  if (!document.querySelector('style[data-patch-v25]')) {
    const s = document.createElement('style');
    s.setAttribute('data-patch-v25', '1');
    s.textContent = `
      .btn-purple { background: linear-gradient(135deg, #8e44ad, #6c3483); color: #fff; border: none; }
      .btn-purple:hover { background: linear-gradient(135deg, #9b59b6, #7d3c98); }
      .period-tag { display: inline-block; background: rgba(142,68,173,0.15); border: 1px solid rgba(142,68,173,0.4); border-radius: 4px; padding: 2px 8px; font-size: 10px; color: #c39bd3; margin: 2px; }
      #notebooklm-modal .content-box { background: var(--ink2); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
    `;
    document.head.appendChild(s);
  }
});

// ══════════════════════════════════════════════════════════════════
// PIXEL SKILL TREE  — Pockademy Skill Tree Patch
// Snake RPG map for Curriculum page
// ══════════════════════════════════════════════════════════════════

let _stView = 'tree'; // 'tree' | 'list'

// ── Toggle between tree and list view ──────────────────────────
function stSwitchView(v) {
  _stView = v;
  const tBtn = document.getElementById('vt-tree');
  const lBtn = document.getElementById('vt-list');
  if (tBtn) tBtn.classList.toggle('vt-active', v === 'tree');
  if (lBtn) lBtn.classList.toggle('vt-active', v === 'list');

  const stv = document.getElementById('skill-tree-view');
  const cl  = document.getElementById('curriculum-list');
  if (stv) stv.style.display = v === 'tree' ? 'block' : 'none';
  if (cl)  cl.style.display  = v === 'list'  ? 'block' : 'none';

  // Also hide next-phase in tree mode
  const nps = document.getElementById('next-phase-section');
  if (nps && v === 'tree') nps.style.display = 'none';

  if (v === 'tree') renderSkillTree();
  else if (_stPrevEnterCurriculum) _stPrevEnterCurriculum();
}

// ── Main skill tree renderer ───────────────────────────────────
function renderSkillTree() {
  const container = document.getElementById('skill-tree-container');
  if (!container) return;

  const curriculum = S.status?.curriculum || [];

  // Empty state
  if (!curriculum.length) {
    container.innerHTML = [
      '<div style="text-align:center;padding:52px 20px">',
      '<div style="font-size:32px;margin-bottom:10px">🗺️</div>',
      '<div style="font-size:13px;color:var(--muted)">ยังไม่มีหลักสูตร</div>',
      '<div style="font-size:11px;color:var(--muted);margin-top:4px">เริ่มลงทะเบียนก่อนนะครับ</div>',
      '</div>',
    ].join('');
    return;
  }

  const done   = S.status?.progress?.days_completed || [];
  const curr   = S.status?.progress?.current_day    || 1;
  const total  = curriculum.length;
  const doneN  = done.length;
  const pct    = total ? Math.round(doneN / total * 100) : 0;

  // Update progress bar
  const pl = document.getElementById('st-prog-label');
  const pf = document.getElementById('st-prog-fill');
  const pp = document.getElementById('st-prog-pct');
  if (pl) pl.textContent = 'CLEARED ' + doneN + '/' + total;
  if (pf) pf.style.width = pct + '%';
  if (pp) pp.textContent = pct + '%';

  // ── Vertical treasure-map layout ──────────────────────────────
  // Two alternating columns (zigzag) in vertical scroll
  const NW  = 130;  // node width
  const NH  = 60;   // node height
  const GY  = 52;   // vertical gap between rows
  const GX  = 30;   // horizontal gap between columns
  const PAD = 16;   // padding

  // 2-column zigzag: col 0 = left, col 1 = right
  const COL_X = [PAD, PAD + NW + GX];
  const svgW  = PAD * 2 + NW * 2 + GX;
  const totalRows = curriculum.length;
  const svgH  = PAD * 2 + totalRows * (NH + GY) + PAD;

  function _pos(i) {
    var col = i % 2;
    var row = Math.floor(i / 2) * 2 + (i % 2 === 0 ? 0 : 1); // just row = i
    return { x: COL_X[i % 2], y: PAD + i * (NH + GY) };
  }

  var lines = '';
  var nodes = '';

  // ── Connection lines (vertical dashed path) ──────────────────
  for (var i = 0; i < curriculum.length - 1; i++) {
    var a = _pos(i), b = _pos(i + 1);
    var ax = a.x + NW / 2, ay = a.y + NH;
    var bx = b.x + NW / 2, by = b.y;

    var lit = done.indexOf(curriculum[i].day) >= 0;
    var sc  = lit ? 'rgba(155,89,255,0.8)' : 'rgba(94,45,158,0.25)';
    var sw  = lit ? '3' : '2';
    var da  = lit ? 'stroke-dasharray="6,0"' : 'stroke-dasharray="6,5"';

    // Mid bezier for zigzag effect
    var mx1 = ax, my1 = ay + (by - ay) * 0.4;
    var mx2 = bx, my2 = ay + (by - ay) * 0.6;
    lines += '<path d="M' + ax + ',' + ay +
             ' C' + mx1 + ',' + my1 +
             ' ' + mx2 + ',' + my2 +
             ' ' + bx  + ',' + by + '"' +
             ' stroke="' + sc + '" stroke-width="' + sw + '" fill="none" ' + da + '/>';

    // Animated dot on active path segment
    if (lit) {
      lines += '<circle r="4" fill="#ffd60a" opacity="0.9">' +
               '<animateMotion dur="2s" repeatCount="indefinite">' +
               '<mpath href="#path' + i + '"/>' +
               '</animateMotion></circle>';
      // re-add path with id for animateMotion
      lines += '<path id="path' + i + '" d="M' + ax + ',' + ay +
               ' C' + mx1 + ',' + my1 +
               ' ' + mx2 + ',' + my2 +
               ' ' + bx  + ',' + by + '"' +
               ' stroke="none" fill="none"/>';
    }
  }

  // ── Nodes ────────────────────────────────────────────────────
  for (var j = 0; j < curriculum.length; j++) {
    var p      = curriculum[j];
    var pos    = _pos(j);
    var x      = pos.x, y = pos.y;
    var isDone = done.indexOf(p.day) >= 0;
    var isCurr = p.day === curr;
    var isLock = p.day > curr && !isDone;
    var isExam = !!p.is_exam_day;

    var fill   = '#1e0a38';
    var stroke = '#4a2480';
    var sw     = '1.5';
    var op     = '1';
    var animCls = '';

    if (isDone)            { fill='#240d48'; stroke='#9b59ff'; sw='2';   animCls='std'; }
    if (isCurr && !isDone) { fill='#2d1058'; stroke='#ffd60a'; sw='2.5'; animCls='stc'; }
    if (isLock)            { op='0.35'; stroke='#2d1060'; }
    if (isExam && !isLock) { stroke = isDone ? '#2ed573' : (isCurr ? '#ffd60a' : '#ff4757'); }

    var dayCol  = isDone ? '#9b59ff' : (isCurr ? '#ffd60a' : '#4a2480');
    var textCol = isLock ? '#382060' : '#d4b8f0';
    var dayLbl  = isExam ? ('👑 BOSS ' + p.day) : ('DAY ' + p.day);
    var icon    = isDone ? '✓' : (isLock ? '🔒' : (isCurr ? '▶' : ''));

    var rawT   = typeof globalCleanDayTitle === 'function'
                   ? globalCleanDayTitle(p.title || '', p.day)
                   : (p.title || ('Day ' + p.day));
    var shortT = rawT.length > 18 ? rawT.slice(0, 17) + '…' : rawT;
    var safeT  = shortT.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

    // Milestone marker every 5 days
    if (p.day % 5 === 0 && !isExam) {
      nodes += '<text x="' + (x + NW + 6) + '" y="' + (y + NH/2 + 4) + '"' +
               ' font-size="14" opacity="' + (isLock?'0.3':'0.7') + '">⭐</text>';
    }

    // Shadow
    nodes += '<rect x="' + (x+3) + '" y="' + (y+4) + '" width="' + NW + '" height="' + NH + '" rx="10"' +
             ' fill="rgba(0,0,0,0.5)" opacity="' + op + '"/>';
    // Main body
    nodes += '<rect x="' + x + '" y="' + y + '" width="' + NW + '" height="' + NH + '" rx="10"' +
             ' fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + sw + '"' +
             ' opacity="' + op + '" class="' + animCls + '"/>';
    // Top accent bar
    nodes += '<rect x="' + (x+10) + '" y="' + y + '" width="' + (NW-20) + '" height="3" rx="1.5"' +
             ' fill="' + stroke + '" opacity="' + op + '"/>';

    // Day label
    nodes += '<text x="' + (x+10) + '" y="' + (y+18) + '"' +
             ' font-family="DM Mono,monospace" font-size="8.5" font-weight="700"' +
             ' fill="' + dayCol + '" opacity="' + op + '" letter-spacing="1">' +
             dayLbl + '</text>';
    // Title
    nodes += '<text x="' + (x+10) + '" y="' + (y+36) + '"' +
             ' font-family="Noto Sans Thai,sans-serif" font-size="11" font-weight="600"' +
             ' fill="' + textCol + '" opacity="' + op + '">' +
             safeT + '</text>';
    // Status icon (top-right)
    if (icon) {
      nodes += '<text x="' + (x+NW-18) + '" y="' + (y+20) + '"' +
               ' font-size="13" opacity="' + op + '">' + icon + '</text>';
    }
    // Difficulty dots (bottom)
    var diff = Math.min(p.difficulty || 1, 5);
    for (var d2 = 0; d2 < 5; d2++) {
      var dc = d2 < diff ? stroke : 'rgba(94,45,158,0.12)';
      nodes += '<circle cx="' + (x+12+d2*9) + '" cy="' + (y+NH-10) + '" r="3"' +
               ' fill="' + dc + '" opacity="' + op + '"/>';
    }
    // Click overlay
    var fn = isLock ? ('stLocked(' + p.day + ')') : ('stClick(' + p.day + ')');
    nodes += '<rect x="' + x + '" y="' + y + '" width="' + NW + '" height="' + NH + '" rx="10"' +
             ' fill="transparent" onclick="' + fn + '"' +
             ' style="cursor:' + (isLock?'not-allowed':'pointer') + '"/>';
  }

  // ── Assemble SVG ─────────────────────────────────────────────
  var svg = [
    '<svg viewBox="0 0 ' + svgW + ' ' + svgH + '"',
    '     xmlns="http://www.w3.org/2000/svg"',
    '     style="display:block;width:100%;height:' + svgH + 'px">',
    '<defs><style>',
    '  .std{animation:stGlow 3.5s ease-in-out infinite}',
    '  .stc{animation:stPulse 2s ease-in-out infinite}',
    '  @keyframes stPulse{',
    '    0%,100%{filter:drop-shadow(0 0 6px rgba(255,214,10,.95))}',
    '    50%{filter:drop-shadow(0 0 22px rgba(255,214,10,1))}',
    '  }',
    '  @keyframes stGlow{',
    '    0%,100%{filter:drop-shadow(0 0 4px rgba(155,89,255,.5))}',
    '    50%{filter:drop-shadow(0 0 14px rgba(155,89,255,.95))}',
    '  }',
    '</style></defs>',
    lines,
    nodes,
    '</svg>',
  ].join('\n');

  container.innerHTML = svg;
}

// ── Node click → detail panel ──────────────────────────────────
function stClick(day) {
  var p = (S.status?.curriculum || []).find(function(c){ return c.day === day; });
  if (!p) return;

  var done   = S.status?.progress?.days_completed || [];
  var curr   = S.status?.progress?.current_day    || 1;
  var isDone = done.indexOf(day) >= 0;
  var isCurr = day === curr;
  var isExam = !!p.is_exam_day;

  var accent = isDone ? '#9b59ff' : (isCurr ? '#ffd60a' : '#ff6b2b');
  var rawT   = typeof globalCleanDayTitle === 'function'
                 ? globalCleanDayTitle(p.title || '', day)
                 : (p.title || ('Day ' + day));
  var periods = p.periods || [];
  var diff    = Math.min(p.difficulty || 1, 5);
  var stars   = '';
  for (var i = 0; i < diff; i++) stars += '\u2605'; // filled star
  for (var i = diff; i < 5; i++) stars += '\u2606'; // empty star

  var statusBadge = isDone
    ? '<span style="color:#2ed573">\u2713 CLEARED</span>'
    : (isCurr ? '<span style="color:#ffd60a">\u25b6 CURRENT</span>' : '');

  var panel = document.getElementById('st-detail-panel');
  panel.style.borderColor = accent;
  panel.innerHTML = [
    '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px">',
    '  <div style="flex:1;min-width:0">',
    '    <div class="st-detail-day" style="color:' + accent + '">',
    (isExam ? '\ud83d\udc51 BOSS DAY ' : 'DAY ') + day,
    statusBadge ? (' \u00b7 ' + statusBadge) : '',
    '    </div>',
    '    <div class="st-detail-title">' + rawT.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '</div>',
    p.objectives
      ? '<div class="st-detail-obj">\ud83c\udfaf ' + p.objectives + '</div>'
      : '',
    periods.length
      ? '<div class="st-detail-meta">\ud83d\udcda ' + periods.length + ' คาบเรียน</div>'
      : '',
    p.homework_brief
      ? '<div class="st-detail-meta">\ud83d\udcdd การบ้าน: ' + p.homework_brief + '</div>'
      : '',
    '    <div style="margin-top:6px;font-size:16px;letter-spacing:2px">' + stars + '</div>',
    '  </div>',
    '  <button onclick="stCloseDetail()" style="background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;flex-shrink:0;line-height:1;padding:0">\u00d7</button>',
    '</div>',
    '<div class="btn-row" style="margin-top:14px">',
    '  <button class="btn btn-sm" onclick="stGoLesson(' + day + ')">\u25b6 เรียนเลย</button>',
    '  <button class="btn btn-ghost btn-sm" onclick="stGoQuiz(' + day + ')">\ud83e\udde9 Quiz</button>',
    '  <button class="btn btn-ghost btn-sm" onclick="stCloseDetail()">ปิด</button>',
    '</div>',
  ].join('');

  panel.className = 'st-detail st-open';
  setTimeout(function() {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 60);
}

function stCloseDetail() {
  var panel = document.getElementById('st-detail-panel');
  if (panel) panel.className = 'st-detail';
}

function stLocked(day) {
  var curr = S.status?.progress?.current_day || 1;
  toast('\ud83d\udd12 Day ' + day + ' ยังล็อคอยู่ — ผ่าน Day ' + curr + ' ก่อนนะครับ', 'err');
}

function stGoLesson(day) {
  if (typeof loadDayFromCurr === 'function') { loadDayFromCurr(day); }
  else {
    var el = document.getElementById('lesson-day-sel');
    if (el) { el.value = day; if (typeof onDaySelChange === 'function') onDaySelChange(); }
    nav('lesson');
    if (typeof loadLesson === 'function') loadLesson();
  }
  stCloseDetail();
}

function stGoQuiz(day) {
  if (typeof openQuizFromCurr === 'function') { openQuizFromCurr(day); }
  else {
    var el = document.getElementById('lesson-day-sel');
    if (el) { el.value = day; if (typeof onDaySelChange === 'function') onDaySelChange(); }
    if (typeof openInteractiveQuiz === 'function') openInteractiveQuiz();
  }
  stCloseDetail();
}

// ── Hook into onEnterCurriculum ────────────────────────────────
var _stPrevEnterCurriculum = (typeof onEnterCurriculum !== 'undefined') ? onEnterCurriculum : null;
function onEnterCurriculum() {
  // Update subtitle regardless of view
  var d = S.status || {};
  var sub = document.getElementById('curr-sub');
  if (sub && d.title) sub.textContent = d.title + ' \u2014 ' + (d.total_days || 0) + ' \u0e27\u0e31\u0e19';

  var stv = document.getElementById('skill-tree-view');
  var cl  = document.getElementById('curriculum-list');

  if (_stView === 'tree') {
    if (stv) stv.style.display = 'block';
    if (cl)  cl.style.display  = 'none';
    renderSkillTree();
  } else {
    if (stv) stv.style.display = 'none';
    if (cl)  cl.style.display  = 'block';
    if (_stPrevEnterCurriculum) _stPrevEnterCurriculum();
  }
}

</script>

<script>
/* ════ POCKADEMY GIMMICK JS v1.0 ════ */

// 1. Set glitch data-text on brand
(function(){
  var b = document.querySelector('.brand-name');
  if(b) b.setAttribute('data-text', b.textContent.trim());
})();

// 2. Floating pixel coins
(function(){
  var C = ['🪙','⭐','💎','🏅','✨'];
  function spawn(){
    var el = document.createElement('div');
    el.className = 'pixel-coin';
    el.textContent = C[Math.floor(Math.random()*C.length)];
    el.style.left = (Math.random()*95)+'vw';
    var dur = 8+Math.random()*10;
    el.style.animationDuration = dur+'s';
    el.style.animationDelay   = (Math.random()*dur*-1)+'s';
    el.style.fontSize = (14+Math.random()*10)+'px';
    document.body.appendChild(el);
    setTimeout(function(){ el.remove(); }, dur*1000+500);
  }
  for(var i=0;i<6;i++) setTimeout(spawn, i*1200);
  setInterval(spawn, 4000);
})();

// 3. Pixel cursor trail
(function(){
  var last=0;
  document.addEventListener('mousemove',function(e){
    var now=Date.now(); if(now-last<60) return; last=now;
    var d=document.createElement('div'); d.className='cursor-trail';
    d.style.left=e.clientX+'px'; d.style.top=e.clientY+'px';
    var colors=['#ffd60a','#ff6b2b','#9b59ff','#2ed573'];
    d.style.background=colors[Math.floor(Math.random()*4)];
    document.body.appendChild(d); setTimeout(function(){d.remove();},520);
  });
})();

// 4. Level-up flash — hook into toast
(function(){
  var orig=window.showToast||window.toast;
  if(typeof orig==='function'){
    var _hook=function(msg,type,dur){
      orig.call(this,msg,type,dur);
      if(msg&&(msg.includes('LEVEL')||msg.includes('level')||msg.includes('เลเวล')||msg.includes('🆙'))){
        var f=document.getElementById('levelup-flash');
        if(f){f.classList.add('show');setTimeout(function(){f.classList.remove('show');},900);}
      }
    };
    if(window.showToast) window.showToast=_hook;
    if(window.toast) window.toast=_hook;
  }
})();

// 5. Count-up stat animation
function _animateCount(el,target){
  var dur=800,t0=performance.now();
  var suffix=el.textContent.replace(/[\d]/g,'');
  (function step(now){
    var p=Math.min((now-t0)/dur,1),ease=1-Math.pow(1-p,3);
    el.textContent=Math.floor(ease*target)+suffix;
    if(p<1) requestAnimationFrame(step); else el.textContent=target+suffix;
  })(t0);
}
new MutationObserver(function(ms){
  ms.forEach(function(m){
    m.addedNodes.forEach(function(n){
      if(n.nodeType!==1) return;
      var vs=[];
      if(n.classList&&n.classList.contains('stat-val')) vs=[n];
      else if(n.querySelectorAll) vs=Array.from(n.querySelectorAll('.stat-val'));
      vs.forEach(function(v){
        var num=parseInt(v.textContent);
        if(!isNaN(num)&&num>0&&!v.dataset.anim){v.dataset.anim='1';_animateCount(v,num);}
      });
    });
  });
}).observe(document.body,{childList:true,subtree:true});

// 6. Brand hover flash
(function(){
  var b=document.querySelector('.brand-name'); if(!b) return;
  b.addEventListener('mouseenter',function(){
    b.style.color='var(--yellow)';
    b.style.textShadow='0 0 20px rgba(255,214,10,0.9),2px 2px 0 rgba(0,0,0,0.5)';
    setTimeout(function(){b.style.color='';b.style.textShadow='';},300);
  });
})();

// 7. Konami code easter egg ↑↑↓↓←→←→BA
(function(){
  var seq=[38,38,40,40,37,39,37,39,66,65],idx=0;
  document.addEventListener('keydown',function(e){
    if(e.keyCode===seq[idx]) idx++; else idx=0;
    if(idx===seq.length){
      idx=0;
      var coins=['🪙','💎','⭐','🏅','🎖️'];
      for(var i=0;i<20;i++) setTimeout(function(){
        var el=document.createElement('div'); el.className='pixel-coin';
        el.textContent=coins[Math.floor(Math.random()*5)];
        el.style.left=(Math.random()*95)+'vw';
        el.style.animationDuration='3s'; el.style.animationDelay='0s';
        el.style.fontSize=(20+Math.random()*20)+'px';
        document.body.appendChild(el); setTimeout(function(){el.remove();},3500);
      }, i*120);
      if(typeof toast==='function') toast('🎮 CHEAT CODE ACTIVATED!');
    }
  });
})();
</script>

</body>
</html>"""



# ═══════════════════════════════════════════════════════════════════
# WEB SERVER — v2.0 All Endpoints Implemented
# ═══════════════════════════════════════════════════════════════════
class PockademyRequestHandler(http.server.SimpleHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Suppress normal access log noise
        pass

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            try:
                html_bytes = build_html().encode('utf-8')
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(html_bytes)))
                self.end_headers()
                # [FIX-2 v2.5] ครอบ BrokenPipeError — client ปิดก่อนส่งเสร็จ
                try:
                    self.wfile.write(html_bytes)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            except Exception as e:
                print(c(C.RED, f"[do_GET] HTML build error: {e}"))
            return
        if self.path.startswith('/api/'):
            self.handle_api()
            return
        try:
            super().do_GET()
        except Exception:
            try:
                self.send_error(404)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
            return
        self.send_error(405)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(length).decode('utf-8')) if length > 0 else {}

    def _json(self, data, status=200):
        # [FIX-2b v2.5] ครอบ BrokenPipeError — ป้องกัน crash เวลา client ปิด
        try:
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_api(self):
        parsed   = urllib.parse.urlparse(self.path)
        endpoint = parsed.path
        params   = urllib.parse.parse_qs(parsed.query)
        def qp(k, default=''):
            return params.get(k, [default])[0]

        try:
            data = {}
            if self.command == 'POST':
                ct = self.headers.get('Content-Type', '')
                if 'multipart' in ct:
                    data = {}   # handled separately for file uploads
                else:
                    length = int(self.headers.get('Content-Length', 0))
                    if length > 0:
                        raw = self.rfile.read(length).decode('utf-8')
                        data = json.loads(raw) if raw.strip() else {}

            # ─── GET endpoints ───────────────────────────────────
            if endpoint == '/api/courses':
                self._json({"courses": Course.list_all()})

            elif endpoint.startswith('/api/course/') and self.command == 'GET':
                course_id = endpoint.split('/')[-1]
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}, 404); return
                prog  = course.get_summary()
                # [v3.1] เพิ่ม quiz_results และ periods_read ใน progress สำหรับ JS lock check
                prog["quiz_results"]  = course.progress.get("quiz_results", {})
                prog["periods_read"]  = course.progress.get("periods_read", {})
                prog["homework_submissions"] = course.progress.get("homework_submissions", {})
                ginfo = GamificationEngine.get_level_info(course.progress.get("exp", 0))
                self._json({
                    "id"          : course.id,
                    "title"       : course.title,
                    "subject"     : course.subject,
                    "total_days"  : course.total_days,
                    "level"       : course.level,
                    "teacher"     : course.teacher_persona,
                    "curriculum"  : course.curriculum,
                    "progress"    : prog,
                    "gamification": {
                        "exp"       : ginfo["exp"],
                        "level"     : ginfo["level"],
                        "level_name": ginfo["name"],
                        "level_pct" : ginfo["pct"],
                        "next"      : ginfo["next"],
                        "badges"    : course.progress.get("badges", []),
                    },
                    "learner_profile": course.learner_profile,
                    "rag_url"     : course.rag_url,
                    "mentor_style": course.mentor_style,
                    "chat_main"   : course.progress.get("chat_history_main", [])[-20:],
                    "chat_lesson" : {k: v[-10:] for k, v in course.progress.get("chat_history_lesson", {}).items()},
                })

            elif endpoint == '/api/config':
                cfg = ConfigManager.load_all()
                self._json({
                    "provider" : cfg.get("last_provider", ""),
                    "model"    : cfg.get("last_model", ""),
                    "providers": cfg.get("providers", {}),
                })

            elif endpoint == '/api/lesson' and self.command == 'GET':
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                regen     = qp('regen', '0') == '1'
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                engine = LessonEngine(ai, course)
                if regen:
                    course.deduct_score_for_day(day)
                    course.invalidate_cache_day(day)
                    content = engine.get_lesson(day, force_regen=True)
                else:
                    content = engine.get_lesson(day)
                self._json({"content": content, "day": day})

            elif endpoint == '/api/homework_view' and self.command == 'GET':
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                content = LessonEngine(ai, course).get_homework(day)
                self._json({"content": content})

            elif endpoint == '/api/quiz' and self.command == 'GET':
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                content = LessonEngine(ai, course).get_quiz(day)
                self._json({"content": content})

            # ── [v2.9.3] Interactive Quiz (structured JSON) ──────────────
            elif endpoint == '/api/quiz_structured' and self.command == 'GET':
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                period    = int(qp('period', '0'))
                regen     = qp('regen', '0') == '1'
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                data = LessonEngine(ai, course).get_quiz_structured(day, period, force_regen=regen)
                self._json(data)

            # ── [v2.9.3] Period (sub-lesson) endpoint ────────────────────
            elif endpoint == '/api/period_lesson' and self.command == 'GET':
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                period    = int(qp('period', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                content = LessonEngine(ai, course).get_period_lesson(day, period)
                self._json({"content": content, "day": day, "period": period})


            # ── [v3.0] Lazy Generation: expand day periods ──────────────
            elif endpoint == '/api/day_detail' and self.command in ('GET', 'POST'):
                """[v3.0] Phase 2 Lazy — เติม periods ให้วันที่ยัง pending"""
                if self.command == 'GET':
                    course_id = qp('course_id')
                    day       = int(qp('day', '1'))
                else:
                    course_id = data.get('course_id')
                    day       = int(data.get('day', 1))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                result = expand_day_periods(course, day)
                self._json(result)


            # ── [v2.9.6] Core Logic Gate Endpoints ──────────────────────

            elif endpoint == '/api/progression_barrier' and self.command == 'GET':
                """ตรวจสอบว่าผู้เรียนสามารถเข้า target_day ได้หรือไม่"""
                course_id  = qp('course_id')
                target_day = int(qp('day', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                result = check_progression_barrier(course, target_day)
                self._json(result)

            elif endpoint == '/api/activity_gate' and self.command == 'GET':
                """ตรวจสอบว่าการบ้าน/แบบฝึกหัดปลดล็อกแล้วหรือยัง"""
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                activity  = qp('activity', 'homework')
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                result = check_activity_gate(course, day, activity)
                self._json(result)

            elif endpoint == '/api/mark_period_read' and self.command == 'POST':
                """Mark Period as Read — ปลดล็อก Activity ถ้าเรียนครบ"""
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                period    = int(data.get("period", 1))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                result = mark_period_read(course, day, period)
                # ตรวจสอบสถานะ deadline ของการบ้านด้วย
                hw_deadline = check_homework_deadline(course, day)
                result["hw_deadline"] = hw_deadline
                self._json(result)

            # ── [v3.0] Save Quiz Result + Auto-unlock period ─────────────
            elif endpoint == '/api/save_quiz_result' and self.command == 'POST':
                """บันทึก Quiz Result — ถ้าผ่าน (passed=True) และเป็น period quiz → mark_period_read อัตโนมัติ"""
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                period    = int(data.get("period", 0))
                score     = int(data.get("score", 0))
                total     = int(data.get("total", 5))
                passed    = bool(data.get("passed", False))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return

                # บันทึก result ใน progress
                quiz_results = course.progress.setdefault("quiz_results", {})
                result_key = f"{day}_{period}"
                prev = quiz_results.get(result_key, {})
                quiz_results[result_key] = {
                    "day": day, "period": period,
                    "score": score, "total": total, "passed": passed,
                    "attempts": prev.get("attempts", 0) + 1,
                    "best_score": max(score, prev.get("best_score", 0)),
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                }

                # [v3.2] ตรวจสอบว่าอ่านจบแล้วหรือยัง (ต้องอ่านจบ + ผ่าน quiz ถึงจะปลดล็อกคาบถัดไป)
                periods_read = course.progress.get("periods_read", {})
                current_period_read = period in periods_read.get(str(day), [])

                unlock_info = {}
                if passed and period > 0:
                    # [v3.2] บันทึก quiz result — แต่ไม่ mark period read ซ้ำ (JS จะ mark เมื่อโหลดบทเรียน)
                    # ตรวจสอบว่าปลดล็อกคาบถัดไปได้หรือไม่: ต้องอ่านจบ AND ผ่าน quiz ของคาบนี้
                    plan = next((p for p in course.curriculum if p.get("day") == day), {})
                    total_periods = len(plan.get("periods", []))
                    next_period = period + 1

                    if current_period_read:
                        # อ่านจบแล้วและผ่าน quiz → ปลดล็อกคาบถัดไป
                        unlock_info = {
                            "next_period_unlocked": next_period if next_period <= total_periods else None,
                            "both_conditions_met": True,
                            "read": True,
                            "passed": True,
                        }
                    else:
                        # ผ่าน quiz แต่ยังไม่ได้อ่านบทเรียน — แจ้งให้กลับไปอ่านก่อน
                        unlock_info = {
                            "next_period_unlocked": None,
                            "both_conditions_met": False,
                            "read": False,
                            "passed": True,
                            "message": f"ผ่าน quiz แล้ว แต่ยังไม่ได้อ่านบทเรียนคาบ {period} — กลับไปเรียนคาบ {period} ก่อน",
                        }
                    course.save()
                else:
                    course.save()

                GamificationEngine.award_exp(course, "quiz")
                GamificationEngine.check_badges(course)
                self._json({"ok": True, "passed": passed, "unlock": unlock_info})

            elif endpoint == '/api/homework_deadline' and self.command == 'GET':
                """ตรวจสอบ deadline การบ้าน 24 ชั่วโมง"""
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                # Auto-check missed
                deadline = check_homework_deadline(course, day)
                if deadline["status"] == "missed":
                    mark_homework_missed(course, day)
                self._json(deadline)

            elif endpoint == '/api/homework_submit':
                """[v2.9.6] ส่งการบ้านพร้อม Submission Check + Timestamp Validation"""
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                content   = data.get("content", "")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return

                # Activity Gate check
                gate = check_activity_gate(course, day, "homework")
                if not gate["enabled"]:
                    self._json({"ok": False, "locked": True, "reason": gate["reason"]}); return

                # Grade it first
                ai = _make_ai_for_course(course)
                feedback = HomeworkEngine(ai, course).grade_text(day, "synthesis", content, "")

                # Extract score from feedback (ค้นหา pattern "xx/20" หรือ "คะแนน: xx")
                score = 15  # default
                score_match = re.search(r'(\d+)\s*/\s*20', feedback)
                if score_match:
                    score = min(20, int(score_match.group(1)))

                result = submit_homework(course, day, content, score, feedback)
                self._json(result)

            elif endpoint == '/api/recovery_task' and self.command == 'GET':
                """[v2.9.6] ดึง Recovery Task สำหรับการบ้านที่ Missed"""
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                submissions = course.progress.get("homework_submissions", {})
                hw_key = f"day_{day}"
                if submissions.get(hw_key, {}).get("status") != "missed":
                    self._json({"error": "การบ้าน Day นี้ยังไม่ Missed — ไม่ต้องทำ Recovery"}); return
                ai = _make_ai_for_course(course)
                task = generate_recovery_task(ai, course, day)
                self._json({"task": task, "day": day})

            elif endpoint == '/api/recovery_submit':
                """[v2.9.6] ส่ง Recovery Task"""
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                content   = data.get("content", "")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                feedback = HomeworkEngine(ai, course).grade_text(day, "recovery", content, "Recovery Task")
                score_match = re.search(r'(\d+)\s*/\s*20', feedback)
                score = int(score_match.group(1)) if score_match else 12
                passed = score >= 12
                if passed:
                    recovery_done = course.progress.setdefault("recovery_tasks_done", {})
                    recovery_done[str(day)] = True
                    # อัปเดต submission status
                    subs = course.progress.setdefault("homework_submissions", {})
                    subs[f"day_{day}"] = {"status": "recovered", "score": score,
                                          "feedback": feedback[:300], "ts": datetime.now().isoformat()}
                    course.record_homework(day, score, feedback)
                    course.save()
                self._json({"ok": passed, "score": score, "feedback": feedback,
                             "passed": passed, "message": "✅ ผ่าน Recovery Task" if passed else f"❌ ยังไม่ผ่าน (ได้ {score}/20 ต้องการ ≥ 12)"})

            elif endpoint == '/api/quiz_timed' and self.command == 'GET':
                """[v2.9.6] เริ่ม Exercise Speed-Run — สร้าง session + countdown"""
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                period    = int(qp('period', '0'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return

                # Activity Gate
                if period > 0:
                    periods_read = course.progress.get("periods_read", {}).get(str(day), [])
                    if period not in periods_read:
                        self._json({"locked": True, "error": f"🔒 ต้องเรียนคาบที่ {period} ก่อน"}); return

                # ตรวจ timer เดิม — ถ้า expired ให้ regen
                timer = check_quiz_timer(course, day, period)
                force_regen = timer.get("expired", False)

                # สร้าง session ใหม่
                session = create_timed_quiz_session(course, day, period)

                # สร้าง quiz
                ai = _make_ai_for_course(course)
                quiz_data = LessonEngine(ai, course).get_quiz_structured(day, period, force_regen=force_regen)
                quiz_data["timer_session"] = session
                self._json(quiz_data)

            elif endpoint == '/api/quiz_timer_check' and self.command == 'GET':
                """[v2.9.6] ตรวจสอบสถานะ timer ของ quiz"""
                course_id = qp('course_id')
                day       = int(qp('day', '1'))
                period    = int(qp('period', '0'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                result = check_quiz_timer(course, day, period)
                self._json(result)

            elif endpoint == '/api/cache_info' and self.command == 'GET':
                course_id = qp('course_id')
                course = Course.load(course_id)
                if not course:
                    self._json({"entries": [], "total_keys": 0, "lesson_count": 0}); return
                entries = [
                    {"key": k, "ts": v.get("ts", "") if isinstance(v, dict) else ""}
                    for k, v in sorted(course.cache.items())
                ]
                lesson_count = sum(1 for k in course.cache if k.startswith("lesson_"))
                last_ts = max((e["ts"] for e in entries if e["ts"]), default="—")
                self._json({
                    "entries": entries, "total_keys": len(entries),
                    "lesson_count": lesson_count, "last_updated": last_ts
                })

            elif endpoint == '/api/certificate' and self.command == 'GET':
                course_id = qp('course_id')
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                html = CertificateEngine.generate_html(course)
                self._json({"html": html})

            # ─── POST endpoints ──────────────────────────────────
            elif endpoint == '/api/verify_key':
                provider = data.get("provider")
                api_key  = data.get("api_key", "")
                if not provider:
                    self._json({"ok": False, "error": "ไม่มี provider"}); return
                if provider == "ollama":
                    self._json({"ok": True, "message": "✅ Ollama พร้อม"}); return
                if not api_key.strip():
                    self._json({"ok": False, "error": "กรุณาใส่ API Key"}); return
                try:
                    model = data.get("model") or PROVIDERS[provider]["models"][0]["id"]
                    client = AIClient(provider, api_key.strip(), model)
                    ok, msg = client.test_connection()
                    self._json({"ok": ok, "message": msg, "error": "" if ok else msg})
                except Exception as e:
                    self._json({"ok": False, "error": str(e)})

            elif endpoint == '/api/config/save':
                ConfigManager.save_api_key(data.get("provider",""), data.get("api_key",""), data.get("model",""))
                self._json({"ok": True})

            elif endpoint == '/api/enrollment/create':
                eid = create_enrollment_state(
                    provider     = data.get("provider", "gemini"),
                    api_key      = data.get("api_key", ""),
                    model        = data.get("model", "gemini-3.1-flash-lite-preview"),
                    subject      = data.get("subject", ""),
                    learner_name = data.get("learner_name", "นักเรียน"),
                    mentor_style = data.get("mentor_style", "friendly"),
                    rag_url      = data.get("rag_url", ""),
                )
                self._json({"enroll_id": eid})

            elif endpoint == '/api/enrollment/question':
                eid = data.get("enroll_id", "")
                self._json(enrollment_next_question(eid))

            elif endpoint == '/api/enrollment/answer':
                eid    = data.get("enroll_id", "")
                answer = data.get("answer", "")
                self._json(enrollment_process_answer(eid, answer))

            elif endpoint == '/api/enrollment/preview':
                eid = data.get("enroll_id", "")
                self._json(enrollment_preview_curriculum(eid))

            elif endpoint == '/api/enrollment/generate':
                eid = data.get("enroll_id", "")
                print(c(C.CYAN, f"[Generate Course] eid={eid}"))
                result = enrollment_generate_course(eid)
                self._json(result)

            elif endpoint == '/api/homework_text':
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                hw_type   = data.get("hw_type", "practice")
                note      = data.get("note", "")
                content   = data.get("content", "")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                feedback = HomeworkEngine(ai, course).grade_text(day, hw_type, content, note)
                self._json({"feedback": feedback})

            elif endpoint == '/api/homework_file':
                # Multipart — parse manually
                ct = self.headers.get('Content-Type', '')
                length = int(self.headers.get('Content-Length', 0))
                raw = self.rfile.read(length)
                # Quick parse for text fields + file
                try:
                    import cgi
                    import io
                    env = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ct, 'CONTENT_LENGTH': str(length)}
                    fs = cgi.FieldStorage(fp=io.BytesIO(raw), headers=self.headers, environ=env)
                    course_id = fs.getvalue('course_id', '')
                    day       = int(fs.getvalue('day', '1'))
                    hw_type   = fs.getvalue('hw_type', 'practice')
                    note      = fs.getvalue('note', '')
                    file_item = fs['file'] if 'file' in fs else None
                    file_content = ""
                    if file_item:
                        fname = getattr(file_item, 'filename', '')
                        fbytes = file_item.file.read()
                        if fname.lower().endswith(('.jpg','.jpeg','.png','.webp')):
                            file_content = f"[ผู้เรียนส่งรูปภาพ: {fname}]"
                        elif fname.lower().endswith('.pdf'):
                            file_content = f"[ผู้เรียนส่ง PDF: {fname}]"
                        else:
                            file_content = fbytes.decode('utf-8', errors='ignore')[:3000]
                    course = Course.load(course_id)
                    if not course:
                        self._json({"error": "ไม่พบหลักสูตร"}); return
                    ai = _make_ai_for_course(course)
                    feedback = HomeworkEngine(ai, course).grade_file_text(day, hw_type, file_content, note)
                    self._json({"feedback": feedback})
                except Exception as e:
                    self._json({"error": str(e)})

            elif endpoint == '/api/chat':
                course_id   = data.get("course_id")
                message     = data.get("message", "")
                day         = int(data.get("day", 1))
                history     = data.get("history", [])
                persist_key = data.get("persist_key", "main")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                reply = ChatEngine(ai, course).chat(message, history, day, persist_key=persist_key)
                self._json({"reply": reply})

            elif endpoint == '/api/study_time':
                course_id = data.get("course_id")
                seconds   = int(data.get("seconds", 60))
                course = Course.load(course_id)
                if course:
                    course.progress["study_time_secs"] = course.progress.get("study_time_secs", 0) + seconds
                    course.save()
                self._json({"ok": True})

            elif endpoint == '/api/cache_delete':
                course_id = data.get("course_id")
                key       = data.get("key")
                day       = data.get("day")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                deducted = 0
                if day:
                    deducted = course.deduct_score_for_day(int(day))
                course.cache.pop(key, None)
                course.save()
                self._json({"ok": True, "score_deducted": deducted})

            elif endpoint == '/api/cache_clear':
                course_id = data.get("course_id")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                sync = {}
                lesson_days = set()
                for k in list(course.cache.keys()):
                    m = re.match(r'lesson_(\d+)', k)
                    if m: lesson_days.add(int(m.group(1)))
                for day in lesson_days:
                    ded = course.deduct_score_for_day(day)
                    if ded > 0: sync[str(day)] = ded
                course.cache.clear()
                course.save()
                self._json({"ok": True, "sync": sync})

            elif endpoint == '/api/course/delete':
                course_id = data.get("course_id")
                ok = Course.delete(course_id)
                self._json({"ok": ok})

            elif endpoint == '/api/rag_fetch':
                url = data.get("url", "")
                result = RAGFetcher.fetch(url)
                self._json(result)

            # ── [FEAT-2 v2.5] NotebookLM Script Generator ──────────────
            elif endpoint == '/api/notebooklm_script':
                course_id = data.get("course_id")
                day       = int(data.get("day", 1))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                ai = _make_ai_for_course(course)
                script = _generate_notebooklm_script(ai, course, day)
                self._json({"script": script})

            # ── [FEAT-1c v2.5] Next Phase for Roadmap ───────────────────
            elif endpoint == '/api/course/next_phase':
                course_id = data.get("course_id")
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                if not course.roadmap_mode:
                    self._json({"error": "หลักสูตรนี้ไม่ใช่ Roadmap mode"}); return
                result = _generate_next_phase(course)
                self._json(result)

            # ── [FEAT-4 v2.5] Certificate of Phase ──────────────────────
            elif endpoint == '/api/certificate/phase' and self.command == 'GET':
                course_id = qp('course_id')
                phase     = int(qp('phase', '1'))
                course = Course.load(course_id)
                if not course:
                    self._json({"error": "ไม่พบหลักสูตร"}); return
                html = _cert_generate_phase_html(course, phase)
                self._json({"html": html})


            # ── [TTS] GET /api/tts — serve cached mp3 ───────────────────
            elif endpoint == '/api/tts' and self.command == 'GET':
                course_id = qp('course_id')
                day       = qp('day', '1')
                period    = qp('period', '0')
                cache_key = f"tts_{course_id}_day{day}_p{period}"
                tts_path  = TTS_DIR / f"{cache_key}.mp3"
                if tts_path.exists():
                    mp3_bytes = tts_path.read_bytes()
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Content-Length', str(len(mp3_bytes)))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.end_headers()
                    self.wfile.write(mp3_bytes)
                else:
                    self._json({"error": "ยังไม่มีไฟล์เสียง กด สร้างเสียง ก่อนครับ"}, 404)
                return


            # ── [TTS] POST /api/tts_generate — สร้าง mp3 ด้วย edge-tts ──
            elif endpoint == '/api/tts_generate':
                course_id = data.get("course_id", "")
                day       = str(data.get("day", "1"))
                period    = str(data.get("period", "0"))
                text      = data.get("text", "")
                voice     = data.get("voice", "th-TH-PremwadeeNeural")
                if not text:
                    self._json({"error": "ไม่มีเนื้อหา"}); return
                cache_key = f"tts_{course_id}_day{day}_p{period}"
                tts_path  = TTS_DIR / f"{cache_key}.mp3"
                # ถ้ามี cache แล้ว return ทันที
                if tts_path.exists():
                    self._json({"ok": True, "cached": True, "url": f"/api/tts?course_id={course_id}&day={day}&period={period}"})
                    return
                # สร้างใหม่ด้วย edge-tts (async ใน thread)
                try:
                    import asyncio, edge_tts
                    async def _gen():
                        communicate = edge_tts.Communicate(text, voice)
                        await communicate.save(str(tts_path))
                    asyncio.run(_gen())
                    self._json({"ok": True, "cached": False, "url": f"/api/tts?course_id={course_id}&day={day}&period={period}"})
                except ImportError:
                    self._json({"error": "edge-tts ยังไม่ได้ติดตั้ง — รัน: pip install edge-tts"})
                except Exception as e:
                    self._json({"error": f"สร้างเสียงไม่สำเร็จ: {e}"})

            # ── [TTS] DELETE /api/tts_cache — ลบ cache เสียงของวันนั้น ──
            elif endpoint == '/api/tts_cache':
                course_id = data.get("course_id", "")
                day       = str(data.get("day", ""))
                period    = str(data.get("period", ""))
                if day and period:
                    # ลบเฉพาะ period นั้น
                    p = TTS_DIR / f"tts_{course_id}_day{day}_p{period}.mp3"
                    if p.exists(): p.unlink()
                    self._json({"ok": True})
                elif day:
                    # ลบทุก period ของวันนั้น (backward-compat)
                    deleted = 0
                    for p in TTS_DIR.glob(f"tts_{course_id}_day{day}_p*.mp3"):
                        p.unlink(); deleted += 1
                    self._json({"ok": True, "deleted": deleted})
                else:
                    # ลบทั้งหมดของ course นี้
                    deleted = 0
                    for p in TTS_DIR.glob(f"tts_{course_id}_day*.mp3"):
                        p.unlink(); deleted += 1
                    self._json({"ok": True, "deleted": deleted})

            else:
                self._json({"error": f"Unknown endpoint: {endpoint}"}, 404)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(c(C.RED, f"[API Error] {endpoint}: {e}"))
            self._json({"ok": False, "error": str(e)}, 500)

# ═══════════════════════════════════════════════════════════════════
# MAIN — unchanged from v1.0 + v2.0 banner
# ═══════════════════════════════════════════════════════════════════
