#!/usr/bin/env bash
# ============================================================
#  Font Organizer — Unix installer (Linux & macOS)
# ============================================================
#  Usage:
#    bash install.sh
#
#  What it does:
#    1. Verifies Python 3.10+
#    2. Clones (or updates) the repo
#    3. Installs the package with pip (editable install)
#    4. Symlinks the binary into /usr/local/bin for sudo access
#    5. Adds the pip scripts dir to PATH in your shell profile
# ============================================================

set -euo pipefail

REPO_URL="https://github.com/ZingerEngineer/font_organizer.git"
INSTALL_DIR="${HOME}/.font-organizer"
BINARY_NAME="font-organizer"
SYMLINK_PATH="/usr/local/bin/${BINARY_NAME}"

# ── colours ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}  ❯${RESET}  $*"; }
success() { echo -e "${GREEN}  ✔${RESET}  $*"; }
warn()    { echo -e "${YELLOW}  ⚠${RESET}  $*"; }
error()   { echo -e "${RED}  ✗${RESET}  $*" >&2; exit 1; }

banner() {
  echo -e "${CYAN}"
  echo "  ███████╗ ██████╗ ███╗   ██╗████████╗███████╗"
  echo "  ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝"
  echo "  █████╗  ██║   ██║██╔██╗ ██║   ██║   ███████╗"
  echo "  ██╔══╝  ██║   ██║██║╚██╗██║   ██║   ╚════██║"
  echo "  ██║     ╚██████╔╝██║ ╚████║   ██║   ███████║"
  echo "  ╚═╝      ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝"
  echo ""
  echo "  ██████╗ ██████╗  ██████╗  █████╗ ███╗   ██╗██╗███████╗███████╗██████╗ "
  echo "  ██╔══██╗██╔══██╗██╔════╝ ██╔══██╗████╗  ██║██║╚══███╔╝██╔════╝██╔══██╗"
  echo "  ██║  ██║██████╔╝██║  ███╗███████║██╔██╗ ██║██║  ███╔╝ █████╗  ██████╔╝"
  echo "  ██║  ██║██╔══██╗██║   ██║██╔══██║██║╚██╗██║██║ ███╔╝  ██╔══╝  ██╔══██╗"
  echo "  ██████╔╝██║  ██║╚██████╔╝██║  ██║██║ ╚████║██║███████╗███████╗██║  ██║"
  echo "  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝"
  echo -e "${RESET}"
  echo -e "${BOLD}  Installer — Linux / macOS${RESET}"
  echo ""
}

# ── 1. Python version check ──────────────────────────────────
check_python() {
  local py_bin
  for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
      local ver
      ver=$("$candidate" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null)
      if [[ "$ver" == "True" ]]; then
        py_bin="$candidate"
        break
      fi
    fi
  done

  if [[ -z "${py_bin:-}" ]]; then
    error "Python 3.10+ is required but was not found.\n  Install it from https://python.org or via your package manager."
  fi

  PY="$py_bin"
  local version
  version=$("$PY" -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')")
  success "Python ${version} found  (${PY})"
}

# ── 2. Git check ─────────────────────────────────────────────
check_git() {
  if ! command -v git &>/dev/null; then
    error "git is required but was not found.\n  Install it via your package manager (e.g. brew install git / apt install git)."
  fi
  success "git found  ($(git --version | awk '{print $3}'))"
}

# ── 3. Clone or update repo ──────────────────────────────────
clone_or_update() {
  if [[ -d "${INSTALL_DIR}/.git" ]]; then
    info "Repository already exists — pulling latest changes..."
    git -C "${INSTALL_DIR}" pull --ff-only
    success "Repository updated  (${INSTALL_DIR})"
  else
    info "Cloning repository..."
    git clone "${REPO_URL}" "${INSTALL_DIR}"
    success "Repository cloned  (${INSTALL_DIR})"
  fi
}

# ── 4. Install package ───────────────────────────────────────
install_package() {
  info "Installing font-organizer (editable)..."
  "$PY" -m pip install --quiet --editable "${INSTALL_DIR}"
  success "Package installed"
}

# ── 5. Symlink into /usr/local/bin for sudo access ───────────
create_symlink() {
  local bin_path
  bin_path=$(command -v "${BINARY_NAME}" 2>/dev/null || true)

  if [[ -z "$bin_path" ]]; then
    error "Could not find '${BINARY_NAME}' binary after installation.\n  Make sure pip's scripts directory is on PATH."
  fi

  if [[ "$bin_path" == "${SYMLINK_PATH}" ]]; then
    success "Symlink already in place  (${SYMLINK_PATH})"
    return
  fi

  info "Creating symlink in /usr/local/bin (requires sudo)..."
  if sudo ln -sf "${bin_path}" "${SYMLINK_PATH}"; then
    success "Symlink created  ${bin_path} → ${SYMLINK_PATH}"
  else
    warn "Could not create symlink — sudo permission may be required."
    warn "To add sudo support manually, run:"
    warn "  sudo ln -sf ${bin_path} ${SYMLINK_PATH}"
  fi
}

# ── 6. Add pip scripts dir to PATH ───────────────────────────
add_to_path() {
  local scripts_dir
  scripts_dir=$("$PY" -m site --user-scripts 2>/dev/null || true)

  # On system pip installs scripts go to a different location
  if [[ -z "$scripts_dir" ]] || [[ ! -d "$scripts_dir" ]]; then
    scripts_dir=$("$PY" -c "import sysconfig; print(sysconfig.get_path('scripts'))")
  fi

  # Detect current shell and profile file
  local profile_file=""
  local shell_name
  shell_name=$(basename "${SHELL:-bash}")
  case "$shell_name" in
    zsh)  profile_file="${ZDOTDIR:-$HOME}/.zshrc" ;;
    bash)
      if [[ "$(uname)" == "Darwin" ]]; then
        profile_file="${HOME}/.bash_profile"
      else
        profile_file="${HOME}/.bashrc"
      fi
      ;;
    fish) profile_file="${HOME}/.config/fish/config.fish" ;;
    *)    profile_file="${HOME}/.profile" ;;
  esac

  local export_line
  if [[ "$shell_name" == "fish" ]]; then
    export_line="fish_add_path \"${scripts_dir}\""
  else
    export_line="export PATH=\"${scripts_dir}:\$PATH\""
  fi

  if echo "$PATH" | grep -q "${scripts_dir}"; then
    success "Scripts directory already on PATH  (${scripts_dir})"
    return
  fi

  if [[ -f "$profile_file" ]] && grep -qF "${scripts_dir}" "${profile_file}"; then
    success "PATH entry already in ${profile_file}"
    return
  fi

  info "Adding ${scripts_dir} to PATH in ${profile_file}..."
  {
    echo ""
    echo "# font-organizer — added by installer"
    echo "${export_line}"
  } >> "${profile_file}"

  success "PATH updated in ${profile_file}"
  warn "Restart your terminal or run:  source ${profile_file}"
}

# ── main ─────────────────────────────────────────────────────
main() {
  banner
  check_python
  check_git
  clone_or_update
  install_package
  create_symlink
  add_to_path

  echo ""
  echo -e "${GREEN}${BOLD}  ✔  Font Organizer installed successfully!${RESET}"
  echo ""
  echo "  Usage:"
  echo "    font-organizer /path/to/fonts"
  echo "    font-organizer /path/to/fonts --dry-run"
  echo "    font-organizer /path/to/fonts --theme pick"
  echo "    sudo font-organizer /path/to/protected/fonts"
  echo ""
}

main "$@"
