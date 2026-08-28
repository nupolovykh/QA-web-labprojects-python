FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# --- System deps: Google Chrome (stable) + Xvfb (virtual display) + fonts ---
# The lab scripts in this repo launch Selenium's Chrome driver in NON-headless
# mode (they call driver.maximize_window(), etc.), so instead of patching every
# lab to add --headless flags, we give the container a real (virtual) display
# via Xvfb and run scripts through `xvfb-run`. Chrome itself must be installed
# so webdriver-manager's ChromeDriverManager() can pair a matching chromedriver.
# The base image's Node feature preconfigures a dl.yarnpkg.com apt source
# whose signing key isn't installed (NO_PUBKEY 62D54FD4003F6525), which makes
# `apt-get update` fail outright. This project doesn't use Node/Yarn, so drop
# that source before updating rather than trying to fix its key.
RUN grep -rl "yarnpkg" /etc/apt/sources.list.d/ 2>/dev/null | xargs -r rm -f \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        ca-certificates \
        xvfb \
        xauth \
        x11-utils \
        fluxbox \
        wmctrl \
        fonts-liberation \
        fonts-noto-color-emoji \
        libnss3 \
        libxss1 \
        libasound2 \
    && wget -q -O /etc/apt/trusted.gpg.d/google-chrome.gpg.asc https://dl-ssl.google.com/linux/linux_signing_key.pub \
    && gpg --dearmor -o /etc/apt/trusted.gpg.d/google-chrome.gpg /etc/apt/trusted.gpg.d/google-chrome.gpg.asc \
    && echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Chrome's own internal Linux sandbox (separate from the container's own
# isolation) sets up nested namespaces + a seccomp-bpf filter, which can
# conflict with the outer container's own namespaces/seccomp under rootless
# Podman and crash the renderer outright (observed as SIGILL, not a sandbox-
# permission error, which is what makes it confusing to diagnose). Selenium
# resolves the real binary path directly (/opt/google/chrome/chrome), so
# that's the one place to inject --no-sandbox that's guaranteed to apply
# regardless of how it was launched. --disable-dev-shm-usage avoids a
# separate, unrelated crash class from /dev/shm defaulting to 64MB in
# containers, which Chrome's shared memory usage can exceed.
RUN mv /opt/google/chrome/chrome /opt/google/chrome/chrome-real \
    && printf '#!/usr/bin/env bash\nexec /opt/google/chrome/chrome-real --no-sandbox --disable-dev-shm-usage "$@"\n' \
        > /opt/google/chrome/chrome \
    && chmod +x /opt/google/chrome/chrome

# Persist an X display number all shells in the container agree on.
ENV DISPLAY=:99
ENV SCREEN_GEOMETRY="1920x1080x24"

# xvfb-run wrapper baked into PATH so `run-headed <command>` "just works"
# from any shell (VS Code terminal, postCreateCommand, CI, etc.) without
# remembering the xvfb-run flags every time. Useful for one-off invocations
# outside the devcontainer's own persistent Xvfb (see ensure-xvfb below).
# Also starts fluxbox against xvfb-run's own display first, for the same
# reason ensure-xvfb does below (driver.maximize_window() needs a WM).
RUN printf '#!/usr/bin/env bash\nset -e\nexec xvfb-run --auto-servernum --server-args="-screen 0 %s" \\\n    bash -c '"'"'setsid fluxbox </dev/null >/tmp/fluxbox-run-headed.log 2>&1 & disown; sleep 1; exec "$@"'"'"' bash "$@"\n' "$SCREEN_GEOMETRY" \
        > /usr/local/bin/run-headed \
    && chmod +x /usr/local/bin/run-headed

# Every shell in the container already sees DISPLAY=:99 (remoteEnv +
# terminal.integrated.env.linux in devcontainer.json), so plain `python
# lab06/loading-to-browser.py` should just work without an `run-headed`
# prefix. That only holds if something actually started an X server on :99
# first: this script does that once, persistently, for the life of the
# container. devcontainer.json's postStartCommand calls it on every start.
#
# A bare Xvfb has no window manager. driver.maximize_window() (several labs
# call it) relies on the window manager to carry out the EWMH window-state
# change; without one, Chrome/chromedriver throws "unknown error: JavaScript
# code failed / unknown command: 'Runtime.evaluate' wasn't found" instead of
# actually maximizing. fluxbox is a minimal WM that fixes this.
#
# postStartCommand runs this inside a one-shot exec session. `& disown` only
# stops the shell itself from SIGHUPing the child on exit — it does not
# detach it from that exec session's process group, which some container
# runtimes (rootless Podman included) tear down as a whole once the exec
# session ends. Observed in practice: Xvfb (backgrounded first, before
# anything else touched the group) survived, but fluxbox (backgrounded
# second) got its X connection killed moments later, so the WM silently
# never actually came up despite the script reporting success. `setsid`
# gives each process its own session, immune to that.
RUN cat > /usr/local/bin/ensure-xvfb <<'SCRIPT'
#!/usr/bin/env bash
set -e

if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    setsid Xvfb "$DISPLAY" -screen 0 "$SCREEN_GEOMETRY" </dev/null >/tmp/xvfb.log 2>&1 &
    disown
    for _ in $(seq 1 20); do
        xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
        sleep 0.5
    done
    xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 || {
        echo "ensure-xvfb: Xvfb did not come up on $DISPLAY" >&2
        exit 1
    }
fi

if ! DISPLAY="$DISPLAY" wmctrl -m >/dev/null 2>&1; then
    setsid env DISPLAY="$DISPLAY" fluxbox </dev/null >/tmp/fluxbox.log 2>&1 &
    disown
    for _ in $(seq 1 20); do
        DISPLAY="$DISPLAY" wmctrl -m >/dev/null 2>&1 && break
        sleep 0.5
    done
    DISPLAY="$DISPLAY" wmctrl -m >/dev/null 2>&1 || {
        echo "ensure-xvfb: fluxbox did not come up on $DISPLAY" >&2
        exit 1
    }
fi
SCRIPT
RUN chmod +x /usr/local/bin/ensure-xvfb

WORKDIR /workspaces/QA-web-labprojects-python
