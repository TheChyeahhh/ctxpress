# ctxpress

> Loss-aware context compression. Shrink any text while keeping what actually matters.

Most summarizers lose critical information. **ctxpress** is built specifically for LLM workflows — it always preserves named entities, numbers, dates, code, decisions, and action items, while aggressively removing noise.

---

## Why it exists

When you're working with LLMs, context windows fill up fast. Naive summarizers drop the wrong things — they'll cut a critical decision or a specific number while keeping filler paragraphs.

ctxpress treats compression as a precision task: it knows what to keep (entities, code, facts, decisions) and what to cut (filler, redundancy, pleasantries, verbose restatements).

---

## Three compression levels

| Level | Target | What happens |
| --- | --- | --- |
| `light` | ~70% | Remove filler and redundancy. Keep structure. |
| `medium` | ~40% | Summarize verbose sections. Extract key points. |
| `heavy` | ~15% | Bullet-point extraction only. Maximum compression. |

---

## What is always preserved

Regardless of compression level, ctxpress never drops:

- Named entities (people, companies, products, places)
- Numbers, dates, percentages, measurements
- Code blocks, commands, file paths, URLs
- Decisions made and conclusions reached
- Action items and next steps
- Errors, warnings, risks, and blockers

---

## Demo

```bash
$ cat meeting_notes.txt | ctxpress --level medium
```

```text
──────────────────────────────── ctxpress ────────────────────────────────────
  Level:    MEDIUM — Extract key points, summarize verbose sections...
  Input:    4,821 chars (~1,205 tokens)
  Target:   ~40% of original
  Backend:  claude

╭──────────────────────── Compression Stats ───────────────────────────────────╮
│  Level       MEDIUM                                                           │
│  Original    4,821 chars  (~1,205 tokens)                                     │
│  Compressed  1,876 chars  (~469 tokens)                                       │
│  Ratio       ████████░░░░░░░░░░░░  61% smaller                               │
╰───────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────── Compressed Output ───────────────────────────────╮
│  Q3 planning meeting, 2024-09-12. Attendees: Sarah (PM), Dev (Eng lead)...   │
╰───────────────────────────────────────────────────────────────────────────────╯
```

---

## Installation

**Mac / Linux:**

```bash
git clone https://github.com/TheChyeahhh/ctxpress.git
cd ctxpress
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Windows:**

```bash
git clone https://github.com/TheChyeahhh/ctxpress.git
cd ctxpress
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

---

## Setup

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
AI_BACKEND=claude
```

---

## Usage

```bash
# Compress a file
ctxpress document.txt

# Compress with level
ctxpress document.txt --level heavy

# Write output to file
ctxpress document.txt --level medium --output compressed.txt

# Pipe input
cat long_doc.txt | ctxpress
cat meeting_notes.txt | ctxpress --level light

# Interactive paste mode
ctxpress
# Paste text, then Ctrl+D (Mac/Linux) or Ctrl+Z+Enter (Windows)

# See stats only, don't print compressed text
ctxpress document.txt --stats-only

# Use OpenAI
ctxpress document.txt --backend openai
```

---

## Use cases

- Fitting long documents into an LLM context window
- Compressing chat logs or conversation history before sending to AI
- Reducing API costs by shrinking input token counts
- Pre-processing meeting notes, PRDs, or research papers for AI analysis
- Summarizing log files before feeding to devlog

---

## Requirements

- Python 3.9+
- A [Claude API key](https://console.anthropic.com) or [OpenAI API key](https://platform.openai.com)

---

## Future Ideas

- `--preserve` flag to force-keep specific terms or sections
- Streaming output for large documents
- Token budget mode: `--max-tokens 2000`
- Batch compression of multiple files

---

## License

MIT
