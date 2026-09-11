import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
def font(style, size):
    p = subprocess.check_output(['fc-match', '-f', '%{file}', f'JetBrainsMono Nerd Font Mono:style={style}']).decode()
    return ImageFont.truetype(p, size)
GREEN = (0, 255, 65)
def build(h, out):
    src = Image.open('src/matrix_background_1080.png').convert('RGB')
    pad = (h - 1080) // 2
    bg = Image.new('RGB', (1920, h))
    bg.paste(src, (0, pad))
    if pad:  # mirror-pad so the paper texture continues seamlessly
        bg.paste(ImageOps.flip(src.crop((0, 0, 1920, pad))), (0, 0))
        bg.paste(ImageOps.flip(src.crop((0, 1080 - pad, 1920, 1080))), (0, pad + 1080))
    # "CHOOSE YOUR FATE_" terminal headline with phosphor glow
    f = font('ExtraBold', 58); text = 'CHOOSE YOUR FATE'; spacing = 14
    widths = [f.getlength(c) for c in text]; cur = f.getlength('_')
    total = sum(widths) + spacing * (len(text) - 1) + spacing + cur
    x0 = (1920 - total) / 2; y = pad + 120
    layer = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x = x0
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=GREEN + (255,)); x += w + spacing
    d.text((x, y), '_', font=f, fill=GREEN + (255,))
    glow = layer.filter(ImageFilter.GaussianBlur(14))
    bg = bg.convert('RGBA')
    for _ in range(2): bg.alpha_composite(glow)
    bg.alpha_composite(layer)
    bg.convert('RGB').save(out, optimize=True)
build(1080, 'background.png')
build(1200, 'background-1920x1200.png')
