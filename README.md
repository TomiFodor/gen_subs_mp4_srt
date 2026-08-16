# How to Use

*Quick start guide for generating subtitles for any video.*

---

## PART 0: PREREQUISITES

### **Python 3.9+**

Python 3.9+ must already be installed and available on your PATH. Generally you shouldn't worry about this, but check just to be sure.

#### **Linux/macOS:**
```
python3 --version
```

#### **Windows (Command Prompt)**
```
python --version
```

Confirm the printed version is 3.9 or higher. If Python is not installed, download it from https://www.python.org/downloads/

#### **Windows users:** check “Add Python to PATH” during installation.

#### **Linux Fedora:** If you need to update, use:
```
sudo dnf install python3.12
```
Then, instead of python3 (in the commands below) use whatever version you installed above (in this case, python3.12).

### **ffmpeg**

You also need ffmpeg installed:
| OS | Command |
| Linux | sudo dnf install ffmpeg |
| Windows | Download from ffmpeg.org or choco install ffmpeg |
| macOS | brew install ffmpeg

## PART 1: SETUP

### 1. Create and Activate Virtual Environment

Open bash/cmd prompt inside this application folder, then run the appropriate command for your OS.

#### Linux / macOS (bash/zsh):
```
python3 -m venv venv && source venv/bin/activate
```
#### Windows (Command Prompt):
```
python -m venv venv && venv\Scripts\activate.bat
```
You should see (venv) appear at the start of your terminal prompt. If it doesn’t, the activation failed — try again or check the path.

### 2. Install GPU Support

Check your CUDA/ROCm version with the following:

#### For NVIDIA GPUs:
```
nvidia-smi
```

#### For AMD GPUs (Linux only):
```
rocm-smi
```
or
```
rocminfo
```

Look at the top-right corner of the output for CUDA Version: XX.X / rocmX.X, then match the appropriate cuXXX / rocmX.X index number. Pick the closest supported version at or below your max — see pytorch.org/get-started/locally.

#### For NVIDIA
(replace cuXXX with your version, e.g. cu121):
```
pip install torch --index-url https://download.pytorch.org/whl/cuXXX
```

Alternatively, install it without the --index-url
```
pip install torch
```

#### For AMD
(replace rocmX.X with your version, e.g. rocm5.7):
```
pip install torch --index-url https://download.pytorch.org/whl/rocmX.X
```
#### No GPU / prefer CPU-only
Just skip this step entirely. The script will run on CPU (much slower, but it works).

### 3. Install Dependencies
```
pip install -r requirements.txt
```
Verify GPU acceleration is still working:
```
python -c "import torch; print(torch.cuda.is_available())"
```
- Prints True → GPU acceleration is active, no action needed ✓
- Prints False → torch fell back to CPU-only, re-run the appropriate pip install torch line from step 2, then repeat this check

## PART 2: RUNNING

### 4. Re-running Later (skip to PART 3: USING if you just finished Part 1)

Once set up, you don’t need to recreate the venv — just activate it each session. Anytime you want to use the script, go inside this application folder, open a terminal, and activate the venv:

#### Linux/macOS
```
source venv/bin/activate
```
#### Windows (Command Prompt)
```
venv\Scripts\activate.bat
```

- You should see (venv) in your prompt. If it’s there, you’re ready to use the script.
- To exit the venv when you’re done: type deactivate, or just close the terminal.
- First run note: The first time you run the script, it will download the Whisper model (500 MB – 3 GB depending on which size you choose). This happens once only — subsequent runs use the cached model and are much faster.

## PART 3: USING
### 5. Content Type Prompt
Every time you run the script, it will ask you what kind of content this is:

```
What type of content is this?
  1 - Movie / TV show (dialogue)
  2 - Song (lyrics)
  3 - Other / not sure
Enter 1, 2, or 3:
```
This tunes how subtitles are split around pauses — dialogue has sharp silences between lines, while songs have sustained notes and natural breathing pauses that shouldn’t trigger a line break. If unsure, 3 is a safe middle-ground default.

### 6. Single Video
```
python generate_subs.py "video.mkv"
```

Replace video.mkv with your actual video filename. You can also drag the script and video file into the terminal instead of typing the path.

### 7. Single Video with Options
Specify model size (small, medium, large-v3) and/or burn subtitles directly into the video:
```
python generate_subs.py "video.mkv" --model medium
python generate_subs.py "video.mkv" --burn
python generate_subs.py "video.mkv" --model large-v3 --burn
```

Model sizes:
| Model | Size | Speed | Accuracy |
| small | ~500 MB | ~20–40× realtime | Good |
| medium | ~1.5 GB | 10–15× realtime | Better (recommended) |
| large-v3 | ~3 GB | ~5–8× realtime | Best |

### 8. Batch Processing (Multiple Videos in a Folder)
The batch script will:
- Find all .mkv files in the current folder and subfolders
- Skip videos that already have subtitles (safe to re-run)
- Process them one by one
- Log everything to subtitle_log.txt so you can check results later

#### Linux/macOS
1. Activate the venv (see Part 2, step 4)
2. Navigate to the folder containing your videos:
```
cd /path/to/my/shows
```
3. Run the batch script:
```
/path/to/generate_subs_batches.sh
```
Or, if you’re inside the script folder:
```
~/path/to/venv/bin/activate && ./generate_subs_batches.sh
```
4. Wait for it to finish.

#### Windows

Batch processing on Windows requires PowerShell.
```
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
.\generate_subs_batches.ps1 2>&1 | Tee-Object -FilePath subtitle_log.txt
```

## PART 4: TROUBLESHOOTING
Problem	Solution
ModuleNotFoundError: No module named 'faster_whisper'	Make sure the venv is activated. You should see (venv) in your prompt. If not, re-run the activation command from Part 2, step 4.
nvidia-smi: command not found	NVIDIA drivers aren’t installed. Either install them from nvidia.com or use CPU-only (skip GPU setup in Part 1, step 2).
ffmpeg: command not found	ffmpeg isn’t installed. See Part 0, section ii.
Script is very slow	You’re running on CPU. This is normal. If you have a GPU, re-check Part 1, step 3 (verify GPU acceleration).
Subtitles are wrong/garbled	Try a larger model (e.g. --model medium or --model large-v3) for better accuracy.
Subtitle text lingers on screen after speech ends	Choose the correct content type when prompted (movie vs. song) — this affects how aggressively lines are split around pauses.

That’s it. Thanks for using my script!
