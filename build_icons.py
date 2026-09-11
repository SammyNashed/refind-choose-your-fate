import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
def fpath(style):
    return subprocess.check_output(['fc-match', '-f', '%{file}', f'JetBrainsMono Nerd Font Mono:style={style}']).decode()
BIG, SMALL = 384, 56
GREEN = (0, 255, 65)
BLUE, RED = (40, 190, 255), (255, 45, 45)
ART_TOP, ART_BOTTOM, ART_MAXW = 16, 280, 260   # art box inside the 384 canvas (clears the hands)

def ascii_icon(txt, color, out):
    lines = open(txt).read().rstrip('\n').split('\n')
    cols = max(len(l) for l in lines); rows = len(lines)
    pitch = (ART_BOTTOM - ART_TOP) / rows
    size = min(pitch / 1.05, ART_MAXW / cols / 0.6)
    f = ImageFont.truetype(fpath('Bold'), round(size)); cw = f.getlength('M')
    pitch = min(pitch, size * 1.05)
    w, h = cw * cols, pitch * rows
    x0, y0 = (BIG - w) / 2, ART_BOTTOM - h
    layer = Image.new('RGBA', (BIG, BIG), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i, l in enumerate(lines):
        t = i / max(rows - 1, 1)            # fade toward the bottom, like the Matrix pills
        c = tuple(int(v * (1 - 0.35 * t)) for v in color)
        for j, ch in enumerate(l):
            if ch != ' ': d.text((x0 + j * cw, y0 + i * pitch), ch, font=f, fill=c + (255,))
    out_img = Image.new('RGBA', (BIG, BIG), (0, 0, 0, 0))
    a = layer.getchannel('A').filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
    shadow = Image.new('RGBA', (BIG, BIG), (0, 0, 0, 0)); shadow.putalpha(a.point(lambda v: min(255, v * 2)))
    out_img.alpha_composite(shadow)
    glow = layer.filter(ImageFilter.GaussianBlur(7))
    out_img.alpha_composite(glow); out_img.alpha_composite(glow); out_img.alpha_composite(layer)
    out_img.save(out, optimize=True)
    return y0, h

ascii_icon('src/logo_windows.txt', BLUE, 'icons/os_win.png')
y0, h = ascii_icon('src/logo_arch.txt', RED, 'icons/os_arch.png')
import shutil
for n in ['os_win8', 'os_win10', 'os_win11']: shutil.copy('icons/os_win.png', f'icons/{n}.png')
shutil.copy('icons/os_arch.png', 'icons/os_linux.png')

# selection: terminal-style corner brackets, drawn at exact tile size so rEFInd does not rescale them
def brackets(size, box, arm, width, out):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = box
    for (cx, cy, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.line([(cx, cy + dy * arm), (cx, cy), (cx + dx * arm, cy)], fill=GREEN + (255,), width=width, joint='curve')
    o = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    o.alpha_composite(im.filter(ImageFilter.GaussianBlur(4))); o.alpha_composite(im)
    o.save(out, optimize=True)
T0, T1 = BIG * 9 // 8, SMALL * 4 // 3
off = (T0 - BIG) // 2   # icon sits this far inside the tile
brackets(T0, (off + 50, off + ART_TOP - 12, off + BIG - 50, off + ART_BOTTOM + 10), 36, 4, 'selection_big.png')
o1 = (T1 - SMALL) // 2
brackets(T1, (o1 + 2, o1 + 2, o1 + SMALL - 3, o1 + SMALL - 3), 12, 3, 'selection_small.png')

# tool buttons: Nerd Font glyphs in Matrix green
glyphs = {'func_shutdown': '', 'func_reset': '', 'func_firmware': '',
          'func_exit': '', 'func_about': '', 'func_hidden': ''}
gf = ImageFont.truetype(fpath('Regular'), 34)
for name, g in glyphs.items():
    im = Image.new('RGBA', (SMALL, SMALL), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((SMALL/2, SMALL/2), g, font=gf, fill=GREEN + (230,), anchor='mm')
    out = Image.new('RGBA', (SMALL, SMALL), (0, 0, 0, 0))
    out.alpha_composite(im.filter(ImageFilter.GaussianBlur(3))); out.alpha_composite(im)
    out.save(f'icons/{name}.png', optimize=True)

# simulated boot screen, using rEFInd 0.14's layout math (verified against Matrix-rEFInd's own screenshot)
def preview(bgfile, out, selected=1):
    bg = Image.open(bgfile).convert('RGBA'); W, H = bg.size
    t0 = BIG * 9 // 8; t1 = SMALL * 4 // 3
    r0x = (W + 8 - (t0 + 8) * 2) // 2; r0y = H // 2 - t0 // 2
    selimg = Image.open('selection_big.png').resize((t0, t0))
    for i, ic in enumerate(['icons/os_win.png', 'icons/os_arch.png']):
        x = r0x + i * (t0 + 8)
        if i == selected: bg.alpha_composite(selimg, (x, r0y))
        bg.alpha_composite(Image.open(ic), (x + (t0 - BIG) // 2, r0y + (t0 - BIG) // 2))
    tools = ['func_reset', 'func_shutdown', 'func_firmware']
    r1x = (W + 8 - (t1 + 8) * len(tools)) // 2; r1y = r0y + t0 + 16
    for i, n in enumerate(tools):
        x = r1x + i * (t1 + 8)
        bg.alpha_composite(Image.open(f'icons/{n}.png'), (x + (t1 - SMALL) // 2, r1y + (t1 - SMALL) // 2))
    bg.convert('RGB').save(out, quality=90)
preview('background-1920x1200.png', 'preview-1920x1200.jpg')
preview('background.png', 'preview.jpg')
