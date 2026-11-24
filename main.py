"""Entry program for make.fun news-image-20261123, version 3.

Copies the committed news image (one image summing up the world's news
of Monday 23 November 2026) to the output directory. Standard library only.

Why a third version exists: the first version's readable 27-story layout
ranked 187th of 7,226 in round 1, while the second version's denser
42-story layout fell to 2,676th of 9,643 in round 2. Density cost more
than it bought, so this version goes back to the first version's shape —
one hero, three medium cards, sixteen grid cards, seven ticker items —
with the full day's facts instead of the morning's. The artwork is
finished before grading, so this program never renders anything: it
checks the file and copies it.

Contract with the grader:
  - Output is exactly one file, /output/entry.png, a real PNG by its
    first bytes, at most 1 MiB (1,048,576 bytes).
  - Running this program twice must write identical bytes both times,
    so the copy is verified against the source before exiting.

How the checks are ordered, and why:
  - The format check reads only the signature bytes first, so a wrong
    file fails fast instead of being copied and rejected later.
  - The size check runs before the copy, for the same reason: a file
    over the ceiling never reaches the output directory.
  - The copy is followed by a full read-back of both files, compared
    byte for byte, which also catches a truncated write if the disk
    fills halfway through.
  - MAKEFUN_OUTPUT_DIR exists so the same program can be exercised
    locally against a scratch directory; in grading it defaults to
    /output and nothing else changes.
  - Exit codes: 0 means the copy landed and verified; 1 means the
    source failed a check or the copy mismatched. On success the only
    output is one line naming the file and its byte count.
  - Size note: this version's image is 131,656 bytes, roughly an
    eighth of the ceiling, so the readable layout costs nothing in
    budget terms — the density that hurt version 2 was never needed
    to fit.
"""
import os
import shutil
import sys

BYTE_CAP = 1_048_576
PNG_HEAD = b"\x89PNG\r\n\x1a\n"


def _complain(text):
    print(text, file=sys.stderr)
    return 1


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(folder, "entry.png")
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    dest = os.path.join(out, "entry.png")
    # Cheap format check first: only the signature bytes are read, so a
    # wrong file fails fast before the size check and the copy happen.
    with open(source, "rb") as stream:
        head = stream.read(len(PNG_HEAD))
    if head != PNG_HEAD:
        return _complain("entry.png is not a PNG file")
    if os.path.getsize(source) > BYTE_CAP:
        return _complain("entry.png exceeds the 1 MiB limit")
    shutil.copyfile(source, dest)
    # Second pass over both files: the grader runs this twice and both
    # runs must write identical bytes, so a truncated copy is caught
    # here instead of reaching the grader as a corrupt entry.
    with open(source, "rb") as stream:
        original = stream.read()
    with open(dest, "rb") as stream:
        copied = stream.read()
    if original != copied:
        return _complain("copy mismatch between entry.png and output")
    print(f"wrote {dest} ({len(copied)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
