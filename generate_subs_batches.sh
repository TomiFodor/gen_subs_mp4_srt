# Bash script for batch processes

find . -name "*.mkv" | while read f; do
    if ! ls "${f%.*}".*.srt &>/dev/null; then
        generate_subs "$f"
    fi
done 2>&1 | tee ~/subtitle_log.txt
