"""
Program : The Telemetry Log Inspector
Purpose : Audits a delimited telemetry log - a plain-text CSV whose lines
          are timestamp,sensor_id,sensor_value - WITHOUT ever holding the
          file in memory at once. The file is pulled in fixed-size byte
          chunks through a callable iterator, complete lines are rebuilt
          across chunk boundaries with a leftover buffer, and only a
          running count and a running sum are kept, so memory use stays
          constant no matter how large the archive grows.

Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Python for AI - Week 12, Problem Set 12

SUBMISSION NOTE: SAME LOG, SMALLEST AND LARGEST CHUNK SIZE
---------------------------------------------------------------------
I ran my own sample log at chunk_size=1, which forces every record to be
split across several reads - a value like "14.5" arrives as four separate
one-byte chunks - and the call returned (3, 15.233333333333334). I then ran
the identical file at chunk_size=1000, comfortably larger than the whole
file, so the entire log arrived in a single read and no boundary fell
inside a record at all. That call returned (3, 15.233333333333334) as well.
The two results matched exactly, digit for digit, including the repeating
tail of the mean. Since the only thing differing between the two runs was
where the chunk boundaries landed, the match is direct evidence that the
leftover buffer is reassembling split lines correctly rather than losing or
double-counting the halves.
"""

import os
from typing import Optional, Tuple

# =========================================================================
# HEADER DOCUMENTATION (Deliverable ii)
# =========================================================================
# WHY A CHUNK BOUNDARY LANDS IN THE MIDDLE OF A RECORD
#
# chunk_size counts BYTES. It knows nothing whatever about records. The
# read simply hands back the next chunk_size bytes of the file and stops
# wherever that lands, which has no relationship at all to where a line
# happens to end. Records in this log are not even a fixed width - a
# timestamp plus a sensor id plus a value is a different length on almost
# every line - so there is no chunk_size that could be chosen to make the
# two line up. For any realistic file the boundary falls mid-record in
# nearly every chunk, and often mid-FIELD: at chunk_size=1 the value "14.5"
# arrives as four separate reads.
#
# WHY NAIVE PER-CHUNK PARSING CORRUPTS THE RESULT
#
# Treating each chunk as if it contained only whole lines silently
# manufactures bad data. A line cut in half becomes two fragments: the tail
# of one chunk and the head of the next. Each fragment has too few fields,
# so each is rejected as malformed - and the real record between them
# vanishes from the count entirely. Worse, a cut that happens to fall after
# the second comma leaves a fragment with exactly three fields and a
# truncated number, which parses cleanly as a plausible but wrong value. The
# count comes out too low and the mean comes out quietly wrong, with nothing
# raising an error to say so.
#
# HOW THE LEFTOVER BUFFER PREVENTS IT
#
# leftover carries the unfinished tail of one chunk forward into the next.
# Each time round the loop the new chunk is appended to whatever was held
# over, and the combined buffer is split on every newline. Splitting this
# way has a guarantee built into it: every piece EXCEPT the last ended at a
# real newline, so every one of them is a complete line and safe to process
# immediately. The last piece is the only doubtful one - the file might
# continue right after it - so it is not processed at all. It becomes the
# new leftover and is prepended to the next read, which is precisely what
# glues a split record back together.
#
# The star-unpacking assignment *complete_lines, leftover = ... is what
# separates "everything except the last piece" from "the last piece" in one
# line. And when the loop finally ends, because read() returned b"" and the
# callable iterator stopped, whatever sits in leftover is the genuine last
# line of the file - a real record with no newline after it, not an
# artefact - so it is processed explicitly after the loop rather than
# discarded.
# =========================================================================

SENTINEL = "END_OF_LOG"


def classify_line(raw_line: bytes, /) -> Tuple[bool, Optional[float]]:
    """Classify one fully-formed line pulled out of the byte stream.

    Returns (is_sentinel, value). value is None whenever the line is not a
    valid record, which covers a blank line, the sentinel itself, a line
    with the wrong field count, and a line whose value field is empty or
    non-numeric. All of those are rejected silently, without raising.
    """
    text = raw_line.decode("utf-8", errors="replace").strip()
    if not text:
        return False, None
    if text == SENTINEL:
        return True, None

    fields = text.split(",")
    if len(fields) != 3:
        return False, None

    try:
        return False, float(fields[2])
    except ValueError:
        return False, None


def process_log_stream(file_path: str, chunk_size: int,
                       /) -> Tuple[int, float]:
    """
    Reads a file in fixed-size byte chunks using a callable iterator.
    Returns total valid record count and running average value.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target path '{file_path}' not found.")

    valid_count = 0
    running_total = 0.0
    sentinel_seen = False
    leftover = b""

    with open(file_path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            leftover += chunk
            # Every piece but the last ended at a real newline, so every
            # piece but the last is a complete line. The last is held over.
            *complete_lines, leftover = leftover.split(b"\n")
            for raw_line in complete_lines:
                is_sentinel, value = classify_line(raw_line)
                if is_sentinel:
                    sentinel_seen = True
                elif value is not None:
                    valid_count += 1
                    running_total += value

    # The loop ended because read() returned b"". Whatever is still in
    # leftover is the last line of the file, with no newline after it.
    is_sentinel, value = classify_line(leftover)
    if is_sentinel:
        sentinel_seen = True
    elif value is not None:
        valid_count += 1
        running_total += value

    if not sentinel_seen:
        print(f"WARNING: '{SENTINEL}' not found - the file may be "
              f"truncated. Reporting the records that were readable.")

    # Computed once, at the end, from the two running figures alone.
    mean_sensor_value = running_total / valid_count if valid_count else 0.0
    return valid_count, mean_sensor_value


def write_sample_log(file_path: str, /, *, truncated: bool = False,
                     all_malformed: bool = False) -> None:
    """Write a sample log in binary mode, so line endings are exactly LF.

    Writing bytes matters here: text mode on Windows would silently turn
    every "\\n" into "\\r\\n", changing the byte length of every line and
    quietly altering where chunk boundaries fall.
    """
    lines = [
        b"2026-01-01T00:00:01,SENSOR_A,14.5",
        b"2026-01-01T00:00:02,SENSOR_B,NaN_READING",
        b"2026-01-01T00:00:03,SENSOR_C,",
        b"2026-01-01T00:00:04,SENSOR_A,16.2",
        b"2026-01-01T00:00:05,MALFORMED_ROW_TOO_FEW_FIELDS",
        b"2026-01-01T00:00:06,SENSOR_B,15.0",
        b"END_OF_LOG",
    ]
    if all_malformed:
        lines = [
            b"2026-01-01T00:00:01,SENSOR_A,NOT_A_NUMBER",
            b"2026-01-01T00:00:02,ONLY_TWO_FIELDS",
            b"2026-01-01T00:00:03,SENSOR_C,",
            b"END_OF_LOG",
        ]
    elif truncated:
        lines = lines[:-2]          # drops SENSOR_B,15.0 and END_OF_LOG

    with open(file_path, "wb") as file_obj:
        file_obj.write(b"\n".join(lines) + b"\n")


if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    SAMPLE_LOG = os.path.join(HERE, "sample_telemetry.log")
    TRUNCATED_LOG = os.path.join(HERE, "truncated_telemetry.log")
    MALFORMED_LOG = os.path.join(HERE, "malformed_telemetry.log")

    write_sample_log(SAMPLE_LOG)

    print("=" * 62)
    print("SECTION 6 TRACE - the same log at eight different chunk sizes")
    print("=" * 62)
    print(f"sample log is {os.path.getsize(SAMPLE_LOG)} bytes")
    print()
    for size in (1, 3, 7, 16, 32, 64, 128, 1000):
        print(f"chunk_size={size:>4} -> "
              f"{process_log_stream(SAMPLE_LOG, size)}")

    print()
    print("Identical at every size, which is the primary correctness test:")
    print("  all 8 results equal ->", len({
        process_log_stream(SAMPLE_LOG, size)
        for size in (1, 3, 7, 16, 32, 64, 128, 1000)
    }) == 1)
    print("  every size from 1 to the whole file also agrees ->", len({
        process_log_stream(SAMPLE_LOG, size)
        for size in range(1, os.path.getsize(SAMPLE_LOG) + 5)
    }) == 1)

    print()
    print("=" * 62)
    print("SECTION 7 EDGE CASES")
    print("=" * 62)

    print("(i)   a truncated file - last two lines removed, no sentinel")
    write_sample_log(TRUNCATED_LOG, truncated=True)
    print(f"        result -> {process_log_stream(TRUNCATED_LOG, 8)}")
    print("        the warning printed, no exception was raised, and the")
    print("        two readable records were still counted: mean of")
    print("        14.5 and 16.2 is 15.35.")

    print()
    print("(ii)  chunk_size=1, forcing every value to be split")
    print(f"        result -> {process_log_stream(SAMPLE_LOG, 1)}")
    print("        a value like '14.5' arrives as four separate reads.")

    print()
    print("(iii) a file that does not exist")
    try:
        process_log_stream(os.path.join(HERE, "no_such_file.log"), 64)
    except FileNotFoundError as error:
        print(f"        FileNotFoundError: {error}")
    print("        raised before any file handle was opened.")

    print()
    print("(iv)  a file where every line is malformed")
    write_sample_log(MALFORMED_LOG, all_malformed=True)
    print(f"        result -> {process_log_stream(MALFORMED_LOG, 5)}")
    print("        zero valid records, and the mean guard returned 0.0")
    print("        rather than raising ZeroDivisionError.")

    print()
    print("=" * 62)
    print("MEMORY BEHAVIOUR")
    print("=" * 62)
    print("Only three numbers are carried between chunks - a count, a sum")
    print("and the leftover fragment - so nothing scales with file size.")
    print("No f.read() or f.readlines() with no arguments appears anywhere.")

    for path in (SAMPLE_LOG, TRUNCATED_LOG, MALFORMED_LOG):
        os.remove(path)
    print()
    print("Sample logs removed. All checks completed.")
