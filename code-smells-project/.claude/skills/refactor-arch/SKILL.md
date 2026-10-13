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
4. **Remove original monolithic files** only after all new files are verified

### Validation:

After refactoring, validate:
1. Run `python app.py` or `node src/app.js` (depending on stack) and confirm it boots without errors
2. Verify that all original endpoints are still registered and respond correctly
3. Check that zero critical anti-patterns remain

Print the final summary:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of new directory structure>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

If any validation step fails, report the error and do NOT mark the phase as complete.
