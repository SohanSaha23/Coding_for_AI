"""
Program : The Multi-Dimensional Packet Scrambler (Data Rotation Engine)
Purpose : Takes a list representing a data packet and puts it through a fixed
          four-stage pipeline of transformations, using only built-in list
          operations - no external libraries.
Author  : SOHAN SAHA
Date    : 21/08/2026
Course  : Coding for AI - Module 1, week 3-4, Problem Set 3
"""

packet = [5, 12, 0, 8, 21, 34, 7, 19, 0, 3]

print("--- Stage 1: Input Validation ---")
print(f"Original packet: {packet}")

if packet and len(packet) >= 10:
    print("Validation passed. Processing packet...")

    print("\n--- Stage 2: Middle-Out Swap ---")

    midpoint = len(packet) // 2
    front_half = packet[:midpoint]
    back_half = packet[midpoint:]

    print(f"Front half: {front_half}")
    print(f"Back half : {back_half}")

    scrambled = back_half[::-1] + front_half
    print(f"Scrambled : {scrambled}")

    print(f"id(packet) == id(front_half) -> {id(packet) == id(front_half)}"
          "   # Expect: False")
    print("\n--- Stage 3: In-Place Correction ---")

    middle_index = len(scrambled) // 2
    print(f"Middle index {middle_index} holds: {scrambled[middle_index]!r}")

    if type(scrambled[middle_index]) is int:
        scrambled.insert(middle_index + 1, "SYNC-BIT")
        print(f"After sync-bit insertion: {scrambled}")
    else:
        print("Middle index is not an integer - sync-bit insertion skipped.")
    while 0 in scrambled:
        scrambled.remove(0)

    print(f"After zero removal      : {scrambled}")

    print("\n--- Stage 4: Memory Integrity Check ---")


    first, *middle, last = scrambled

    print(f"Original packet : {packet}")
    print(f"Final scrambled : {scrambled}")
    print(f"Header: {first}  Footer: {last}  Body length: {len(middle)}")
    print(f"Original packet intact: {packet == [5, 12, 0, 8, 21, 34, 7, 19, 0, 3]}")
else:
    print("Validation failed: packet is empty or too short.")

def scramble(data_packet):
    """Run the four-stage pipeline and return the final list.

    The caller's list is never modified: `data_packet[:]` takes a full slice,
    which allocates a new list, so the in-place stages below cannot reach the
    original object.
    """
    if not data_packet or len(data_packet) < 10:
        return []

    midpoint = len(data_packet) // 2
    front = data_packet[:midpoint]
    back = data_packet[midpoint:]
    result = back[::-1] + front

    middle_position = len(result) // 2
    if type(result[middle_position]) is int:
        result.insert(middle_position + 1, "SYNC-BIT")

    while 0 in result:
        result.remove(0)

    return result


print("\n=== Stretch Goal: Edge-Case Test Packets ===")

odd_packet = [5, 12, 0, 8, 21, 34, 7, 19, 0, 3, 99]
print(f"\nOdd-length input : {odd_packet}")
print(f"  front half len {len(odd_packet) // 2}, "
      f"back half len {len(odd_packet) - len(odd_packet) // 2} (unequal)")
print(f"  Output         : {scramble(odd_packet)}")
print(f"  Input intact   : {odd_packet == [5, 12, 0, 8, 21, 34, 7, 19, 0, 3, 99]}")

no_zero_packet = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"\nNo-zeros input   : {no_zero_packet}")
print(f"  Output         : {scramble(no_zero_packet)}")

float_packet = [1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"\nFloat-at-middle  : {float_packet}")
print(f"  Output         : {scramble(float_packet)}   # no SYNC-BIT inserted")
