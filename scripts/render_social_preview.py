#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def load_font(size: int, *, serif: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if mono:
        candidates = [
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
        ]
    elif serif:
        candidates = [
            "/System/Library/Fonts/NewYork.ttf",
            "/System/Library/Fonts/Times.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Avenir.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for candidate in candidates:
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_rotated_word(
    base: Image.Image,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    angle: int = 0,
) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    text_img = Image.new("RGBA", (width + 16, height + 16), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((8, 2), text, font=font, fill=fill)
    rotated = text_img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    layer.alpha_composite(rotated, xy)
    base.alpha_composite(layer)


def rounded_badge(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    *,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    text_fill: tuple[int, int, int],
) -> None:
    width = int(draw.textlength(text, font=font)) + 34
    draw.rounded_rectangle((x, y, x + width, y + 42), radius=20, fill=fill)
    draw.text((x + 17, y + 8), text, font=font, fill=text_fill)


def make_hero_preview() -> Path:
    width, height = 1400, 860
    bg = (245, 234, 216)
    ink = (28, 31, 46)
    muted = (83, 88, 110)
    orange = (201, 95, 31)
    teal = (27, 148, 138)
    gold = (201, 150, 48)
    sky = (74, 113, 201)

    img = Image.new("RGBA", (width, height), bg + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.ellipse((-120, -60, 420, 460), fill=(227, 198, 123, 115))
    draw.ellipse((1020, -70, 1520, 390), fill=(182, 224, 218, 140))
    draw.ellipse((990, 520, 1490, 980), fill=(240, 200, 176, 120))
    draw.ellipse((440, 610, 860, 1030), fill=(194, 204, 230, 120))

    draw.rounded_rectangle((62, 70, 740, 792), radius=44, fill=(252, 247, 241, 214))
    draw.rounded_rectangle((795, 114, 1328, 694), radius=48, fill=(247, 239, 228, 255), outline=(220, 201, 180, 255), width=4)

    title_font = load_font(68, serif=True)
    subtitle_font = load_font(28)
    label_font = load_font(22)
    mono_font = load_font(25, mono=True)
    body_font = load_font(22)
    word_large = load_font(70)
    word_med = load_font(42)
    word_small = load_font(28)

    draw.text((106, 116), "Small Rust tools\nwith clear jobs.", font=title_font, fill=ink)

    subtitle = "A Homebrew tap for a few utilities worth keeping sharp. Not a giant toolbox. Just a few tools that do their work cleanly."
    lines: list[str] = []
    current = ""
    for word in subtitle.split():
        attempt = word if not current else f"{current} {word}"
        if draw.textlength(attempt, font=subtitle_font) < 500:
            current = attempt
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 338
    for line in lines:
        draw.text((110, y), line, font=subtitle_font, fill=muted)
        y += 38

    draw.rounded_rectangle((110, 520, 456, 572), radius=24, fill=(255, 252, 248, 235), outline=(222, 205, 183, 255), width=2)
    draw.text((130, 532), "brew tap acture/ac", font=mono_font, fill=ink)

    draw.rounded_rectangle((110, 590, 530, 642), radius=24, fill=(27, 31, 46), outline=(27, 31, 46))
    draw.text((130, 602), "brew install glyphweave", font=mono_font, fill=(247, 242, 236))

    draw.rounded_rectangle((110, 684, 238, 688), radius=2, fill=orange)
    draw.text((110, 708), "Kept small. Easy to scan. Boring to install.", font=body_font, fill=muted)

    draw.text((842, 146), "glyphweave / hanzi-sort", font=label_font, fill=muted)
    draw.rounded_rectangle((842, 182, 1218, 184), radius=1, fill=(220, 201, 180, 255))

    cloud = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cloud_draw = ImageDraw.Draw(cloud, "RGBA")
    cloud_draw.ellipse((856, 210, 1030, 390), fill=(238, 220, 176, 120))
    cloud_draw.ellipse((988, 250, 1216, 510), fill=(214, 229, 224, 138))
    cloud_draw.ellipse((1012, 198, 1236, 404), fill=(242, 216, 203, 130))
    img.alpha_composite(cloud)

    draw_rotated_word(img, "glyph", (892, 302), word_large, orange + (255,), -8)
    draw_rotated_word(img, "svg", (1120, 232), word_med, sky + (255,), 90)
    draw_rotated_word(img, "weave", (888, 226), word_small, ink + (255,), 0)
    draw_rotated_word(img, "seed", (1030, 520), word_small, teal + (255,), 0)
    draw_rotated_word(img, "cli", (1170, 346), word_small, orange + (255,), 0)
    draw_rotated_word(img, "typst", (1080, 392), word_med, ink + (255,), 0)
    draw_rotated_word(img, "hanzi", (864, 458), word_med, teal + (255,), -12)
    draw_rotated_word(img, "strokes", (1010, 556), word_small, gold + (255,), 0)
    draw_rotated_word(img, "brew", (1132, 520), word_small, gold + (255,), 0)
    draw_rotated_word(img, "sort", (892, 338), word_small, ink + (255,), 0)
    draw_rotated_word(img, "rust", (962, 548), word_small, sky + (255,), 90)

    out = ASSETS / "hero-preview.png"
    img.convert("RGB").save(out, format="PNG")
    return out


def make_social_preview() -> Path:
    width, height = 1280, 640
    bg = (238, 224, 203)
    panel = (248, 241, 232)
    ink = (26, 29, 44)
    muted = (84, 89, 110)
    orange = (209, 101, 34)
    teal = (26, 143, 135)
    gold = (209, 162, 58)
    sky = (54, 110, 198)

    img = Image.new("RGBA", (width, height), bg + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.ellipse((-100, -110, 330, 250), fill=(216, 190, 124, 130))
    draw.ellipse((930, -70, 1390, 320), fill=(186, 223, 218, 145))
    draw.ellipse((990, 378, 1380, 760), fill=(239, 199, 179, 120))

    draw.rounded_rectangle((52, 58, 660, 572), radius=42, fill=panel + (235,))
    draw.rounded_rectangle((728, 80, 1216, 558), radius=42, fill=(243, 234, 222, 255), outline=(217, 196, 171, 255), width=4)

    title_font = load_font(56, serif=True)
    subtitle_font = load_font(25)
    mono_font = load_font(24, mono=True)
    label_font = load_font(21)
    word_large = load_font(58)
    word_med = load_font(34)
    word_small = load_font(24)

    draw.text((92, 128), "Small Rust tools\nwith clear jobs.", font=title_font, fill=ink)
    draw.text((92, 304), "A Homebrew tap for a few utilities worth keeping sharp.\nNot a giant toolbox. Just a few tools that do their work cleanly.", font=subtitle_font, fill=muted)

    draw.rounded_rectangle((92, 446, 408, 494), radius=22, fill=(255, 251, 246, 225), outline=(223, 206, 185, 255), width=2)
    draw.text((112, 458), "brew tap acture/ac", font=mono_font, fill=ink)

    draw.text((784, 122), "glyphweave / hanzi-sort", font=label_font, fill=muted)
    draw.rounded_rectangle((784, 156, 1138, 158), radius=1, fill=(217, 196, 171, 255))

    cloud = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cloud_draw = ImageDraw.Draw(cloud, "RGBA")
    cloud_draw.ellipse((788, 166, 962, 352), fill=(235, 219, 174, 126))
    cloud_draw.ellipse((948, 190, 1168, 480), fill=(213, 226, 219, 138))
    cloud_draw.ellipse((976, 184, 1184, 392), fill=(239, 214, 201, 128))
    img.alpha_composite(cloud)

    draw_rotated_word(img, "glyph", (846, 262), word_large, orange + (255,), -8)
    draw_rotated_word(img, "svg", (1035, 200), word_med, sky + (255,), 90)
    draw_rotated_word(img, "weave", (980, 330), word_small, ink + (255,), 0)
    draw_rotated_word(img, "hanzi", (836, 372), word_med, teal + (255,), -13)
    draw_rotated_word(img, "typst", (1026, 332), word_med, ink + (255,), 0)
    draw_rotated_word(img, "strokes", (1032, 476), word_small, gold + (255,), 0)
    draw_rotated_word(img, "brew", (1092, 444), word_small, gold + (255,), 0)
    draw_rotated_word(img, "sort", (836, 276), word_small, ink + (255,), 0)
    draw_rotated_word(img, "cli", (1098, 280), word_small, orange + (255,), 0)
    draw_rotated_word(img, "tap", (944, 264), word_small, teal + (255,), 90)
    draw_rotated_word(img, "rust", (918, 480), word_small, sky + (255,), 90)

    out = ASSETS / "social-preview.png"
    img.convert("RGB").save(out, format="PNG")
    return out


def main() -> None:
    hero = make_hero_preview()
    social = make_social_preview()
    print(hero.relative_to(ROOT))
    print(social.relative_to(ROOT))


if __name__ == "__main__":
    main()
