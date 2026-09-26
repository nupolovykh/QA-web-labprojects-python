# Dependency updates

Updates land on `deps` without a human and reach `main` through one reviewed
pull request. Built for an **archived** project: nobody is watching, so the
design optimises for "keeps working unattended" over "clever".

```
Dependabot ─▶ PR ─▶ CI ──green on this exact commit──▶ squash-merged into deps
                                                              │
                                          promotion PR (CI runs on the result)
                                                              │
                                                       ◀ human merges ▶
                                                              ▼
                                                             main
                                                              │
                                        deps re-cut from main ┘
```

## Branch contract

| Branch | Who writes | History |
|---|---|---|
| `main` | humans only | amend-only — the archive's history stays flat |
| `deps` | bots only (Dependabot, Actions) | **disposable**, re-cut from `main` after every promotion |

`deps` holding nothing but bot commits is not a style rule, it is what makes the
rest work — see below.

## Why `deps` is reset, never merged

The usual design keeps the integration branch level by merging `main` into it.
That design breaks: `deps` exists to change lockfiles, `main` changes lockfiles,
and lockfiles conflict on nearly every line. GitHub answers `409 Merge conflict`,
no token changes that, and a human has to resolve a generated file by hand.

`deps` does not need merging, because **every bot commit is regenerable**. Reset
the branch and Dependabot re-reads the manifest, sees the old versions, and
raises the same bumps on its next scan. So the branch is thrown away and re-cut
from `main` instead of merged into. No merge, no conflict, no human.

The guard in `deps-promote.yml` is what keeps that assumption true: one non-bot
commit on `deps` and the workflow resets nothing and turns red. The single
exception is a commit that is provably `main`'s own amended-away tip (detected
via `github.event.before` on the force-push), which is debris, not work.

Every state the two branches can be in is handled. *Adds content* below is one
precise question: of the paths `deps` changed relative to the commit the two
branches split from, is there one where `main` does not already hold `deps`'s
content? It is answered by comparing blob SHAs in three trees — the split point,
`main`'s tip and `deps`'s tip — because a tree is addressed by its own SHA and
cannot be read stale.

Two simpler tests were tried first and both are wrong. *"The compare endpoint
reported changed files"* is cached and answers from before a merge that has
already landed. *"`deps`'s tree differs from `main`'s tip"* is true the moment
`main` carries anything `deps` never had, and *"`deps`'s tree differs from the
split point"* is true the moment `deps` carries a bump — including one `main`
has since taken by squash merge, which is exactly what a completed promotion
leaves behind. Each of the three opened a promotion for updates already on
`main`:

| `main` vs `deps` | Cause | Action |
|---|---|---|
| identical | steady state | nothing |
| ahead, adds content | updates collected | open/refresh the promotion PR |
| ahead, adds nothing | one full cycle's leftover merge | reset `deps` |
| behind | promotion merged with a merge commit | fast-forward `deps` |
| diverged, adds nothing | promotion squash-merged, or `main` moved on | reset `deps` |
| diverged, adds content, promotion open | `main` moved on under real bumps | merge `main` in through `update-branch`, keep the bumps |
| diverged, adds content, no promotion | same, nothing to merge through | open the promotion as it stands |
| diverged, amended tip | `git commit --amend` on `main` | reset `deps`, bumps re-raised |
| diverged, real human commit | someone pushed to `deps` | refuse, run turns red |

The `update-branch` row is the one that is easy to get wrong. Treating every
divergence as a rewrite and re-cutting the branch means the update queue
restarts from nothing on every single commit to `main` — and on every security
fix, once those are enabled. Only a genuine force-push re-cuts it now.

## Why there is no checkout

Neither automation workflow checks out the repository — every step is a `gh api`
call. There is no working tree and no on-disk script for a push to `deps` to
poison, so a job holding `contents: write` can never be made to execute code
that came from the branch it writes to. This is why no `ref:` pin is needed:
the class of problem it defends against does not exist here.

## How updates are grouped

Monthly, and per directory: one pull request carrying every minor and patch
bump, and one pull request per major. Minor and patch bumps rarely break
anything, so grouping them costs little and turns a weekly stream of single-bump
pull requests into one a month. Majors stay separate, so a major that breaks the
build blocks only itself while the group still lands.

Packages that have to move together — here `pytest` and its `pytest-*` plugins —
get a group of their own across all update types, so a major of one never
arrives without the others. `minor-and-patch` excludes the family's patterns, so
the two groups never edit the same line in one scan — two pull requests of one
scan touching the same line would conflict, and a conflicting pull request gets
no CI run.

## Why the vulnerability audit is not in CI

It answers a question about the global advisory database, not about the commit
under test. A newly published advisory turns every open pull request red at once
— including the bump that fixes it — and in a repository where green CI is what
merges updates, that stops updates from landing exactly when they matter most.
It runs weekly in `security-audit.yml`, blocks nothing, and writes its findings
into the run's summary and warnings rather than an issue.

## How silence is broken

An unattended repository's real failure mode is not a bad merge, it is a queue
that quietly stops moving. Failing the run is not an option for that: these
workflows run against the default branch, so a red run pins a check to whatever
commit `main` points at, permanently. Each problem goes into an issue that its
own workflow opens and closes:

| Issue | Opened by | Opened when | Closed when |
|---|---|---|---|
| *Dependency updates are stuck* | the weekly sweep | a Dependabot pull request has sat unmerged for 14 days, or passed CI and the merge was refused | the first sweep that finds the queue moving |
| *Dependency promotion is blocked* | `deps-promote.yml` | the branch contract is violated, or the promotion cannot be opened | the first promotion run that is not blocked |

The two use different markers on purpose. They used to share one, and the sweep
kept closing an issue the promotion was still blocked on, which the next
promotion run reopened as a new issue — every day.

A run turns red only when its issue cannot be filed. The issues are opened
through `DEPS_PAT`, so under the owner's account: GitHub does not notify you of
your own actions, and they show up in the Issues tab rather than in the inbox.

## Known limits

- **Security updates are switched off.** `target-branch` is a version-update
  option; a fix raised from a Dependabot alert goes to the default branch
  whatever `dependabot.yml` says, and nothing in a repository can redirect it.
  Left on, they would put bot commits on `main` past the promotion, so they are
  disabled in the repository settings. Advisories still show in the Security tab
  and in `security-audit.yml`'s summary, and the monthly version updates carry
  most fixes through `deps` anyway.
- **The gate is only as good as CI.** `CI` green on a bump means the labs lint
  and import cleanly, not that a Selenium or requests exercise still drives the
  site it was written against. Auto-merge does not make the suite stronger; it
  makes its gaps land faster.
- **Actions are pinned to major tags, not commit SHAs.** A retargeted tag would
  execute in a job holding a write token. Pinning to SHAs closes that, and
  Dependabot still updates them; it is the obvious next hardening step.
- **The automation runs on a personal access token, not `GITHUB_TOKEN`.** See
  *The token* below. Two limits disappeared with it and are recorded here so
  nobody reintroduces them: `GITHUB_TOKEN` may not write `.github/workflows/`,
  which left every action bump unmergeable whenever it sat behind its base; and
  it could not ask for help either, because `@dependabot rebase` from
  `github-actions[bot]` is answered *"Sorry, only users with push access can use
  that command"*. The promotion also no longer parks a second CI entry at
  `action_required`, because it is opened by a real account.
- **A sweep can be cancelled while it is queued.** `concurrency` with
  `cancel-in-progress: false` keeps exactly one run waiting per group; during a
  burst of events the waiting one is cancelled by the next. Nothing is lost —
  every sweep re-reads state from the API rather than from the event — so a
  `cancelled` sweep in the run list is expected, not a fault. Each push to
  `main` also spends one sweep that exits `skipped`, because `workflow_run`
  fires for CI runs of every event type and only `pull_request` ones matter.

## The token

`dependabot-auto-merge.yml` and `deps-promote.yml` authenticate as the repository
secret `DEPS_PAT`. Nothing else does: `ci.yml` and `security-audit.yml` never see
it.

That split is the reason a personal access token is acceptable here at all. Those
two are the only workflows that check out the repository and run third-party code
— `pip install`, `pip-audit`, the labs themselves. The two that hold the token do
no checkout at all; every step is an API call, so there is no working tree, no
script on disk that a push to `deps` could poison, and no package install that
could read the environment. Grep for `actions/checkout` in either file and the
count is zero. Keep it that way: adding a checkout step to a workflow that holds
`DEPS_PAT` hands the token to whatever the update being tested chooses to run.

What it must be able to do: read and write contents, read and write pull
requests, read and write Actions, and write files under `.github/workflows/`.

When it expires both workflows start failing with 401. The weekly sweep turns
red, which is the intended notification, but that is up to seven days of a queue
that has silently stopped. Renew it before the expiry date rather than after the
first red run.

## Repository settings this depends on

Not in the repository, so listed here:

1. **Settings → Secrets and variables → Actions**: `DEPS_PAT` — see above.
   Without it both automation workflows fail immediately with 401.
2. **Settings → Actions → General → Workflow permissions**: *Allow GitHub
   Actions to create and approve pull requests* — ticked. Without it the
   promotion pull request cannot be opened and the step fails with 403.
3. **Settings → General → Pull Requests**: squash merging enabled.
4. **Settings → Advanced Security → Dependabot alerts**: enabled, so advisories
   show in the Security tab. **Dependabot security updates**: disabled — they
   target `main` directly and would bypass `deps`; see *Known limits*.
5. **Branch protection on `main`: require a pull request, and tick *Do not allow
   bypassing the above settings*.** The second half is what actually stops a
   direct push by an administrator. Leave *Require approvals* unticked — its
   minimum is 1, and a repository with one maintainer cannot satisfy it. Do not
   add required status checks from a matrix: the check names carry the matrix
   values, so renaming one entry blocks every future pull request permanently.
   Rewriting history then needs a bypass-list entry, not just *Allow force
   pushes*: the pull-request requirement refuses any direct ref update, force or
   not, and answers `GH006 … Changes must be made through a pull request`.

## Putting it in another repository

`docs/porting-the-dependency-pipeline.md` — the four files, the four things that
differ per repository, the five settings that are not in the repository, and
where each of the other repositories currently stands.

## Running it by hand

```
Actions → Dependency promotion → Run workflow   # creates/realigns deps, opens the promotion PR
Actions → Dependency auto-merge → Run workflow  # sweeps; one log line per open update
```

Both are safe to run repeatedly: they read state and act only where there is
something to do.

## Verified end to end, 2026-09-12

Run against real updates rather than a description of them, twice. The second
round is the one recorded here, because the first exposed four defects in these
two workflows and the history carrying them was rewritten away; what is written
below was measured on the code as it now stands.

`pytest` was pinned one release back on purpose to give Dependabot something to
raise — every other pin was current, and `selenium` 4.49.0 was still inside
Dependabot's cooldown window at the time. By the time the update job ran, the
cooldown had expired, so the round exercised two updates instead of one, which
is the more interesting case: they race for the same file.

| UTC | What happened |
|---|---|
| 15:26:26 | `main` force-pushed: `Bypassed rule violations … Changes must be made through a pull request` |
| 15:26:36 | promotion: `deps is 'diverged' relative to main: 9 commit(s), adds content: yes` |
| 15:26:40 | `main was amended` → nine commits listed as `dropped` → `Reset deps to main` |
| 15:26:29 / 15:26:42 | CI on `main` and on `deps`: one run each |
| 15:28:54–15:29:16 | CI on the scaffolding pull request: 6/6 green in 22 s |
| 15:29:23 | merged, squash, no approval required |
| 15:29:28 | `Graph Update: pip in /.` — the graph refreshed, **no update job** |
| 15:29:33 | promotion: `behind … 0 commit(s)` → `Fast-forwarded deps` |
| 15:32:36 / 15:32:41 | Dependabot opened `selenium 4.47.0 → 4.49.0` and `pytest 9.1.0 → 9.1.1`, both against `deps` |
| 15:33:19 | the gate merged the `pytest` bump |
| 15:33:30 | the promotion opened, one update |
| 15:33:52 | a sweep was `cancelled` while queued — expected, see *Known limits* |
| 15:34:27 | the gate merged the `selenium` bump, which Dependabot had rebased after losing the race for `requirements.txt` |
| 15:34:30 | the gate handed off to the promotion, which refreshed it to two updates |
| 15:34:30 / 15:34:34 | CI on `deps`'s new head: **two** runs, one from the push and one from the pull request |
| 15:43:22 | the promotion merged, squash |
| 15:43:5x | promotion: `deps` re-cut from `main` |

`main` and `deps` ended level, with no open pull requests and `requirements.txt`
back where it started plus one real upgrade.

Four things the two rounds settled that guesswork had not:

- **A manifest change does not start an update job.** It produces only a
  `Graph Update`. An update job starts on the configured schedule, on a change
  to `.github/dependabot.yml`, or from *Insights → Dependency graph →
  Dependabot → … → Check for updates* on the manifest's row. Nothing else.
- **Two updates racing for one file need no help.** Dependabot rebased the
  loser by itself and the gate merged it 68 seconds later.
- **CI runs twice on `deps`'s head, not once and not four times.** Twice is the
  floor: the branch is both a pushed branch and the head of the promotion. Four
  was the two hand-written dispatches, and they are gone.
- **The amend path works.** It had never executed before this round; a history
  rewrite is exactly what it was written for, and it re-cut the branch instead
  of refusing it.

A fifth thing was settled by porting these workflows to a second repository
rather than by running them again here, and it is the reason the branch
comparison is now written against three trees. In `Smart-Plan-Mortgage-Calculator`
the promotion carrying ten updates was squash-merged, and the next run opened a
second promotion for the same ten. `main` there had also taken the workflow
upgrade itself, so `deps`'s tree matched neither `main`'s tip nor the split
point, and both of the cheap tests said the branch still had something to
promote. It did not. A test that is merely sufficient looks correct for as long
as nothing else lands on `main`.
