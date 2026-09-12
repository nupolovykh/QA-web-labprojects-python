# Porting the dependency pipeline to another repository

This repository is the reference implementation. `docs/dependency-updates.md`
explains why it is shaped the way it is; this file is the checklist for putting
it somewhere else, and the record of what each of the other repositories still
needs.

The pipeline is four files, one branch and five settings that do not live in the
repository. Nothing about it is clever, and every step below exists because
skipping it produced a failure that took a while to diagnose.

## The four files

| File | What it is |
|---|---|
| `.github/dependabot.yml` | routes every ecosystem to `deps` via `target-branch` |
| `.github/workflows/dependabot-auto-merge.yml` | the gate: merges a Dependabot PR into `deps` once CI is green **on that exact commit** |
| `.github/workflows/deps-promote.yml` | the promotion: opens one human-merged PR `deps` → default branch, and realigns `deps` afterwards |
| `.github/workflows/security-audit.yml` | weekly advisory scan, deliberately outside CI |

Copy them from this repository, then change the four things below. Do **not**
create the `deps` branch by hand — the promotion's bootstrap path creates it from
the default branch on its first run, and doing it manually is how you end up with
a branch that was cut from something else.

## The four things that are repository-specific

1. **`workflows: ["…"]` in the gate's `workflow_run` trigger is the CI workflow's
   `name:`, not its filename.** Get this wrong and there is no error anywhere: the
   gate simply never fires on a finished CI run and updates sit green until the
   Monday cron sweeps them. In this repository it is `"CI"`; Smart-Plan's workflow
   is named `CI Pipeline` and MyDuoCards' is `Build & Integration Smoke Test`.
2. **`CI_WORKFLOW:` in the gate's `env` is the filename**, because it is read
   through `/actions/workflows/{file}/runs`. `ci.yml` almost everywhere,
   `build-and-smoke-test.yml` in MyDuoCards.
3. **CI must run on `deps`.** Add the branch to the `push:` and `pull_request:`
   branch filters of the CI workflow. Without it nothing on `deps` is ever green,
   so nothing merges and the promotion has no checks — the pipeline looks
   installed and does nothing.
4. **`security-audit.yml` is ecosystem-specific.** `pip-audit` here;
   `dotnet list package --vulnerable --include-transitive` for the .NET
   repositories, `npm audit` for the Node ones, `composer audit` for Smart-Plan's
   backend. Keep one matrix entry per manifest, including dev-scoped ones — the
   Dependabot rule preset dismisses low-impact advisories in development
   dependencies, so this audit is the only report they get.

## The five settings that are not in the repository

Per repository, in Settings. The pipeline cannot install these for itself and
fails in a different way for each one that is missing.

1. **Secrets and variables → Actions → `DEPS_PAT`.** A fine-grained personal
   access token with *Contents* read+write, *Pull requests* read+write, *Actions*
   read+write and *Workflows* read+write, scoped to that repository. Absent, both
   automation workflows fail with 401 on their first API call. One token can cover
   several repositories — select them all when creating it — but the secret itself
   has to be added to each repository separately.
2. **Actions → General → Workflow permissions → *Allow GitHub Actions to create
   and approve pull requests***. Absent, the promotion cannot open its pull
   request and says so explicitly in the log.
3. **General → Pull Requests → squash merging enabled.** The gate merges with
   `--squash`.
4. **Advanced Security → Dependabot alerts enabled.** Absent, no advisory is ever
   detected and the gate's check for a security update stranded on the default
   branch can never fire, because no such pull request is raised.
5. **Branch protection on the default branch: require a pull request, and tick
   *Do not allow bypassing the above settings*.** The second half is the one that
   actually stops an admin pushing straight to the branch; without it the rule is
   advisory. Leave *Require approvals* unticked — its minimum is 1, and a repository
   with one maintainer cannot satisfy it. Do **not** add required status checks
   from a matrix: the check names contain the matrix values, so renaming one entry
   blocks every future pull request permanently.

Why a personal access token at all: `GITHUB_TOKEN` cannot merge a pull request
that edits `.github/workflows/` while that pull request is **behind** its base
(level with the base it can, which is why this looked intermittent), and it cannot
ask for help either — `@dependabot rebase` from `github-actions[bot]` is answered
*"Sorry, only users with push access can use that command"*. Every action bump
was therefore unmergeable. The price is that the token must never reach a
workflow that checks out the repository; see *The token* in
`docs/dependency-updates.md`.

## Two blockers in the repositories as they stand

**A CI job that commits back to the branch it ran on.** Marketplace's `ci.yml`
and Desktop's `ci.yml` both have a screenshot job that ends in
`git config user.name "nupolovykh"` … `git commit` … `git push origin
"HEAD:${TARGET_REF}"`, with no condition restricting it to the default branch.
Marketplace's CI already runs on `deps`. That lands a commit on `deps` that has
real file changes and a human author, which is exactly what the promotion's guard
refuses to reset — so the promotion turns red and stays red, correctly. Restrict
that job to the default branch before switching the pipeline on.

**Smart-Plan and Marketplace run generation 1.** Their `deps-promote.yml` is byte
for byte the same file (blob `394f28f`) and predates everything verified on
2026-09-12. They inherit, in order of how much it matters:

- `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` — so the workflow-file problem above is
  still live in both;
- the decision taken from `files_changed` in a cached `/compare`, instead of tree
  SHAs, and compared against the tip of the default branch instead of the merge
  base;
- `deps` never re-cut when it is ahead in commits but adds no content, so merge
  commits accumulate one per cycle;
- a bot filter with no merge-commit exemption, which turns the guard red on the
  workflow's own `update-branch` merge;
- two redundant CI dispatches, which produced 24 check runs on one commit here.

Porting to them is therefore an upgrade, not an install: replace both workflow
files with this repository's current versions, add `DEPS_PAT`, and check what
their `deps` branches have accumulated in the meantime (they are at `5c5091d` and
`2f72bfd`, neither level with its default branch).

## Where each repository stands

| Repository | Pipeline | `deps` | Dependabot routed to | What it needs |
|---|---|---|---|---|
| QA-web (this one) | generation 2, verified | level with `main` | `deps` | nothing |
| Smart-Plan | generation 1 | exists, diverged | `deps` | upgrade both workflows, `DEPS_PAT`, settings |
| Marketplace | generation 1 | exists, diverged | `deps` | the same, **plus** guard the screenshot job |
| Webdev | gate only, no promotion | none | `security-features-main` | full install, retarget Dependabot |
| Desktop | gate only, no promotion | none | `security-features-main` | full install, retarget, guard the screenshot job |
| MyDuoCards | gate only, no promotion | none | `security-features-main` | full install, retarget, CI name and filename differ |
| EmployMe | none (`build.yml`, `labels.yml`) | none | — | out of scope while the project is in active development: the pipeline is built for repositories nobody is watching |
| HB-AI-Interface, WinAPI | no workflows at all | none | — | needs CI before it needs a dependency pipeline |

`security-features-main` is the dead end this whole exercise came out of: three
repositories still point Dependabot at a branch with no promotion behind it, so
their updates land there and stop. Retargeting to `deps` is part of the install,
not a separate task.

## Order of work, per repository

1. Fix the blockers above (the screenshot job) **first** — the pipeline's guard is
   working correctly when it refuses, so installing it over a broken CI job just
   produces a red run you then have to interpret.
2. Add the five settings.
3. Copy the four files, adjusting the four repository-specific things.
4. Retarget `.github/dependabot.yml` to `deps` and add `deps` to the CI branch
   filters, in the same commit.
5. Run `Dependency promotion` by hand. It creates `deps` and exits. Nothing else
   happens yet.
6. Trigger an update: *Insights → Dependency graph → Dependabot → … → Check for
   updates* on one manifest row. A manifest change alone does **not** start an
   update job — it only refreshes the graph. Releases inside Dependabot's cooldown
   window are filtered out and the log says so, so an empty queue is not proof
   that anything is wrong.

## What "it works" means, and how to see it

Six things, all readable from the Actions log rather than inferred:

1. a Dependabot pull request opens against `deps`, not the default branch;
2. CI runs on it once — not twice, not four times;
3. the gate merges it and the log names the commit CI passed on;
4. the promotion opens one pull request with a **non-empty** diff;
5. after a human merges that, the promotion's next run reports either
   `behind … Fast-forwarded deps` or `adds content: no … Reset deps`, and the
   promotion pull request is closed;
6. `deps` and the default branch end level, with no open pull requests.

Point 4 is the one that catches a bad port: an empty promotion means the branch
comparison is wrong, and that shape cost two rounds of fixes here.
