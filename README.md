# How to Use

Quick start guide for generating subtitles for any video

## PART 0: PREREQUISITES

i) Python 3.9+ must already be installed and available on your PATH.
Generally you shouldn't worry about this, but check just to be sure.

### Linux/macOS:
python3 --version

### Windows (Command Prompt):
python --version

Confirm the printed version is 3.9 or higher.
If Python is not installed, download it from https://www.python.org/downloads/

#### Windows users: check "Add Python to PATH" during installation

#### For Linux Fedora: If you need to update, use: sudo dnf install python3.12
Then, instead of 'python3' (in the commands below) use whatever version you installed above (in this case, 'python3.12')

ii) You also need ffmpeg installed:

#### Linux: sudo dnf install ffmpeg
#### Windows: Download from https://ffmpeg.org/download.html or choco install ffmpeg
#### macOS: brew install ffmpeg

## PART 1: SETUP

### 1. Setup Commands

Open bash/cmd prompt inside this application folder, then run the appropriate command for your OS.

#### a) Linux / macOS (bash/zsh):
python3 -m venv venv && source venv/bin/activate

#### b) Windows (Command Prompt):
python -m venv venv && venv\Scripts\activate.bat

You should see (venv) appear at the start of your terminal prompt. If it doesn’t, the activation failed — try again or check the path.

### 2. Install GPU Support

Check your CUDA version with the following:

#### For NVIDIA GPUs:
nvidia-smi

#### For AMD GPUs (Linux only):
rocm-smi
OR
rocminfo

Look at the top-right corner of the output for CUDA/ROCm Version: XX.X / rocmX.X,
then match the appropriate cuXXX / rocmX.X index number. Note that the user needs to pick
the closest supported version at or below their max (https://pytorch.org/get-started/locally/)

#### For NVIDIA:
pip install torch --index-url https://download.pytorch.org/whl/cuXXX

#### For AMD:
pip install torch --index-url https://download.pytorch.org/whl/rocmX.X

If you have no GPU or prefer CPU-only:
Just skip this step entirely. The script will run on CPU (much slower, but it works).

### 3. Install Dependencies:
pip install -r requirements.txt

Verify GPU acceleration is still working:
python -c "import torch; print(torch.cuda.is_available())"

If it prints True → GPU acceleration is active, no action needed
If it prints False → torch fell back to CPU-only, re-run the appropriate pip install torch line from step 2a, then repeat this check

## PART 2: RUNNING

### 4. Re-running Later (skip if you just finished step 2)

Once set up, you don’t need to recreate the venv — just activate it each session.
Anytime you want to use the script, go inside this application folder, open a terminal, and activate the venv:

#### Linux/macOS: source venv/bin/activate

#### Windows (Command Prompt): venv\Scripts\activate.bat

You should see (venv) in your prompt. If it’s there, you’re ready to use the script.
To exit the venv when you're done: type 'deactivate', or just close the terminal.

The first time you run the script, it will download the Whisper model (500 MB – 3 GB depending on which size you choose). This happens once only — subsequent runs use the cached model and are much faster.

## PART 3: USING

### 5. Using for single videos or batch processing

#### a) Single video: python generate_subs.py "video.mkv"
Replace video.mkv with your actual video filename. You can also drag the script and video file into the terminal instead of typing the path.

#### b) Single Video with Options: Specify model size (small, medium, large-v3) and/or burn subtitles into the video:
python generate_subs.py "video.mkv" --model medium
python generate_subs.py "video.mkv" --burn
python generate_subs.py "video.mkv" --model large-v3 --burn

#### Model sizes:
small (~500 MB) — ~20-40× realtime, good accuracy
medium (~1.5 GB) — ~10-15× realtime, better accuracy (recommended)
large-v3 (~3 GB) — ~5-8× realtime, best accuracy

#### c) Batch Processing (Multiple Videos in a Folder)
- Finds all .mkv files in the current folder and subfolders
- Skips videos that already have subtitles (safe to re-run)
- Processes them one by one
- Logs everything to subtitle_log.txt so you can check results later

### Linux/macOS:
Activate the venv (see Part 2, step 4)
Navigate to the folder containing your videos: cd /path/to/my/shows
Run the batch script: /path/to/generate_subs_batches.sh
OR
If you’re inside the script folder: ~/path/to/venv/bin/activate && ./generate_subs_batches.sh
Wait for it to finish

### Windows:
Batch processing on Windows requires PowerShell.
Open PowerShell and run the script:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
.\generate_subs_batches.ps1 2>&1 | Tee-Object -FilePath subtitle_log.txt

### 6. Troubleshooting
"ModuleNotFoundError: No module named ‘faster_whisper’"
→ Make sure the venv is activated. You should see (venv) in your prompt. If not, re-run the activation command from Part 2, step 5a.
"nvidia-smi: command not found"
→ NVIDIA drivers aren’t installed. Either install them from nvidia.com or use CPU-only (skip the GPU setup in Part 1, step 2).
"ffmpeg: command not found"
→ ffmpeg isn’t installed. See the ffmpeg install instructions in Part 0.
Script is very slow
→ You’re running on CPU. This is normal. If you have a GPU, re-check Part 1, step 3 (verify GPU acceleration).
Subtitles are wrong/garbled
→ Try a larger or smaller model (e.g., --model medium or --model large-v3) for better accuracy.

That’s it. Thanks for using my script!
