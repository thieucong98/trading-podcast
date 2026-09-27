# Plan: Git Push Project Code & Antigravity Cross-Machine Chat History

**Goal:** Push the entire project codebase to GitHub along with Antigravity chat history, workspace rules, and context, enabling seamless session resumption on any computer with 0% secret leaks.

---

## 1. Context & Brainstorm Contract
- **Outcome:**
  - Code pushed to `git@github.com:thieucong98/trading-podcast.git` (main branch).
  - Antigravity sessions (`dc80f4a9...` and `d7d40cd3...`) preserved in `.antigravity/` and resumable on any machine via `agy --resume <id>` or Antigravity IDE.
  - Workspace rules and project memory codified in `GEMINI.md` and `AGENTS.md`.
  - Human/LLM-readable conversation logs in `docs/chat_history/*.md`.
  - Zero secrets (OpenAI, Google, Fal.ai keys, cookies) leaked to GitHub.
- **Constraints:**
  - All secrets MUST be redacted with placeholders (`sk-REDACTED-KEY`, etc.).
  - No large video binaries (`*.mp4`) committed.
  - 100% backward compatibility and no disruption to running services.
- **Acceptance Criteria:**
  1. Updated `.gitignore` prevents `*.mp4`, `*.mov`, `*.avi`, `*.webm`.
  2. `GEMINI.md` and `AGENTS.md` established at project root.
  3. Sanitized session SQLite DBs and transcripts stored in `.antigravity/`.
  4. Markdown digests created in `docs/chat_history/`.
  5. 1-command restore script `scripts/restore_antigravity.py` verified.
  6. Automated security scan proves 0 secret leaks.
  7. Successful `git push origin main`.

---

## 2. Implementation Phases

### Phase 1: Security Hardening & .gitignore Update
- Update `.gitignore` to block all video binaries (`*.mp4`, `*.mov`, `*.avi`, `*.webm`, `*.mkv`).
- Verify `git status` ignores video outputs.

### Phase 2: Project Rules & Agent Context (`GEMINI.md` & `AGENTS.md`)
- Create `GEMINI.md` and `AGENTS.md` at project root with complete context, rules, and architecture for automatic agent discovery.

### Phase 3: Sanitization & Packaging (`.antigravity/` & `docs/chat_history/`)
- Write and run `scripts/export_and_sanitize_antigravity.py`:
  - Redacts sensitive keys from SQLite DBs and transcripts.
  - Packages `.antigravity/conversations/`, `.antigravity/brain/`, and `.antigravity/summaries.json`.
  - Generates readable Markdown logs in `docs/chat_history/`.

### Phase 4: Automated Restore Engine (`scripts/restore_antigravity.py`)
- Implement `scripts/restore_antigravity.py` with automatic OS detection, SQLite DB restoration, transcript mapping, and summary registration.
- Verify restore logic.

### Phase 5: Verification & Security Audit
- Execute comprehensive secret scan on staged changes.
- Verify git diff and staged files.

### Phase 6: Git Commit & Remote Push
- Stage all files, commit with conventional commit message.
- Push to `origin main` and verify remote state.
