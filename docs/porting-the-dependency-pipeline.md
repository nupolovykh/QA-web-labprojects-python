# Porting the dependency pipeline to another repository

This repository is the reference implementation. `docs/dependency-updates.md`
explains why it is shaped the way it is; this file is the checklist for putting
it somewhere else, and the record of what each of the other repositories still
needs.

Four files, one branch, and five settings that do not live in the repository.
Nothing about it is clever, and every step below exists because skipping it
produced a failure that took a while to diagnose.

## The four files

| File | What it is |
|---|---|
| `.github/dependabot.yml` | routes every ecosystem to `deps` via `target-branch` |
| `.github/workflows/dependabot-auto-merge.yml` | the gate: merges a Dependabot pull request into `deps` once CI is green **on that exact commit** |
| `.github/workflows/deps-promote.yml` | the promotion: opens one human-merged pull request `deps` → default branch, and realigns `deps` afterwards |
| `.github/workflows/security-audit.yml` | weekly advisory scan, deliberately outside CI |

Copy them, then change the four things below. Do **not** create the `deps`
branch by hand — the promotion's bootstrap path cuts it from the default branch
on its first run, and doing it manually is how you end up with a branch cut from
something else.

## The four things that are repository-specific

1. **`workflows: ["…"]` in the gate's `workflow_run` trigger is the CI
   workflow's `name:`, not its filename.** Get this wrong and nothing reports an
   error: the gate simply never fires when CI finishes, and updates sit green
   until the weekly cron sweeps them. It is `"CI"` here, `"CI Pipeline"` in
   Smart-Plan, `"Build & Integration Smoke Test"` in MyDuoCards.
2. **`CI_WORKFLOW:` in the gate's `env` is the filename**, because it is read
   through `/actions/workflows/{file}/runs`. `ci.yml` almost everywhere,
   `build-and-smoke-test.yml` in MyDuoCards.
3. **CI must run on `deps`.** Add the branch to the `push:` and `pull_request:`
   filters of the CI workflow. Without it nothing on `deps` is ever green, so
   nothing merges and the promotion has no checks — the pipeline looks installed
   and does nothing.
4. **`security-audit.yml` is ecosystem-specific.** `pip-audit` here;
   `dotnet list package --vulnerable --include-transitive` for the .NET
   repositories, `npm audit` for the Node ones, `composer audit` for Smart-Plan's
   backend. One matrix entry per manifest, development-scoped ones included —
   the Dependabot rule preset dismisses low-impact advisories there, so this
   audit is the only report they get.

## The five settings that are not in the repository

Per repository, in Settings. The pipeline cannot install these for itself and
fails differently for each one that is missing.

1. **Secrets and variables → Actions → `DEPS_PAT`.** A fine-grained token with
   *Contents* read+write, *Pull requests* read+write, *Actions* read+write and
   *Workflows* read+write, scoped to that repository. Absent, both automation
   workflows fail with 401 on their first call. One token can cover several
   repositories — select them all when creating it — but the secret has to be
   added to each repository separately.
2. **Actions → General → Workflow permissions → *Allow GitHub Actions to create
   and approve pull requests***. Absent, the promotion cannot open its pull
   request and says so in the log.
3. **General → Pull Requests → squash merging enabled.** The gate merges with
   `--squash`.
4. **Advanced Security → Dependabot alerts enabled.** Absent, no advisory is
   detected and the sweep's check for a security update stranded on the default
   branch can never fire, because no such pull request is raised.
5. **Branch protection on the default branch: require a pull request, and tick
   *Do not allow bypassing the above settings*.** The second half is what
   actually stops a direct push by an administrator. Leave *Require approvals*
   unticked — its minimum is 1, and one maintainer cannot satisfy it. Do not add
   required status checks from a matrix: the names carry the matrix values, so
   renaming one entry blocks every future pull request permanently.

Why a personal access token at all: `GITHUB_TOKEN` cannot merge a pull request
that edits `.github/workflows/` while that pull request is **behind** its base
(level with it, it can — which is why the failure looked intermittent), and it
cannot ask for help either, because `@dependabot rebase` from
`github-actions[bot]` is answered *"Sorry, only users with push access can use
that command"*. Every action bump was therefore unmergeable. The price is that
the token must never reach a workflow that checks out the repository; see
*The token* in `docs/dependency-updates.md`.

## Two blockers in the repositories as they stand

**A CI job that commits back to the branch it ran on.** Marketplace's `ci.yml`
and Desktop's `ci.yml` both end a screenshot job with
`git config user.name "nupolovykh"` … `git push origin "HEAD:${TARGET_REF}"`,
with no condition limiting it to the default branch — and Marketplace's CI
already runs on `deps`. That lands a commit on `deps` with real file changes and
a human author, which is exactly what the promotion's guard refuses to reset, so
the promotion goes red and stays red. Correctly. Restrict that job to the
default branch before switching the pipeline on.

**Smart-Plan and Marketplace run generation 1.** Their `deps-promote.yml` is
byte for byte the same file and predates everything verified here. They inherit,
in order of how much it matters:

- `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`, so the workflow-file problem above is
  still live in both;
- the decision taken from the file count in a cached `/compare` rather than from
  tree SHAs, and measured against the tip of the default branch rather than the
  merge base;
- `deps` never re-cut when it is ahead in commits but adds no content, so merge
  commits accumulate one per cycle;
- every divergence treated as a rewrite, so unpromoted bumps are dropped
  whenever anything lands on the default branch;
- a bot filter with no merge-commit exemption, which turns the guard red on the
  workflow's own merge;
- two redundant CI dispatches.

Porting to them is an upgrade, not an install: replace both workflow files with
this repository's current versions, add `DEPS_PAT`, and check what their `deps`
branches have accumulated in the meantime.

## Where each repository stands

| Repository | Pipeline | `deps` | Dependabot routed to | What it needs |
|---|---|---|---|---|
| QA-web (this one) | generation 2, verified twice | level with `main` | `deps` | nothing |
| Smart-Plan | generation 1 | exists, diverged | `deps` | upgrade both workflows, `DEPS_PAT`, settings |
| Marketplace | generation 1 | exists, diverged | `deps` | the same, **plus** guard the screenshot job |
| Webdev | gate only, no promotion | none | `security-features-main` | full install, retarget Dependabot |
| Desktop | gate only, no promotion | none | `security-features-main` | full install, retarget, guard the screenshot job |
| MyDuoCards | gate only, no promotion | none | `security-features-main` | full install, retarget, CI name and filename differ |
| EmployMe | none (`build.yml`, `labels.yml`) | none | — | out of scope while the project is in active development: this pipeline is built for repositories nobody is watching |
| HB-AI-Interface, WinAPI | no workflows at all | none | — | needs CI before it needs a dependency pipeline |

`security-features-main` is the dead end this exercise came out of: three
repositories still point Dependabot at a branch with no promotion behind it, so
their updates land there and stop. Retargeting to `deps` is part of the install,
not a separate task.

## Order of work, per repository

1. Fix the blockers above first. The guard is working correctly when it refuses,
   so installing the pipeline over a broken CI job just produces a red run you
   then have to interpret.
2. Add the five settings.
3. Copy the four files, adjusting the four repository-specific things.
4. Retarget `.github/dependabot.yml` to `deps` and add `deps` to the CI branch
   filters, in the same commit.
5. Run *Dependency promotion* by hand. It creates `deps` and exits.
6. Trigger an update: *Insights → Dependency graph → Dependabot → … → Check for
   updates* on one manifest row. A manifest change alone does not start an
   update job, and releases inside Dependabot's cooldown window are filtered out
   with a line in the log saying so, so an empty queue is not evidence of a
   broken port.

## What "it works" means, and how to see it

Six things, all readable from the Actions log rather than inferred:

1. a Dependabot pull request opens against `deps`, not the default branch;
2. CI runs on it once;
3. the gate merges it and the log names the commit CI passed on;
4. the promotion opens one pull request with a **non-empty** diff;
5. after a human merges that, the promotion's next run reports either
   `behind … Fast-forwarded deps` or `adds content: no … Reset deps`, and closes
   the promotion pull request;
6. `deps` and the default branch end level, with no open pull requests.

Point 4 is the one that catches a bad port. An empty promotion means the branch
comparison is wrong, and that shape cost two rounds of fixes here.
