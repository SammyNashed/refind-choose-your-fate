# rEFInd — Choose Your Fate

> *"You take the blue pill… the story ends, you wake up in Windows. You take the red pill… you stay in Arch, and I show you how deep the rabbit hole goes."*

A [rEFInd](https://www.rodsbooks.com/refind/) theme where Morpheus holds out your two operating systems — rendered as glowing neofetch-style ASCII art. **Windows is the blue pill, Linux is the red pill.**

![preview](preview.jpg)

## What's in it

- Morpheus background from **Matrix-rEFInd**, with a terminal-green `CHOOSE YOUR FATE_` headline
- ASCII-art OS icons in the spirit of **refind-efifetch**, re-rendered crisp at native size and tinted pill-blue / pill-red
- Terminal-style `⌜ ⌟` selection brackets and green reboot / shutdown / firmware buttons
- Native backgrounds for **16:9** (1920×1080) and **16:10** (1920×1200) screens, so the pills sit on the hands instead of drifting

## Install

```bash
git clone https://github.com/SammyNashed/refind-choose-your-fate
cd refind-choose-your-fate
sudo ./install.sh           # 16:9 screens
sudo ./install.sh --16x10   # 16:10 screens (1920x1200, 2560x1600)
```

The script finds **every** rEFInd install on the ESP — `EFI/refind/` and, if rEFInd is also your fallback loader, `EFI/BOOT/` — copies the theme into each one's `themes/` folder, comments out any previous `include themes/...` line, and backs up each `refind.conf` first.

### Getting the pills in the right hands

The theme is built for **exactly two** entries (`max_tags 2`). rEFInd shows manual `menuentry` blocks in file order, then auto-detected ones — so for Windows on the left (blue) and Linux on the right (red), declare both as manual entries with Windows first:

```
scanfor manual,external

menuentry "Windows" {
    icon   /EFI/refind/themes/refind-choose-your-fate/icons/os_win.png
    volume <PARTUUID of the Windows ESP>
    loader /EFI/Microsoft/Boot/bootmgfw.efi
}
menuentry "Arch Linux" {
    icon   /EFI/refind/themes/refind-choose-your-fate/icons/os_arch.png
    ...
}
```

> **Icon paths are absolute from the root of the ESP.** The `icon` lines above assume rEFInd lives in `EFI/refind/`. If yours only lives in `EFI/BOOT/` (common when it was installed with `refind-install --usedefault`), use `/EFI/BOOT/themes/refind-choose-your-fate/icons/...` instead — otherwise rEFInd can't find them and shows generic icons.

## Troubleshooting

**The theme (or the pills) disappears on some boots, then comes back.**
Your firmware is alternating between two copies of rEFInd: `EFI/refind/refind_x64.efi` (its NVRAM entry) and `EFI/BOOT/BOOTX64.EFI` (the fallback it boots when that entry gets deleted — some ASUS, HP and Lenovo firmwares do this after updates or resets). Each copy reads its own `refind.conf`, so a theme installed into only one of them seems to vanish. Re-run `sudo ./install.sh` (it now themes both), and check that both `refind.conf` files have the same entries.

**Windows boots straight away and rEFInd never shows up.**
Windows moved *Windows Boot Manager* to the front of the UEFI boot order, or the firmware dropped rEFInd's entry. From Linux:

```bash
efibootmgr                         # is there a "rEFInd" entry? what's BootOrder?
sudo efibootmgr --create --disk /dev/nvme0n1 --part <ESP partition number> \
     --loader '\EFI\refind\refind_x64.efi' --label rEFInd   # only if it's missing
sudo efibootmgr --bootorder XXXX,YYYY,...                     # rEFInd's number first
```

## Rebuilding the art

Everything except the Morpheus photo is generated: `python3 build_bg.py && python3 build_icons.py` (needs Pillow, JetBrainsMono Nerd Font, and the logo text in `src/`). `build_icons.py` also writes `preview*.jpg` using rEFInd's own layout math, so you can check placement without rebooting.

## Credits

- [Matrix-rEFInd](https://github.com/Yannis4444/Matrix-rEFInd) by Yannis Vierkötter — background and the pills-in-hands idea
- [refind-efifetch](https://github.com/CriticalPulsar/refind-efifetch) by Evan Nosich — ASCII-logo icons idea
- ASCII logos from [fastfetch](https://github.com/fastfetch-cli/fastfetch) / neofetch

MIT — see [LICENSE](LICENSE). The Morpheus still is from *The Matrix* (Warner Bros.) and isn't covered by the license.
