"""
Program : The Calibration Log Synthesizer
Purpose : Walks a calibration feed backwards, batch by batch, computing
          sums, maxima and minima entirely by hand - no length function,
          no aggregate builtins, no reverse slicing, and no functions of
          my own. The whole data flow stays visible in one top-down script.
Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Week 5, Problem Set 5

CONTROL-SIGNAL SUMMARY
----------------------
"IGNORE"  noise       -> skip this one reading, keep auditing the batch
"FAULT"   sensor dead -> abandon the rest of THIS batch, move to the next
"HALT"    catastrophe -> abandon this batch and stop the whole feed

SUBMISSION NOTE: WHICH BATCHES HAD THEIR ELSE BLOCK SKIPPED, AND WHY
---------------------------------------------------------------------
Two batches had their else block skipped: Batch 2 and Batch 4. In both, the
inner loop was ended early by a break - "FAULT" in Batch 2, "HALT" in Batch 4
- and Python skips a loop's else clause precisely when that loop is exited by
its own break. Their readings still counted toward Total Valid Readings,
because counting happens per reading as each one is processed, but neither
batch_sum ever reached the odd/even multiplier or the running checksum.
Batches 0 and 3 simply ran out of readings, which is normal loop completion,
so their else blocks fired and contributed 15.6 and 20.6 respectively. Batch 1
is a third case: it was empty, so the continue statement skipped it before the
inner loop ever started, and a loop that never begins has no else clause to
run or to skip.
"""

calibration_feed = [
    [201, 6.0, 9.5, "IGNORE", 4.0],
    [],
    [202, 11.2, "FAULT", 7.8, 5.5],
    [203, 14.0, 3.5, 8.25],
    [204, 2.75, "HALT", 6.0]
]

total_valid_readings = 0
total_checksum = 0.0
global_max = None
global_min = None
halt_triggered = False

feed_cursor = 0

while (current_slice := calibration_feed[feed_cursor:feed_cursor + 1]):
    batch = current_slice[0]

    # Requirement 1: emptiness by truthiness, never by a length call.
    if not batch:
        print(f"Batch {feed_cursor} is EMPTY. Proceeding.")
        feed_cursor += 1
        continue

    calibration_id = batch[0]
    print(f"Evaluating Batch {feed_cursor} (ID: {calibration_id})...")

    # Manual length counter - the length builtin is banned.
    batch_length = 0
    for _ in batch:
        batch_length += 1

    batch_sum = 0.0

    # Requirement 2: right-to-left traversal by index arithmetic alone.
    for i in range(1, batch_length):
        target_index = batch_length - i
        reading = batch[target_index]

        # Requirement 3: control signals are tested before any arithmetic,
        # so a string is never added to a float.
        if reading == "IGNORE":
            print(f"Signal IGNORE encountered at Batch {calibration_id}.")
            continue

        if reading == "FAULT":
            print("Signal FAULT detected. Suppressing batch "
                  f"{calibration_id}.")
            break

        if reading == "HALT":
            print("Signal HALT detected. Executing emergency protocol.")
            halt_triggered = True
            break

        # Requirement 4: metrics, accumulated and compared by hand.
        if isinstance(reading, (int, float)):
            total_valid_readings += 1
            batch_sum += reading

            if global_max is None or reading > global_max:
                global_max = reading

            if global_min is None or reading < global_min:
                global_min = reading
    else:
        # Requirement 5: attached to the INNER loop. Runs only when that
        # loop finished on its own, i.e. no FAULT and no HALT.
        if calibration_id % 2 == 0:
            total_checksum += batch_sum * 1.5
        else:
            total_checksum += batch_sum * 0.8

    if halt_triggered:
        break

    feed_cursor += 1

print()
print("=" * 40)
if halt_triggered:
    print("CALIBRATION COMPLETE: EMERGENCY TERMINATION")
else:
    print("CALIBRATION COMPLETE: FEED FULLY PROCESSED")
print("=" * 40)
print(f"Total Valid Readings Processed: {total_valid_readings}")
print(f"Global Calibration Checksum: {total_checksum:.1f}")
print(f"Maximum Reading Encountered: {global_max}")
print(f"Minimum Reading Encountered: {global_min}")
