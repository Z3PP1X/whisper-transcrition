import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
CHUNK_SECONDS = 600  # keeps each base64 request small


def find_videos(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in VIDEO_EXTS)


def extract_audio_chunks(video: Path, out_dir: Path) -> list[tuple[float, Path]]:
    """Strip the video track and split audio into mono 16 kHz mp3 chunks.

    Returns [(start_offset_seconds, chunk_path), ...].
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "chunk_%04d.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn",
         "-ac", "1", "-ar", "16000", "-b:a", "48k",
         "-f", "segment", "-segment_time", str(CHUNK_SECONDS), str(pattern)],
        check=True,
    )
    return [(i * CHUNK_SECONDS, p) for i, p in enumerate(sorted(out_dir.glob("chunk_*.mp3")))]
