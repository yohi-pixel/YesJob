# Resume Module

Parse and AI-optimize resume sections (experiences + self-description).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/resume/parse` | Upload PDF/DOCX → extract experiences & self-description |
| POST | `/api/resume/optimize` | AI-rewrite a section for a target job tag |

## Architecture

```
upload PDF/DOCX
     │
     ▼
  parser.py        → raw text extraction (pdfplumber / python-docx)
     │
     ▼
  splitter.py      → split into experience / self_description sections
     │  (fails?)      ↓
     │  ─────────→ optimizer.py (AI fallback splitting via DeepSeek)
     ▼
  extractor.py     → structured ExperienceItem[] from experience text
     │
     ▼
  router.py        → POST /api/resume/parse returns ParseResumeResponse
```

## Notes

- **Basic info is NOT parsed** — users fill it in manually on the frontend.
- All persistence is handled by the frontend (localStorage).
- This module only provides parsing and AI optimization APIs.
- AI optimization reuses the existing DeepSeek LLM client from `ai_agent.orchestrator`.
