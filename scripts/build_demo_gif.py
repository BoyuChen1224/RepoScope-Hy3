from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BEFORE = ROOT / "assets" / "screenshots" / "before-analysis.png"
AFTER = ROOT / "assets" / "screenshots" / "overview.png"
OUTPUT = ROOT / "assets" / "demo" / "reposcope-hy3-demo.gif"

FRAME_WIDTH = 960
FRAME_HEIGHT = 600
CAPTION_HEIGHT = 58


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def frame(source: Image.Image, top: int, caption: str, number: str) -> Image.Image:
    visible_height = FRAME_HEIGHT - CAPTION_HEIGHT
    source_height = round(visible_height * source.width / FRAME_WIDTH)
    top = min(top, max(0, source.height - source_height))
    crop = source.crop((0, top, source.width, top + source_height))
    crop = crop.resize((FRAME_WIDTH, visible_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), "#0b0e0d")
    canvas.paste(crop, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, visible_height, FRAME_WIDTH, FRAME_HEIGHT), fill="#101513")
    draw.rectangle((0, visible_height, 6, FRAME_HEIGHT), fill="#c8ff5a")
    draw.text((24, visible_height + 15), number, font=font(18), fill="#c8ff5a")
    draw.text((68, visible_height + 14), caption, font=font(19), fill="#f4f0e8")
    return canvas


def main() -> None:
    before = Image.open(BEFORE).convert("RGB")
    after = Image.open(AFTER).convert("RGB")
    specifications = [
        (before, 0, "输入公开仓库与真实采用目标", "01"),
        (before, 570, "固定 commit，建立受限证据快照", "02"),
        (after, 560, "采集 README、许可证、测试与 CI 信号", "03"),
        (after, 1040, "Hy3 输出结论、风险、未知项与逐条引用", "04"),
        (after, 1550, "规则层验证证据，并展示六维得分与硬门槛", "05"),
        (after, 2070, "Hy3 语义复核逐条判断事实与证据蕴含", "06"),
    ]
    frames = [frame(*specification) for specification in specifications]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=[1700, 1800, 1900, 2300, 2300, 2500],
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
