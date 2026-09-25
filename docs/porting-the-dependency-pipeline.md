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
| `.github/workflows/security-audit.yml` | weekly advisory scan, deliberately outside CI; reports in the run summary, never as an issue or a red run |

Copy them, then change the four things below. Do **not** create the `deps`
branch by hand — the promotion's bootstrap path cuts it from the default branch
on its first run, and doing it manually is how you end up with a branch cut from
something else.

## The five things that are repository-specific

1. **`workflows: ["…"]` in the gate's `workflow_run` trigger is the CI
   workflow's `name:`, not its filename.** Get this wrong and nothing reports an
   error: the gate simply never fires when CI finishes, and updates sit green
   until the weekly cron sweeps them. It is `"CI"` here and in Webdev,
   Marketplace and Desktop, `"CI Pipeline"` in Smart-Plan, and
   `"Build & Integration Smoke Test"` in MyDuoCards.
2. **`CI_WORKFLOW:` in the gate's `env` is the filename**, because it is read
   through `/actions/workflows/{file}/runs`. `ci.yml` everywhere except
   MyDuoCards, which is `build-and-smoke-test.yml`.
3. **CI must actually run on the updates.** Two shapes work:
   `pull_request:` with no branch filter (Webdev, MyDuoCards — a pull request
   into `deps` is built and a push to it is not, which is one run fewer), or
   `deps` listed in both `push:` and `pull_request:` (Smart-Plan, Marketplace).
   **Check `paths:` as well as `branches:`.** Desktop filtered on
   `.github/workflows/ci.yml`, so a Dependabot pull request bumping an action
   inside the automation workflows produced **no CI run at all** — and the gate
   reads CI's conclusion, so it would have waited forever while the sweep went
   red at fourteen days over a pull request that could never turn green. Any
   path filter must match `.github/workflows/**`.
4. **`security-audit.yml` is ecosystem-specific.** `pip-audit` here;
   `dotnet list package --vulnerable --include-transitive` for .NET, `npm audit`
   for Node, `composer audit` for Smart-Plan's backend. Development-scoped
   manifests included. It reports into the run summary and never fails the run,
   so it is safe to install even in a repository that already carries hundreds
   of open advisories. For .NET it is the only place transitive advisories show
   up: without a NuGet lock file the dependency graph lists direct packages only,
   so Dependabot alerts cannot see them.
5. **A repository with package families needs `groups`, and the cap depends on
   its target framework.** See the third blocker below.

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
4. **Advanced Security → Dependabot alerts enabled, Dependabot security updates
   disabled.** Alerts put advisories in the Security tab. Security updates
   always target the default branch and would bypass `deps`, so they stay off.
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

## Three blockers, all of them measured

**1. A CI job that commits back to the branch it ran on.** Marketplace's and
Desktop's `ci.yml` both ended a screenshot job with
`git config user.name "nupolovykh"` … `git push origin "HEAD:${TARGET_REF}"`,
with no condition on the branch. On `deps` that lands a commit with real file
changes and a human name — exactly what the promotion's guard refuses to reset,
correctly, because it cannot tell such a commit from someone's real work. The
job is fenced off instead:

```yaml
    if: >-
      (github.head_ref || github.ref_name) != 'deps' &&
      github.actor != 'dependabot[bot]'
```

Fence the job, never loosen the guard — the guard is the only thing protecting
the branch contract.

This also leaves a trap behind. Desktop's old integration branch had **already**
collected such commits, so `deps` cut from it carried stale copies of three
screenshots and of `ci.yml`. The promotion opened, GitHub reported `dirty`
(binary files changed on both sides do not three-way merge), and the next run
did the right thing on its own: `update-branch` failed on the conflict, the
fallback reset the branch and closed the pull request. One action bump was lost
and Dependabot will raise it again. That is the branch contract working, not a
failure — but expect it when the old branch has been written to by CI.

**2. Package families have to be grouped, and the cap is a target-framework
fact.** Measured in Marketplace: `Microsoft.EntityFrameworkCore.Design` 9.0.20
pulls `Relational` 9.0.20, which demands `EntityFrameworkCore >= 9.0.20` while
the project still pinned 8.0.30 — thirteen checks red. And
`Extensions.DependencyInjection` moved in one project and not in another that
references it, so the restore refused on both. Ungrouped, that is not one
blocked bump but a queue that cannot drain, because every pull request in it
breaks the same way.

The version cap is not caution, it is arithmetic, and it differs per repository
because the target frameworks differ. Check every `.csproj` rather than assuming:

| Repository | Projects | Highest EF Core that restores | Cap |
|---|---|---|---|
| Marketplace | `net8.0` | 9.x | `>= 10.0.0` |
| MyDuoCards | `net8.0` | 9.x | `>= 10.0.0` |
| Desktop | `net6.0`, mostly `net6.0-windows` | 7.x | `>= 8.0.0` |

`Microsoft.Extensions.*` is not capped in any of them: its 8.x, 9.x and 10.x
still ship `netstandard2.0` or `net8.0` assets.

**3. The old integration branch usually holds unpromoted work.** Every
repository that had been routing Dependabot at `security-features-main` had
updates merged there with no way out: eleven in Webdev, four in MyDuoCards, one
in Desktop, and Smart-Plan and Marketplace had ten and three waiting on a
promotion that could not complete. Cut `deps` from **that branch**, not from the
default branch:

```bash
git push origin origin/security-features-main:refs/heads/deps
```

The promotion's bootstrap creates `deps` from the default branch when it is
missing, which would throw all of that away. Dependabot would raise it again
eventually, but there is no reason to spend the cycle.

## Where each repository stands

All six are installed and ran a full cycle on 2026-09-12/13. Twenty-eight
updates that had been stuck reached `main`.

| Repository | Ecosystem | Landed | What was specific |
|---|---|---|---|
| QA-web | pip | — | the reference; the design was measured here first |
| Smart-Plan | composer, npm | 10 | upgrade from generation 1; CI named `CI Pipeline` |
| Webdev | npm ×6 | 11 | `deps` cut from the old branch; audit deliberately omitted at 414 advisories |
| Marketplace | nuget | 3 | screenshot job fenced; EF Core grouped, capped `>= 10` |
| MyDuoCards | nuget | 4 | CI name **and** filename both differ; EF Core grouped, capped `>= 10` |
| Desktop | nuget ×15 | 0 | `paths:` filter excluded the workflows; screenshot job fenced; EF Core capped `>= 8` for `net6.0`; stale screenshots on the old branch forced one reset |

`security-features-main` is dead in all three repositories that used it. Nothing
targets it and nothing reads it; the branches are still there and can be deleted
whenever.

EmployMe is out of scope while it is in active development — this pipeline is
built for repositories nobody is watching. HB-AI-Interface and WinAPI have no CI
at all, and need that before they need this.

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
2. CI runs on it;
3. the gate merges it and the log names the commit CI passed on;
4. the promotion opens one pull request with a **non-empty** diff;
5. after a human merges that, the promotion's next run reports either
   `behind … Fast-forwarded deps` or `adds content: no … Reset deps`, and closes
   the promotion pull request;
6. `deps` and the default branch end level, with no open pull requests.

Point 4 is the one that catches a bad port, and point 5 the one that catches a
bad comparison. Both were caught that way here.

## When the comparison says something you do not believe

`deps-promote.yml` prints its inputs before deciding. Read that group before
reasoning about anything:

```
branch comparison inputs
  split point 5b92a5b… tree dafa9fe678bb8ca98a23e1e3eb5dc4be7f1a3853
  main        67d55a4… tree 65f7b05f4a567199d256e29d4e82326f9d5e53cc
  deps        44bd258… tree dafa9fe678bb8ca98a23e1e3eb5dc4be7f1a3853
  verdict: nothing
  changed by deps: .github/workflows/ci.yml  split=72ecdccc main=ef84f978 deps=cfcc22ef
```

Three tree SHAs and one line per path it considered changed. That block was
added after an hour of arguing with a branch that kept merging `main` into
itself; it gave the answer on its first run — the verdict was being printed as
`"nothing"`, quotes included, because `jq` was called without `-r`, so the
comparison never matched and the branch could never be reset. The same block
then explained Desktop's conflict in one line: the old integration branch was
carrying stale screenshots.

Keep it. An automation nobody watches has to be able to explain itself.
