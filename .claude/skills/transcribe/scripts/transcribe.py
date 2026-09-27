# /// script
# requires-python = ">=3.9"
# dependencies = ["faster-whisper==1.2.1"]
# ///
"""Thai meeting recording (video or voice) -> transcript with [mm:ss] lines.

Runs on Mac and Windows through uv, no Python install needed:

    uv run .claude/skills/transcribe/scripts/transcribe.py <recording> <transcript.md>
    uv run .claude/skills/transcribe/scripts/transcribe.py check <transcript.md>

The first form transcribes on this computer (nothing is uploaded), writes the
transcript, then prints the lines a person must check. The second form only
prints those lines again, so the check can be re-run after fixing the file.

Names in core/team.md (first column of its tables) are passed to the model as
hints. The model still mishears Thai names, weekdays and dates, so every line
holding a number, a date word, a weekday (or a known mishearing of one), a time
or a team name is listed for checking.
"""

import datetime as dt
import os
import re
import sys
import time
from pathlib import Path

MODEL = "large-v3-turbo"
MODEL_SIZE_GB = 1.6
TEAM_FILE = Path("core/team.md")

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WEEKDAYS = ["จันทร์", "อังคาร", "พุธ", "พฤหัส", "ศุกร์", "เสาร์", "อาทิตย์"]
# heard in place of a weekday in the Thai test runs (เสาร์ -> สาว in 7 of 7)
WEEKDAY_MISHEARD = ["สาว", "เสา", "ซาว", "สุข", "สุก", "สุด", "ศุก", "พุทธ", "พุท", "พุด",
                    "พรือหัด", "พรหัส", "พะหัด", "พฤหัด", "จัน", "อังคาน", "อาทิต", "อาธิต"]
MONTHS = ["มกรา", "กุมภา", "มีนา", "เมษา", "พฤษภา", "มิถุนา", "กรกฎา", "กรกดา", "สิงหา",
          "กันยา", "กัญญา", "ตุลา", "พฤศจิกา", "พฤศจิ", "ธันวา",
          "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
DATE_WORDS = ["รุ่งนี้", "มะรืน", "เมื่อวาน", "อาทิตย์หน้า", "สัปดาห์หน้า", "เดือนหน้า", "สิ้นเดือน",
              "ต้นเดือน", "กลางเดือน", "ปีหน้า", "deadline", "เดดไลน์"]
TIME_WORDS = ["โมง", "ทุ่ม", "นาฬิกา", "เที่ยง", "ตีหนึ่ง", "ตีสอง", "ตีสาม", "ตีสี่", "ตีห้า"]

RE_NUMBER = re.compile(r"[0-9๐-๙]+(?:[.,:/-][0-9๐-๙]+)*")
# anything outside Thai, ASCII and Latin-1: the model slipped into another script or broke a character
RE_GARBLED = re.compile(r"[^\u0e00-\u0e7f\x00-\xff\u2000-\u206f]")
RE_WEEKDAY_MISHEARD = re.compile(
    r"(?:วัน|ก่อน|ภายใน|ทุก|ถึง|ช่วง|ตั้งแต่)\s*(?:" + "|".join(WEEKDAY_MISHEARD) + r")"
    r"|(?:" + "|".join(WEEKDAY_MISHEARD) + r")\s*(?:ที่\s*)?[0-9๐-๙]")


def mmss(seconds):
    s = max(0, int(seconds))
    return f"{s // 60:02d}:{s % 60:02d}"  # minutes keep counting past 60, like the sample transcript


def team_names(path=TEAM_FILE):
    """Leading cell of every markdown table row in core/team.md, minus header rows."""
    if not path.exists():
        return []
    names, lines = [], path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if re.fullmatch(r"\|[\s:|-]+\|?", line.strip()) or re.fullmatch(r"\|[\s:|-]+\|?", nxt):
            continue  # separator row, or the header row above it
        cell = line.strip().strip("|").split("|")[0].strip().strip("*")
        if cell and cell not in names and len(cell) <= 20:
            names.append(cell)
    return names


def reasons(text, names):
    """Each reason names the words that tripped it, so every one of them gets asked about."""
    found = []

    def add(kind, words):
        words = list(dict.fromkeys(words))  # drop repeats, keep order
        if words:
            found.append(kind + " " + " ".join(words))

    add("ถอดเพี้ยน", RE_GARBLED.findall(text))
    add("ตัวเลข", RE_NUMBER.findall(text))
    add("เดือน", [m for m in MONTHS if m in text])
    days = [w for w in WEEKDAYS if w in text] + RE_WEEKDAY_MISHEARD.findall(text)
    if days:  # a line with one weekday often lists more: name every misheard form on it too
        for w in WEEKDAY_MISHEARD:
            if w in text and not any(w in d for d in days):
                days.append(w)
    add("วัน", days)
    add("วันที่", [w for w in DATE_WORDS if w in text])
    add("เวลา", [w for w in TIME_WORDS if w in text])
    add("ชื่อ", [n for n in names if n in text])
    return found


def check(transcript, names):
    rows = []
    for n, line in enumerate(transcript.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"\[(\d+:\d\d)\]\s*(.*)", line)
        if m:
            why = reasons(m.group(2), names)
            if why:
                rows.append((n, m.group(1), m.group(2), why))
    kinds = {}
    for *_, why in rows:
        for w in why:
            k = w.split()[0]
            kinds[k] = kinds.get(k, 0) + 1
    print(f"\nต้องตรวจ {len(rows)} บรรทัด · " + " · ".join(f"{k} {v}" for k, v in kinds.items()))
    print("ชื่อในทีม (จาก core/team.md): " + (" ".join(names) if names else "ไม่มีไฟล์ core/team.md"))
    for n, ts, text, why in rows:
        print(f"บรรทัด {n} [{ts}] {text}   ← {' · '.join(why)}")
    return rows


def model_cached():
    try:
        from faster_whisper.utils import _MODELS
        from huggingface_hub import try_to_load_from_cache
        return isinstance(try_to_load_from_cache(_MODELS[MODEL], "model.bin"), str)
    except Exception:
        return False


def transcribe(media, out, names):
    from faster_whisper import WhisperModel

    if not model_cached():
        print(f"ครั้งแรก: ดาวน์โหลดโมเดลถอดเสียงประมาณ {MODEL_SIZE_GB} GB (ครั้งเดียว ครั้งต่อไปไม่ต้องโหลด)", flush=True)
    t0 = time.time()
    model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
    t1 = time.time()
    segments, info = model.transcribe(
        str(media), language="th", beam_size=1, vad_filter=True,
        condition_on_previous_text=False, temperature=0.0,  # no sampling retries: they wrote Korean and Japanese into Thai and doubled the time
        hotwords=" ".join(names) or None)
    print(f"ไฟล์ยาว {mmss(info.duration)} · บนเครื่องที่ทดสอบ ใช้เวลาประมาณหนึ่งในสามของความยาว"
          f" (ประมาณ {max(1, round(info.duration / 180))} นาที) เครื่องช้ากว่านี้อาจนานกว่า", flush=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    head = [
        f"# transcript · {media.stem}",
        "",
        f"ถอดจาก: {media.name} · ยาว {mmss(info.duration)} · ถอดเมื่อ {dt.date.today().isoformat()}",
        "วันที่ประชุม: ยังไม่ได้ใส่",
        "คนเข้า: ยังไม่ได้ใส่",
        "ยังไม่ได้ตรวจ: AI ถอดเสียงชื่อคน วัน วันที่ และตัวเลขผิดได้ ตรวจด้วย /transcribe ก่อนใช้",
        "ไม่มีชื่อคนพูด: เครื่องถอดเสียงไม่รู้ว่าใครพูดบรรทัดไหน",
        "",
    ]
    last, count = time.time(), 0
    with out.open("w", encoding="utf-8") as f:
        f.write("\n".join(head) + "\n")
        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            f.write(f"[{mmss(seg.start)}] {text}\n")
            f.flush()
            count += 1
            if time.time() - last > 30:
                print(f"ถึงนาที {mmss(seg.end)} จาก {mmss(info.duration)}", flush=True)
                last = time.time()
    t2 = time.time()
    print(f"เสร็จ: {count} บรรทัด · ถอด {mmss(t2 - t1)} สำหรับไฟล์ยาว {mmss(info.duration)}"
          f" (เร็ว {info.duration / max(t2 - t1, 1):.1f} เท่าของเวลาจริง) · โหลดโมเดล {t1 - t0:.0f} วินาที")
    print(f"เขียนไฟล์: {out}")


def main(argv):
    if len(argv) == 2 and argv[0] == "check":
        check(Path(argv[1]), team_names())
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 1
    media, out = Path(argv[0]).expanduser(), Path(argv[1])
    if not media.exists():
        print(f"ไม่เจอไฟล์: {media}")
        return 1
    if out.exists():
        print(f"มีไฟล์ {out} อยู่แล้ว ไม่เขียนทับ ตั้งชื่อใหม่ หรือลบไฟล์เดิมก่อน")
        return 1
    names = team_names()
    transcribe(media, out, names)
    check(out, names)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
