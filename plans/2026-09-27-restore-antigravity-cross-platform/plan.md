# Implementation Plan: Cross-Platform Antigravity Session Restoration Engine

**Status:** ✅ COMPLETED & VERIFIED
**Goal:** Upgrade `scripts/restore_antigravity.py` and provide `scripts/restore_antigravity.ps1` for 100% seamless cross-platform session restoration across Windows Antigravity IDE, Antigravity CLI, and WSL/Linux.

---

## 1. Context & Brainstorm Contract (Reused)
- **Outcome:**
  - Both historical Antigravity sessions (`dc80f4a9-5ff0-4d5e-9a80-ffa4d985f271` and `d7d40cd3-2a98-4270-99bf-102cbafd0350`) are fully restored into active Antigravity environments on Windows (`antigravity-ide` and `antigravity`) and Linux/WSL (`antigravity-cli`).
  - Seamless 1-command execution on Windows (PowerShell) without needing native Python installed on PATH.
  - Smart URI adaptation from old Linux path (`/home/popeye/projects/trading-podcast`) to current Windows workspace (`file:///d:/Project/trading-podcast`).
- **Constraints:**
  - Windows environment does not have native Python on PATH (WSL has Python 3.12).
  - Must never corrupt or overwrite unrelated active conversations in `.gemini`.
  - 100% backward compatible with Linux/WSL/macOS.
- **Non-Goals:**
  - Re-extracting or re-sanitizing original data (already complete in `.antigravity/`).
- **Acceptance Criteria:**
  1. `scripts/restore_antigravity.py` auto-detects all existing `.gemini` profiles (`antigravity-ide`, `antigravity`, `antigravity-cli`).
  2. `scripts/restore_antigravity.ps1` runs natively in PowerShell without errors.
  3. Restored SQLite databases exist in `C:\Users\thieu\.gemini\antigravity-ide\conversations\`.
  4. Restored brain directories exist in `C:\Users\thieu\.gemini\antigravity-ide\brain\`.
  5. Both sessions are registered with correct local workspace URIs.

---

## 2. Implementation Phases

### Phase 1: Upgrade `scripts/restore_antigravity.py`
- Add multi-target discovery logic:
  - Check for `~/.gemini/antigravity-ide`, `~/.gemini/antigravity`, and `~/.gemini/antigravity-cli`.
  - Support restoring to multiple targets simultaneously if they exist.
- Implement URI adaptation:
  - Generate correct `workspace_uris` based on current project path (e.g. `file:///d:/Project/trading-podcast`).
- Safe SQLite summary updating with error resilience.

### Phase 2: Create Native Windows Helper `scripts/restore_antigravity.ps1`
- Pure PowerShell script requiring 0 external dependencies.
- Automatically copies session `.db` files and `brain/` folders to `$env:USERPROFILE\.gemini\antigravity-ide\` and `$env:USERPROFILE\.gemini\antigravity\`.
- If Python (native or WSL) is available, invokes `restore_antigravity.py` to register metadata; otherwise falls back gracefully.
- Displays clear success messages and resume commands.

### Phase 3: Update System Rules & Docs
- Update `GEMINI.md`, `AGENTS.md`, and `docs/chat_history/README.md` to document both:
  - Windows: `.\scripts\restore_antigravity.ps1`
  - Linux/WSL/macOS: `python3 scripts/restore_antigravity.py`

### Phase 4: Execute Restoration & Verify
- Execute the restoration process on the current host.
- Validate file presence and integrity:
  - Check `C:\Users\thieu\.gemini\antigravity-ide\conversations\`
  - Check `C:\Users\thieu\.gemini\antigravity-ide\brain\`
- Verify resume capability.
