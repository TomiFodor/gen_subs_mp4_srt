#!/usr/bin/env python3
#v3.1
"""
Generate an .srt subtitle file from any video file using faster-whisper.
Optionally hard-code (burn) the subtitles into a new video file.

Usage:
    generate_subs "video.mkv"                                           # soft subs only (.srt)
    generate_subs "video.mkv" --burn --model small|medium|large-v3      # also produce a hard-subbed video

VENV: With a venv, run this first:  python3.12 -m venv ~/.../whisper-env
                                    source ~/.../whisper-env/bin/activate

Dependencies (install with: pip install <package>):
    - faster-whisper
    - nvidia-cublas-cu12      (NVIDIA GPU support; skip if CPU-only)
    - nvidia-cudnn-cu12       (NVIDIA GPU support; skip if CPU-only)
    - tqdm                    (progress bar)

Also requires: ffmpeg (system package, usually pre-installed)

VENV: If done with a venv, anytime you want to use the script, just run:    source ~/whisper-env/bin/activate
                                                                            generate_subs whatever.mp4
When you're done (or want to use system Python again):                      deactivate

ALTERNATIVELY, change the first line at the top to #!/home/user/.../whisper-env/bin/python

Either way: sudo cp generate_subs.py /usr/local/bin/generate_subs
            sudo chmod +x /usr/local/bin/generate_subs
"""
import subprocess
import sys
from pathlib import Path
from tqdm import tqdm
from faster_whisper import WhisperModel

# --- Subtitle line-splitting settings ---
# gap_threshold  -- silence (seconds) between words that triggers a new line
# max_duration   -- max seconds a single line can stay on screen, even
#                    without a pause, purely for readability
# max_chars      -- max characters before forcing a new line (readability)
# end_grace      -- extra seconds ADDED onto a line's end time so it doesn't
#                    disappear the instant speech stops. Capped so it never
#                    overlaps into the next line.
GAP_THRESHOLD = 1.0
MAX_DURATION = 9.0
MAX_CHARS = 42
END_GRACE = 0.4

def transcribe(video_path, model_size="medium"):
    print(f"Loading {model_size} model and analyzing audio (this takes a moment)...")
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # word_timestamps=True gives per-word start/end times, not just per-segment.
    # This lets us trim subtitles to when speech actually happens, instead of
    # leaving text on screen during silent pauses.
    segments, info = model.transcribe(
        str(video_path),
        vad_filter=True,
        word_timestamps=True,
    )

    print(f"Detected language: {info.language} ({info.language_probability:.2f})")

    segments_list = []
    with tqdm(total=round(info.duration, 2), unit="sec", desc="Transcribing") as pbar:
        last_end = 0.0
        for segment in segments:
            segments_list.append(segment)
            pbar.update(segment.end - last_end)
            last_end = segment.end

    return info.language, segments_list

def format_time(seconds):
    # SRT timestamp format: HH:MM:SS,mmm (comma, not period, before ms)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = round((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def build_subtitle_lines(segments):
    """
    Rebuild subtitle lines from word-level timestamps instead of using
    Whisper's raw segments directly. This prevents subtitles from lingering
    on screen during silent pauses, while still giving text a small grace
    period so it doesn't vanish the instant speech ends.
    """
    lines = []
    current_words = []

    for segment in segments:
        # segment.words only exists because we passed word_timestamps=True
        for word in segment.words:
            if not current_words:
                current_words.append(word)
                continue

            prev_word = current_words[-1]
            gap = word.start - prev_word.end
            current_text = "".join(w.word for w in current_words)
            duration_if_added = word.end - current_words[0].start

            # Decide whether to cut a new line BEFORE adding this word
            if (gap > GAP_THRESHOLD
                    or len(current_text) > MAX_CHARS
                    or duration_if_added > MAX_DURATION):
                lines.append(current_words)
                current_words = [word]
            else:
                current_words.append(word)

    if current_words:
        lines.append(current_words)

    # --- Add a small grace period to each line's end time ---
    # This lets text linger a little instead of disappearing the instant
    # the last word ends, but never overlaps into the next line.
    for i, words in enumerate(lines):
        grace_end = words[-1].end + END_GRACE

        if i + 1 < len(lines):
            next_start = lines[i + 1][0].start
            grace_end = min(grace_end, next_start - 0.05)  # small buffer, no overlap

        words[-1].end = grace_end

    return lines

def generate_subtitle_file(video_path, language, segments, model_size):
    # Sidecar naming: "show.mkv" -> "show.en-medium.srt"
    srt_path = video_path.with_suffix(f".{language}-{model_size}.srt")

    lines = build_subtitle_lines(segments)

    with open(srt_path, "w", encoding="utf-8") as f:
        for index, words in enumerate(lines, start=1):
            start = words[0].start
            end = words[-1].end
            text = "".join(w.word for w in words).strip()

            f.write(f"{index}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{text}\n\n")

    return srt_path

def burn_subtitles_into_video(video_path, srt_path):
    # Hard-subs: re-encodes video with subtitles baked into the pixels.
    # Only useful for players/devices/uploads that don't support sidecar subs.
    output_path = video_path.with_name(f"{video_path.stem}_subbed.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles='{srt_path}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)
    return output_path

def run(video_path, model_size="medium", burn=False):
    language, segments = transcribe(video_path, model_size)
    srt_path = generate_subtitle_file(video_path, language, segments, model_size)
    print(f"\nSubtitles saved to: {srt_path}")

    if burn:
        output_path = burn_subtitles_into_video(video_path, srt_path)
        print(f"Hard-subbed video saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_subs <video> [--burn] [--model small|medium|large-v3]")
        sys.exit(1)

    video_path = Path(sys.argv[1])
    if not video_path.is_file():
        print(f"File not found: {video_path}")
        sys.exit(1)

    args = sys.argv[2:]
    burn = "--burn" in args
    model_size = "medium"
    if "--model" in args:
        model_size = args[args.index("--model") + 1]

    run(video_path, model_size=model_size, burn=burn)
