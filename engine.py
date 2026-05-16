#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pockademy — engine.py
Core AI, Course model, Enrollment, Lesson/Homework/Chat engines.
"""
import os, sys, json, time, re, random, threading, hashlib, uuid
import http.server, socketserver, urllib.parse, base64, shutil, subprocess
import urllib.request, urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; MAGENTA = "\033[95m"; WHITE = "\033[97m"
    ACID = "\033[92m\033[1m"; WARN = "\033[93m\033[1m"
    ERR = "\033[91m\033[1m"; PINK = "\033[95m\033[1m"
    BLUE = "\033[94m\033[1m"

def c(color, text): return f"{color}{text}{C.RESET}"

# ═══════════════════════════════════════════════════════════════════
# CONFIG & CONSTANTS — v1.0 kept, v2.0 additions marked
# ═══════════════════════════════════════════════════════════════════
WEB_PORT      = 7070
DATA_DIR      = Path("pockademy_data")
COURSES_DIR   = DATA_DIR / "courses"
UPLOADS_DIR   = DATA_DIR / "uploads"
SESSIONS_FILE = DATA_DIR / "sessions.json"
CONFIG_FILE   = DATA_DIR / "config.json"   # v2.0: persistent settings

PROVIDERS = {
    "gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models": [
            {"id": "gemini-3.1-flash-lite-preview", "label": "Gemini 3.1 Flash Lite ⭐ (แนะนำ)", "recommended": True},
            {"id": "gemini-3.1-flash-lite-preview",    "label": "Gemini 3.1 Flash Lite (Free Tier)"},
            {"id": "gemini-2.0-flash",               "label": "Gemini 2.0 Flash"},
            {"id": "gemini-2.0-flash-lite",          "label": "Gemini 2.0 Flash Lite"},
            {"id": "gemini-1.5-flash",               "label": "Gemini 1.5 Flash"},
            {"id": "gemini-1.5-pro",                 "label": "Gemini 1.5 Pro (ช้า/ฉลาด)"},
        ],
        "key_hint": "AIza...",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": [
            {"id": "gpt-4o",       "label": "GPT-4o ⭐ (แนะนำ)", "recommended": True},
            {"id": "gpt-4o-mini",  "label": "GPT-4o Mini (เร็ว/ประหยัด)"},
            {"id": "gpt-4-turbo",  "label": "GPT-4 Turbo"},
            {"id": "gpt-3.5-turbo","label": "GPT-3.5 Turbo"},
        ],
        "key_hint": "sk-...",
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            {"id": "claude-sonnet-4-6", "label": "Claude Sonnet 4.6 ⭐ (แนะนำ)", "recommended": True},
            {"id": "claude-3-5-haiku-20241022",  "label": "Claude 3.5 Haiku (เร็ว)"},
            {"id": "claude-3-opus-20240229",      "label": "Claude 3 Opus (ฉลาดสุด)"},
        ],
        "key_hint": "sk-ant-...",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "base_url": "http://localhost:11434/api",
        "models": [
            {"id": "llama3.2",    "label": "Llama 3.2 ⭐ (แนะนำ)", "recommended": True},
            {"id": "llama3.1",    "label": "Llama 3.1"},
            {"id": "mistral",     "label": "Mistral"},
            {"id": "deepseek-r1", "label": "DeepSeek R1"},
            {"id": "phi3",        "label": "Phi-3"},
        ],
        "key_hint": "(ไม่ต้องใส่ key)",
    },
}

# v2.0: Mentor personality presets
MENTOR_STYLES = {
    "strict":      {"label": "🔥 สายโหด", "desc": "เข้มงวด ตรงไปตรงมา ไม่ปล่อยผ่าน", "emoji": "🔥"},
    "friendly":    {"label": "😊 สายใจดี", "desc": "เป็นกันเอง ให้กำลังใจ อดทน", "emoji": "😊"},
    "funny":       {"label": "🤣 สายฮา",   "desc": "ใช้มุกตลก ยกตัวอย่างสนุก", "emoji": "🤣"},
    "professional":{"label": "💼 สายมือโปร", "desc": "จริงจัง ละเอียด เป็นทางการ", "emoji": "💼"},
}

# ═══════════════════════════════════════════════════════════════════
# v2.0: CONFIG MANAGER — Persistent API Keys per Provider
# ═══════════════════════════════════════════════════════════════════
class ConfigManager:
    """บันทึกและโหลด API Keys + ค่าตั้งต้น แยกตาม Provider"""

    @classmethod
    def save_api_key(cls, provider: str, api_key: str, model: str = ""):
        DATA_DIR.mkdir(exist_ok=True)
        cfg = cls.load_all()
        if "providers" not in cfg:
            cfg["providers"] = {}
        cfg["providers"][provider] = {"api_key": api_key, "model": model}
        cfg["last_provider"] = provider
        cfg["last_model"]    = model
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_api_key(cls, provider: str) -> str:
        cfg = cls.load_all()
        return cfg.get("providers", {}).get(provider, {}).get("api_key", "")

    @classmethod
    def get_last(cls) -> dict:
        cfg = cls.load_all()
        return {
            "provider": cfg.get("last_provider", ""),
            "model":    cfg.get("last_model", ""),
            "api_key":  cfg.get("providers", {}).get(cfg.get("last_provider",""), {}).get("api_key", ""),
        }

    @classmethod
    def load_all(cls) -> dict:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

# ═══════════════════════════════════════════════════════════════════
# AI CLIENT — unchanged from v1.0
# ═══════════════════════════════════════════════════════════════════
class AIClient:
    """Universal AI client รองรับ Gemini / OpenAI / Anthropic / Ollama"""

    def __init__(self, provider: str, api_key: str, model: str):
        self.provider  = provider
        self.api_key   = api_key
        self.model     = model
        self.cfg       = PROVIDERS.get(provider, {})
        self.base_url  = self.cfg.get("base_url", "")
        self._last_err = ""

    def call(self, prompt: str, system: str = "", temperature: float = 0.7,
             max_tokens: int = 3000, stream_cb=None) -> str:
        try:
            import requests
        except ImportError:
            return "❌ pip install requests"
        try:
            if self.provider == "gemini":
                return self._call_gemini(prompt, system, temperature, max_tokens, requests)
            elif self.provider == "openai":
                return self._call_openai(prompt, system, temperature, max_tokens, requests)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt, system, temperature, max_tokens, requests)
            elif self.provider == "ollama":
                return self._call_ollama(prompt, system, temperature, max_tokens, requests)
            else:
                return f"❌ ไม่รู้จัก provider: {self.provider}"
        except Exception as e:
            self._last_err = str(e)
            return f"❌ Error: {e}"

    def _call_gemini(self, prompt, system, temperature, max_tokens, requests) -> str:
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system:
            contents.append({"role": "user",  "parts": [{"text": f"[SYSTEM]\n{system}"}]})
            contents.append({"role": "model", "parts": [{"text": "เข้าใจแล้ว พร้อมดำเนินการ"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        body = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }
        resp = requests.post(url, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, prompt, system, temperature, max_tokens, requests) -> str:
        url = f"{self.base_url}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages,
                "temperature": temperature, "max_tokens": max_tokens}
        resp = requests.post(url, json=body, timeout=60,
                             headers={"Authorization": f"Bearer {self.api_key}",
                                      "Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self, prompt, system, temperature, max_tokens, requests) -> str:
        url = f"{self.base_url}/messages"
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system
        resp = requests.post(url, json=body, timeout=60,
                             headers={"x-api-key": self.api_key,
                                      "anthropic-version": "2023-06-01",
                                      "Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    def _call_ollama(self, prompt, system, temperature, max_tokens, requests) -> str:
        url = f"{self.base_url}/chat"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body = {"model": self.model, "messages": messages, "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens}}
        resp = requests.post(url, json=body, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def call_with_history(self, history: list, system: str = "") -> str:
        """Multi-turn conversation"""
        try:
            import requests
        except ImportError:
            return "❌ pip install requests"
        try:
            if self.provider == "gemini":
                url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
                contents = []
                if system:
                    contents.append({"role": "user",  "parts": [{"text": f"[SYSTEM]\n{system}"}]})
                    contents.append({"role": "model", "parts": [{"text": "เข้าใจแล้ว"}]})
                contents.extend(history)
                body = {"contents": contents,
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000}}
                resp = requests.post(url, json=body, timeout=60)
                resp.raise_for_status()
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif self.provider in ("openai", "anthropic", "ollama"):
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                for msg in history:
                    role    = "assistant" if msg.get("role") == "model" else "user"
                    content = msg.get("parts", [{}])[0].get("text", "")
                    messages.append({"role": role, "content": content})
                if self.provider == "openai":
                    url  = f"{self.base_url}/chat/completions"
                    body = {"model": self.model, "messages": messages, "max_tokens": 3000}
                    resp = requests.post(url, json=body, timeout=60,
                                         headers={"Authorization": f"Bearer {self.api_key}"})
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"]
                elif self.provider == "anthropic":
                    url  = f"{self.base_url}/messages"
                    body = {"model": self.model, "max_tokens": 3000,
                            "messages": [m for m in messages if m["role"] != "system"]}
                    if system: body["system"] = system
                    resp = requests.post(url, json=body, timeout=60,
                                         headers={"x-api-key": self.api_key,
                                                  "anthropic-version": "2023-06-01"})
                    resp.raise_for_status()
                    return resp.json()["content"][0]["text"]
                else:
                    url  = f"{self.base_url}/chat"
                    body = {"model": self.model, "messages": messages, "stream": False}
                    resp = requests.post(url, json=body, timeout=120)
                    resp.raise_for_status()
                    return resp.json()["message"]["content"]
        except Exception as e:
            return f"❌ Error: {e}"

    def test_connection(self) -> tuple:
        result = self.call("ตอบว่า 'OK' เพียงคำเดียว", max_tokens=10, temperature=0)
        if result.startswith("❌"):
            return False, result
        return True, f"✅ เชื่อมต่อสำเร็จ ({self.provider}/{self.model})"

# ═══════════════════════════════════════════════════════════════════
# v2.0: RAG FETCHER — ดึงข้อมูลจาก URL มาใช้ในบทเรียน
# ═══════════════════════════════════════════════════════════════════
class RAGFetcher:
    """ดึงและ clean HTML จาก URL เพื่อใช้เป็น context สำหรับบทเรียน"""

    @staticmethod
    def fetch(url: str, max_chars: int = 3000) -> dict:
        """คืน {ok, content, url, title, error}"""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (ARIA-University/2.0 RAG-Fetcher)',
                'Accept': 'text/html,application/xhtml+xml,*/*'
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')

            # Strip scripts, styles, tags
            clean = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', raw, flags=re.IGNORECASE)
            clean = re.sub(r'<style[^>]*>[\s\S]*?</style>',  '', clean, flags=re.IGNORECASE)
            # Extract title
            title_m = re.search(r'<title[^>]*>(.*?)</title>', clean, re.IGNORECASE | re.DOTALL)
            title = title_m.group(1).strip() if title_m else url
            # Strip remaining tags + collapse whitespace
            clean = re.sub(r'<[^>]+>', ' ', clean)
            clean = re.sub(r'[ \t]+', ' ', clean)
            clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
            content = clean[:max_chars]
            return {"ok": True, "content": content, "url": url, "title": title, "error": ""}
        except Exception as e:
            return {"ok": False, "content": "", "url": url, "title": "", "error": str(e)}

# ═══════════════════════════════════════════════════════════════════
# v2.0: GAMIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════════
class GamificationEngine:
    """EXP, Level, Badge system"""

    LEVELS = [
        (0,     "🌱 Seedling"),
        (500,   "📚 Scholar"),
        (1500,  "⭐ Rising Star"),
        (3000,  "🔥 Expert"),
        (5000,  "💎 Master"),
        (10000, "🏆 Legend"),
    ]

    BADGES = {
        "first_lesson": {"name": "First Step",    "icon": "👣", "desc": "เรียนบทเรียนแรก",           "exp": 50},
        "hw_submitted": {"name": "Diligent",      "icon": "📝", "desc": "ส่งการบ้านครั้งแรก",         "exp": 80},
        "perfect_hw":   {"name": "Perfect Score", "icon": "💯", "desc": "ได้ 20/20 ในการบ้าน",        "exp": 150},
        "week_warrior": {"name": "Week Warrior",  "icon": "⚔️", "desc": "เรียนจบ 7 วัน",              "exp": 300},
        "graduate":     {"name": "Graduate",      "icon": "🎓", "desc": "เรียนจบหลักสูตร",             "exp": 500},
    }

    EXP_REWARDS = {
        "lesson_read":  50,
        "hw_submit":    80,
        "hw_bonus":     20,   # per point above 15/20
        "quiz":         30,
        "day_complete": 40,
    }

    @classmethod
    def get_level_info(cls, exp: int) -> dict:
        level_idx = 0
        for i, (threshold, _) in enumerate(cls.LEVELS):
            if exp >= threshold:
                level_idx = i
        threshold, name = cls.LEVELS[level_idx]
        next_threshold = cls.LEVELS[level_idx + 1][0] if level_idx + 1 < len(cls.LEVELS) else threshold
        pct = 0 if next_threshold == threshold else int((exp - threshold) / (next_threshold - threshold) * 100)
        return {
            "level":      level_idx + 1,
            "name":       name,
            "exp":        exp,
            "threshold":  threshold,
            "next":       next_threshold,
            "pct":        min(100, pct),
        }

    @classmethod
    def award_exp(cls, course: "Course", exp_type: str, amount: int = 0) -> int:
        base = cls.EXP_REWARDS.get(exp_type, 0) + amount
        course.progress["exp"] = course.progress.get("exp", 0) + base
        course.save()
        print(c(C.YELLOW, f"  +{base} EXP ({exp_type}) → total {course.progress['exp']}"))
        return base

    @classmethod
    def unlock_badge(cls, course: "Course", badge_id: str) -> bool:
        """Returns True if newly unlocked"""
        badges = course.progress.get("badges", [])
        if badge_id in badges:
            return False
        badges.append(badge_id)
        course.progress["badges"] = badges
        # Award badge EXP
        bonus = cls.BADGES.get(badge_id, {}).get("exp", 0)
        if bonus:
            course.progress["exp"] = course.progress.get("exp", 0) + bonus
        course.save()
        print(c(C.MAGENTA, f"  🏅 Badge unlocked: {badge_id} (+{bonus} EXP)"))
        return True

    @classmethod
    def check_badges(cls, course: "Course"):
        """Auto-check and unlock earned badges"""
        prog = course.progress
        days_done = prog.get("days_completed", [])
        hw_scores = prog.get("homework_scores", {})

        if days_done:
            cls.unlock_badge(course, "first_lesson")
        if hw_scores:
            cls.unlock_badge(course, "hw_submitted")
        if any(v >= 20 for v in hw_scores.values()):
            cls.unlock_badge(course, "perfect_hw")
        if len(days_done) >= 7:
            cls.unlock_badge(course, "week_warrior")
        if len(days_done) >= course.total_days:
            cls.unlock_badge(course, "graduate")

# ═══════════════════════════════════════════════════════════════════
# v2.0: CERTIFICATE ENGINE
# ═══════════════════════════════════════════════════════════════════
class CertificateEngine:
    """สร้างใบประกาศนียบัตรดิจิทัล"""

    @staticmethod
    def generate_html(course: "Course") -> str:
        prog   = course.get_summary()
        t      = course.teacher_persona
        lp     = course.learner_profile
        ginfo  = GamificationEngine.get_level_info(course.progress.get("exp", 0))
        badges = course.progress.get("badges", [])
        date   = datetime.now().strftime("%d %B %Y")
        badge_html = " ".join(
            GamificationEngine.BADGES.get(b, {}).get("icon", "") + " "
            + GamificationEngine.BADGES.get(b, {}).get("name", b)
            for b in badges
        )
        is_complete = prog["days_done"] >= prog["total_days"]
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{background:#0d0f12;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;font-family:'Georgia',serif}}
  .cert{{background:linear-gradient(135deg,#1e242e,#252d3a);border:3px solid #c8a84b;border-radius:20px;padding:50px;max-width:680px;width:100%;text-align:center;color:#f5f0e6;box-shadow:0 0 60px rgba(200,168,75,0.3)}}
  .logo{{font-size:48px;color:#c8a84b;margin-bottom:8px}}
  .uni{{font-size:13px;letter-spacing:5px;color:#8a9ab0;margin-bottom:32px}}
  .cert-title{{font-size:14px;letter-spacing:3px;color:#c8a84b;margin-bottom:16px}}
  .learner{{font-size:36px;color:#e8cc7a;margin:16px 0;border-bottom:2px solid #c8a84b;padding-bottom:16px}}
  .course-name{{font-size:20px;color:#f5f0e6;margin:16px 0}}
  .stats{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin:24px 0}}
  .stat{{background:rgba(200,168,75,0.1);border:1px solid #2e3a4a;border-radius:8px;padding:12px}}
  .sv{{font-size:24px;color:#c8a84b;font-weight:bold}}
  .sl{{font-size:10px;color:#8a9ab0;letter-spacing:2px}}
  .badges{{margin:20px 0;font-size:13px;color:#e8cc7a;line-height:2}}
  .teacher{{margin-top:24px;font-size:12px;color:#8a9ab0}}
  .seal{{font-size:60px;margin:16px 0}}
  .incomplete{{color:#e88080;font-size:12px;margin-top:8px}}
</style>
</head>
<body>
<div class="cert">
  <div class="logo">Pockademy</div>
  <div class="uni">UNIVERSITY · CERTIFICATE OF COMPLETION</div>
  <div class="cert-title">ขอมอบใบประกาศนียบัตรแก่</div>
  <div class="learner">{lp.get('name', 'ผู้เรียน')}</div>
  <div class="cert-title">ในการสำเร็จการศึกษาวิชา</div>
  <div class="course-name">"{course.title}"</div>
  <div class="stats">
    <div class="stat"><div class="sv">{prog['days_done']}/{prog['total_days']}</div><div class="sl">DAYS</div></div>
    <div class="stat"><div class="sv">{prog['total_score']}</div><div class="sl">SCORE</div></div>
    <div class="stat"><div class="sv">{ginfo['exp']}</div><div class="sl">EXP · {ginfo['name']}</div></div>
  </div>
  <div class="badges">🏅 Badges: {badge_html or '—'}</div>
  {"" if is_complete else '<div class="incomplete">⚠️ หลักสูตรยังไม่สมบูรณ์ 100%</div>'}
  <div class="seal">{"🎓" if is_complete else "📚"}</div>
  <div class="teacher">สอนโดย {t.get('name', 'ครู ARIA')} ({t.get('title', '')})<br>วันที่: {date}</div>
</div>
</body></html>"""

# ═══════════════════════════════════════════════════════════════════
# [FEAT-4 v2.5] PHASE CERTIFICATE + NEW BADGE
# ═══════════════════════════════════════════════════════════════════

# เพิ่ม badge ใหม่ใน GamificationEngine.BADGES สำหรับ phase
# (ไม่แก้ class โดยตรง — patch ผ่าน monkey-patch หลัง class define)

def _patch_gamification_phase_badge():
    """เรียกครั้งเดียวหลัง GamificationEngine define แล้ว"""
    GamificationEngine.BADGES["phase_complete"] = {
        "name": "Phase Master", "icon": "🏛️",
        "desc": "เรียนจบ Phase ใน Roadmap", "exp": 400
    }

# (ถูกเรียกใน __main__ block)


# ─────────────────────────────────────────────────────────────────────
# [FEAT-2 v2.5] NotebookLM Script Generator function
# ─────────────────────────────────────────────────────────────────────
def _generate_notebooklm_script(ai: "AIClient", course: "Course", day: int) -> str:
    """สร้าง Script 7-9 นาที สำหรับ Google NotebookLM"""
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    lesson_content = course.get_cache(f"lesson_{day}") or ""
    lang_map = {"th": "ภาษาไทย", "en": "English", "th_en": "ไทย+English ผสม"}
    lang = lang_map.get(course.lang, "ภาษาไทย")
    t = course.teacher_persona

    # สร้าง context จาก periods ถ้ามี
    periods_info = ""
    periods = plan.get("periods", [])
    if periods:
        periods_info = "\nคาบเรียนในวันนี้:\n" + "\n".join(
            f"  - {p.get('name','')}: {p.get('focus','')}" for p in periods
        )

    prompt = f"""คุณคือ {t.get('name','ครู ARIA')} ผู้เชี่ยวชาญด้าน {course.subject}
กำลังสร้าง Script สำหรับ Google NotebookLM Podcast/Audio Overview

บทเรียน: Day {day} — {plan.get('title', '')}
หัวข้อ: {plan.get('topics', '')}
วัตถุประสงค์: {plan.get('objectives', '')}{periods_info}
เนื้อหาบทเรียน (อ้างอิง):\n{lesson_content[:1200]}

ภาษา: {lang}

สร้าง Script สำหรับ NotebookLM ที่มีความยาวเหมาะกับ 7-9 นาที (ประมาณ 900-1200 คำ)
โครงสร้างต้องมีดังนี้:

# 🎙️ NotebookLM Script — Day {day}: {plan.get('title', '')}

## บทนำ (1-1.5 นาที)
[เขียนบทนำที่น่าสนใจ แนะนำหัวข้อและทำไมสิ่งนี้สำคัญ]

## เนื้อหาหลัก จุดที่ 1: [ชื่อหัวข้อ] (1.5-2 นาที)
[เนื้อหาละเอียด พร้อมตัวอย่าง]

## เนื้อหาหลัก จุดที่ 2: [ชื่อหัวข้อ] (1.5-2 นาที)
[เนื้อหาละเอียด พร้อมตัวอย่าง]

## เนื้อหาหลัก จุดที่ 3: [ชื่อหัวข้อ] (1.5-2 นาที)
[เนื้อหาละเอียด พร้อมตัวอย่าง]

## บทสรุปและ Call to Action (1 นาที)
[สรุปประเด็นสำคัญ + ให้กำลังใจ + บอกว่าต่อไปจะเรียนเรื่องอะไร]

---
💡 วิธีใช้: คัดลอก Script นี้ทั้งหมด → วางใน Google NotebookLM → กด Generate Audio Overview
"""
    result = ai.call(prompt, max_tokens=3000, temperature=0.7)
    return result


# ─────────────────────────────────────────────────────────────────────
# [FEAT-1c v2.5] Generate Next Phase for Roadmap
# ─────────────────────────────────────────────────────────────────────
def _generate_next_phase(course: "Course") -> dict:
    """สร้าง curriculum Phase ถัดไปสำหรับ Roadmap"""
    try:
        ai = _make_ai_for_course(course)
        agent = EnrollmentAgent(ai)
        lp = course.learner_profile

        current_phase = course.current_phase
        next_phase    = current_phase + 1
        phase_size    = course.phase_size or 30
        start_day     = current_phase * phase_size + 1
        end_day       = next_phase * phase_size

        # สร้าง context จาก phase ก่อนหน้า
        completed_titles = []
        for plan in course.curriculum:
            if plan.get("title"):
                completed_titles.append(f"Day {plan['day']}: {plan['title']}")

        teacher = course.teacher_persona
        lang_map = {"th": "ภาษาไทย", "en": "English", "th_en": "ไทย+English ผสม"}
        lang_str = lang_map.get(course.lang, "ภาษาไทย")

        hrs_per_day = lp.get('hours_per_day', 1)
        # [v2.9] use time-slot calculator
        _ts_slots = EnrollmentAgent._build_timeslots(hrs_per_day)
        periods_per_day = len([s for s in _ts_slots if not s["is_break"]])

        phase_labels = {1: "Intermediate", 2: "Advanced", 3: "Mastery"}
        phase_label  = phase_labels.get(next_phase, f"Phase {next_phase}")

        prompt = f"""คุณคือ {teacher.get('name')} ออกแบบ Phase {next_phase} ของ Roadmap
วิชา: {course.subject} | ระดับ: {phase_label}
ภาษา: {lang_str} | {periods_per_day} คาบ/วัน

Phase ก่อนหน้าครอบคลุม:
{chr(10).join(completed_titles[-10:])}

ตอนนี้ต้องสร้าง Day {start_day} ถึง Day {end_day} ({phase_size} วัน)
เน้นเนื้อหาระดับสูงขึ้นจาก Phase ก่อน ไม่ซ้ำเนื้อหาเดิม

ตอบเป็น JSON array เท่านั้น (Day {start_day} ถึง {end_day}):
[
  {{
    "day": {start_day},
    "title": "ชื่อบทเรียน",
    "topics": "หัวข้อย่อย",
    "objectives": "วัตถุประสงค์",
    "homework_type": "practice|reflection|project|quiz",
    "homework_brief": "โจทย์การบ้าน",
    "is_exam_day": false,
    "difficulty": {min(5, 2 + next_phase)},
    "periods": [
      {{"period": 1, "name": "คาบที่ 1: ชื่อ", "focus": "หัวข้อ"}}
    ]
  }}
]"""

        raw = ai.call(prompt, temperature=0.6, max_tokens=4000)
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        m = re.search(r'\[[\s\S]*\]', cleaned)
        new_curriculum = json.loads(m.group()) if m else []

        if new_curriculum:
            # Append to existing curriculum
            course.curriculum.extend(new_curriculum)
            course.total_days   = end_day
            course.current_phase = next_phase
            course.save()

            # Award Phase badge + EXP
            GamificationEngine.award_exp(course, "day_complete", 200)
            GamificationEngine.unlock_badge(course, "phase_complete")

            print(c(C.GREEN, f"  ✅ Next Phase generated: Phase {next_phase} (Day {start_day}-{end_day})"))
            return {
                "ok": True,
                "phase": next_phase,
                "days_added": len(new_curriculum),
                "new_total_days": course.total_days,
                "start_day": start_day,
                "end_day": end_day,
            }
        else:
            return {"ok": False, "error": "ไม่สามารถสร้าง curriculum ได้"}
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"ok": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────
# [FEAT-4 v2.5] CertificateEngine.generate_phase_html
# แทรกไว้ใน CertificateEngine class หลัง generate_html
# (patch ผ่าน function แยก เรียกจาก handle_api)
# ─────────────────────────────────────────────────────────────────────
def _cert_generate_phase_html(course: "Course", phase: int) -> str:
    """สร้าง Certificate of Phase"""
    prog   = course.get_summary()
    t      = course.teacher_persona
    lp     = course.learner_profile
    ginfo  = GamificationEngine.get_level_info(course.progress.get("exp", 0))
    date   = datetime.now().strftime("%d %B %Y")
    phase_size = course.phase_size or 30
    phase_end  = phase * phase_size
    phase_start = (phase - 1) * phase_size + 1
    phase_labels = {1: "Foundation", 2: "Intermediate", 3: "Advanced", 4: "Mastery"}
    phase_label  = phase_labels.get(phase, f"Phase {phase}")

    days_in_phase = [d for d in course.progress.get("days_completed", [])
                     if phase_start <= d <= phase_end]
    completion_pct = int(len(days_in_phase) / max(phase_size, 1) * 100)

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{background:#0d0f12;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;font-family:'Georgia',serif}}
  .cert{{background:linear-gradient(135deg,#1a1f2e,#252d3a);border:3px solid #8e44ad;border-radius:20px;padding:50px;max-width:680px;width:100%;text-align:center;color:#f5f0e6;box-shadow:0 0 60px rgba(142,68,173,0.4)}}
  .logo{{font-size:48px;color:#8e44ad;margin-bottom:8px}}
  .uni{{font-size:12px;letter-spacing:5px;color:#8a9ab0;margin-bottom:32px}}
  .phase-badge{{display:inline-block;background:rgba(142,68,173,0.2);border:2px solid #8e44ad;border-radius:50px;padding:8px 24px;font-size:14px;letter-spacing:2px;color:#c39bd3;margin-bottom:24px}}
  .cert-title{{font-size:13px;letter-spacing:3px;color:#c39bd3;margin-bottom:12px}}
  .learner{{font-size:34px;color:#e8cc7a;margin:16px 0;border-bottom:2px solid #8e44ad;padding-bottom:16px}}
  .course-name{{font-size:18px;color:#f5f0e6;margin:16px 0}}
  .stats{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin:24px 0}}
  .stat{{background:rgba(142,68,173,0.1);border:1px solid #2e3a4a;border-radius:8px;padding:12px}}
  .sv{{font-size:22px;color:#c39bd3;font-weight:bold}}
  .sl{{font-size:10px;color:#8a9ab0;letter-spacing:2px}}
  .seal{{font-size:60px;margin:16px 0}}
  .teacher{{margin-top:24px;font-size:12px;color:#8a9ab0}}
  .prog-bar{{background:#1e242e;border-radius:4px;height:8px;margin:12px auto;max-width:300px}}
  .prog-fill{{background:linear-gradient(90deg,#8e44ad,#c8a84b);height:100%;border-radius:4px}}
</style>
</head>
<body>
<div class="cert">
  <div class="logo">🏛️</div>
  <div class="uni">POCKADEMY · ROADMAP CERTIFICATE</div>
  <div class="phase-badge">PHASE {phase}: {phase_label.upper()}</div>
  <div class="cert-title">ขอมอบใบรับรองความสำเร็จ Phase {phase} แก่</div>
  <div class="learner">{lp.get('name', 'ผู้เรียน')}</div>
  <div class="cert-title">วิชา</div>
  <div class="course-name">"{course.subject}"</div>
  <div class="prog-bar"><div class="prog-fill" style="width:{completion_pct}%"></div></div>
  <div style="font-size:12px;color:#8a9ab0;margin-bottom:16px">Day {phase_start}–{phase_end} | เรียนจบ {len(days_in_phase)}/{phase_size} วัน ({completion_pct}%)</div>
  <div class="stats">
    <div class="stat"><div class="sv">{phase}</div><div class="sl">PHASE</div></div>
    <div class="stat"><div class="sv">{ginfo['exp']}</div><div class="sl">EXP</div></div>
    <div class="stat"><div class="sv">{prog['total_score']}</div><div class="sl">SCORE</div></div>
  </div>
  <div class="seal">🏛️</div>
  <div style="font-size:13px;color:#c39bd3;margin:8px 0">{ginfo['name']}</div>
  <div class="teacher">สอนโดย {t.get('name', 'ครู ARIA')} ({t.get('title', '')})<br>วันที่: {date}</div>
</div>
</body></html>"""


# Alias ให้ handle_api ใช้ได้
class CertificateEngine_Phase:
    generate_phase_html = staticmethod(_cert_generate_phase_html)


# ═══════════════════════════════════════════════════════════════════
# COURSE DATA MODEL — v1.0 + v2.0 additions
# ═══════════════════════════════════════════════════════════════════
class Course:
    """ข้อมูลหลักสูตรทั้งหมด (v2.0: + EXP/Level/Badges/RAG/persistent chat)"""

    def __init__(self, data: dict = None):
        d = data or {}
        self.id          : str  = d.get("id", str(uuid.uuid4())[:8])
        self.title       : str  = d.get("title", "")
        self.subject     : str  = d.get("subject", "")
        # [v2.9.8] subject_name — key ใหม่สำหรับ UI; fallback → subject (backward compat)
        self.subject_name: str  = d.get("subject_name", "") or self.subject
        self.description : str  = d.get("description", "")
        self.total_days  : int  = d.get("total_days", 7)
        self.level       : str  = d.get("level", "beginner")
        self.style       : str  = d.get("style", "practical")
        self.lang        : str  = d.get("lang", "th")
        self.created_at  : str  = d.get("created_at", datetime.now().isoformat())
        self.teacher_persona: dict = d.get("teacher_persona", {})
        self.curriculum  : list = d.get("curriculum", [])
        self.learner_profile: dict = d.get("learner_profile", {})
        self.provider    : str  = d.get("provider", "gemini")
        self.model       : str  = d.get("model", "gemini-3.1-flash-lite-preview")

        # v2.0: RAG context
        self.rag_context : str  = d.get("rag_context", "")
        self.rag_url     : str  = d.get("rag_url", "")
        self.mentor_style: str  = d.get("mentor_style", "friendly")
        # [FEAT-1d v2.5] Roadmap fields
        self.roadmap_mode: bool = d.get("roadmap_mode", False)
        self.phase_size  : int  = d.get("phase_size", 0)
        self.current_phase: int = d.get("current_phase", 1)

        # Progress (v1 fields + v2 EXP/Level/Badges + persistent chat)
        default_prog = {
            "total_score"      : 0,
            "days_completed"   : [],
            "homework_scores"  : {},
            "exam_scores"      : {},
            "study_time_secs"  : 0,
            "current_day"      : 1,
            "day_scores"       : {},
            "last_lesson_day"  : None,
            "last_hw_day"      : None,
            "last_hw_result"   : None,
            "notes"            : [],
            # v2.0 additions
            "exp"              : 0,
            "badges"           : [],
            "chat_history_main": [],   # persistent main chat [{user, ai, ts}]
            "chat_history_lesson": {}, # {day_str: [{user, ai, ts}]}
            # [v2.9.6] Core Logic Gate fields
            "periods_read"          : {},
            "period_read_timestamps": {},
            "homework_submissions"  : {},
            "recovery_tasks_done"   : {},
            "quiz_sessions"         : {},
            "quiz_attempts"         : {},
        }
        saved_prog = d.get("progress", {})
        for k, v in default_prog.items():
            if k not in saved_prog:
                saved_prog[k] = v
        self.progress = saved_prog

        self.cache : dict = d.get("cache", {})

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title,
            "subject": self.subject,
            # [v2.9.8] subject_name — ส่ง key ใหม่ไปด้วย เพื่อให้ JS อ่านได้
            "subject_name": self.subject_name or self.subject,
            "description": self.description, "total_days": self.total_days,
            "level": self.level, "style": self.style, "lang": self.lang,
            "created_at": self.created_at, "teacher_persona": self.teacher_persona,
            "curriculum": self.curriculum, "learner_profile": self.learner_profile,
            "progress": self.progress, "cache": self.cache,
            "provider": self.provider, "model": self.model,
            "rag_context": self.rag_context, "rag_url": self.rag_url,
            "mentor_style": self.mentor_style,
            # [FEAT-1d v2.5]
            "roadmap_mode" : self.roadmap_mode,
            "phase_size"   : self.phase_size,
            "current_phase": self.current_phase,
        }

    def save(self):
        COURSES_DIR.mkdir(parents=True, exist_ok=True)
        path = COURSES_DIR / f"{self.id}.json"
        tmp  = str(path) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)

    @classmethod
    def load(cls, course_id: str) -> Optional["Course"]:
        path = COURSES_DIR / f"{course_id}.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        except Exception:
            return None

    @classmethod
    def delete(cls, course_id: str) -> bool:
        path = COURSES_DIR / f"{course_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    @classmethod
    def list_all(cls) -> list:
        COURSES_DIR.mkdir(parents=True, exist_ok=True)
        courses = []
        for p in sorted(COURSES_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    prog = d.get("progress", {})
                    exp  = prog.get("exp", 0)
                    ginfo = GamificationEngine.get_level_info(exp)
                    courses.append({
                        "id"          : d.get("id"),
                        "title"       : d.get("title"),
                        "subject"     : d.get("subject"),
                        "total_days"  : d.get("total_days"),
                        "level"       : d.get("level"),
                        "created_at"  : d.get("created_at"),
                        "days_done"   : len(prog.get("days_completed", [])),
                        "total_score" : prog.get("total_score", 0),
                        "learner_name": d.get("learner_profile", {}).get("name", ""),
                        "exp"         : exp,
                        "level_name"  : ginfo["name"],
                        "badges"      : prog.get("badges", []),
                        "mentor_style": d.get("mentor_style", "friendly"),
                    })
            except Exception:
                pass
        return courses

    # ── Progress helpers (v1.0 unchanged) ───────────────────────
    def add_score(self, points: int, day: int = None):
        self.progress["total_score"] = min(9999, self.progress["total_score"] + points)
        if day is not None:
            dk = str(day)
            self.progress["day_scores"][dk] = self.progress["day_scores"].get(dk, 0) + points
        self.save()

    def deduct_score_for_day(self, day: int) -> int:
        dk = str(day)
        amount = self.progress["day_scores"].get(dk, 0)
        hw_key = f"day_{day}"
        hw_sc  = self.progress["homework_scores"].get(hw_key, 0)
        if amount == 0 and hw_sc > 0:
            amount = hw_sc + 10
        if amount > 0:
            self.progress["total_score"] = max(0, self.progress["total_score"] - amount)
            self.progress["day_scores"].pop(dk, None)
        self.progress["homework_scores"].pop(hw_key, None)
        if day in self.progress["days_completed"]:
            self.progress["days_completed"].remove(day)
        if self.progress["days_completed"]:
            self.progress["current_day"] = max(self.progress["days_completed"]) + 1
        else:
            self.progress["current_day"] = 1
        self.save()
        return amount

    def mark_day_complete(self, day: int):
        if day not in self.progress["days_completed"]:
            self.progress["days_completed"].append(day)
            self.add_score(10, day=day)
        self.progress["current_day"] = max(self.progress.get("current_day", 1), day)
        self.save()

    def record_homework(self, day: int, score: int, feedback: str = ""):
        self.progress["homework_scores"][f"day_{day}"] = score
        self.progress["last_hw_day"] = day
        self.progress["last_hw_result"] = feedback[:500] if feedback else f"{score} คะแนน"
        self.add_score(score, day=day)

    def get_cache(self, key: str) -> Optional[str]:
        entry = self.cache.get(key)
        if isinstance(entry, dict): return entry.get("content")
        return None

    def set_cache(self, key: str, content: str):
        self.cache[key] = {"content": content, "ts": datetime.now().isoformat()}
        self.save()

    def invalidate_cache_day(self, day: int):
        for k in [f"lesson_{day}", f"homework_{day}", f"quiz_{day}"]:
            self.cache.pop(k, None)
        self.save()

    # v2.0: persistent chat helpers
    def append_chat_main(self, user: str, ai: str):
        h = self.progress.setdefault("chat_history_main", [])
        # [FIX-1b v2.5] เก็บทั้ง 'ai' และ 'assistant' เพื่อ backward-compat
        h.append({"user": user, "ai": ai, "assistant": ai, "ts": datetime.now().isoformat()})
        if len(h) > 60:  # keep last 60 turns
            self.progress["chat_history_main"] = h[-60:]
        self.save()

    def append_chat_lesson(self, day: int, user: str, ai: str):
        dk = str(day)
        h  = self.progress.setdefault("chat_history_lesson", {})
        day_h = h.setdefault(dk, [])
        # [FIX-1b v2.5] เก็บทั้ง 'ai' และ 'assistant'
        day_h.append({"user": user, "ai": ai, "assistant": ai, "ts": datetime.now().isoformat()})
        if len(day_h) > 30:
            h[dk] = day_h[-30:]
        self.save()

    def get_summary(self) -> dict:
        done  = len(self.progress["days_completed"])
        total = self.total_days
        secs  = self.progress.get("study_time_secs", 0)
        h, m  = secs // 3600, (secs % 3600) // 60
        exp   = self.progress.get("exp", 0)
        ginfo = GamificationEngine.get_level_info(exp)
        return {
            "total_score" : self.progress["total_score"],
            "days_done"   : done,
            "total_days"  : total,
            "pct"         : int(done / max(total, 1) * 100),
            "study_time"  : f"{h:02d}:{m:02d}",
            "current_day" : self.progress.get("current_day", 1),
            "hw_total"    : sum(self.progress["homework_scores"].values()),
            # v2.0
            "exp"         : exp,
            "level"       : ginfo["level"],
            "level_name"  : ginfo["name"],
            "level_pct"   : ginfo["pct"],
            "badges"      : self.progress.get("badges", []),
        }

# ═══════════════════════════════════════════════════════════════════
# [v2.9.6] THE CORE LOGIC GATE — Sequential Discipline Engine
# ═══════════════════════════════════════════════════════════════════

QUIZ_TIMER_SECONDS = 600  # 10 นาทีสำหรับ Exercise Speed-Run


def check_progression_barrier(course: "Course", target_day: int) -> dict:
    """
    [v2.9.6] Hard-Lock Mechanism
    ตรวจสอบว่าผู้เรียนสามารถเข้าถึง target_day ได้หรือไม่
    Returns: { "allowed": bool, "reason": str, "missing": list }
    """
    if target_day <= 1:
        return {"allowed": True, "reason": "Day 1 is always open", "missing": []}

    current_day = course.progress.get("current_day", 1)
    days_completed = course.progress.get("days_completed", [])

    # ── Day Lock: ต้องทำ Day ก่อนหน้าให้ครบก่อน ───────────────
    prev_day = target_day - 1
    missing = []

    if prev_day not in days_completed:
        # ตรวจสอบว่า Day ก่อนหน้าครบเงื่อนไขทุกข้อหรือไม่
        barrier = _check_day_completion(course, prev_day)
        if not barrier["complete"]:
            missing.extend(barrier["missing"])
            return {
                "allowed": False,
                "reason": f"❌ Day {prev_day} ยังไม่ครบ 100% — ต้องทำให้เสร็จก่อน",
                "missing": missing,
                "blocked_at_day": prev_day,
            }

    return {"allowed": True, "reason": "✅ ผ่านเงื่อนไขทั้งหมด", "missing": []}


def _check_day_completion(course: "Course", day: int) -> dict:
    """
    ตรวจสอบว่า Day ครบ 100% หรือไม่:
    1. ทุก Period ถูก mark_as_read
    2. มีการส่งการบ้าน (Submission Check)
    3. การบ้านไม่ Missed
    """
    missing = []
    prog = course.progress

    # ── 1. Activity Gate: ทุก Period ต้องถูกอ่าน ─────────────
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    periods = plan.get("periods", [])
    periods_read = prog.get("periods_read", {})
    day_periods_read = periods_read.get(str(day), [])

    for i, period in enumerate(periods, 1):
        if i not in day_periods_read:
            missing.append(f"คาบที่ {i}: {period.get('name', f'Period {i}')} — ยังไม่ได้เรียน")

    # ── 2. Submission Check: ต้องส่งการบ้าน ──────────────────
    hw_scores = prog.get("homework_scores", {})
    hw_key = f"day_{day}"
    submissions = prog.get("homework_submissions", {})

    if hw_key not in submissions:
        missing.append(f"การบ้าน Day {day} — ยังไม่ได้ส่ง")
    else:
        # ตรวจสอบ Missed
        sub = submissions[hw_key]
        if sub.get("status") == "missed":
            recovery_done = prog.get("recovery_tasks_done", {}).get(str(day), False)
            if not recovery_done:
                missing.append(f"การบ้าน Day {day} หมดเวลา — ต้องทำ Recovery Task ก่อน")

    complete = len(missing) == 0
    return {"complete": complete, "missing": missing}


def check_activity_gate(course: "Course", day: int, activity: str) -> dict:
    """
    [v2.9.6] Activity Gate
    การบ้านและแบบฝึกหัดจะ Enabled ก็ต่อเมื่อเรียนครบทุก Period
    activity: "homework" | "exercise"
    """
    prog = course.progress
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    periods = plan.get("periods", [])
    periods_read = prog.get("periods_read", {})
    day_periods_read = periods_read.get(str(day), [])

    total_periods = len(periods)
    read_count = len([p for p in day_periods_read if 1 <= p <= total_periods])

    if total_periods == 0 or read_count >= total_periods:
        return {"enabled": True, "reason": "✅ เรียนครบทุกคาบแล้ว", "read": read_count, "total": total_periods}

    remaining = total_periods - read_count
    unread = [
        f"คาบที่ {i}: {periods[i-1].get('name', f'Period {i}')}"
        for i in range(1, total_periods + 1)
        if i not in day_periods_read
    ]
    return {
        "enabled": False,
        "reason": f"🔒 ต้องเรียนให้ครบก่อน — ยังเหลืออีก {remaining} คาบ",
        "unread_periods": unread,
        "read": read_count,
        "total": total_periods,
    }


def check_homework_deadline(course: "Course", day: int) -> dict:
    """
    [v2.9.6] 24-Hour Homework Rule
    การบ้านต้องส่งภายในวันรุ่งขึ้น (24 ชั่วโมงหลังจากเรียนวันนั้น)
    """
    prog = course.progress
    periods_read = prog.get("periods_read", {})
    day_periods_read = periods_read.get(str(day), [])

    if not day_periods_read:
        return {"status": "not_started", "message": "ยังไม่ได้เริ่มเรียน Day นี้"}

    # ดึง timestamp ของ period แรกที่อ่าน (start of learning day)
    period_timestamps = prog.get("period_read_timestamps", {})
    day_ts = period_timestamps.get(str(day), {})

    if not day_ts:
        return {"status": "open", "deadline": None, "message": "ยังไม่ระบุเวลา — เปิดรับงาน"}

    # หา timestamp เร็วสุดของวันนั้น
    earliest_ts_str = min(day_ts.values())
    try:
        earliest_ts = datetime.fromisoformat(earliest_ts_str)
        deadline = earliest_ts + timedelta(hours=24)
        now = datetime.now()
        remaining_secs = (deadline - now).total_seconds()

        if remaining_secs > 0:
            h = int(remaining_secs // 3600)
            m = int((remaining_secs % 3600) // 60)
            return {
                "status": "open",
                "deadline": deadline.isoformat(),
                "remaining_seconds": int(remaining_secs),
                "message": f"⏰ เหลือเวลา {h} ชั่วโมง {m} นาที",
            }
        else:
            return {
                "status": "missed",
                "deadline": deadline.isoformat(),
                "remaining_seconds": 0,
                "message": "❌ หมดเวลาส่งการบ้านแล้ว — ระบบจะสร้าง Recovery Task",
            }
    except Exception:
        return {"status": "open", "deadline": None, "message": "เปิดรับงาน"}


def mark_homework_missed(course: "Course", day: int):
    """[v2.9.6] ตั้งสถานะ Missed และบังคับทำ Recovery Task"""
    submissions = course.progress.setdefault("homework_submissions", {})
    hw_key = f"day_{day}"
    if hw_key not in submissions or submissions[hw_key].get("status") != "submitted":
        submissions[hw_key] = {
            "status": "missed",
            "ts": datetime.now().isoformat(),
            "score": 0,
            "feedback": "หมดเวลาส่งการบ้าน — กรุณาทำ Recovery Task",
        }
        course.save()


def generate_recovery_task(ai: "AIClient", course: "Course", day: int) -> str:
    """[v2.9.6] สร้าง Recovery Task สำหรับวันที่ Missed"""
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    prompt = f"""ผู้เรียนส่งการบ้าน Day {day}: "{plan.get('title', '')}" ไม่ทันเวลา
หัวข้อ: {plan.get('topics', '')} | วัตถุประสงค์: {plan.get('objectives', '')}

สร้าง **Recovery Task** ที่:
1. ครอบคลุมเนื้อหาสำคัญของ Day {day} ทั้งหมด
2. ยากกว่างานเดิมเล็กน้อย (เพื่อให้ผู้เรียนทบทวนจริง)
3. ส่งได้ภายใน 2 ชั่วโมง
4. มีเกณฑ์การผ่าน (ต้องได้ ≥ 12/20)

โครงสร้าง:
🚨 Recovery Task — Day {day}
🎯 เหตุผล (ส่งงานช้า → ต้องพิสูจน์ความเข้าใจ)
📋 โจทย์ Recovery
⭐ เกณฑ์การผ่าน"""
    content = ai.call(prompt, system=course.teacher_persona.get("personality", ""), max_tokens=1500)
    return content


def generate_comprehensive_homework(ai: "AIClient", course: "Course", day: int) -> str:
    """
    [v2.9.6] Comprehensive Synthesis Homework + Adaptive Workload
    """
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    periods = plan.get("periods", [])

    # Adaptive Workload: กำหนดให้ทุกๆ 3 วันเป็นการบ้านแบบเบา (Reflection)
    is_rest_day = (day % 3 == 0)
    
    if is_rest_day:
        prompt = f"""วันเรียนที่ {day} เป็นช่วงเวลาพักสมอง (Spacing Effect) ให้ผู้เรียน
สร้างการบ้านแบบ **Reflection (สะท้อนความคิด)** สั้นๆ ใช้เวลาทำไม่เกิน 10 นาที
หัวข้อ: "{plan.get('title', '')}"
คำสั่ง: ให้ผู้เรียนเขียนสรุปสั้นๆ ว่าสิ่งที่เรียนไปใน 2-3 วันที่ผ่านมา จะนำไปใช้จริงได้อย่างไรบ้าง และตั้งเป้าหมายในวันถัดไป"""
    else:
        period_summaries = "\n".join(
            f"  คาบ {i+1}: {p.get('name', '')} — {p.get('focus', p.get('detail', ''))[:100]}"
            for i, p in enumerate(periods)
        )
        prompt = f"""สร้างการบ้านแบบ **Comprehensive Synthesis** สำหรับ Day {day}: "{plan.get('title', '')}"

เนื้อหาจากทุกคาบในวันนี้:
{period_summaries}

**กฎสำคัญ:**
- ต้องสร้างโจทย์ **1 ข้อเดียว** ที่บังคับให้ผู้เรียนต้องนำความรู้จากทุกคาบมาใช้ร่วมกัน
- ห้ามถามแค่เรื่องใดเรื่องหนึ่ง — ต้องบูรณาการทุกคาบ
- โจทย์ต้องเป็น Real-World Scenario / Case Study ที่ต้องใช้ความรู้หลายมิติ
- คะแนนเต็ม 20 (ต้องแบ่งคะแนนย่อยตามการนำแต่ละคาบมาใช้)

โครงสร้าง:
📚 **Synthesis Homework** — Day {day}: {plan.get('title', '')}
🌐 **สถานการณ์จำลอง** (Real-World Case)
🎯 **โจทย์** (1 ข้อ — ต้องใช้ความรู้จากคาบ 1-{len(periods)} ทั้งหมด)
📋 **สิ่งที่ต้องส่ง**
⭐ **เกณฑ์คะแนน** (แยกตามคาบที่เชื่อมโยง รวม 20 คะแนน)
⏰ **กำหนดส่ง:** ภายใน 24 ชั่วโมงนับจากเริ่มเรียนวันนี้"""

    content = ai.call(prompt, system=course.teacher_persona.get("personality", ""), max_tokens=2000)
    return content


def mark_period_read(course: "Course", day: int, period: int) -> dict:
    """
    [v2.9.6] Mark Period as Read/Finished
    บันทึกว่าผู้เรียนเรียนคาบนี้เสร็จแล้ว พร้อม timestamp
    """
    prog = course.progress
    periods_read = prog.setdefault("periods_read", {})
    day_key = str(day)
    if day_key not in periods_read:
        periods_read[day_key] = []

    if period not in periods_read[day_key]:
        periods_read[day_key].append(period)

    # บันทึก timestamp
    period_ts = prog.setdefault("period_read_timestamps", {})
    if day_key not in period_ts:
        period_ts[day_key] = {}
    period_ts[day_key][str(period)] = datetime.now().isoformat()

    # ตรวจสอบว่าครบทุก period หรือยัง
    plan = next((p for p in course.curriculum if p.get("day") == day), {})
    total_periods = len(plan.get("periods", []))
    read_count = len([p for p in periods_read[day_key] if 1 <= p <= total_periods])

    GamificationEngine.award_exp(course, "lesson")
    course.save()

    return {
        "ok": True,
        "day": day,
        "period": period,
        "read_count": read_count,
        "total_periods": total_periods,
        "all_read": read_count >= total_periods and total_periods > 0,
        "activity_unlocked": read_count >= total_periods,
    }


def submit_homework(course: "Course", day: int, content: str, score: int, feedback: str) -> dict:
    """
    [v2.9.6] บันทึกการส่งการบ้านจริง (Submission Check)
    """
    # ตรวจ deadline ก่อน
    deadline_status = check_homework_deadline(course, day)
    if deadline_status["status"] == "missed":
        mark_homework_missed(course, day)
        return {
            "ok": False,
            "status": "missed",
            "message": "❌ หมดเวลาส่งการบ้านแล้ว — ระบบบันทึกสถานะ Missed",
            "recovery_required": True,
        }

    prog = course.progress
    submissions = prog.setdefault("homework_submissions", {})
    hw_key = f"day_{day}"
    submissions[hw_key] = {
        "status": "submitted",
        "ts": datetime.now().isoformat(),
        "score": score,
        "feedback": feedback[:500],
        "content_preview": content[:200],
    }

    # บันทึกคะแนน
    course.record_homework(day, score, feedback)

    # ตรวจว่า Day นี้ Complete ได้หรือยัง
    completion = _check_day_completion(course, day)
    if completion["complete"]:
        course.mark_day_complete(day)
        GamificationEngine.unlock_badge(course, "homework_hero")
        badge_awarded = True
    else:
        badge_awarded = False

    course.save()
    return {
        "ok": True,
        "status": "submitted",
        "score": score,
        "feedback": feedback,
        "day_complete": completion["complete"],
        "badge_awarded": badge_awarded,
        "remaining": completion.get("missing", []),
    }


def create_timed_quiz_session(course: "Course", day: int, period: int = 0) -> dict:
    """
    [v2.9.6] Exercise Speed-Run — สร้าง session พร้อม countdown timer
    """
    session_id = str(uuid.uuid4())[:8]
    session_key = f"quiz_session_{day}_{period}"
    session_data = {
        "session_id": session_id,
        "day": day,
        "period": period,
        "start_ts": datetime.now().isoformat(),
        "deadline_ts": (datetime.now() + timedelta(seconds=QUIZ_TIMER_SECONDS)).isoformat(),
        "timer_seconds": QUIZ_TIMER_SECONDS,
        "status": "active",
        "attempts": course.progress.get("quiz_attempts", {}).get(f"{day}_{period}", 0) + 1,
    }
    # บันทึก session
    quiz_sessions = course.progress.setdefault("quiz_sessions", {})
    quiz_sessions[session_key] = session_data
    course.progress.setdefault("quiz_attempts", {})[f"{day}_{period}"] = session_data["attempts"]
    course.save()
    return session_data


def check_quiz_timer(course: "Course", day: int, period: int = 0) -> dict:
    """[v2.9.6] ตรวจสอบว่า Quiz timer หมดหรือยัง"""
    session_key = f"quiz_session_{day}_{period}"
    session = course.progress.get("quiz_sessions", {}).get(session_key)
    if not session:
        return {"status": "no_session", "expired": False}

    try:
        deadline = datetime.fromisoformat(session["deadline_ts"])
        now = datetime.now()
        remaining = (deadline - now).total_seconds()
        if remaining <= 0:
            return {"status": "expired", "expired": True, "remaining_seconds": 0,
                    "message": "⏰ หมดเวลา — ระบบจะ Regenerate คำถามใหม่"}
        return {
            "status": "active",
            "expired": False,
            "remaining_seconds": int(remaining),
            "session_id": session.get("session_id"),
        }
    except Exception:
        return {"status": "error", "expired": False}


# ═══════════════════════════════════════════════════════════════════
# ENROLLMENT AGENT — v1.0 unchanged
# ═══════════════════════════════════════════════════════════════════
class EnrollmentAgent:
    # [REFACTOR] Assessment Questions — structured format with UI choices
    # type: "choice"  → แสดงเป็นปุ่มเลือก (choices list)
    # type: "choice+reason" → ปุ่มเลือก + ช่องเหตุผล (reason_placeholder)
    # type: "choice_timeline" → ปุ่มเลือกจำนวนวัน + ปุ่มชั่วโมง (special UI)
    # type: "text"    → ช่องพิมพ์ข้อความ (fallback เดิม)
    ASSESSMENT_QUESTIONS = [
        {
            "id"   : "goal",
            "type" : "choice+reason",
            "q"    : "สวัสดี {name}! 🎓\nคุณต้องการเรียน '{subject}' เพื่ออะไรครับ?",
            "choices": [
                {"value": "เปลี่ยนสายงาน / หางานใหม่",   "emoji": "💼"},
                {"value": "เพิ่มทักษะในงานปัจจุบัน",       "emoji": "📈"},
                {"value": "ทำโปรเจคส่วนตัว / Freelance",  "emoji": "🚀"},
                {"value": "เรียนรู้เพื่อความสนใจ",          "emoji": "📚"},
                {"value": "เตรียมสอบ / ใบรับรอง",          "emoji": "🎯"},
            ],
            "reason_placeholder": "บอกรายละเอียดเพิ่มเติม (ไม่บังคับ)",
        },
        {
            "id"   : "prior",
            "type" : "choice",
            "q"    : "ตอนนี้รู้เรื่อง '{subject}' อยู่ในระดับไหน? 💪",
            "choices": [
                {"value": "0 — ไม่รู้เลย เริ่มจากศูนย์",   "emoji": "🌱"},
                {"value": "2 — เคยได้ยิน รู้คร่าวๆ",        "emoji": "👀"},
                {"value": "5 — รู้บ้าง ทำงานพื้นฐานได้",    "emoji": "🙂"},
                {"value": "7 — ค่อนข้างเชี่ยวชาญ",          "emoji": "💪"},
                {"value": "9 — เชี่ยวชาญมาก ต้องการขั้นสูง","emoji": "🏆"},
            ],
        },
        {
            "id"   : "experience",
            "type" : "choice+reason",
            "q"    : "มีประสบการณ์เกี่ยวกับ '{subject}' แบบไหนบ้าง? 📖",
            "choices": [
                {"value": "ไม่มีประสบการณ์เลย",             "emoji": "❌"},
                {"value": "เรียนจากคอร์สออนไลน์",            "emoji": "🖥️"},
                {"value": "ทำงานจริง / ใช้ในชีวิตประจำวัน", "emoji": "🛠️"},
                {"value": "เคยทำโปรเจคของตัวเอง",           "emoji": "💡"},
                {"value": "สอนหรือแชร์ให้คนอื่น",            "emoji": "🎤"},
            ],
            "reason_placeholder": "เล่าให้ฟังสั้นๆ (เช่น โปรเจคที่เคยทำ)",
        },
        {
            "id"   : "timeline",
            "type" : "choice_timeline",
            "q"    : "อยากเรียนนานแค่ไหน และวันละกี่ชั่วโมง? 📅",
            "days_choices": [
                {"value": "7",  "label": "7 วัน"},
                {"value": "14", "label": "14 วัน"},
                {"value": "21", "label": "21 วัน"},
                {"value": "30", "label": "30 วัน"},
                {"value": "60", "label": "60 วัน"},
            ],
            "hours_choices": [
                {"value": "0.5", "label": "30 นาที"},
                {"value": "1",   "label": "1 ชม."},
                {"value": "2",   "label": "2 ชม."},
                {"value": "3",   "label": "3 ชม."},
                {"value": "4",   "label": "4+ ชม."},
            ],
        },
        {
            "id"   : "style",
            "type" : "choice",
            "q"    : "ชอบเรียนสไตล์ไหน? 🎯",
            "choices": [
                {"value": "practice", "emoji": "🛠️", "label": "เน้น Practice — ลงมือทำก่อน"},
                {"value": "theory",   "emoji": "📖", "label": "เน้น Theory — ทฤษฎีก่อน"},
                {"value": "mixed",    "emoji": "⚖️", "label": "ผสม — ทฤษฎี + ปฏิบัติสลับกัน"},
            ],
        },
        {
            "id"   : "lang",
            "type" : "choice",
            "q"    : "ต้องการให้ครูสอนเป็นภาษาอะไร? 🌐",
            "choices": [
                {"value": "Thai",             "emoji": "🇹🇭", "label": "ภาษาไทย"},
                {"value": "English",          "emoji": "🇬🇧", "label": "English"},
                {"value": "Thai + English",   "emoji": "🌐", "label": "Thai + English ผสม"},
            ],
        },
    ]

    def __init__(self, ai: AIClient):
        self.ai = ai

    def generate_teacher_persona(self, subject: str, level: str, lang: str,
                                  learner_profile: dict, mentor_style: str = "friendly") -> dict:
        style_desc = MENTOR_STYLES.get(mentor_style, MENTOR_STYLES["friendly"])["desc"]
        prompt = f"""สร้าง persona ครู AI สำหรับสอน "{subject}" ให้ผู้เรียนระดับ {level}
ภาษาที่ใช้สอน: {lang}
สไตล์บุคลิกครู: {style_desc}
เป้าหมายผู้เรียน: {learner_profile.get('goal','')}
ประสบการณ์: {learner_profile.get('experience','')}

ตอบเป็น JSON เท่านั้น (ไม่มี backtick หรือ markdown):
{{
  "name": "ชื่อครู",
  "title": "ตำแหน่ง/ความเชี่ยวชาญ",
  "personality": "บุคลิก 2-3 คำ",
  "teaching_style": "วิธีสอนสั้นๆ",
  "tone": "น้ำเสียง",
  "expertise_summary": "ความเชี่ยวชาญ (2-3 ประโยค)",
  "greeting_phrase": "ประโยคทักทายเฉพาะตัว",
  "catchphrase": "ประโยคเด็ดที่ชอบพูด"
}}"""
        raw = self.ai.call(prompt, temperature=0.8)
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "name": "อาจารย์ ARIA",
                "title": f"ผู้เชี่ยวชาญด้าน {subject}",
                "personality": "เป็นกันเอง ละเอียด ให้กำลังใจ",
                "teaching_style": "ยกตัวอย่างก่อน อธิบายทฤษฎีตาม",
                "tone": "พี่สอนน้อง",
                "expertise_summary": f"มีประสบการณ์สอน {subject} มายาวนาน",
                "greeting_phrase": "สวัสดีครับ พร้อมเรียนรู้ไปด้วยกันไหม?",
                "catchphrase": "ลองทำก่อน แล้วค่อยเข้าใจ!",
            }

    # ── [v2.9] Time-Slot helpers ────────────────────────────────────
    @staticmethod
    def _build_timeslots(hrs_per_day: float, start_hour: int = 8, start_min: int = 30) -> list:
        """คำนวณ time-slots จาก hours_per_day คืนรายการ (slot_idx, time_str, duration_min, type)"""
        total_mins = int(hrs_per_day * 60)
        # กำหนดจำนวน periods และ break
        if hrs_per_day <= 1:
            slots = [("theory", 60)]
        elif hrs_per_day <= 2:
            slots = [("theory", 60), ("practice", int((hrs_per_day-1)*60))]
        elif hrs_per_day <= 3:
            slots = [("theory", 60), ("demo", 45), ("practice", int((hrs_per_day-1.75)*60))]
        elif hrs_per_day <= 4:
            slots = [("theory", 60), ("demo", 45), ("break", 15), ("practice", 60), ("review", int((hrs_per_day-3)*60))]
        elif hrs_per_day <= 6:
            slots = [("theory", 75), ("demo", 60), ("break", 15), ("practice", 90), ("lab", 60), ("summary", 15)]
        else:  # 7-10 ชม.
            slots = [
                ("theory",   90), ("demo",     60), ("break",    15),
                ("practice", 90), ("lab",       60), ("break",    10),
                ("advanced", 60), ("summary",   20),
            ]
            # trim หรือขยายให้ตรง total_mins
        used = sum(d for _, d in slots)
        # scale ถ้าไม่ตรง
        if used > 0 and abs(used - total_mins) > 10:
            scale = total_mins / used
            slots = [(t, max(10, int(d * scale))) for t, d in slots]

        result = []
        cur_h, cur_m = start_hour, start_min
        type_labels = {"theory":"ทฤษฎี","demo":"สาธิต","practice":"ปฏิบัติ",
                       "lab":"Lab/ปฏิบัติขั้นสูง","review":"ทบทวน","summary":"สรุปผล","break":"พัก","advanced":"ขั้นสูง"}
        for slot_type, dur in slots:
            start_str = f"{cur_h:02d}:{cur_m:02d}"
            end_m = cur_m + dur
            end_h = cur_h + end_m // 60
            end_m = end_m % 60
            end_str = f"{end_h:02d}:{end_m:02d}"
            result.append({
                "time_slot": f"{start_str} – {end_str}",
                "duration_min": dur,
                "type_key": slot_type,
                "type": type_labels.get(slot_type, slot_type),
                "is_break": slot_type == "break",
            })
            cur_h, cur_m = end_h, end_m
        return result


    def generate_skeleton(self, subject: str, total_days: int, level: str,
                          style: str, lang: str, learner_profile: dict,
                          teacher: dict, rag_context: str = "") -> list:
        """
        [v3.0 Phase 1] สร้าง Skeleton หลักสูตร — เฉพาะชื่อวัน + objectives
        JSON เล็ก ไม่มี periods → parse ง่าย 100%
        periods จะถูก generate แยกใน generate_day_detail() เมื่อผู้ใช้กำลังจะเรียน
        """
        lang_str = "ภาษาไทย" if lang == "th" else ("English" if lang == "en" else "ไทย+English ผสม")
        rag_part = f"\nข้อมูลอ้างอิง (RAG):\n{rag_context[:600]}" if rag_context else ""
        hrs_per_day = learner_profile.get("hours_per_day", 2)
        # คำนวณจำนวนคาบ (สำหรับใส่ใน objectives)
        timeslots = self._build_timeslots(hrs_per_day)
        content_slots = [s for s in timeslots if not s["is_break"]]
        periods_per_day = len(content_slots)

        system_prompt = f"""คุณคือ Head of Curriculum Design ของ Pockademy
ภารกิจ: สร้างโครงสร้างหลักสูตร "{subject}" จำนวน {total_days} วัน
กฎเหล็ก:
1. ชื่อวัน (title) ต้องสั้น กระชับ สื่อถึงเนื้อหาจริง ใช้ Domain-Specific Term ของ "{subject}"
2. ห้ามใช้: "Day X Overview", "Introduction", "Basic", "Foundations & Core Taxonomy"
3. ถ้าวิชาเป็นภาษาไทย → ชื่อวันต้องเป็นภาษาไทยหรือผสม Term เฉพาะทาง
4. ต้องสร้างครบ {total_days} วัน — ไม่ขาด ไม่เกิน
5. ตอบ JSON array เท่านั้น ห้ามมี text นอก JSON ห้ามมี markdown backtick"""

        prompt = f"""สร้างโครงสร้างหลักสูตร "{subject}" {total_days} วัน
ระดับ: {level} | สไตล์: {style} | ภาษา: {lang_str}
วันละ {hrs_per_day} ชั่วโมง ({periods_per_day} คาบ/วัน)
เป้าหมาย: {learner_profile.get("goal", "")}{rag_part}

ตัวอย่างชื่อวันที่ดี:
- วิชาธรรมะ: "ไตรลักษณ์และอนิจจัง", "อริยสัจ 4 — ทุกขสมุทัย"
- วิชาการตลาด: "Customer Persona & Pain-Point Mapping", "Hook Formula & Copywriting"
- วิชาอาหาร: "Wok Hei & การควบคุมไฟ", "Sauce Base Matrix"

ตอบเป็น JSON array (ไม่มี backtick):
[
  {{
    "day": 1,
    "title": "ชื่อบทเรียนวันที่ 1 — Domain-Specific ไม่เกิน 8 คำ",
    "topics": "หัวข้อย่อย comma-separated",
    "objectives": "สิ่งที่ผู้เรียนทำได้หลังเรียน (Measurable) — {periods_per_day} คาบ",
    "homework_type": "practice",
    "homework_brief": "โจทย์การบ้านสั้นๆ",
    "is_exam_day": false,
    "difficulty": 1,
    "start_time": "08:30",
    "periods": []
  }}
]
สร้างครบ {total_days} วัน sequential learning (วันหลังยากกว่าวันก่อน)"""


        # ── เรียก AI พร้อม retry เมื่อได้วันไม่ครบ ─────────────
        # คำนวณ max_tokens ให้เพียงพอ: ~160 tokens/วัน + buffer
        needed_tokens = max(6000, total_days * 180 + 1000)

        def _try_generate(temp: float) -> list:
            """เรียก AI 1 ครั้ง คืน skeleton list หรือ [] ถ้าไม่ผ่าน"""
            raw = self.ai.call(prompt, system=system_prompt, temperature=temp, max_tokens=needed_tokens)
            try:
                cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
                m = re.search(r'\[[\s\S]*\]', cleaned)
                if not m:
                    return []
                skeleton = json.loads(m.group())
                if len(skeleton) >= 1 and skeleton[0].get("title"):
                    return skeleton
            except Exception:
                pass
            return []

        MAX_RETRIES = 3
        best: list = []
        for attempt in range(1, MAX_RETRIES + 1):
            temp = 0.6 if attempt == 1 else (0.4 if attempt == 2 else 0.7)
            print(f"  [Phase1] Attempt {attempt}/{MAX_RETRIES} — skeleton {total_days} days (temp={temp}, max_tokens={needed_tokens})...")
            result = _try_generate(temp)
            got = len(result)
            if got >= total_days:
                print(f"  [Phase1] ✅ Skeleton OK: {got} days parsed")
                for item in result:
                    item["periods"] = []
                    item["_periods_pending"] = True
                return result
            elif got > len(best):
                best = result
                print(f"  [Phase1] ⚠️ Got {got}/{total_days} days — retrying...")

        # ── retry แล้วยังไม่ครบ — merge best + fallback ──────────
        if best:
            existing_days = {item.get("day") for item in best}
            fallback_all = self._build_domain_skeleton(subject, total_days, level, style, lang_str, hrs_per_day, periods_per_day)
            merged = list(best)
            for fb_item in fallback_all:
                if fb_item["day"] not in existing_days:
                    merged.append(fb_item)
            merged.sort(key=lambda x: x.get("day", 0))
            for item in merged:
                item["periods"] = []
                item["_periods_pending"] = True
            print(f"  [Phase1] ⚡ Merged best({len(best)}) + fallback → {len(merged)} days")
            return merged

        # ── Fallback สมบูรณ์ ──────────────────────────────────────
        print(f"  [Phase1] Building domain-aware fallback skeleton...")
        return self._build_domain_skeleton(subject, total_days, level, style, lang_str, hrs_per_day, periods_per_day)
    def _build_domain_skeleton(self, subject: str, total_days: int, level: str,
                                style: str, lang_str: str, hrs_per_day: float,
                                periods_per_day: int) -> list:
        """[FIX] Fallback skeleton — ทุกวันได้ชื่อ unique โดยใช้ % position ของหลักสูตร"""
        subj_short = subject.split("—")[0].split("-")[0].strip()

        # theme pool สำหรับแต่ละช่วงของหลักสูตร (5 ช่วง x 6 themes = 30 unique titles)
        arc_themes = [
            # 0-19% : ช่วงรากฐาน
            ["แนวคิดหลักและโครงสร้าง", "หลักการพื้นฐาน",
             "Mental Model & Framework", "Core Concept Mapping",
             "กลไกและตรรกะเบื้องต้น", "Anatomy & Terminology"],
            # 20-39% : ช่วงกลไก
            ["การทำงานเชิงลึก", "เครื่องมือและการ Setup",
             "Workflow & Process Design", "Pattern Recognition",
             "Systematic Analysis", "Component Interaction"],
            # 40-59% : ช่วงลงมือทำ
            ["Output จริงครั้งแรก", "Guided Build & Iterate",
             "Error Detection & Fix", "Skill Execution Under Constraint",
             "Production-Ready Run", "Structured Problem Solving"],
            # 60-79% : ช่วง Integration
            ["บูรณาการทักษะ", "Real-World Workflow",
             "Cross-Skill Synthesis", "Quality Control & Optimization",
             "Advanced Technique Application", "Complex Scenario Handling"],
            # 80-100% : ช่วง Mastery
            ["Edge Cases & Robustness", "Scaling & Performance",
             "Expert-Level Refinement", "Full Challenge",
             "Proof of Mastery", "Capstone Integration"],
        ]
        arc_labels = ["รากฐาน", "กลไก", "ลงมือทำ", "Integration", "Mastery"]

        results = []
        for d in range(1, total_days + 1):
            pct = (d - 1) / max(1, total_days - 1)   # 0.0 → 1.0
            arc_idx = min(int(pct * 5), 4)            # 0–4
            themes = arc_themes[arc_idx]
            # วนใน theme pool ของช่วงนั้น ทำให้ทุกวัน unique ภายในช่วง
            theme = themes[(d - 1) % len(themes)]
            title = f"{arc_labels[arc_idx]}: {theme}"
            diff = min(5, 1 + (d - 1) // max(1, total_days // 5))
            results.append({
                "day": d,
                "title": title,
                "topics": f"{subj_short} Core, Practice, Application",
                "objectives": f"ผู้เรียนสามารถ Execute งานจริงใน {subj_short} วันที่ {d} ได้ครบ {periods_per_day} คาบ",
                "homework_type": "practice",
                "homework_brief": f"สรุปและประยุกต์ทักษะ {subj_short} จากวันที่ {d} ทั้ง {periods_per_day} คาบ",
                "is_exam_day": (d % 7 == 0) or (d == total_days),
                "difficulty": diff,
                "start_time": "08:30",
                "periods": [],
                "_periods_pending": True,
            })
        return results

    def generate_day_detail(self, subject: str, day: int, day_plan: dict,
                             level: str, style: str, lang: str,
                             learner_profile: dict, teacher: dict,
                             prev_day_summary: str = "") -> dict:
        """
        [v3.0 Phase 2] เติม periods ให้กับ 1 วัน — เรียกแบบ Lazy เมื่อผู้ใช้กำลังจะเรียน
        ส่ง prev_day_summary → รักษา Sequential Continuity ระหว่างวัน
        """
        lang_str = "ภาษาไทย" if lang == "th" else ("English" if lang == "en" else "ไทย+English ผสม")
        hrs_per_day = learner_profile.get("hours_per_day", 2)
        timeslots = self._build_timeslots(hrs_per_day)
        content_slots = [s for s in timeslots if not s["is_break"]]
        periods_per_day = len(content_slots)

        slot_info = chr(10).join(
            f"  ชั่วโมง {i+1}: {s['time_slot']} ({s['type']})"
            for i, s in enumerate(content_slots)
        )

        continuity_note = ""
        if prev_day_summary:
            continuity_note = f"\n[Sequential Context] Day ก่อนหน้าสอน: {prev_day_summary[:300]}\nDay นี้ต้องต่อยอดจากนั้น"

        prompt = f"""คุณคือ {teacher.get("name", "ครู ARIA")} กำลังออกแบบคาบเรียนของ Day {day}
วิชา: "{subject}" | Day {day}: "{day_plan.get("title", "")}"
หัวข้อ: {day_plan.get("topics", "")}
วัตถุประสงค์: {day_plan.get("objectives", "")}
ระดับ: {level} | สไตล์: {style} | ภาษา: {lang_str}{continuity_note}

ตารางเวลา ({periods_per_day} คาบ):
{slot_info}

[กฎการตั้งชื่อคาบ — บังคับ]:
- รูปแบบ: "ชั่วโมง N: [ชื่อหัวข้อ Domain-Specific ของ {subject}]"
- ✅ ถูก: "ชั่วโมง 1: Price Action & Candlestick Anatomy"
- ❌ ผิด: "คาบที่ 1: Case Study 1" หรือ "ชั่วโมง 1: ฝึก {subject}"
- แต่ละคาบต้องไม่ซ้ำกัน และต่อยอดจากคาบก่อนอย่างมีตรรกะ

ตอบ JSON object เดียว (ไม่มี backtick):
{{
  "day": {day},
  "periods": [
    {{
      "period": 1,
      "time_slot": "{content_slots[0]["time_slot"] if content_slots else "08:30 – 09:30"}",
      "name": "ชั่วโมง 1: [ชื่อหัวข้อ]",
      "type": "{content_slots[0]["type"] if content_slots else "ทฤษฎี"}",
      "focus": "จุดโฟกัสหลัก 1 ประโยค",
      "detail": "[Concepts]: ... [Project Linkage]: ... [Actionable Task]: ..."
    }}
  ]
}}
สร้างครบ {periods_per_day} คาบ"""

        raw = self.ai.call(prompt, temperature=0.65, max_tokens=3000)
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            m = re.search(r'\{{[\s\S]*\}}', cleaned)
            if m:
                detail = json.loads(m.group())
                periods = detail.get("periods", [])
                if len(periods) >= 1:
                    # Validate period names ไม่ซ้ำกัน
                    names = [p.get("name", "").lower() for p in periods]
                    if len(set(names)) < len(names):
                        print(f"  [Phase2] ⚠️ Duplicate period names Day {day} — keeping anyway")
                    # อัปเดต day_plan
                    updated = dict(day_plan)
                    updated["periods"] = periods
                    updated["_periods_pending"] = False
                    print(f"  [Phase2] ✅ Day {day} detail: {len(periods)} periods")
                    return updated
        except Exception as e:
            print(f"  [Phase2] ⚠️ Parse error Day {day}: {e}")

        # Fallback periods สำหรับวันนี้
        return self._fill_fallback_periods(day_plan, day, content_slots, subject)

    def _fill_fallback_periods(self, day_plan: dict, day: int,
                                content_slots: list, subject: str) -> dict:
        """Fallback periods — ดึง topics จาก skeleton ก่อน ถ้าไม่มีค่อย fallback generic"""
        subj_short = subject.split("—")[0].split("-")[0].strip()

        # [FIX] ดึง topics จาก skeleton ที่ AI เจน ไว้แล้ว
        raw_topics = day_plan.get("topics", "")
        topic_list = [t.strip() for t in re.split(r"[,，、\n]", raw_topics) if t.strip()]

        type_missions = {
            "ทฤษฎี":              ["หลักการพื้นฐาน", "กรอบแนวคิดหลัก", "Mental Models", "ทฤษฎีเชิงลึก", "Core Framework"],
            "สาธิต":              ["ตัวอย่างจริง", "Case Study", "Step-by-Step Execution", "Expert Walkthrough", "Demo จริง"],
            "ปฏิบัติ":            ["ลงมือสร้าง", "แก้ปัญหาจริง", "Guided Practice", "Error Debugging", "Production Run"],
            "Lab/ปฏิบัติขั้นสูง": ["Advanced Lab", "System Integration", "Performance Testing", "Edge Case Handling", "Full Challenge"],
            "ทบทวน":              ["Cross-Period Synthesis", "Gap Analysis", "Spaced Repetition", "Reflection", "Concept Linking"],
            "สรุปผล":             ["Mastery Verification", "Next-Phase Planning", "Portfolio Summary", "Q&A เชิงลึก", "Achievement Review"],
            "ขั้นสูง":            ["Expert Techniques", "Production Optimization", "Best Practices", "Research-Grade", "Mastery Challenge"],
        }
        periods = []
        for i, s in enumerate(content_slots):
            # ใช้ topic จาก skeleton ถ้ามี มิฉะนั้น fallback generic
            if i < len(topic_list):
                mission = topic_list[i]
            else:
                mission_list = type_missions.get(s["type"], ["Mission"])
                mission = mission_list[i % len(mission_list)]
            periods.append({
                "period": i + 1,
                "time_slot": s["time_slot"],
                "name": f"ชั่วโมง {i+1}: {mission}",
                "type": s["type"],
                "focus": f"[{s['type']}] {mission}",
                "detail": (
                    f"ชั่วโมงที่ {i+1} ({s['type']}): {mission}. "
                    f"{'ต่อยอดจากชั่วโมงที่ '+str(i) if i > 0 else 'จุดเริ่มต้นของวัน'}"
                ),
            })
        updated = dict(day_plan)
        updated["periods"] = periods
        updated["_periods_pending"] = False
        return updated

    # Keep backward-compat: generate_curriculum now calls generate_skeleton
    def generate_curriculum(self, subject: str, total_days: int, level: str,
                             style: str, lang: str, learner_profile: dict,
                             teacher: dict, rag_context: str = "") -> list:
        """[v3.0] Wrapper — calls generate_skeleton (Phase 1 only)"""
        return self.generate_skeleton(
            subject, total_days, level, style, lang,
            learner_profile, teacher, rag_context
        )


    def _generate_curriculum_legacy(self, subject: str, total_days: int, level: str,
                             style: str, lang: str, learner_profile: dict,
                             teacher: dict, rag_context: str = "") -> list:
        """[LEGACY - ไม่ถูกเรียกใช้แล้ว] เก็บไว้เพื่อ reference เท่านั้น"""
        lang_str = "ภาษาไทย" if lang == "th" else ("English" if lang == "en" else "ไทย+English ผสม")
        rag_part = f"\nข้อมูลอ้างอิงเพิ่มเติม (RAG):\n{rag_context[:800]}" if rag_context else ""

        # [v2.9] Time-Based Period calculation
        hrs_per_day  = learner_profile.get('hours_per_day', 2)
        roadmap_mode = learner_profile.get('roadmap_mode', False)
        timeslots    = self._build_timeslots(hrs_per_day)
        content_slots = [s for s in timeslots if not s["is_break"]]
        periods_per_day = len(content_slots)

        # สร้าง slot schema string สำหรับ prompt
        slot_schema = ""
        type_example = {
            "ทฤษฎี":              "แนวคิด X คืออะไร / หลักการ Y",
            "สาธิต":              "ตัวอย่าง Z จริง / Case Study",
            "ปฏิบัติ":            "ลงมือทำ A / สร้าง B",
            "Lab/ปฏิบัติขั้นสูง": "ทดลอง C / แก้ปัญหา D",
            "ทบทวน":              "ทบทวน E / เชื่อมโยง F-G",
            "สรุปผล":             "สรุป H / วางแผน I",
            "ขั้นสูง":            "เจาะลึก J / ประยุกต์ K",
        }
        for i, s in enumerate(content_slots, 1):
            ex = type_example.get(s["type"], "หัวข้อเฉพาะของคาบ")
            slot_schema += f'      {{"period": {i}, "time_slot": "{s["time_slot"]}", "name": "ชั่วโมง {i}: [ชื่อหัวข้อย่อยที่สอนจริงๆ เฉพาะคาบนี้ เช่น {ex}]", "type": "{s["type"]}", "focus": "[จุดโฟกัสหลัก 1 ประโยค สำหรับแสดงบน Dashboard]", "detail": "[อธิบาย 2-3 ประโยค ว่าคาบนี้สอนอะไรโดยเฉพาะ ต่อยอดจากคาบก่อนอย่างไร ห้ามซ้ำชื่อหลักสูตร]"}},\n'
        slot_schema = slot_schema.rstrip(",\n")

        # สร้าง break info
        breaks_info = ""
        for s in timeslots:
            if s["is_break"]:
                breaks_info += f"  - พัก {s['time_slot']} ({s['duration_min']} นาที)\n"

        roadmap_note = ""
        if roadmap_mode:
            roadmap_note = f"""
⚠️ นี่คือ Roadmap ระยะยาว (Phase 1 จาก 3 Phases):
- Phase 1 (Day 1-30): พื้นฐานและ Core Concepts
- Phase 2 (Day 31-60): Intermediate + Projects
- Phase 3 (Day 61-90): Advanced + Mastery
ให้สร้าง Day 1-{total_days} ให้ครบ ห้ามหยุดแค่ 7 วัน"""

        # [v2.9.9] Enrollment System Prompt — ชัดเจนเรื่องชื่อภาษาไทย + ชั่วโมงยืดหยุ่น
        enrollment_system = f"""คุณคือ "Head of Curriculum Design" ประจำ Aria University
ภารกิจ: สร้างหลักสูตรเชิงลึกระดับ "Deep Context Integration" โดยยึดคุณภาพสูงสุดจากมาตรฐาน SKALEX Full Code Edition

[RULES OF EVOLUTION & DIVERSITY]
- ห้ามเจนเนื้อหาแบบ Pattern ซ้ำๆ เดิมๆ ทุกวันต้องมีการยกระดับความยาก (Progressive Complexity)
- [Context-Aware]: คุณต้องวิเคราะห์วิชาที่เรียนและเจาะจงไปยัง Logic จริงๆ ของวิชานั้น ห้ามใช้คำกว้างๆ
- หากเป็นวิชาเกี่ยวกับโปรเจคที่มีโค้ด: ต้องระบุชื่อฟังก์ชัน/บรรทัดที่ต่างกันในแต่ละคาบเรียน

[1. กฎการคำนวณเวลา (Dynamic Time Scaling) — บังคับ]
- ผู้ใช้เลือก {hrs_per_day} ชั่วโมง/วัน → ต้องสร้างพอดี {periods_per_day} คาบ ไม่ขาด ไม่เกิน
- ห้าม hardcode จำนวนคาบ — ต้องใช้จำนวน {periods_per_day} คาบตามที่คำนวณจาก hours_per_day จริง
- เนื้อหาต้องเป็น Sequential Learning: คาบที่ 2 ต้องต่อยอดจากคาบที่ 1 และวันถัดไปต้องยากกว่าวันก่อนหน้า

[2. กฎการตั้งชื่อ Day Title — ห้ามละเมิดโดยเด็ดขาด]
- ชื่อวันต้องสั้น กระชับ มีสาระ สื่อถึงสิ่งที่เรียนจริง
- ถ้าวิชาเป็นภาษาไทย ชื่อวันต้องเป็นภาษาไทยหรือผสมคำเฉพาะทาง เช่น "การออกแบบสีและองค์ประกอบภาพ" หรือ "ธรรมชาติของจิตและสติปัฏฐาน 4"
- ห้ามใช้: "Day X Overview", "Introduction", "Basic" ในชื่อวัน
- ห้ามใส่ชื่อวิชาซ้ำในชื่อวัน เช่น ถ้าวิชาคือ "ธรรมะ" ห้ามชื่อวันเป็น "ธรรมะ — Day 1 Overview"
- ✅ ตัวอย่างที่ถูก: "ไตรลักษณ์และอนิจจัง", "Signal Flow & Audio Routing Architecture", "กลไกเครื่องยนต์สันดาป"
- ❌ ตัวอย่างที่ผิด: "ธรรมะ — Day 1 Overview", "Foundations & Core Taxonomy", "วิชา X — Day X"

[3. กฎการตั้งชื่อคาบ (Period Naming) — ห้ามละเมิดโดยเด็ดขาด]
- ชื่อคาบ (name) ต้องอยู่ในรูปแบบ: "ชั่วโมง N: [ชื่อหัวข้อหลักเฉพาะทาง]"
- ชื่อหัวข้อต้องเป็น Domain-Specific Technical Term ของวิชา "{subject}"
- ✅ ถูก: "ชั่วโมง 1: Price Action & Candlestick Anatomy", "ชั่วโมง 2: สติปัฏฐาน 4 — อิริยาบถบรรพ"
- ❌ ผิด: "คาบที่ 1: Case Study 1", "ชั่วโมง 1: {subject}", "ชั่วโมง 1: ฝึกปฏิบัติ"
- แต่ละคาบในวันเดียวกันห้ามมีชื่อซ้ำกัน

[4. โครงสร้างเนื้อหาต่อ 1 คาบ (Period Structure)]
ต้องมี 3 ส่วนนี้ในทุกชั่วโมงเรียน (ใส่ใน field "detail"):
- [Concepts]: ทฤษฎีที่ต้องใช้ (สั้น ดุดัน เข้าเป้า)
- [Project Linkage]: ระบุชื่อไฟล์, ฟังก์ชัน, หรือ Logic ที่ต้องไปดูจริง (ต้องเปลี่ยนไปตามบทเรียน ห้ามซ้ำ)
- [Actionable Task]: งานที่ต้องลงมือทำจริงใน Environment จริง

[5. คุมโทน (Cyberpunk Protocol)]
- ภาษา 'รุ่นพี่สายเทค' (Professional-Technical Thai)
- "ถ้าพลาดตรงนี้ = ระบบฉิบหาย/เสียเงินจริง" เพื่อให้เห็นความสำคัญ

[6. TOKEN MANAGEMENT]
- ห้ามประหยัด Token! เจนเนื้อหาให้ละเอียดที่สุดเหมือนคนเขียนคู่มือระดับโลก"""

        prompt = f"""คุณคือ {teacher.get('name')} ({teacher.get('title')})
กำลังออกแบบหลักสูตรสอน "{subject}" จำนวน {total_days} วัน
ระดับ: {level} | สไตล์: {style} | ภาษา: {lang_str}
เป้าหมายผู้เรียน: {learner_profile.get('goal','')}
ความรู้พื้นฐาน: {learner_profile.get('prior_knowledge_score',0)}/10
ชั่วโมงต่อวัน: {hrs_per_day} ชม. → {periods_per_day} คาบเนื้อหา/วัน{breaks_info}{rag_part}{roadmap_note}

════════════════════════════════════════════════════
[v2.9.9 NO-GENERIC MISSION-BASED CURRICULUM ENGINE]
════════════════════════════════════════════════════

{enrollment_system}

🎓 หลักการออกแบบหลักสูตร: Sequential Learning (การเรียนรู้เชิงลำดับ)
คุณคือผู้ออกแบบหลักสูตรมหาวิทยาลัยจริง ต้องนึกถึง Syllabus ของสถาบันการศึกษาระดับสูง

⚡ กฎเหล็ก Sequential Learning (ห้ามละเมิดโดยเด็ดขาด):
1. แต่ละคาบใน 1 วัน ต้องมีชื่อหัวข้อ ไม่ซ้ำกันเลย — ห้ามซ้ำแม้แต่คำเดียว
2. ชื่อคาบต้องอยู่ในรูปแบบ "ชั่วโมง N: [ชื่อหัวข้อ Domain-Specific]" — บังคับทุกคาบ
   ✅ ถูก: "ชั่วโมง 1: Price Action & Candlestick Anatomy" → "ชั่วโมง 2: Support/Resistance Zone Mapping"
   ✅ ถูก: "ชั่วโมง 1: ไตรลักษณ์และอนิจจัง" → "ชั่วโมง 2: อริยสัจ 4 — ทุกขสมุทัย"
   ❌ ผิด: "คาบที่ 1: Case Study 1" → "คาบที่ 2: Case Study 2"
   ❌ ผิด: "ชั่วโมง 1: ฝึก {subject}" → "ชั่วโมง 2: ฝึก {subject} ต่อ"
   ❌ ผิด: ชื่อวันเป็น "{subject} — Day 1 Overview" หรือ "Foundations & Core Taxonomy"
3. Day Title ต้องสั้น กระชับ สื่อสาระ (ไม่เกิน 8 คำ) — ดูกฎข้อ [2] ใน enrollment_system
4. คาบที่ N ต้องต่อยอดจากคาบที่ N-1 อย่างมีตรรกะ — ไม่ใช่แค่เปลี่ยนตัวเลข
5. ใช้ Taxonomy ของวิชานั้นๆ เป็นแนวทาง: ดึง Term จากตำราวิชา {subject} มาตั้งชื่อคาบ

ตารางเวลาที่ต้องใช้ต่อวัน (คาบเนื้อหา {periods_per_day} คาบ):
{chr(10).join(f"  ชั่วโมง {i+1}: {s['time_slot']} ({s['type']})" for i, s in enumerate(content_slots))}

สร้าง curriculum {total_days} วัน ตอบเป็น JSON array เท่านั้น — ห้ามมี text นอก JSON:
[
  {{
    "day": 1,
    "title": "ชื่อบทเรียนรวมวันนี้ — กระชับ มีสาระ ไม่เกิน 8 คำ เช่น 'ไตรลักษณ์และอนิจจัง' หรือ 'Signal Flow & Audio Routing Architecture'",
    "topics": "หัวข้อย่อย Technical (comma separated) — ใช้คำศัพท์เฉพาะทาง ไม่ใช่คำทั่วไป",
    "objectives": "สิ่งที่ผู้เรียนจะทำได้หลังเรียน (เขียนเป็น Measurable Outcome)",
    "homework_type": "practice|reflection|project|quiz",
    "homework_brief": "โจทย์รวมศูนย์: สรุปเนื้อหาจากทุกคาบวันนี้ ({periods_per_day} คาบ) มาสร้างโจทย์ชุดเดียวที่ครอบคลุมทั้งทฤษฎีและปฏิบัติ",
    "is_exam_day": false,
    "difficulty": 1,
    "start_time": "08:30",
    "periods": [
{slot_schema}
    ]
  }}
]

[v2.9.9 กฎการสร้าง periods — บังคับใช้ทุกวัน]:
1. ทุกวันต้องมีพอดี {periods_per_day} periods ตาม time_slot ที่กำหนด — ห้ามสร้างน้อยหรือมากกว่านี้
2. ชื่อคาบ (name) ต้องอยู่ในรูปแบบ "ชั่วโมง N: [Technical Term เฉพาะของ {subject}]"
   ✅ format: "ชั่วโมง N: [ชื่อหัวข้อ Domain-Specific ของ {subject}]"
   ❌ ห้าม: "คาบที่ 1: {subject}" / "Case Study 1" / "ฝึก 1" / "Exercise 1" / ชื่อซ้ำจากคาบอื่น
3. type ต้องเป็น: ทฤษฎี / สาธิต / ปฏิบัติ / Lab/ปฏิบัติขั้นสูง / ทบทวน / สรุปผล / ขั้นสูง
4. detail = อธิบาย 2-3 ประโยคว่าคาบนี้สอน/ทำอะไร ใช้ Technical Language และระบุว่าต่อยอดจากคาบก่อนอย่างไร
5. focus = จุดโฟกัสหลัก 1 ประโยค ใช้ Technical Term — แสดงบน Dashboard ให้ผู้เรียนรู้ทันทีว่าคาบนี้สอนอะไร
6. homework_brief ต้องอ้างถึงทุกคาบของวันนั้น
7. ต้องสร้างครบ {total_days} วัน — ห้ามสร้างแค่บางวัน
8. ชั่วโมงที่ N+1 ต้องต่อยอดจากชั่วโมงที่ N อย่างมีตรรกะ (Sequential Continuity)
9. ห้ามมีชื่อคาบซ้ำกันในวันเดียวกัน — ถ้าคาบซ้ำกันเกิน 50% ระบบจะ regenerate วันนั้นใหม่"""
        raw = self.ai.call(prompt, temperature=0.6, max_tokens=4000)
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            m = re.search(r'\[[\s\S]*\]', cleaned)
            if m:
                curriculum = json.loads(m.group())
                # [v2.9.5] Duplicate period name detection & regeneration
                curriculum = self._validate_and_fix_periods(curriculum, subject, teacher, lang_str, level, style, hrs_per_day, periods_per_day, content_slots, slot_schema, rag_part, roadmap_note, learner_profile)
                return curriculum
        except Exception:
            pass
        # fallback — v2.9 with timeslots
        fallback_slots = self._build_timeslots(learner_profile.get('hours_per_day', 2))
        fallback_content = [s for s in fallback_slots if not s["is_break"]]
        # [v2.9.9] fallback period name templates — Mission-Based, Domain-Specific, ใช้ ชั่วโมง N format
        fallback_period_missions = {
            "ทฤษฎี": [
                "หลักการพื้นฐานและกรอบแนวคิดหลัก",
                "กลไกและตรรกะเชิงลึก",
                "โครงสร้างและการวิเคราะห์เชิงระบบ",
                "Mental Models และการประยุกต์ใช้",
                "Conceptual Mastery & Core Framework",
            ],
            "สาธิต": [
                "ตัวอย่างจริง — การประยุกต์ใช้งาน",
                "Case Dissection: รูปแบบความสำเร็จ vs ความล้มเหลว",
                "Step-by-Step Execution Walkthrough",
                "การวิเคราะห์เปรียบเทียบเครื่องมือและแนวทาง",
                "Expert Workflow Deconstruction",
            ],
            "ปฏิบัติ": [
                "ลงมือสร้าง — Core Skill Execution",
                "แก้ปัญหาภายใต้ข้อจำกัดจริง",
                "Guided Practice: ความแม่นยำและความเร็ว",
                "Error Detection & Debugging Workflow",
                "Production-Ready Implementation",
            ],
            "Lab/ปฏิบัติขั้นสูง": [
                "Advanced Lab: System Integration Testing",
                "Complex Problem Decomposition & Solution",
                "Performance Optimization & Benchmarking",
                "Edge Case Handling & Robustness Testing",
                "Full-Stack Challenge: End-to-End Execution",
            ],
            "ทบทวน": [
                "สรุปความรู้และวิเคราะห์ช่องว่าง",
                "เชื่อมโยงทุกคาบ — Cross-Period Synthesis",
                "Spaced Repetition: ทบทวนจุดสำคัญ",
                "แก้ความเข้าใจผิดและชี้แจง",
                "Self-Assessment & Reflection",
            ],
            "สรุปผล": [
                "ทบทวนผลลัพธ์ — สิ่งที่ทำได้แล้ว",
                "แผนการต่อยอด — Next-Phase Roadmap",
                "Q&A เชิงลึก: ปัญหาที่ยังค้างคาใจ",
                "Portfolio-Ready Deliverable Summary",
                "ตรวจสอบความเชี่ยวชาญ — Mastery Verification",
            ],
            "ขั้นสูง": [
                "เทคนิคระดับผู้เชี่ยวชาญและกลยุทธ์ขั้นสูง",
                "Production Optimization & Scalability",
                "Industry-Standard Best Practices",
                "Research-Grade Problem Solving",
                "Mastery-Level Integration Challenge",
            ],
        }
        # [v2.9.9] Day title arc — ภาษาไทย กระชับ ไม่ติด "Foundations & Core Taxonomy"
        day_title_arc = [
            "รากฐานและโครงสร้างหลัก",
            "กลไกและหลักการทำงาน",
            "เครื่องมือ การติดตั้ง และการ Execute ครั้งแรก",
            "Pattern Recognition & Analysis",
            "ลงมือสร้าง: จากศูนย์สู่ Output จริง",
            "Debugging, Optimization & Quality Control",
            "Integration: เชื่อมทุกองค์ประกอบเข้าด้วยกัน",
            "Real-World Workflow Simulation",
            "Edge Cases, Scaling & Robustness",
            "Capstone: Full Production Challenge",
        ]
        return [
            {
                "day": d,
                # [v2.9.9] Day title กระชับ ไม่ติด subject prefix
                "title": f"{day_title_arc[(d-1) % len(day_title_arc)]}",
                "topics": f"{subject} Core Concepts, Hands-On Practice, Sequential Application",
                "objectives": f"ผู้เรียนสามารถ Execute งานจริงในทุกชั่วโมงของวันที่ {d} ได้ครบ {len(fallback_content)} ชั่วโมง",
                "homework_type": "practice",
                "homework_brief": f"สร้างผลงานที่รวมทักษะจากทุก {len(fallback_content)} ชั่วโมงของวันที่ {d} — ต้องครอบคลุมทั้งทฤษฎีและ Execution จริง",
                "is_exam_day": d % 7 == 0 or d == total_days,
                "difficulty": min(5, 1 + (d - 1) // max(1, total_days // 5)),
                "start_time": "08:30",
                "periods": [
                    {
                        "period": i+1,
                        "time_slot": s["time_slot"],
                        # [v2.9.9] ชั่วโมง N format — sequential unique missions
                        "name": f"ชั่วโมง {i+1}: {(fallback_period_missions.get(s['type'], ['Mission '+str(i+1)]))[i % len(fallback_period_missions.get(s['type'], ['Mission '+str(i+1)]))]}",
                        "type": s["type"],
                        "focus": f"[{s['type']}] {(fallback_period_missions.get(s['type'], ['Mission '+str(i+1)]))[i % len(fallback_period_missions.get(s['type'], ['Mission '+str(i+1)]))]}",
                        "detail": (
                            f"ชั่วโมงที่ {i+1} ({s['type']}): เจาะลึก{subject}ในมิติ '{(fallback_period_missions.get(s['type'], ['Mission']))[i % max(1, len(fallback_period_missions.get(s['type'], ['Mission'])))]}'  "
                            f"{'— ต่อยอดจากชั่วโมงที่ '+str(i)+' สู่ระดับถัดไป' if i > 0 else '— จุดเริ่มต้นที่สำคัญที่สุดของวัน'}"
                        ),
                    }
                    for i, s in enumerate(fallback_content)
                ],
            }
            for d in range(1, total_days + 1)
        ]

    def _check_period_duplicates(self, day_plan: dict) -> float:
        """คืน % ของชื่อคาบที่ซ้ำกันในวันนั้น (0.0 – 1.0)"""
        periods = day_plan.get("periods", [])
        if len(periods) <= 1:
            return 0.0
        names = [p.get("name", "").strip().lower() for p in periods]
        unique_names = set(names)
        # นับคาบที่ซ้ำ = จำนวนทั้งหมด - unique
        duplicate_count = len(names) - len(unique_names)
        return duplicate_count / len(names)

    def _validate_and_fix_periods(self, curriculum: list, subject: str, teacher: dict,
                                   lang_str: str, level: str, style: str, hrs_per_day: float,
                                   periods_per_day: int, content_slots: list, slot_schema: str,
                                   rag_part: str, roadmap_note: str, learner_profile: dict) -> list:
        """[v2.9.5] ตรวจสอบและ regenerate วันที่มีชื่อคาบซ้ำเกิน 50%"""
        fixed = []
        for day_plan in curriculum:
            dup_ratio = self._check_period_duplicates(day_plan)
            if dup_ratio > 0.5:
                day_num = day_plan.get("day", 0)
                day_title = day_plan.get("title", f"Day {day_num}")
                print(c(C.WARN, f"  ⚠️ [v2.9.5] Day {day_num} มีชื่อคาบซ้ำ {dup_ratio:.0%} — กำลัง regenerate..."))
                regen_prompt = f"""คุณคือ {teacher.get('name')} ออกแบบ {periods_per_day} ชั่วโมงเรียนสำหรับ Day {day_num}
วิชา: {subject} | บทเรียน: {day_title}
ภาษา: {lang_str} | ระดับ: {level} | สไตล์: {style}

[v2.9.9 CRITICAL] ชื่อแต่ละชั่วโมงต้องไม่ซ้ำกันเลย ต้องใช้ Domain-Specific Technical Term ของวิชา {subject}
รูปแบบบังคับ: "ชั่วโมง N: [ชื่อหัวข้อ Domain-Specific เฉพาะทาง]"
- ห้ามใช้ "Case Study 1", "Case Study 2" หรือชื่อซ้ำกัน
- ต้องใช้ Term จากตำราวิชา {subject} จริงๆ
- ชั่วโมงที่ N+1 ต้องต่อยอดจากชั่วโมงที่ N ตาม Sequential Learning

ตาราง:
{chr(10).join(f"  ชั่วโมง {i+1}: {s['time_slot']} ({s['type']})" for i, s in enumerate(content_slots))}

ตอบเป็น JSON object เท่านั้น (1 วัน) — ห้ามมี text นอก JSON:
{{
  "day": {day_num},
  "title": "{day_title}",
  "topics": "Technical terms comma-separated",
  "objectives": "{day_plan.get('objectives', '')}",
  "homework_type": "{day_plan.get('homework_type', 'practice')}",
  "homework_brief": "{day_plan.get('homework_brief', '')}",
  "is_exam_day": {str(day_plan.get('is_exam_day', False)).lower()},
  "difficulty": {day_plan.get('difficulty', 1)},
  "start_time": "08:30",
  "periods": [
{slot_schema}
  ]
}}"""
                try:
                    raw2 = self.ai.call(regen_prompt, temperature=0.7, max_tokens=2000)
                    cleaned2 = re.sub(r"```(?:json)?|```", "", raw2).strip()
                    obj = re.search(r'\{{[\s\S]*\}}', cleaned2)
                    if obj:
                        new_plan = json.loads(obj.group())
                        new_dup = self._check_period_duplicates(new_plan)
                        if new_dup <= 0.5:
                            print(c(C.ACID, f"  ✅ Day {day_num} regenerated — dup ratio: {new_dup:.0%}"))
                            fixed.append(new_plan)
                            continue
                except Exception as e:
                    print(c(C.ERR, f"  ❌ Regen failed Day {day_num}: {e}"))
            fixed.append(day_plan)
        return fixed

    def assess_knowledge(self, subject: str, answers: dict) -> dict:
        raw_score = 0
        try:
            raw_score = int(re.search(r'\d+', str(answers.get("prior", "0"))).group())
        except Exception:
            pass
        timeline_raw = str(answers.get("timeline", "7 วัน วันละ 2 ชั่วโมง"))

        # [FEAT-1a v2.5] รองรับ 'ตลอดชีวิต' / 'lifetime' → roadmap 90 วัน
        roadmap_mode = False
        lifetime_keywords = ["ตลอดชีวิต", "ไม่มีกำหนด", "lifetime", "forever", "long term", "ระยะยาว"]
        if any(kw in timeline_raw.lower() for kw in lifetime_keywords):
            roadmap_mode = True
            total_days  = 90          # Phase 1 (30 วัน) + ขยายได้เรื่อยๆ
            hrs_per_day = 1.0
            phase_size  = 30          # แบ่งเป็น phase ละ 30 วัน
        else:
            days_match = re.search(r'(\d+)\s*วัน', timeline_raw)
            hrs_match  = re.search(r'(\d+(?:\.\d+)?)\s*(?:ชั่วโมง|ชม|hr)', timeline_raw)
            total_days  = int(days_match.group(1)) if days_match else 7
            hrs_per_day = float(hrs_match.group(1)) if hrs_match else 2.0
            total_days  = max(1, min(365, total_days))
            hrs_per_day = max(0.5, min(12.0, hrs_per_day))
            phase_size  = 0
        style_raw = str(answers.get("style", "ผสม")).lower()
        if any(x in style_raw for x in ["a", "practice", "ลงมือ"]):
            style = "practical"
        elif any(x in style_raw for x in ["b", "theory", "ทฤษฎี"]):
            style = "theoretical"
        else:
            style = "mixed"
        if raw_score <= 2:    level = "beginner"
        elif raw_score <= 5:  level = "intermediate"
        else:                 level = "advanced"
        lang_raw = str(answers.get("lang", "ไทย")).lower()
        if ("c" in lang_raw) or ("english" in lang_raw and "ไทย" in lang_raw):
            lang = "th_en"
        elif "b" in lang_raw or "english" in lang_raw or "eng" in lang_raw:
            lang = "en"
        else:
            lang = "th"
        return {
            "goal"                 : str(answers.get("goal", "")),
            "prior_knowledge_score": raw_score,
            "experience"           : str(answers.get("experience", "")),
            "total_days"           : total_days,
            "hours_per_day"        : hrs_per_day,
            "style"                : style,
            "level"                : level,
            "lang"                 : lang,
            "name"                 : str(answers.get("name", "นักเรียน")),
            # [FEAT-1a v2.5] Roadmap fields
            "roadmap_mode"         : roadmap_mode,
            "phase_size"           : phase_size,
            "current_phase"        : 1,
        }

# ═══════════════════════════════════════════════════════════════════
# LESSON ENGINE — v1.0 + v2.0 RAG injection
# ═══════════════════════════════════════════════════════════════════
class LessonEngine:
    def __init__(self, ai: AIClient, course: Course):
        self.ai     = ai
        self.course = course

    def _teacher_system(self, extra: str = "") -> str:
        t    = self.course.teacher_persona
        lp   = self.course.learner_profile
        prog = self.course.get_summary()
        lang_map = {"th": "ภาษาไทย", "en": "English", "th_en": "ไทย+English ผสม"}
        lang = lang_map.get(self.course.lang, "ภาษาไทย")
        rag_part = f"\n=== ข้อมูลอ้างอิง RAG ===\n{self.course.rag_context[:600]}" if self.course.rag_context else ""
        return f"""คุณคือ {t.get('name', 'ครู ARIA')} ({t.get('title', '')})
บุคลิก: {t.get('personality', 'เป็นกันเอง')}
สไตล์การสอน: {t.get('teaching_style', '')}
น้ำเสียง: {t.get('tone', 'ครู')}
ประโยคเด็ด: "{t.get('catchphrase', '')}"

=== หลักสูตร ===
วิชา: {self.course.subject} | ระดับ: {self.course.level} | ภาษา: {lang}
=== ผู้เรียน ===
ชื่อ: {lp.get('name', 'นักเรียน')} | เป้าหมาย: {lp.get('goal', '')}
ความรู้พื้นฐาน: {lp.get('prior_knowledge_score', 0)}/10
=== ความคืบหน้า ===
เรียนมา {prog['days_done']}/{prog['total_days']} วัน | คะแนน: {prog['total_score']} | EXP: {prog['exp']}
{rag_part}
[สำคัญ] รักษา persona และน้ำเสียงนี้ตลอด ตอบใน{lang}{extra}"""

    def get_lesson(self, day: int, force_regen: bool = False) -> str:
        key = f"lesson_{day}"
        if not force_regen and self.course.get_cache(key):
            self.course.progress["last_lesson_day"] = day
            self.course.save()
            return self.course.get_cache(key)
        plan = self._get_day_plan(day)
        prompt = f"""สอนบทเรียน Day {day}: "{plan['title']}"
หัวข้อ: {plan['topics']}
วัตถุประสงค์: {plan['objectives']}

สอนด้วยโครงสร้าง (ไม่เกิน 600 คำ):
🎯 วันนี้เรียนรู้อะไร
📚 เนื้อหาหลัก พร้อมตัวอย่างจริง
🔍 จุดสำคัญที่ต้องจำ
[สำคัญ] ห้ามใส่คำถาม Quiz หรือ Quick Check ท้ายบทเรียน — ผู้เรียนมีแบบฝึกหัดแยกต่างหากแล้ว

📎 แหล่งศึกษาเพิ่มเติม (ท้ายบทเรียนเสมอ):
แนะนำ 2-3 แหล่งอ้างอิงที่มีอยู่จริง เช่น ชื่อหนังสือ, ชื่อ course ดัง, ชื่อเว็บไซต์ทางการ หรือชื่อ documentation
รูปแบบ:
📚 [ชื่อแหล่ง]: [อธิบาย 1 ประโยคว่าเรียนรู้อะไรได้จากที่นี่]
ห้ามสร้าง URL หรือลิงก์ — ระบุเฉพาะชื่อแหล่งที่มีชื่อเสียงและค้นหาได้ง่ายเท่านั้น"""
        content = self.ai.call(prompt, system=self._teacher_system(), max_tokens=2500)
        if not content.startswith("❌"):
            self.course.set_cache(key, content)
            self.course.progress["last_lesson_day"] = day
            self.course.mark_day_complete(day)
            # v2.0: Award EXP
            GamificationEngine.award_exp(self.course, "lesson_read")
            GamificationEngine.check_badges(self.course)
        return content

    def get_homework(self, day: int, force_regen: bool = False) -> str:
        key = f"homework_{day}"
        if not force_regen and self.course.get_cache(key):
            return self.course.get_cache(key)

        # [v2.9.6] Activity Gate — ต้องเรียนครบทุก Period ก่อน
        gate = check_activity_gate(self.course, day, "homework")
        if not gate["enabled"]:
            return (
                f"🔒 **การบ้าน Day {day} ยังไม่พร้อม**\n\n"
                f"{gate['reason']}\n\n"
                f"**คาบที่ยังไม่ได้เรียน:**\n"
                + "\n".join(f"• {p}" for p in gate.get("unread_periods", []))
                + "\n\n_(เรียนให้ครบทุกคาบก่อน จึงจะปลดล็อกการบ้านได้)_"
            )

        # [v2.9.6] Comprehensive Synthesis Homework
        content = generate_comprehensive_homework(self.ai, self.course, day)
        if not content.startswith("❌"):
            self.course.set_cache(key, content)
        return content

    def get_quiz(self, day: int) -> str:
        key = f"quiz_{day}"
        if self.course.get_cache(key):
            return self.course.get_cache(key)
        plan = self._get_day_plan(day)
        prompt = f"""สร้าง Quiz Day {day}: "{plan['title']}"
5 ข้อ multiple choice (A/B/C/D) พร้อมเฉลย
ระดับ: {plan.get('difficulty', 2)}/5 | หัวข้อ: {plan['topics']}"""
        content = self.ai.call(prompt, system=self._teacher_system(), max_tokens=2000)
        if not content.startswith("❌"):
            self.course.set_cache(key, content)
            GamificationEngine.award_exp(self.course, "quiz")
        return content

    def get_quiz_structured(self, day: int, period: int = 0, force_regen: bool = False) -> dict:
        """สร้าง Quiz แบบ structured JSON สำหรับ interactive UI — รองรับทั้ง quiz รายวัน และรายคาบ
        [v2.9.6] เพิ่ม Activity Gate + Exercise Speed-Run Timer"""

        # [v2.9.6] Activity Gate — period ต้องถูก mark_as_read ก่อน
        # [v3.0]  หรือถ้าผ่าน quiz ของคาบก่อนหน้าแล้ว ก็ปลดล็อกได้เช่นกัน
        if period > 0:
            periods_read = self.course.progress.get("periods_read", {}).get(str(day), [])
            prev_period_passed = (period == 1) or \
                self.course.progress.get("quiz_results", {}).get(f"{day}_{period-1}", {}).get("passed", False)
            if period not in periods_read and not prev_period_passed:
                return {
                    "title": f"แบบฝึกหัด Day {day} คาบ {period}",
                    "day": day, "period": period, "topic": "",
                    "questions": [], "passing_score": 3,
                    "locked": True,
                    "error": f"🔒 ต้องเรียนคาบที่ {period} ให้จบก่อน หรือผ่านแบบฝึกหัดคาบก่อนหน้า",
                }

        # [v2.9.6] ตรวจ timer — ถ้า expired ให้ force_regen
        timer_status = check_quiz_timer(self.course, day, period)
        if timer_status.get("expired"):
            force_regen = True  # Auto-regenerate เพื่อป้องกันการจำคำตอบ

        cache_key = f"quiz_struct_{day}_{period}"
        if not force_regen:
            cached = self.course.get_cache(cache_key)
            if cached:
                try:
                    return json.loads(cached)
                except Exception:
                    pass
        plan = self._get_day_plan(day)
        # ถ้าเลือก period ให้ใช้เนื้อหาเฉพาะคาบ
        period_context = ""
        period_title = plan.get("title", f"Day {day}")
        if period > 0:
            periods = plan.get("periods", [])
            if 0 < period <= len(periods):
                p = periods[period - 1]
                period_title = p.get("name", f"คาบที่ {period}")
                period_context = f"\nเฉพาะคาบ: {period_title}\nรายละเอียดคาบ: {p.get('detail', '')}"
        lesson_cached = self.course.get_cache(f"lesson_{day}") or ""
        lesson_snippet = lesson_cached[:600] if lesson_cached else ""
        prompt = f"""คุณคือครูสร้างแบบฝึกหัดระหว่างเรียน (In-class Exercise) Day {day}: "{period_title}"
หัวข้อ: {plan.get('topics', '')}
วัตถุประสงค์: {plan.get('objectives', '')}
ระดับความยาก: {plan.get('difficulty', 2)}/5{period_context}
{'เนื้อหาบทเรียน (อ้างอิง): ' + lesson_snippet if lesson_snippet else ''}

สร้างแบบฝึกหัด 5 ข้อ multiple choice (A/B/C/D) เหมาะสำหรับระหว่างเรียน
ตอบเป็น JSON เท่านั้น ห้ามมี text นอก JSON ห้ามมี backtick:
{{
  "title": "ชื่อแบบฝึกหัด",
  "day": {day},
  "period": {period},
  "topic": "หัวข้อ",
  "questions": [
    {{
      "no": 1,
      "question": "คำถาม",
      "choices": {{"A": "ตัวเลือก A", "B": "ตัวเลือก B", "C": "ตัวเลือก C", "D": "ตัวเลือก D"}},
      "answer": "A",
      "explanation": "อธิบายเฉลย 1-2 ประโยค"
    }}
  ],
  "passing_score": 3
}}"""
        raw = self.ai.call(prompt, system=self._teacher_system(), max_tokens=2500, temperature=0.6)
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            m = re.search(r'\{[\s\S]*\}', cleaned)
            if m:
                data = json.loads(m.group())
                self.course.set_cache(cache_key, json.dumps(data, ensure_ascii=False))
                GamificationEngine.award_exp(self.course, "quiz")
                return data
        except Exception as e:
            print(f"[quiz_structured parse error] {e}")
        # fallback
        return {
            "title": f"แบบฝึกหัด Day {day}",
            "day": day, "period": period, "topic": plan.get("topics", ""),
            "questions": [], "passing_score": 3,
            "error": "ไม่สามารถสร้างแบบฝึกหัดได้ กรุณาลองใหม่"
        }

    def get_period_lesson(self, day: int, period: int) -> str:
        """สอนเนื้อหาเฉพาะคาบ (sub-lesson) — ใช้ period index (1-based)"""
        cache_key = f"period_{day}_{period}"
        cached = self.course.get_cache(cache_key)
        if cached:
            return cached
        plan = self._get_day_plan(day)
        periods = plan.get("periods", [])
        if not (0 < period <= len(periods)):
            return f"❌ ไม่พบคาบที่ {period} ใน Day {day}"
        p = periods[period - 1]
        prompt = f"""สอนบทเรียนย่อย: {p.get('name', f'คาบที่ {period}')}
วิชา: {self.course.subject} | Day {day}: {plan.get('title', '')}
ประเภทคาบ: {p.get('type', '')}
จุดโฟกัสหลัก: {p.get('focus', '')}
รายละเอียด: {p.get('detail', '')}
เวลา: {p.get('time_slot', '')}

[v2.9.4 Sequential Learning Context]
นี่คือคาบที่ {period} จากทั้งหมด {len(plan.get('periods', []))} คาบในวันนี้
{f"คาบที่ {period-1} ก่อนหน้าสอนเรื่อง: {plan.get('periods', [])[period-2].get('name','')}" if period > 1 and len(plan.get('periods', [])) >= period-1 else "นี่คือคาบแรกของวัน — เริ่มต้นจากพื้นฐาน"}
เนื้อหาคาบนี้ต้องต่อยอดจากคาบก่อนหน้าอย่างเป็นลำดับ ห้ามซ้ำเนื้อหาเดิม

สอนด้วยโครงสร้าง (ไม่เกิน 500 คำ):
🎯 จุดประสงค์ของคาบนี้ (และเชื่อมกับคาบก่อนอย่างไร)
📚 เนื้อหาหลัก พร้อมตัวอย่างที่ชัดเจน
🔍 สิ่งสำคัญที่ต้องจำจากคาบนี้
[สำคัญ] ห้ามใส่คำถาม Quiz หรือ Quick Check ท้ายบทเรียน — ผู้เรียนมีแบบฝึกหัดแยกต่างหากแล้ว

📎 แหล่งศึกษาเพิ่มเติม (สำหรับคาบนี้เท่านั้น):
แนะนำ 1-2 แหล่งที่เกี่ยวข้องกับเนื้อหาคาบนี้โดยตรง
รูปแบบ: 📚 [ชื่อแหล่ง]: [อธิบายสั้นๆ]
ระบุเฉพาะชื่อแหล่งที่มีชื่อเสียง ค้นหาได้ง่าย — ห้ามสร้าง URL"""
        content = self.ai.call(prompt, system=self._teacher_system(), max_tokens=2000)
        if not content.startswith("❌"):
            self.course.set_cache(cache_key, content)
        return content

    def _get_day_plan(self, day: int) -> dict:
        for plan in self.course.curriculum:
            if plan.get("day") == day:
                return plan
        return {"day": day, "title": f"Day {day}", "topics": "",
                "objectives": "", "homework_type": "practice",
                "homework_brief": "", "is_exam_day": False, "difficulty": 2}

# ═══════════════════════════════════════════════════════════════════
# HOMEWORK ENGINE — v1.0 + v2.0 EXP rewards
# ═══════════════════════════════════════════════════════════════════
class HomeworkEngine:
    def __init__(self, ai: AIClient, course: Course):
        self.ai     = ai
        self.course = course

    def _teacher_system(self) -> str:
        t = self.course.teacher_persona
        lang_map = {"th": "ภาษาไทย", "en": "English", "th_en": "ไทย+English ผสม"}
        return f"""คุณคือ {t.get('name', 'ครู ARIA')} กำลังตรวจงานนักเรียน
บุคลิก: {t.get('personality', 'เป็นกันเอง')} | น้ำเสียง: {t.get('tone', 'ครู')}
ภาษา: {lang_map.get(self.course.lang, 'ภาษาไทย')}
[สำคัญ] รักษา persona เดิม ตรวจด้วยความเป็นกันเองและให้กำลังใจ"""

    def _get_day_context(self, day: int) -> str:
        lesson    = self.course.get_cache(f"lesson_{day}") or ""
        hw_prompt = self.course.get_cache(f"homework_{day}") or ""
        plan = next((p for p in self.course.curriculum if p.get("day") == day), {})
        parts = [f"=== บริบทวันที่ {day}: {plan.get('title', '')} ===",
                 f"หัวข้อ: {plan.get('topics', '')}",
                 f"วัตถุประสงค์: {plan.get('objectives', '')}"]
        if lesson:
            parts.append(f"\n--- เนื้อหาที่สอน ---\n{lesson[:600]}")
        if hw_prompt:
            parts.append(f"\n--- โจทย์การบ้าน ---\n{hw_prompt[:500]}")
        return "\n".join(parts)

    def grade_text(self, day: int, hw_type: str, content: str, custom_note: str = "") -> str:
        day_context = self._get_day_context(day)
        custom_str = f"\nหมายเหตุจากผู้เรียน: {custom_note}" if custom_note else ""
        prompt = f"""{day_context}

ประเภทงาน: {hw_type}{custom_str}
งานที่ส่งมา:
{content}

[สำคัญ] ตรวจเปรียบกับโจทย์วันที่ {day} ข้างต้น
ตอบด้วยรูปแบบ:
✅ สิ่งที่ทำได้ดี
❌ สิ่งที่ต้องปรับ
🔍 ความสอดคล้องกับโจทย์
💡 คำแนะนำเพิ่มเติม
⭐ คะแนน: X/20 (อธิบายเหตุผล)"""
        feedback = self.ai.call(prompt, system=self._teacher_system(), max_tokens=2000)
        self._save_and_exp(day, feedback)
        return feedback

    def grade_file_text(self, day: int, hw_type: str, file_content: str, custom_note: str = "") -> str:
        return self.grade_text(day, hw_type, file_content, custom_note)

    def _save_and_exp(self, day: int, feedback: str):
        m = re.search(r"(\d+)\s*/\s*20", feedback)
        score = int(m.group(1)) if m else 0
        if score > 0:
            self.course.record_homework(day, score, feedback)
            # v2.0: EXP rewards
            bonus = max(0, score - 15)  # bonus EXP for high scores
            GamificationEngine.award_exp(self.course, "hw_submit", bonus)
            if score >= 20:
                GamificationEngine.unlock_badge(self.course, "perfect_hw")
            GamificationEngine.check_badges(self.course)

# ═══════════════════════════════════════════════════════════════════
# CHAT ENGINE — v1.0 + v2.0 persistent history
# ═══════════════════════════════════════════════════════════════════
class ChatEngine:
    def __init__(self, ai: AIClient, course: Course):
        self.ai     = ai
        self.course = course

    def _system(self, current_day: int) -> str:
        t    = self.course.teacher_persona
        lp   = self.course.learner_profile
        prog = self.course.get_summary()
        lang_map = {"th": "ภาษาไทย", "en": "English", "th_en": "ไทย+English ผสม"}
        lang = lang_map.get(self.course.lang, "ภาษาไทย")
        last_lesson = ""
        last_day = self.course.progress.get("last_lesson_day")
        if last_day:
            cached = self.course.get_cache(f"lesson_{last_day}")
            if cached: last_lesson = f"\nบทเรียนล่าสุด (Day {last_day}):\n{cached[:400]}"
        rag_part = f"\n[RAG Context]\n{self.course.rag_context[:400]}" if self.course.rag_context else ""

        # [FEAT-3 v2.5] Full Context Awareness — homework history + low scores
        hw_context = ""
        hw_scores = self.course.progress.get("homework_scores", {})
        if hw_scores:
            low_days  = [k for k, v in hw_scores.items() if v < 15]
            good_days = [k for k, v in hw_scores.items() if v >= 18]
            hw_summary = f"คะแนนการบ้าน: {dict(list(hw_scores.items())[-5:])}"
            if low_days:
                hw_summary += f" | วันที่ยังทำได้ไม่ดี: {', '.join(low_days)}"
            if good_days:
                hw_summary += f" | วันที่ทำได้ดีมาก: {', '.join(good_days)}"
            hw_context = f"\n[การบ้าน] {hw_summary}"

        # context ของบทเรียนที่เรียนแล้ว
        days_done = self.course.progress.get("days_completed", [])
        completed_titles = []
        for d in days_done[-5:]:  # 5 วันล่าสุด
            plan = next((p for p in self.course.curriculum if p.get("day") == d), {})
            if plan.get("title"):
                completed_titles.append(f"Day {d}: {plan['title']}")
        done_context = ""
        if completed_titles:
            done_context = f"\n[เรียนมาแล้ว (5 วันล่าสุด)] {' | '.join(completed_titles)}"

        roadmap_context = ""
        if self.course.roadmap_mode:
            phase = self.course.current_phase
            phase_size = self.course.phase_size or 30
            phase_end = phase * phase_size
            roadmap_context = f"\n[Roadmap] Phase {phase} | เป้าหมาย Day {phase_end}"

        # [v2.9] Time-Slot awareness — รู้ตารางเรียนของวันปัจจุบัน
        timeslot_context = ""
        day_plan = next((p for p in self.course.curriculum if p.get("day") == current_day), {})
        periods  = day_plan.get("periods", [])
        if periods:
            now_time = datetime.now().strftime("%H:%M")
            # หา current period โดยเปรียบ now_time กับ time_slot
            current_period_name = None
            for p in periods:
                ts = p.get("time_slot", "")
                # parse "HH:MM – HH:MM"
                parts = ts.replace("–", "-").replace("—", "-").split("-")
                if len(parts) == 2:
                    try:
                        s_h, s_m = map(int, parts[0].strip().split(":"))
                        e_h, e_m = map(int, parts[1].strip().split(":"))
                        n_h, n_m = map(int, now_time.split(":"))
                        s_total = s_h * 60 + s_m
                        e_total = e_h * 60 + e_m
                        n_total = n_h * 60 + n_m
                        if s_total <= n_total < e_total:
                            current_period_name = p.get("name", "")
                    except Exception:
                        pass
            schedule_lines = "\n".join(
                f"  {p.get('time_slot','')}: {p.get('name','')} [{p.get('type','')}]"
                for p in periods
            )
            timeslot_context = f"\n[ตารางเวลาวันนี้ Day {current_day}]\n{schedule_lines}"
            if current_period_name:
                timeslot_context += f"\n[ขณะนี้ {now_time} น.] อยู่ในคาบ: {current_period_name}"

        # [v2.9.6] Context Shield — สถานะการเรียนปัจจุบัน
        prog_status = self.course.get_summary()
        periods_read = self.course.progress.get("periods_read", {}).get(str(current_day), [])
        plan = next((p for p in self.course.curriculum if p.get("day") == current_day), {})
        total_periods = len(plan.get("periods", []))
        hw_submitted = f"day_{current_day}" in self.course.progress.get("homework_submissions", {})
        hw_deadline = check_homework_deadline(self.course, current_day)

        context_shield = f"""
[v2.9.6 CONTEXT SHIELD — ข้อมูลสถานะปัจจุบัน]
Current Day: {current_day}/{prog['total_days']}
คาบที่เรียนแล้ว: {len(periods_read)}/{total_periods}
ส่งการบ้านวันนี้แล้ว: {'✅ ใช่' if hw_submitted else '❌ ยังไม่ได้ส่ง'}
สถานะ Deadline: {hw_deadline.get('message', 'ไม่ทราบ')}
วิชาที่เรียน: {self.course.subject}
หัวข้อวันนี้: {plan.get('title', f'Day {current_day}')}

[ANTI-HALLUCINATION RULES]
1. ห้ามตอบเนื้อหานอกหลักสูตร (วิชา: {self.course.subject}) หรือข้ามไป Day ที่ยังไม่ถึง
2. ถ้าผู้เรียนถามเรื่องนอกเรื่องหรือข้ามเนื้อหา ให้ "ดึงสติ" กลับสู่ Day {current_day} ด้วยความใจดี
3. ห้ามสร้างเนื้อหา/คำตอบขึ้นมาเอง — ตอบตามบริบทหลักสูตรเท่านั้น
4. ถ้าไม่มีข้อมูลใน curriculum ให้บอกตรงๆ ว่า "ยังไม่มีเนื้อหานี้ในหลักสูตร"
5. แจ้งเตือนผู้เรียนทันทีหากการบ้านใกล้หมดเวลา"""

        return f"""คุณคือ {t.get('name')} ({t.get('title')})
บุคลิก: {t.get('personality')} | สไตล์: {t.get('teaching_style')}
น้ำเสียง: {t.get('tone')} | ประโยคเด็ด: "{t.get('catchphrase', '')}"
วิชา: {self.course.subject} | ภาษา: {lang}
ผู้เรียน: {lp.get('name')} | Level {prog['level']} | EXP {prog['exp']}
วันที่: {prog['current_day']}/{prog['total_days']} | คะแนน: {prog['total_score']}
{last_lesson}{hw_context}{done_context}{roadmap_context}{timeslot_context}{rag_part}{context_shield}
[v2.9.6] คุณรู้บริบทหลักสูตร + ตารางเวลา + สถานะ Lock/Unlock ทั้งหมด
ตอบในฐานะครูตัวเองเสมอ รักษาบุคลิก/น้ำเสียง/ภาษาเดิมตลอด"""

    def chat(self, message: str, history: list, current_day: int, persist_key: str = "main") -> str:
        system = self._system(current_day)
        gem_history = []
        for h in history[-10:]:
            # [FIX-1 v2.5] รองรับ key 'ai', 'assistant', 'user' ป้องกัน KeyError
            user_text = h.get("user") or h.get("human") or ""
            ai_text   = h.get("ai") or h.get("assistant") or h.get("model") or ""
            if user_text:
                gem_history.append({"role": "user",  "parts": [{"text": user_text}]})
            if ai_text:
                gem_history.append({"role": "model", "parts": [{"text": ai_text}]})
        gem_history.append({"role": "user", "parts": [{"text": message}]})
        reply = self.ai.call_with_history(gem_history, system=system)
        # v2.0: save to persistent history
        if persist_key == "main":
            self.course.append_chat_main(message, reply)
        else:
            day = int(persist_key) if persist_key.isdigit() else current_day
            self.course.append_chat_lesson(day, message, reply)
        return reply

# ═══════════════════════════════════════════════════════════════════
# SESSION MANAGER — unchanged from v1.0
# ═══════════════════════════════════════════════════════════════════
class SessionManager:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self._sessions: dict = self._load()

    def _load(self) -> dict:
        if SESSIONS_FILE.exists():
            try:
                with open(SESSIONS_FILE) as f:
                    return json.load(f)
            except: pass
        return {}

    def _save(self):
        with open(SESSIONS_FILE, "w") as f:
            json.dump(self._sessions, f)

    def create(self, course_id: str) -> str:
        sid = uuid.uuid4().hex
        self._sessions[sid] = {"course_id": course_id, "created": datetime.now().isoformat()}
        self._save()
        return sid

    def get_course_id(self, sid: str) -> Optional[str]:
        return self._sessions.get(sid, {}).get("course_id")

    def delete(self, sid: str):
        self._sessions.pop(sid, None)
        self._save()

_session_mgr = SessionManager()

# ═══════════════════════════════════════════════════════════════════
# ENROLLMENT STATE — v2.0 FULLY IMPLEMENTED (no stubs)
# ═══════════════════════════════════════════════════════════════════
_enrollment_states: dict = {}

def create_enrollment_state(provider: str, api_key: str, model: str,
                              subject: str, learner_name: str,
                              mentor_style: str = "friendly", rag_url: str = "") -> str:
    eid = uuid.uuid4().hex[:12]
    ai  = AIClient(provider, api_key, model)
    _enrollment_states[eid] = {
        "step"              : 0,
        "provider"          : provider,
        "api_key"           : api_key,
        "model"             : model,
        "subject"           : subject,
        "learner_name"      : learner_name,
        "mentor_style"      : mentor_style,
        "rag_url"           : rag_url,
        "assessment_answers": {"name": learner_name},
        "ai_client"         : ai,
        "done"              : False,
    }
    return eid

def enrollment_next_question(eid: str) -> dict:
    state = _enrollment_states.get(eid)
    if not state:
        return {"question": "❌ Session หมดอายุ", "done": False}
    step = state["step"]
    questions = EnrollmentAgent.ASSESSMENT_QUESTIONS
    if step >= len(questions):
        return {"question": "", "done": True, "summary": "ครบทุกคำถามแล้ว!"}
    q_data = questions[step]
    q_text = q_data["q"].format(name=state["learner_name"], subject=state["subject"])
    # [REFACTOR] Return full question structure for choice-based UI
    result = {
        "question"   : q_text,
        "done"       : False,
        "step"       : step,
        "total_steps": len(questions),
        "q_id"       : q_data["id"],
        "q_type"     : q_data.get("type", "text"),
    }
    if "choices" in q_data:
        result["choices"] = q_data["choices"]
    if "days_choices" in q_data:
        result["days_choices"]  = q_data["days_choices"]
        result["hours_choices"] = q_data["hours_choices"]
    if "reason_placeholder" in q_data:
        result["reason_placeholder"] = q_data["reason_placeholder"]
    return result

def enrollment_process_answer(eid: str, answer: str) -> dict:
    state = _enrollment_states.get(eid)
    if not state:
        return {"question": "❌ Session หมดอายุ", "done": False}
    questions = EnrollmentAgent.ASSESSMENT_QUESTIONS
    step = state["step"]
    if step < len(questions):
        q_id = questions[step]["id"]
        state["assessment_answers"][q_id] = answer
        state["step"] += 1
    if state["step"] >= len(questions):
        state["done"] = True
        return {"question": "", "done": True,
                "summary": "ขอบคุณมากครับ! ตอนนี้ฉันเข้าใจเป้าหมายของคุณแล้ว 🎯\nกดปุ่ม 'ดูแผนหลักสูตร' เพื่อดูก่อนยืนยันได้เลย!"}
    # [REFACTOR] Return full question structure for next step
    return enrollment_next_question(eid)

def enrollment_generate_course(eid: str) -> dict:
    state = _enrollment_states.get(eid)
    if not state:
        return {"error": "Session หมดอายุ"}
    try:
        ai      = state["ai_client"]
        agent   = EnrollmentAgent(ai)
        answers = state["assessment_answers"]
        subject = state["subject"]
        mentor_style = state.get("mentor_style", "friendly")

        # ── ใช้ cache จาก preview ถ้ามี (แนวทาง A — ไม่ generate ซ้ำ) ──
        lp         = state.get("_cached_lp") or agent.assess_knowledge(subject, answers)
        teacher    = state.get("_cached_teacher")
        curriculum = state.get("_cached_skeleton")
        rag_context = state.get("_cached_rag", "")
        rag_url     = state.get("rag_url", "")

        # fallback ถ้าไม่มี cache (กรณีข้าม preview หรือ session reload)
        if not teacher:
            print(c(C.CYAN, "  Generating teacher persona..."))
            teacher = agent.generate_teacher_persona(
                subject, lp["level"], lp["lang"], lp, mentor_style=mentor_style
            )
        if not curriculum:
            if not rag_context and rag_url:
                print(c(C.CYAN, f"  RAG: fetching {rag_url}..."))
                rag_result  = RAGFetcher.fetch(rag_url)
                rag_context = rag_result.get("content", "")
            print(c(C.CYAN, f"  Generating curriculum ({lp['total_days']} days)..."))
            curriculum = agent.generate_curriculum(
                subject, lp["total_days"], lp["level"],
                lp["style"], lp["lang"], lp, teacher, rag_context=rag_context
            )
        else:
            print(c(C.GREEN, f"  ✦ Using cached skeleton ({len(curriculum)} days) — skipping generate"))

        # Build course title [FEAT-1c v2.5]
        level_labels = {"beginner": "เริ่มต้น", "intermediate": "กลาง", "advanced": "ขั้นสูง"}
        if lp.get("roadmap_mode"):
            title = f"{subject} — Roadmap ระยะยาว ({lp['total_days']} วัน / Phase 1)"
        else:
            title = f"{subject} — {level_labels.get(lp['level'], lp['level'])} {lp['total_days']} วัน"

        # Create and save course
        course = Course({
            "title"           : title,
            "subject"         : subject,
            "description"     : lp.get("goal", ""),
            "total_days"      : lp["total_days"],
            "level"           : lp["level"],
            "style"           : lp["style"],
            "lang"            : lp["lang"],
            "teacher_persona" : teacher,
            "curriculum"      : curriculum,
            "learner_profile" : lp,
            "provider"        : state["provider"],
            "model"           : state["model"],
            "rag_context"     : rag_context,
            "rag_url"         : rag_url,
            "mentor_style"    : mentor_style,
        })
        course.save()

        # Save API key to persistent config
        ConfigManager.save_api_key(state["provider"], state["api_key"], state["model"])
        print(c(C.GREEN, f"  ✅ Course created: {course.id} — {title}"))

        # [BUG-FIX] Clean up enrollment state ONLY after successful save
        # ก่อนหน้านี้ pop ออกแม้เกิด error → ทำให้ retry ไม่ได้เพราะ session หาย
        _enrollment_states.pop(eid, None)
        return {"course_id": course.id, "title": title}
    except Exception as e:
        import traceback
        print(c(C.RED, f"  ❌ Generate course error: {e}"))
        traceback.print_exc()
        # [BUG-FIX] ไม่ลบ state — User ยัง retry ได้โดยไม่เสีย session
        return {"error": str(e), "retryable": True}


def enrollment_preview_curriculum(eid: str) -> dict:
    """
    [Preview — แนวทาง A] สร้าง skeleton + teacher จริงแล้ว cache ไว้
    ตอน generate() แค่ save ทันที ไม่ต้อง generate ซ้ำ
    คืน: { days: [{day, title, topics},...], total_days, level, hours_per_day, goal }
    """
    state = _enrollment_states.get(eid)
    if not state:
        return {"error": "Session หมดอายุ"}
    try:
        ai           = state["ai_client"]
        agent        = EnrollmentAgent(ai)
        answers      = state["assessment_answers"]
        subject      = state["subject"]
        mentor_style = state.get("mentor_style", "friendly")
        rag_url      = state.get("rag_url", "")

        # 1. วิเคราะห์ answers → learner profile
        lp = agent.assess_knowledge(subject, answers)
        state["_cached_lp"] = lp

        total_days   = lp["total_days"]
        level_labels = {"beginner": "เริ่มต้น", "intermediate": "กลาง", "advanced": "ขั้นสูง"}
        level_th     = level_labels.get(lp["level"], lp["level"])

        # 2. Fetch RAG ถ้ามี URL
        rag_context = ""
        if rag_url:
            print(c(C.CYAN, f"  [Preview] RAG: fetching {rag_url}..."))
            rag_result  = RAGFetcher.fetch(rag_url)
            rag_context = rag_result.get("content", "")
            state["_cached_rag"] = rag_context

        # 3. Generate teacher persona จริง (cache ไว้)
        print(c(C.CYAN, "  [Preview] Generating teacher persona..."))
        teacher = agent.generate_teacher_persona(
            subject, lp["level"], lp["lang"], lp, mentor_style=mentor_style
        )
        state["_cached_teacher"] = teacher

        # 4. Generate skeleton จริงทุกวัน (cache ไว้ — ตอน confirm แค่ save)
        print(c(C.CYAN, f"  [Preview] Generating full skeleton ({total_days} days)..."))
        skeleton = agent.generate_skeleton(
            subject, total_days, lp["level"],
            lp["style"], lp["lang"], lp, teacher, rag_context=rag_context
        )
        state["_cached_skeleton"] = skeleton

        # 5. แปลง skeleton → format สำหรับ UI (day, title, topics string)
        days_preview = []
        for item in skeleton:
            days_preview.append({
                "day"   : item.get("day", 0),
                "title" : item.get("title", f"วันที่ {item.get('day',0)}"),
                "topics": item.get("topics", ""),
            })

        print(c(C.GREEN, f"  [Preview] ✅ Ready: {len(days_preview)} days"))
        return {
            "days"         : days_preview,
            "total_days"   : total_days,
            "hours_per_day": lp["hours_per_day"],
            "level"        : level_th,
            "level_key"    : lp["level"],
            "goal"         : lp.get("goal", ""),
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def expand_day_periods(course: "Course", day: int) -> dict:
    """
    [v3.0] Phase 2 Lazy Generation — เติม periods ให้กับวันที่ยังมี _periods_pending=True
    เรียกก่อนเริ่มเรียนวันนั้น (หรือเมื่อ Skill Path แสดง ????)
    คืน updated day_plan พร้อม periods
    """
    # หา day_plan ใน curriculum
    plan = next((p for p in course.curriculum if p.get("day") == day), None)
    if not plan:
        return {"error": f"ไม่พบ Day {day} ใน curriculum"}

    # ถ้า periods มีอยู่แล้วและไม่ pending → return ทันที
    if plan.get("periods") and not plan.get("_periods_pending", False):
        return {"ok": True, "day": day, "already_done": True, "plan": plan}

    ai    = _make_ai_for_course(course)
    agent = EnrollmentAgent(ai)
    lp    = course.learner_profile

    # สร้าง prev_day_summary จาก Day ก่อนหน้า (สำหรับ Sequential Continuity)
    prev_summary = ""
    if day > 1:
        prev_plan = next((p for p in course.curriculum if p.get("day") == day - 1), {})
        prev_periods = prev_plan.get("periods", [])
        if prev_periods:
            prev_names = [p.get("name", "") for p in prev_periods]
            prev_summary = f"'{prev_plan.get('title', '')}': " + ", ".join(prev_names[:3])
        else:
            prev_summary = prev_plan.get("title", "")

    print(c(C.CYAN, f"  [Lazy Gen] Expanding Day {day} periods..."))
    updated_plan = agent.generate_day_detail(
        subject      = course.subject,
        day          = day,
        day_plan     = plan,
        level        = course.level,
        style        = course.style,
        lang         = course.lang,
        learner_profile = lp,
        teacher      = course.teacher_persona,
        prev_day_summary = prev_summary,
    )

    # อัปเดต curriculum ใน course
    for i, p in enumerate(course.curriculum):
        if p.get("day") == day:
            course.curriculum[i] = updated_plan
            break
    course.save()

    print(c(C.GREEN, f"  [Lazy Gen] ✅ Day {day} expanded: {len(updated_plan.get('periods', []))} periods"))
    return {"ok": True, "day": day, "plan": updated_plan}


def _make_ai_for_course(course: Course) -> AIClient:
    """สร้าง AIClient โดยดึง API key จาก config"""
    api_key = ConfigManager.get_api_key(course.provider)
    return AIClient(course.provider, api_key, course.model)

