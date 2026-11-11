"""Builds the vertical reel (1080x1920, H.264 + silent AAC, ~18 s) from the four scene JPEGs with ffmpeg."""
import subprocess
from pathlib import Path

SCENE_S, FADE_S, FPS = 5.0, 0.4, 30


def build_reel(scenes: list[Path], out: Path) -> Path:
    n = len(scenes)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for s in scenes:
        args += ["-loop", "1", "-t", str(SCENE_S + FADE_S), "-i", str(s)]
    args += ["-f", "lavfi", "-t", str(n * (SCENE_S - FADE_S) + FADE_S), "-i", "anullsrc=r=44100:cl=stereo"]
    frames = int((SCENE_S + FADE_S) * FPS)
    parts = []
    for i in range(n):  # upscale first so the slow zoom does not shimmer, then gentle Ken-Burns zoom-in
        parts.append(f"[{i}:v]scale=2160:3840,zoompan=z='min(1+0.00022*on,1.04)':x='iw/2-(iw/zoom/2)':"
                     f"y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]")
    last = "v0"
    for i in range(1, n):
        off = i * (SCENE_S - FADE_S)
        parts.append(f"[{last}][v{i}]xfade=transition=fade:duration={FADE_S}:offset={off}[x{i}]")
        last = f"x{i}"
    args += ["-filter_complex", ";".join(parts), "-map", f"[{last}]", "-map", f"{n}:a",
             "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "96k", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(args, check=True)
    return out
