<div align="center">

# 🤖 AI Desktop Assistant

**A modern, chat-style AI desktop application with multi-provider support, persistent chat history, and global text capture — running right from your system tray.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-informational)](https://github.com/TomSchimansky/CustomTkinter)
[![Ollama](https://img.shields.io/badge/Local-Ollama-black)](https://ollama.com)
[![OpenAI](https://img.shields.io/badge/Cloud-OpenAI-412991?logo=openai)](https://platform.openai.com)
[![Gemini](https://img.shields.io/badge/Cloud-Gemini-4285F4?logo=google)](https://ai.google.dev)

</div>

---

## 📖 Overview

AI Desktop Assistant is a **Python-based desktop application** that brings the power of local and cloud AI models to your fingertips — no browser needed. It lives quietly in your **system tray** and pops up on demand with a global keyboard shortcut. You can chat with it, capture selected text from any application, attach files and images, and browse your full conversation history — all in a clean, ChatGPT-inspired interface.

---

## ✨ Features

### 💬 Chat Interface
- **ChatGPT-style layout** — user messages on the right (blue bubbles), AI responses on the left.
- **Streaming responses** — tokens appear word by word as the AI generates them.
- **Animated loading indicator** (● ○ ○) while waiting for the first token.
- **Markdown rendering** — bold, italic, inline code, headings, numbered & bulleted lists.
- **Syntax-highlighted code blocks** — VS Code-style dark theme with keyword colouring for Python (blue keywords, orange strings, green comments, purple builtins).
- **Copy buttons** — individual 📋 Copy code, 📋 Copy table, and 📋 Copy all buttons on every response.

### 🌐 Multi-Provider AI
- **Three backends** supported out of the box: Ollama (local), OpenAI, and Google Gemini.
- **Automatic routing** — the correct client is used based on the selected model's provider.
- **Model dropdown** with provider badges: 💻 Local, ☁️ OpenAI, ✦ Gemini.

### 🔑 Global Shortcut & Context Capture
- **`Ctrl+Shift+A`** — works from anywhere on your system while the app runs in the background.
- Captures the currently **selected text** in any application and pre-loads it as context in the input bar.
- The window is brought to the foreground reliably using Win32 API.

### 🗂️ Chat History & Sidebar
- **Collapsible sidebar** (click ☰ to show/hide) lists all previous conversations.
- **＋ New Chat** button starts a fresh session at any time.
- **Auto-titling** — the first user message becomes the chat title automatically.
- **Rename** (✏️) and **Delete** (🗑) any chat inline.
- **Click any chat** to fully reload and replay the conversation in the chat area.
- All chats are persisted as JSON files in the `user_data/chats/` folder.

### 📎 File Attachments
- **📎 button** in the input bar opens a file picker.
- Supports **images** (PNG, JPG, JPEG, WEBP, GIF), **PDFs**, and plain text files.
- Images are **base64-encoded** and passed directly to vision-capable models like `qwen3-vl:8b`.
- Shows a preview card with filename and a ✕ remove button.

### 🎨 UI & Themes
- **Light mode** (default) and **Dark mode** — toggle with the 🌙/☀️ button in the header.
- Built with **CustomTkinter** for a modern, anti-aliased look.
- Fully responsive — the chat area expands to fill available space.

### ⚙️ Ollama Integration
- **Connection status indicator** (🟢 Connected / 🔴 Offline) shown in the header.
- **▶ Start Ollama button** appears automatically when Ollama is detected as offline, and attempts to launch it in the background using `ollama serve`.

### 🖥️ System Tray
- The app minimises to the **system tray** instead of closing.
- Tray menu has options to **Show** the window or **Quit** the application.
- The window can be restored at any time from the tray icon or via `Ctrl+Shift+A`.

---

## 🧠 Available Models

### 💻 Local (Ollama)
| Model | Type | Size |
|---|---|---|
| `qwen2.5:3b` | General Chat | 1.9 GB |
| `qwen2.5-coder:3b` | Code Generation | 1.9 GB |
| `qwen3:8b` | Advanced Reasoning | 5.2 GB |
| `gemma4:26b` | Most Capable (Local) | 17 GB |
| `qwen3-vl:8b` | 📷 Vision + Language | 6.1 GB |

> Models must be downloaded via Ollama first: `ollama pull <model-name>`

### ☁️ Cloud (OpenAI)
| Model | Type |
|---|---|
| `gpt-4o-mini` | Fast & Smart |
| `gpt-4o` | Most Capable |
| `gpt-3.5-turbo` | Fast & Affordable |

### ✦ Cloud (Google Gemini)
| Model | Type |
|---|---|
| `gemini-2.0-flash` | Fast & Free |
| `gemini-1.5-pro` | Most Capable |
| `gemini-1.5-flash` | Balanced |

---


## ⚡ Installation & Setup

### 1. Prerequisites
- **Python 3.10+**
- **Ollama** installed (for local models): [https://ollama.com](https://ollama.com)

### 2. Clone the Repository
```bash
git clone https://github.com/PrashantPKP/ai-desktop-assistant.git
cd ai-desktop-assistant
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `.env` file in the project root (copy from the example below):
```env
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```
> Cloud models won't work without these. Local Ollama models work without any API key.

### 5. Pull Ollama Models (optional, for local AI)
```bash
ollama pull qwen2.5:3b
ollama pull qwen2.5-coder:3b
ollama pull qwen3:8b
ollama pull qwen3-vl:8b
```

### 6. Run the App
```bash
python main.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Shift+A` | Open assistant with selected text as context |
| `Ctrl+Enter` | Send message |

---

## 🤝 Developer

<table>
  <tr>
    <td><b>Developer</b></td>
    <td>Prashant Parshuramkar</td>
  </tr>
  <tr>
    <td><b>GitHub</b></td>
    <td><a href="https://github.com/PrashantPKP">github.com/PrashantPKP</a></td>
  </tr>
  <tr>
    <td><b>LinkedIn</b></td>
    <td><a href="https://www.linkedin.com/in/prashantpkp/">linkedin.com/in/prashantpkp</a></td>
  </tr>
  <tr>
    <td><b>Repository</b></td>
    <td><a href="https://github.com/PrashantPKP/ai-desktop-assistant.git">ai-desktop-assistant</a></td>
  </tr>
</table>
