# Devcontainer: running the Selenium labs locally to generate screenshots

## Why this exists

CI deliberately skips the Selenium labs ("no headless browser in CI"), and the
lab scripts themselves launch Chrome in normal (visible) mode — they call
`driver.maximize_window()` and never pass `--headless`. To generate result
screenshots you need a real display. This devcontainer gives you one via
**Xvfb** (a virtual X server) so the unmodified lab scripts run exactly as
written, just against a display no one has to look at.

## Setup

1. Copy the `.devcontainer/` folder into the root of `QA-web-labprojects-python`.
2. Open the repo in VS Code with the **Dev Containers** extension (or run
   `devcontainer up --workspace-folder .` from the CLI) and reopen in container.
   First build takes a few minutes (installs Chrome + Xvfb + Python deps).
3. The container installs root `requirements.txt` + `requirements-dev.txt`
   automatically, plus `lab11`/`lab12`'s own requirements files.

## Running a lab and capturing a screenshot

`postStartCommand` starts a persistent Xvfb server on `:99` every time the
container starts, and every shell already has `DISPLAY=:99` set — so you can
just run scripts directly:

```bash
python lab06/loading-to-browser.py
```

`lab06` already saves to `lab06/docs/screenshot.png` — that one just works.

If you're invoking a script from somewhere that isn't a devcontainer shell
(a one-off `docker exec`, CI, etc.) and can't rely on the persistent Xvfb
having started, use the `run-headed` wrapper instead — it starts its own
throwaway Xvfb for the one command and tears it down after:

```bash
run-headed python lab06/loading-to-browser.py
```

For labs that don't yet call `get_screenshot_as_file`, add the same pattern
lab06 uses right before `driver.quit()`:

```python
import os
os.makedirs("docs", exist_ok=True)
driver.save_screenshot("docs/screenshot.png")
```

(`get_screenshot_as_file` / `save_screenshot` are equivalent Selenium calls;
wrap in the existing `try/except WebDriverException` if the lab already has one.)

## Verifying the display works

```bash
ensure-xvfb && google-chrome-stable --version
```

This also runs automatically as `postStartCommand` when the container starts,
so a broken Chrome/Xvfb install shows up immediately instead of mid-lab.
`ensure-xvfb` is idempotent — it checks whether `:99` already has a live X
server (via `xdpyinfo`) and only starts one if it doesn't, so it's safe to
call by hand too.

## Notes

- `DISPLAY=:99` is set for every shell in the container (`remoteEnv` +
  `terminal.integrated.env.linux`), and `postStartCommand` runs `ensure-xvfb`
  on every container start so something is actually listening on it. If you
  ever do hit "cannot connect to display" (e.g. you attached before
  `postStartCommand` finished), just re-run `ensure-xvfb`.
- A bare Xvfb has no window manager, and `driver.maximize_window()` (used by
  several labs) needs one to carry out the actual window-state change —
  without it Chrome/chromedriver throws `unknown command: 'Runtime.evaluate'
  wasn't found`. Both `ensure-xvfb` and `run-headed` start a minimal
  `fluxbox` alongside their Xvfb for this reason — via `setsid`, since a
  plain backgrounded process can get killed along with the one-shot exec
  session `postStartCommand`/`run-headed` runs in (confirmed in practice:
  Xvfb survived, fluxbox didn't, so the WM silently never came up despite
  the script reporting success).
- Under rootless Podman (and sometimes Docker), Chrome's own internal sandbox
  can conflict with the container's own namespaces/seccomp and crash the
  renderer with `SIGILL` before Selenium ever gets a session — a confusing
  failure since it looks like a CPU/instruction-set problem rather than a
  sandbox one. The real `chrome` binary is renamed to `chrome-real` and
  replaced with a wrapper that always adds `--no-sandbox
  --disable-dev-shm-usage`, so this is handled transparently for every lab.
- `webdriver-manager`'s `ChromeDriverManager()` auto-detects the installed
  Chrome version and downloads a matching chromedriver on first run — no
  manual driver path config needed inside the container.
- Screenshots land wherever each lab script writes them (e.g.
  `lab06/docs/screenshot.png`); commit those output files normally from
  inside the devcontainer or after copying them out.
