#!/usr/bin/env bash
# Installs the theme into every rEFInd directory on the ESP and points each
# refind.conf at it.
#   sudo ./install.sh          # 16:9 background
#   sudo ./install.sh --16x10  # 1920x1200-style screens
#
# "Every" matters: rEFInd is often present twice -- EFI/refind/ (booted through
# its own NVRAM entry) and EFI/BOOT/ (the fallback BOOTX64.EFI the firmware
# boots when that NVRAM entry gets wiped, which some firmwares do on updates or
# resets). Each copy reads its own refind.conf and resolves theme paths
# relative to its own directory, so theming only one of them makes the theme
# "randomly" disappear depending on which one the firmware picked.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }
here="$(cd "$(dirname "$0")" && pwd)"

dirs=()
if [[ -n "${REFIND_DIR:-}" ]]; then
  dirs=("$REFIND_DIR")
else
  for esp in "${ESP_ROOT:-}" /boot /boot/efi /efi; do
    [[ -n $esp && -d $esp/EFI ]] || continue
    for d in "$esp"/EFI/*/; do
      d=${d%/}
      # a rEFInd install = a refind.conf next to a rEFInd binary (refind_x64.efi,
      # or the fallback BOOTX64.EFI when that file is rEFInd)
      [[ -f $d/refind.conf ]] || continue
      if compgen -G "$d/refind_*.efi" >/dev/null || grep -qa 'rEFInd' "$d"/BOOT*.EFI 2>/dev/null; then
        dirs+=("$d")
      fi
    done
    ((${#dirs[@]})) && break
  done
fi
((${#dirs[@]})) || { echo "couldn't find refind.conf; set REFIND_DIR=/path/to/EFI/refind"; exit 1; }

for refind in "${dirs[@]}"; do
  dest="$refind/themes/refind-choose-your-fate"
  mkdir -p "$dest/icons"
  cp "$here"/theme.conf "$here"/background*.png "$here"/selection_*.png "$dest/"
  cp "$here"/icons/*.png "$dest/icons/"
  if [[ ${1:-} == --16x10 ]]; then
    sed -i 's#^banner .*#banner themes/refind-choose-your-fate/background-1920x1200.png#' "$dest/theme.conf"
  fi
  conf="$refind/refind.conf"
  cp "$conf" "$conf.bak-$(date +%Y%m%d-%H%M%S)"
  sed -i 's|^\s*include\s\+themes/.*|# &|' "$conf"   # disable any previous theme
  echo "include themes/refind-choose-your-fate/theme.conf" >> "$conf"
  echo "Installed to $dest (backup of refind.conf saved next to it)."
done
