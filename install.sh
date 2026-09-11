#!/usr/bin/env bash
# Installs the theme into rEFInd's directory on the ESP and points refind.conf at it.
#   sudo ./install.sh          # 16:9 background
#   sudo ./install.sh --16x10  # 1920x1200-style screens
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }
here="$(cd "$(dirname "$0")" && pwd)"
refind="${REFIND_DIR:-}"
if [[ -z $refind ]]; then
  for d in /boot/EFI/refind /boot/efi/EFI/refind /efi/EFI/refind; do [[ -f $d/refind.conf ]] && refind=$d && break; done
fi
[[ -n $refind ]] || { echo "couldn't find refind.conf; set REFIND_DIR=/path/to/EFI/refind"; exit 1; }
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
