from pathlib import Path


def ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def write_markdown(video: Path, segments: list[tuple[float, str]], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{video.stem}.md"
    lines = [f"# Transcript: {video.name}", "", f"Source video: `{video}`", ""]
    lines += [f"**[{ts(start)}]** {text.strip()}\n" for start, text in segments if text.strip()]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
