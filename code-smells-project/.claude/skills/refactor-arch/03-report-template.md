# Reference: Audit Report Template

Use this exact format when generating the Phase 2 audit report. Fill in all placeholders.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project directory name>
Stack:   <Language> + <Framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [CRITICAL] <Finding Title>
File: <relative/path/to/file.py>:<start_line>-<end_line>
Description: <One or two sentences describing what the code does that is wrong.>
Impact: <One sentence on what an attacker or bug can cause.>
Recommendation: <One concrete sentence on what to change.>

### [CRITICAL] <Finding Title>
File: <relative/path/to/file.py>:<line>
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <Finding Title>
File: <relative/path/to/file.py>:<start_line>-<end_line>
Description: ...
Impact: ...
Recommendation: ...

[... repeat for all findings, ordered CRITICAL → HIGH → MEDIUM → LOW ...]

================================
Total: <N> findings
================================
```

---

## Rules

1. Every finding must reference an **exact file path** relative to the project root and **exact line numbers**. Do not use approximate ranges.
2. Findings must be ordered: all CRITICAL first, then all HIGH, then MEDIUM, then LOW.
3. The `Description` field must state the specific code pattern found, not a generic description.
4. The `Recommendation` field must be actionable (name the function, library, or pattern to use).
5. Do not include findings you are not certain about. Quality over quantity.
6. Include at minimum: 1 CRITICAL or HIGH finding, 2 MEDIUM findings, 2 LOW findings.
7. Check for deprecated API usage (anti-pattern #12) and include findings if detected.

## Example Finding (filled in)

```
### [CRITICAL] SQL Injection via String Concatenation
File: models.py:28
Description: Query built with string concatenation: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`. The `id` parameter comes from the URL and is cast to int by Flask, but 14 other queries in this file use the same pattern with non-integer inputs (nome, email, senha) that are NOT sanitized.
Impact: Attacker can bypass authentication, exfiltrate all user data including passwords, or drop tables.
Recommendation: Replace all string-concatenated queries with parameterized queries using `?` placeholders and tuple arguments.
```
