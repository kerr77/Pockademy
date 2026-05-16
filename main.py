#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║   POCKADEMY 0.1 Demo                                     ║
║   Your AI University — fits in your pocket               ║
║   "เรียนได้ทุกวิชา บนมือถือ ไม่ต้องมีอินเตอร์เน็ตเร็ว" ║
╚══════════════════════════════════════════════════════════╝

วิธีรัน:
  python main.py
  เปิด Browser: http://localhost:7070
"""

from engine import *
from engine import _patch_gamification_phase_badge
from server import PockademyRequestHandler, WEB_PORT, DATA_DIR, COURSES_DIR, UPLOADS_DIR
import socketserver

def print_banner():
    print(c(C.ACID,   "╔══════════════════════════════════════════╗"))
    print(c(C.ACID,   "║   🎓 POCKADEMY 0.1 Demo                  ║"))
    print(c(C.ACID,   "║   Your AI University in Your Pocket      ║"))
    print(c(C.ACID,   "╠══════════════════════════════════════════╣"))
    print(c(C.GREEN,  "║  ✅ AI Curriculum (Skeleton + Lazy Load)  ║"))
    print(c(C.GREEN,  "║  ✅ Multi-Provider AI (4 providers)       ║"))
    print(c(C.GREEN,  "║  ✅ Sequential Learning Engine            ║"))
    print(c(C.GREEN,  "║  ✅ EXP / Level / Badge / Certificate     ║"))
    print(c(C.GREEN,  "║  ✅ Mentor Chat (4 personas)              ║"))
    print(c(C.GREEN,  "║  ✅ Homework + Quiz Engine                ║"))
    print(c(C.GREEN,  "║  ✅ Progress Tracking + Day Lock          ║"))
    print(c(C.GREEN,  "║  ✅ RAG Light (URL context injection)     ║"))
    print(c(C.CYAN,   "║  🔜 Login Gmail (coming soon)            ║"))
    print(c(C.ACID,   "╚══════════════════════════════════════════╝"))

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    COURSES_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    _patch_gamification_phase_badge()

    print_banner()
    print(c(C.CYAN,   f"\n🚀 http://localhost:{WEB_PORT}"))
    print(c(C.YELLOW, f"📁 Data: {DATA_DIR.absolute()}"))

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", WEB_PORT), PockademyRequestHandler) as httpd:
        print(c(C.GREEN, "✅ Server พร้อมแล้ว — เปิด Browser เลย\n"))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(c(C.RED, "\n🛑 ปิด Server..."))

