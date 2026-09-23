"""
Program : The Sensor Anomaly Filter (Telemetry Audit Engine)
Purpose : Audits a stream of sensor batches for drift anomalies, filtering
          noise with `continue`, halting on an emergency signal with a
          flagged double `break`, and reporting a clean bill of health
          through the outer loop's `else` clause.
Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Module 1, Week 3, Problem Set 3.1

CONTROL-FLOW SUMMARY
--------------------
"ERR"    noise      -> `continue`, skip this reading, keep auditing the batch
"STOP"   emergency  -> set flag, `break` inner loop, then `break` outer loop
> 35.0   drift      -> report an anomaly, keep auditing
delta    spike      -> report a jump of more than 5.0 from the previous
                       numeric reading in the SAME batch

SUBMISSION NOTE: HOW shutdown_triggered PROTECTS THE ELSE CLAUSE
----------------------------------------------------------------
Python attaches a loop's `else` clause to that one specific loop, and skips it
only when that same loop is ended by its own `break`. The `break` inside the
reading loop therefore has no bearing on the outer clause at all: it exits one
batch and hands control straight back to the outer loop, which would happily
move on to the next batch, run out of batches, finish normally, and print the
all-clear even though a "STOP" had just been seen. The shutdown_triggered flag
closes that gap. It is set to True at the moment "STOP" is found, and is tested
immediately after the inner loop ends, in the outer loop's own body. Only that
second `break` can suppress the `else`. The summary therefore prints in every
case except the one where a "STOP" was encountered, which is exactly the
behaviour Requirement 5 asks for.
"""

telemetry_stream = [
    [22.5, 23.0, 22.8],
    [25.1, "ERR", 24.9],
    [30.2, 35.5, 40.1],    # Threshold breach
    [22.0, 22.1, "STOP"],  # Termination signal
]

SAFE_THRESHOLD = 35.0
SPIKE_THRESHOLD = 5.0

shutdown_triggered = False

for batch_id in range(len(telemetry_stream)):
    batch = telemetry_stream[batch_id]
    print(f"--- Auditing Batch {batch_id}: {batch} ---")

    # Declared inside the OUTER loop, so it resets to "no previous reading"
    # at the start of every batch and never carries over between batches.
    previous_value = None

    for reading in batch:
        # Order matters: control strings are tested before any numeric
        # comparison, so a string is never compared against a float.
        if reading == "STOP":
            print(f"Emergency Shutdown at Batch {batch_id}.")
            shutdown_triggered = True
            break                      # exits only the INNER loop

        if reading == "ERR":
            print(f"Noise ignored at Batch {batch_id} (ERR).")
            continue                   # skip to the next reading in the batch

        if isinstance(reading, (int, float)):
            if reading > SAFE_THRESHOLD:
                print(f"Anomaly Detected at Batch {batch_id}: {reading}")

            # Rolling Delta check (Challenge Task). Only runs once a numeric
            # reading has already been seen in THIS batch.
            if previous_value is not None:
                delta = abs(reading - previous_value)
                if delta > SPIKE_THRESHOLD:
                    print(f"Spike Detected at Batch {batch_id}: "
                          f"{previous_value} -> {reading} "
                          f"(Delta {delta:.1f})")

            # Updated only after a successful numeric comparison, so a
            # skipped "ERR" does not silently reset the delta tracking.
            previous_value = reading

    if shutdown_triggered:
        break                          # now exits the OUTER loop too
else:
    # Belongs to the OUTER for loop. Reached only when that loop ran to
    # completion without its own break - i.e. no "STOP" was ever seen.
    print("Audit Complete: No system-wide failures")
