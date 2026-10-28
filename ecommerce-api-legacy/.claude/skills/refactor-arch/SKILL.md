# Skill: refactor-arch

You are an expert software architect. Your task is to analyze the current project, audit it for anti-patterns and code smells, and refactor it to a clean MVC architecture.

Execute the three phases below **sequentially**. Do NOT skip phases or combine them.

---

## PHASE 1 — PROJECT ANALYSIS

Read all source files in the current working directory. Do NOT modify any file in this phase.

Use the heuristics in `01-project-analysis.md` to detect:
- Programming language and version
- Framework and version (from requirements.txt, package.json, etc.)
- Dependencies
- Application domain (what the app does)
- Current architecture style
- Number and list of source files
- Database tables and schema

Print the following summary block:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <comma-separated list>
Domain:        <domain description>
Architecture:  <current architecture description>
Source files:  <N files analyzed>
DB tables:     <comma-separated table names>
================================
```

Then proceed immediately to Phase 2.

---

## PHASE 2 — ARCHITECTURE AUDIT

Using the anti-patterns catalog in `02-antipatterns-catalog.md` and the report template in `03-report-template.md`, cross-reference every source file against all anti-patterns.

For each finding:
- Record exact file path and line number(s)
- Classify severity: CRITICAL, HIGH, MEDIUM, or LOW
- Write a description and impact statement
- Write a concrete recommendation

Order findings by severity (CRITICAL first, then HIGH, MEDIUM, LOW).

Print the full audit report following the format in `03-report-template.md`.

After printing the report, **PAUSE** and ask:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Wait for user confirmation. If the user types anything other than "y" or "yes", stop and do not modify any files.

---

## PHASE 3 — REFACTORING

Only execute after explicit user confirmation from Phase 2.

Use `04-mvc-guidelines.md` to understand the target MVC structure.
Use `05-refactoring-playbook.md` for concrete transformation patterns with before/after examples.

### Steps:

1. **Create MVC directory structure** as defined in `04-mvc-guidelines.md`
2. **Migrate code** applying transformations from `05-refactoring-playbook.md` for each finding
3. **Preserve all existing functionality** — every original endpoint must continue to work
4. **Remove legacy files** after all new files are verified:
   - Delete every source file that existed before the refactor and whose contents have been fully migrated to the new MVC structure (e.g., the root-level `app.py`, `models/`, `services/`, `routes/`, `utils/` if replaced by `src/`).
   - Never delete `requirements.txt`, `package.json`, seed scripts, database files, `.env`, or any non-source asset.
   - If a file cannot be safely removed (e.g., it imports something not yet migrated), report the blocker and stop; do NOT leave the file in place silently.
5. **Update the project README** after legacy removal:
   - Replace any `python app.py` / `node app.js` instructions with the new entry point (e.g., `python src/app.py` or `node src/index.js`).
   - Update the directory tree in the README to reflect the post-refactor structure.
   - Preserve the seed/setup instructions.

### Validation:

After refactoring, validate:
1. Run the new entry point (`python src/app.py` or `node src/app.js`) and confirm it boots without errors
2. Verify that all original endpoints are still registered and respond correctly
3. Confirm legacy source files are no longer present in the project root or their original locations
4. **Verify every CRITICAL and HIGH finding from Phase 2 is resolved** — for each one, open the relevant file(s) in the new structure and confirm the specific code pattern is gone:
   - Hardcoded secret/credential → must now read from `os.environ` or `process.env` **with no fallback string**. A `|| 'change-me'` default is itself a known credential — replace with a fail-fast guard that calls `process.exit(1)` / `sys.exit(1)` if the variable is absent.
   - Weak hash (MD5, `badCrypto`) → must now use bcrypt/scrypt equivalent
   - Sensitive field in API response (password) → must be absent from `to_dict()` and all serializers
   - Duplicated business rule → must exist in exactly one shared service; controllers must import and call it
   - N+1 query inside a loop → the loop must be replaced with a single aggregated query (JOIN + group_by or equivalent)
   - If the finding is still present, fix it before proceeding — do NOT report "zero anti-patterns" with open HIGH/CRITICAL items.
5. **Verify no security-sensitive config has a known-string fallback** — grep the config file for patterns like `|| '...'` (JS) or `os.environ.get("...", "...")` (Python) on variables that hold secrets. Any such pattern is a residual CRITICAL regardless of whether the original finding was listed explicitly.

Print the final summary:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of new directory structure>

## Legacy Files Removed
<list of deleted files>

## README Updated
  ✓ Entry point updated to <new entry point>

## CRITICAL/HIGH Findings Verified
<for each CRITICAL/HIGH finding: ✓ <finding title> — resolved in <file:line>>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

If any validation step fails, report the error and do NOT mark the phase as complete.
