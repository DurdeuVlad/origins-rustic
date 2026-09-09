# Collaboration & Contribution Guidelines (`Collaboration.md`)

This document defines the contribution process, branch naming conventions, review requirements, and quality standards for **Origins Rustic**.

---

## 1. Branch Strategy & Release Workflow

We operate under a release-branch model to protect active server configurations on `master`:

```
master (protected, production-ready, untouched directly)
  └── v2.0 (release integration branch)
        ├── fix/*     (targeted bug repairs)
        ├── docs/*    (specifications, ADRs, documentation)
        ├── test/*    (automated test harness & scripts)
        └── feature/* (new origins, classes, or power mechanics)
```

### Directives:
* **NEVER push directly to `master`**.
* All feature branches must branch off `v2.0` and merge back into `v2.0` via clean, non-fast-forward merge commits (`git merge --no-ff`) with descriptive commit messages.
* When `v2.0` achieves its milestone goals, it will be promoted to `master` through a collaborative Pull Request reviewed by repository maintainers.
* Existing GitHub issues (#1 through #14) represent historical tracks and open feature requests; do not close or overwrite them without explicit authority.

---

## 2. Commit Standards

Commits must follow Conventional Commits:
* `fix:` Patches for broken powers, missing tags, or incorrect registry paths.
* `feat:` Addition of new origins, classes, powers, or item modifiers.
* `docs:` Updates to technical specifications, ADRs, or guides.
* `test:` Addition of automated testing scripts, test functions, or server harness files.
* `refactor:` Restructuring JSON definitions without altering in-game player behavior.

---

## 3. Pull Request Delivery Contract

Every Pull Request submitted to `v2.0` or `master` must include the following mandatory sections in its description:

1. **Intent**: Why this change exists, what problem or player fantasy it addresses, and who benefits.
2. **Expectation**: What is observably true in-game or during datapack loading after this change.
3. **Acceptance Criteria**: Concrete checklist of testable criteria with evidence or current status.
4. **Non-Code Context**: RPG design rationale, compatibility limits, and team decisions that cannot be reconstructed from JSON diffs.
5. **Scope & Non-Goals**: Explicit boundaries on what was implemented and what was deliberately deferred.
6. **Verification & Risk**: Commands run, tests executed, game client/server checks, and any residual risks.

---

## 4. Feature Branch Lifecycle & Team Sign-Off

1. **Clean Integration Base**: Ensure `v2.0` has all completed predecessor branches integrated before branching.
2. **Dedicated Branch Creation**:
   ```bash
   git checkout v2.0
   git pull origin v2.0
   git checkout -b feature/<feature-name>
   ```
3. **Implementation & Static Validation**:
   * Implement all powers, origin tags, and loot tables without placeholder stubs.
   * Run automated JSON syntax validation:
     ```powershell
     Get-ChildItem -Recurse -Filter "*.json" | ForEach-Object { python -m json.tool $_.FullName > $null }
     ```
4. **Integration into `v2.0`**:
   * Merge back into `v2.0` via non-fast-forward merge (`git merge --no-ff feature/<feature-name>`).
   * Push to `origin/v2.0` for staging deployment on the test server.
5. **Team Sign-Off & Promotion to `master`**:
   * Work remains exclusively on `v2.0` until the milestone is complete and approved by the team.
   * Promotion to `master` occurs strictly through a formal Pull Request reviewed and approved by repository maintainers.

---

## 5. Power Authoring & Quality Gate Checklist

Before proposing any change to an origin, class, or power file:
1. **JSON Syntax**: The file must parse without syntax errors (`python -m json.tool <file>`).
2. **Registry Naming**:
   * Block tags must reside in `data/<namespace>/tags/block/` (singular).
   * Item tags must reside in `data/<namespace>/tags/item/` (singular).
   * Power definitions must reside in `data/<namespace>/origins/power/`.
   * Origin definitions must reside in `data/<namespace>/origins/origin/`.
3. **Power Tag Registration**:
   * Every new power must be registered in its corresponding tag file under `data/rustic/tags/origins/power/<name>_powers.json`.
   * The origin definition must reference the tag (`#rustic:<name>_powers`).
4. **No Placeholders**:
   * Never submit dummy files or incomplete `TODO` stubs.
   * If a class is not ready, leave it unlisted in `data/origins_classes/tags/origins/origin/class.json` until fully implemented and verified.
5. **Apoli / Origins Schema Compliance**:
   * Use valid 1.21 types (`origins:action_over_time`, `origins:attribute`, `origins:replace_loot_table`, etc.).
   * Check cooldowns, ambient flags, and particle visibility.
