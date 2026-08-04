#!/usr/bin/env python3
#v2.2
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
When you’re done (or want to use system Python again):                      deactivate

ALTERNATIVELY, change the first line at the top to #!/home/user/.../whisper-env/bin/python

Either way: sudo cp generate_subs.py /usr/local/bin/generate_subs
            sudo chmod +x /usr/local/bin/generate_subs
"""
import subprocess
import sys
from pathlib import Path
from tqdm import tqdm
from faster_whisper import WhisperModel

def transcribe(video_path, model_size="small"):
    print(f"Loading {model_size} model and analyzing audio (this takes a moment)...")
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # tuple unpacking. convert video path type to string. Voice Activity Detection.
    segments, info = model.transcribe(str(video_path), vad_filter=True)
    # f-string lets you embed variables inside {}. language, 2-digit probability
    print(f"Detected language: {info.language} ({info.language_probability:.2f})")
    segments_list = []
    with tqdm(total=round(info.duration, 2), unit="sec", desc="Transcribing") as pbar:
        last_end = 0.0
        for segment in segments:
            segments_list.append(segment)
            # Advance the bar by the amount of new audio this segment covers
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

def generate_subtitle_file(video_path, language, segments, model_size):
    # Sidecar naming: "show.mkv" -> "show.en.srt". VLC auto-loads it.
    srt_path = video_path.with_suffix(f".{language}-{model_size}.srt") # builds output filename
    with open(srt_path, "w", encoding="utf-8") as f:
        for index, segment in enumerate(segments, start=1):
            f.write(f"{index}\n")
            f.write(f"{format_time(segment.start)} --> {format_time(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")
    return srt_path

def burn_subtitles_into_video(video_path, srt_path):
    # Hard-subs: re-encodes video with subtitles baked into the pixels.
    # Only useful for players/devices/uploads that don't support sidecar subs.
    output_path = video_path.with_name(f"{video_path.stem}_subbed.mp4")
    cmd = [
        "ffmpeg", "-y", # program to run, if alrdy exists, overwrite w/o asking
        "-i", str(video_path), # input file
        "-vf", f"subtitles='{srt_path}'", # renders the SRT text onto the video pixels
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", # H.264 re-encode the video because we’re modifying the pixels. medium speed. constant rate factor (lower = better quality, bigger file size)
        "-c:a", "copy", # copy the audio stream unchanged
        str(output_path), #output filename
    ]
    subprocess.run(cmd, check=True) # actually runs the command, exit code raised
    return output_path

def run(video_path, model_size="small", burn=False): #burn=False is the default argument
    language, segments = transcribe(video_path, model_size) # Step 1: transcribe
    srt_path = generate_subtitle_file(video_path, language, segments, model_size) # Step 2: write .srt
    print(f"\nSubtitles saved to: {srt_path}")
    if burn: # Step 3: (optional): burn in
        output_path = burn_subtitles_into_video(video_path, srt_path)
        print(f"Hard-subbed video saved to: {output_path}")

if __name__ == "__main__": # only run this code when the file is executed directly, not when it’s imported
    if len(sys.argv) < 2:
        print("Usage: generate_subs <video> [--burn] [--model small|medium|large-v3]")
        sys.exit(1)
    # user didn’t provide any arguments. print usage instructions. exit with code 1
    video_path = Path(sys.argv[1]) # Grab video filename and wrap in Path object
    if not video_path.is_file():
        print(f"File not found: {video_path}")
        sys.exit(1)
    # Sanity check
    args = sys.argv[2:]
    burn = "--burn" in args # check if --burn flag is enabled
    model_size = "small"
    if "--model" in args:
        model_size = args[args.index("--model") + 1]
    run(video_path, model_size=model_size, burn=burn)
