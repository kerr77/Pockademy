# 🎓 Pockademy

*Your AI University — Fits in Your Pocket*

> **Education for all.** Learn any subject on your mobile device without needing fast internet.

---

## 💭 **The Story Behind Pockademy**

### **Why I Built This**

Two weeks ago, I was trying to learn QA testing to apply for my first tech job. I found courses I wanted to take, but they were too expensive. In that moment, a thought crossed my mind:

> *"If I can't afford to learn, why not build it myself?"*

So I did. I took a free weekend, designed a learning platform blueprint, and asked AI to help build it.

But as I kept developing, something shifted. I started thinking about the millions of people like me—talented people trapped in difficult situations, unable to afford quality education. What if they could just... grab knowledge with their own hands? What would their lives look like?

That thought became fuel. The project grew bigger. More features. Better design. More ambition.

Today, Pockademy exists for everyone who:
- ✅ Can't afford expensive courses
- ✅ Wants to learn but doesn't know where to start
- ✅ Has dreams but not resources
- ✅ Believes they deserve a chance

**This isn't just an app. It's a middle finger to gatekeeping education.** 🚀

---

## 📱 English

### What is Pockademy?

Pockademy is an **AI-powered personalized learning platform** that generates custom curricula, homework, quizzes, and mentoring for any subject. It combines multiple AI providers (Gemini, OpenAI, Anthropic, and Ollama) to deliver a university-grade education experience that fits in your pocket.

Built to be **accessible everywhere**—on any device, with or without fast internet, completely free to start.

### ✨ Key Features

- 🤖 **AI Curriculum Generation** — Automatically creates 30-day learning roadmaps tailored to your level
- 🔄 **Multi-Provider AI Support** — Works with Google Gemini, OpenAI, Anthropic, and Ollama
- 📚 **Sequential Learning Engine** — Lessons unlock progressively; complete prerequisites before advancing
- 🎮 **Gamification System**
  - 📊 EXP points for activities (lessons, homework, quizzes)
  - 📈 Leveling system with milestone rewards
  - 🏆 Achievement badges
  - 📜 Digital certificates for course completion
- 💬 **AI Mentor Chat** — Four personality styles (Socratic, Motivator, Strict, Friendly)
- ✍️ **Homework & Quiz Engine** — AI-graded assignments with instant feedback
- 📊 **Progress Tracking** — Day-by-day completion status, scores, and performance metrics
- 🔒 **Activity Gates** — Homework deadlines and activity requirements prevent rushing
- 🌐 **RAG Light** — Context injection from URLs for real-world learning scenarios
- 💾 **Persistent Chat History** — Resume conversations across sessions
- 📝 **Caching System** — Optimize performance and reduce API calls

### 🚀 Getting Started

#### Prerequisites
- Python 3.9+
- API key for at least one AI provider:
  - [Google Gemini](https://ai.google.dev/)
  - [OpenAI API](https://platform.openai.com/api-keys)
  - [Anthropic Claude](https://console.anthropic.com/)
  - [Ollama](https://ollama.ai/) (local, free)

#### Installation

```bash
# Clone the repository
git clone https://github.com/kerr77/Pockademy.git
cd Pockademy

# Install dependencies (if needed)
# pip install -r requirements.txt

# Run the server
python main.py
```

#### Access the Platform
Open your browser and navigate to: `http://localhost:7070`

### 📖 How It Works

1. **Create a Course**
   - Select subject, level (Beginner/Intermediate/Advanced), and duration
   - Provide your AI provider credentials and preferred model
   - Pockademy generates a personalized 30-day curriculum

2. **Learn Daily**
   - Access lessons for each day
   - Read structured content tailored to your level
   - Unlock new days after completing prerequisites

3. **Practice**
   - Complete homework assignments with AI feedback
   - Take quizzes with a 10-minute time limit
   - Earn EXP and unlock badges

4. **Track Progress**
   - Monitor your level and EXP growth
   - View achievements and earned certificates
   - Access chat history with your AI mentor

### 🏗️ Architecture

#### Core Modules

| Module | Purpose |
|--------|---------|
| `AIClient` | Universal interface for multiple AI providers |
| `EnrollmentAgent` | Generates personalized curricula and assessments |
| `LessonEngine` | Delivers daily lessons and content |
| `HomeworkEngine` | Creates and grades assignments |
| `ChatEngine` | Maintains mentor conversations |
| `GamificationEngine` | Manages EXP, levels, and badges |
| `CertificateEngine` | Generates completion certificates |
| `Course` | Core data model for learner progress |
| `RAGFetcher` | Retrieves external content for context injection |

#### Data Structure

```
pockademy_data/
├── courses/           # Individual course data (JSON)
├── uploads/           # User-submitted files
├── sessions.json      # Active session tracking
├── config.json        # Persistent API keys and settings
└── tts_cache/         # Text-to-speech cache (if enabled)
```

### ⚙️ Configuration

Store API keys securely via the web interface. Supported models:

- **Gemini**: `gemini-2.0-flash`, `gemini-1.5-pro`, etc.
- **OpenAI**: `gpt-4`, `gpt-3.5-turbo`, etc.
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet`, etc.
- **Ollama**: Any local model (`llama2`, `mistral`, etc.)

### 🛠️ Development

#### Project Structure
```
.
├── main.py            # Entry point
├── server.py          # HTTP server and API endpoints
├── engine.py          # Core learning engine
├── .gitignore
├── LICENSE
└── README.md
```

#### Adding a New AI Provider

1. Extend `AIClient._call_provider()` with your provider logic
2. Add provider info to `PROVIDERS` dict
3. Update `ConfigManager` if credentials differ from standard API key

### 📜 License

MIT License — See `LICENSE` file for details.

### 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for more languages
- Enhanced UI/UX
- Mobile app
- Advanced RAG integration
- Real-time collaboration features

### 📧 Support & Contact

For issues, feature requests, or questions, please open a [GitHub Issue](https://github.com/kerr77/Pockademy/issues).

---

## 🇹🇭 ภาษาไทย

### 💭 **เรื่องราวเบื้องหลัง Pockademy**

### **ทำไมผมสร้างมัน**

สองอาทิตย์ที่แล้ว ผมพยายามเรียนรู้เป็น QA Tester เพื่อสมัครงานเทคแรกของผม ผมพบหลักสูตรที่ต้องการเรียน แต่มันแพงเกินไป ในขณะนั้น ความคิดหนึ่งเด้งขึ้นมาในหัว:

> *"ถ้าผมจ่ายไม่ได้ ก็สร้างเองสิ?"*

ผมก็ทำ สิ้นสุดวันหนึ่ง ออกแบบบ้านเรียน ให้ AI ช่วยสร้าง

แต่ตอนที่ผมทำไปเรื่อย ๆ บางอย่างเปลี่ยนไป ผมเริ่มนึกถึงคนอื่น ๆ มากมาย—คนเก่ง ที่ติดอยู่ในสถานการณ์ยากๆ ไม่สามารถจ่ายเรียนได้ แล้วถ้าพวกเค้าสามารถคว้ามันด้วยมือตัวเองล่ะ ชีวิตพวกเค้าจะเปลี่ยนไปแค่ไหน

ความคิดนั้นเป็นเชื้อเพลิง โปรเจคโตขึ้น ฟีเจอร์เยอะขึ้น ความทะเยอทะยานเพิ่มขึ้น

วันนี้ Pockademy มีอยู่สำหรับคนทุกคนที่:
- ✅ จ่ายหลักสูตรแพงไม่ได้
- ✅ ต้องการเรียน แต่ไม่รู้เริ่มจากไหน
- ✅ มีฝัน แต่��ม่มี resources
- ✅ เชื่อว่าตัวเองสมควร

**นี่ไม่ใช่แค่แอป มันคือการเอาเงินหนึ่งให้การศึกษาที่เป็นการค้นหา** 🚀

---

### Pockademy คืออะไร?

Pockademy เป็น **แพลตฟอร์มการเรียนรู้ส่วนบุคคลที่ขับเคลื่อนโดย AI** ซึ่งสร้างหลักสูตร การบ้าน แบบทดสอบ และการสอนส่วนบุคคลสำหรับวิชาใด ๆ โดยรวมผู้ให้บริการ AI หลายราย (Gemini, OpenAI, Anthropic และ Ollama) เพื่อให้ประสบการณ์การเรียนในระดับมหาวิทยาลัยที่พอดีกับกระเป๋าของคุณ

สร้างมาให้เข้าถึงได้ทุกที่—บนอุปกรณ์ใด ๆ ไม่ว่าจะมีอินเทอร์เน็ตเร็วหรือไม่ก็ตาม ฟรีทั้งหมด

### ✨ คุณสมบัติหลัก

- 🤖 **สร้างหลักสูตร AI อัตโนมัติ** — สร้างแผนเรียน 30 วันที่ปรับแต่งตามระดับของคุณ
- 🔄 **รองรับ AI หลายผู้ให้บริการ** — ทำงานได้กับ Google Gemini, OpenAI, Anthropic และ Ollama
- 📚 **เอนจิน Learning ตามลำดับ** — บทเรียนปลดล็อกแบบค่อยเป็นค่อยไป ต้องจบบทเรียนก่อนหน้าก่อน
- 🎮 **ระบบแกมิฟิเคชัน**
  - 📊 คะแนน EXP สำหรับกิจกรรม (บทเรียน การบ้าน แบบทดสอบ)
  - 📈 ระบบ Leveling พร้อมรางวัลเหริญ
  - 🏆 เหรียญรางวัลสำหรับความสำเร็จ
  - 📜 ใบประกาศนียบัตรดิจิทัลสำหรับจบหลักสูตร
- 💬 **แอดไวเซอร์ AI** — สี่สไตล์ส่วนบุคคล (Socratic, Motivator, Strict, Friendly)
- ✍️ **เอนจิน Homework และ Quiz** — การประเมินโดย AI พร้อมข้อมูลย้อนกลับทันที
- 📊 **ติดตามความก้าวหน้า** — สถานะการจบวันต่อวัน คะแนน และเมตริกการประเมิน
- 🔒 **ประตูกิจกรรม** — กำหนดเวลาสิ้นสุดการบ้านและข้อกำหนดกิจกรรมเพื่อป้องกันการวิ่งห้ี
- 🌐 **RAG Light** — ฉีดข้อมูลจาก URL สำหรับสถานการณ์การเรียนรู้ในโลกจริง
- 💾 **ประวัติการสนทนาถาวร** — กลับมาที่การสนทนาต่อจากที่แล้ว
- 📝 **ระบบแคชเก็บ** — ปรับปรุงประสิทธิภาพและลดการเรียก API

### 🚀 เริ่มต้นใช้งาน

#### สิ่งที่ต้องมี
- Python 3.9+
- API key จากผู้ให้บริการ AI อย่างน้อยหนึ่งราย:
  - [Google Gemini](https://ai.google.dev/)
  - [OpenAI API](https://platform.openai.com/api-keys)
  - [Anthropic Claude](https://console.anthropic.com/)
  - [Ollama](https://ollama.ai/) (ท้องถิ่น ฟรี)

#### การติดตั้ง

```bash
# โคลนที่เก็บ
git clone https://github.com/kerr77/Pockademy.git
cd Pockademy

# ติดตั้งการขึ้นต่อกัน (หากจำเป็น)
# pip install -r requirements.txt

# เรียกใช้เซิร์ฟเวอร์
python main.py
```

#### เข้าถึงแพลตฟอร์ม
เปิดเบราว์เซอร์ของคุณและไปที่: `http://localhost:7070`

### 📖 วิธีการทำงาน

1. **สร้างหลักสูตร**
   - เลือกวิชา ระดับ (Beginner/Intermediate/Advanced) และระยะเวลา
   - ให้ข้อมูลประจำตัวผู้ให้บริการ AI และโมเดลที่ต้องการ
   - Pockademy สร้างหลักสูตรส่วนบุคคล 30 วัน

2. **เรียนรู้ทุกวัน**
   - เข้าถึงบทเรียนสำหรับแต่ละวัน
   - อ่านเนื้อหาโครงสร้างที่ปรับแต่งตามระดับของคุณ
   - ปลดล็อกวันใหม่หลังจากจบข้อกำหนดเบื้องต้น

3. **ฝึกซ้อม**
   - ทำการบ้านด้วยข้อมูลย้อนกลับจาก AI
   - ทำแบบทดสอบด้วยขีดจำกัด 10 นาที
   - หารายได้ EXP และปลดล็อกเหรียญ

4. **ติดตามความก้าวหน้า**
   - ตรวจสอบการเติบโตของระดับและ EXP
   - ดูความสำเร็จและใบประกาศนียบัตร
   - เข้าถึงประวัติการสนทนากับที่ปรึกษา AI

### 🏗️ สถาปัตยกรรม

#### โมดูลหลัก

| โมดูล | วัตถุประสงค์ |
|-------|-----------|
| `AIClient` | อินเทอร์เฟซสากลสำหรับผู้ให้บริการ AI หลายราย |
| `EnrollmentAgent` | สร้างหลักสูตรและการประเมินส่วนบุคคล |
| `LessonEngine` | ส่งบทเรียนรายวันและเนื้อหา |
| `HomeworkEngine` | สร้างและให้คะแนนงาน |
| `ChatEngine` | รักษาการสนทนาของที่ปรึกษา |
| `GamificationEngine` | จัดการ EXP ระดับ และเหรียญ |
| `CertificateEngine` | สร้างใบประกาศนียบัตรจบหลักสูตร |
| `Course` | โมเดลข้อมูลหลักสำหรับความก้าวหน้าของผู้เรียน |
| `RAGFetcher` | ดึงข้อมูลภายนอกสำหรับการฉีดบริบท |

#### โครงสร้างข้อมูล

```
pockademy_data/
├── courses/           # ข้อมูลหลักสูตรแต่ละรายการ (JSON)
├── uploads/           # ไฟล์ที่ส่งโดยผู้ใช้
├── sessions.json      # การติดตามเซสชันที่ใช้งาน
├── config.json        # API keys และการตั้งค่าถาวร
└── tts_cache/         # แคชข้อความเป็นเสียง (หากเปิดใช้)
```

### ⚙️ การกำหนดค่า

จัดเก็บ API keys อย่างปลอดภัยผ่านอินเทอร์เฟซเว็บ โมเดลที่รองรับ:

- **Gemini**: `gemini-2.0-flash`, `gemini-1.5-pro`, ฯลฯ
- **OpenAI**: `gpt-4`, `gpt-3.5-turbo`, ฯลฯ
- **Anthropic**: `claude-3-opus-20240229`, `claude-3-sonnet`, ฯลฯ
- **Ollama**: โมเดลท้องถิ่นใด ๆ (`llama2`, `mistral`, ฯลฯ)

### 🛠️ การพัฒนา

#### โครงสร้างโครงการ
```
.
├── main.py            # จุดเข้า
├── server.py          # เซิร์ฟเวอร์ HTTP และจุดสิ้นสุด API
├── engine.py          # เอนจินการเรียนรู้หลัก
├── .gitignore
├── LICENSE
└── README.md
```

#### เพิ่มผู้ให้บริการ AI ใหม่

1. ขยาย `AIClient._call_provider()` ด้วยตรรกะผู้ให้บริการของคุณ
2. เพิ่มข้อมูลผู้ให้บริการเข้ากับพจนานุกรม `PROVIDERS`
3. อัปเดต `ConfigManager` หากข้อมูลประจำตัวแตกต่างจาก API key มาตรฐาน

### 📜 ใบอนุญาต

ใบอนุญาต MIT — ดูไฟล์ `LICENSE` สำหรับรายละเอียด

### 🤝 การมีส่วนร่วม

เรายินดีต้อนรับการมีส่วนร่วม! พื้นที่สำหรับการปรับปรุง:
- รองรับภาษาเพิ่มเติม
- ปรับปรุง UI/UX
- แอปมือถือ
- การรวม RAG ขั้นสูง
- คุณสมบัติความร่วมมือแบบเรียลไทม์

### 📧 การสนับสนุนและติดต่อ

หากมีปัญหา คำขอฟีเจอร์ หรือคำถาม โปรดเปิด [GitHub Issue](https://github.com/kerr77/Pockademy/issues)
