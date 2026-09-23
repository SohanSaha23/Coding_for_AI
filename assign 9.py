"""
Program : The Autonomous Payload Packet Parser
Purpose : Parses a spacecraft downlink packet - a nested, mutable list of
          [packet_id, sensor_readings, status_flag] - and returns a
          corrected, completely independent copy of the sensor readings,
          without ever modifying the caller's original packet.

          The parser is deliberately side-effect free, and its signature
          uses positional-only (/) and keyword-only (*) markers to control
          exactly how each parameter may be supplied.

Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Problem Set 7

SUBMISSION NOTE: WHAT HAPPENED ON THE TWO DELIBERATELY ILLEGAL CALLS
---------------------------------------------------------------------
Calling parse_payload(raw_packet=my_packet, delimiter="|") raised
TypeError: "parse_payload() got some positional-only arguments passed as
keyword arguments: 'raw_packet, delimiter'". Python named both offending
parameters, because the / marker places them before the positional-only
boundary and so forbids either from being supplied by name. Calling
parse_payload(my_packet, "|", 2) raised TypeError: "parse_payload() takes 2
positional arguments but 3 were given". The * marker means correction_offset
sits past the keyword-only boundary, so it cannot absorb a third positional
value and the function genuinely accepts only two. Both errors were raised at
call time, before the body ran, so neither illegal call could have touched the
packet. Together they confirm the signature enforces exactly the calling
convention that Section 3 specifies.
"""

# =========================================================================
# HEADER DOCUMENTATION (Deliverable 2)
# =========================================================================
# WHAT / AND * DO IN A FUNCTION SIGNATURE
#
# Both markers are fences in the parameter list. They carry no value of
# their own; they divide the parameters into regions that differ in HOW a
# caller is permitted to supply them.
#
# Everything written BEFORE the / is positional-only. Those parameters can
# only ever be filled by position, and writing their names at a call site is
# an error. Here that covers raw_packet and delimiter, so
# parse_payload(packet, "|") is the only legal way to pass them.
#
# Everything written AFTER the * is keyword-only. Those parameters can only
# be filled by name, never by sliding a third value along in the argument
# list. Here that covers correction_offset, so a caller must spell out
# correction_offset=2.
#
# WHY THAT MATTERS BEYOND SYNTAX PRACTICE
#
# Making raw_packet and delimiter positional-only keeps their NAMES an
# implementation detail. Nobody is depending on those spellings, so I can
# rename them later without breaking a single caller. Making
# correction_offset keyword-only removes a whole class of silent bug: a
# number cannot drift into the wrong slot, because a number on its own is
# simply refused. If a fourth, similarly typed parameter is added later, no
# existing call site can be quietly misread.
#
# WHY SLICING INSIDE A COMPREHENSION IS ENOUGH TO RULE OUT ALIASING
#
# A list comprehension does not edit anything. It constructs a brand-new
# list object and fills it with whatever the expression evaluates to, so the
# object I hand back was created during this call and no other name anywhere
# in the program refers to it. The caller's raw_packet[1] is a different
# object, and appending to or editing one can never show up in the other.
#
# The [:] slice reinforces that from the other direction: I iterate over a
# snapshot of the readings rather than over the caller's live list, so the
# loop cannot be disturbed by anything the caller does, and I never hold a
# reference to their list beyond the iteration.
#
# A shallow copy is sufficient HERE specifically because the sensor readings
# are floats, and floats are immutable. Sharing a reference to a float is
# harmless, since nothing can change a float in place - value + offset
# always builds a new number rather than editing the old one. If a reading
# were itself a mutable object, say a list of sub-samples, this same code
# would copy the outer list but still share the inner ones, and the
# independence guarantee would quietly fail. That is exactly the distinction
# between a shallow copy and a deep one, and it is why the brief calls this
# technique shallow.
# =========================================================================


def parse_payload(raw_packet: list, delimiter: str, /, *,
                  correction_offset: int = 0) -> tuple:
    """Return (packet_id, corrected_sensors) without touching raw_packet.

    raw_packet and delimiter are positional-only; correction_offset is
    keyword-only and defaults to 0. The corrected sensor list is always a
    new object, built by slicing inside a comprehension.
    """
    status_tokens = raw_packet[2].split(delimiter)
    corrected_sensors = [
        value if "ERROR" in status_tokens else value + correction_offset
        for value in raw_packet[1][:]
    ]
    return raw_packet[0], corrected_sensors


# =========================================================================
# TEST 1: a nominal packet, offset applied
# =========================================================================
test_packet_1 = [501, [12.5, 13.0, 11.8], "NOMINAL|CALIBRATED"]
original_list_1 = test_packet_1[1]          # the object itself, for id()
snapshot_1 = test_packet_1[1][:]            # its values, for ==

packet_id, corrected_sensors = parse_payload(
    test_packet_1, "|", correction_offset=2
)
print(f"Test 1 -> {packet_id} {corrected_sensors}")

assert test_packet_1[1] == snapshot_1, (
    "SIDE EFFECT: Test 1 sensor readings were modified in place"
)
assert id(corrected_sensors) != id(original_list_1), (
    "ALIASING: Test 1 returned the caller's own list object"
)
print("Test 1 side-effect assertions passed.")


# =========================================================================
# TEST 2: an ERROR packet, offset deliberately NOT applied
# =========================================================================
test_packet_2 = [502, [9.0, 8.5], "ERROR|SENSOR_FAULT"]
original_list_2 = test_packet_2[1]
snapshot_2 = test_packet_2[1][:]

packet_id, corrected_sensors = parse_payload(
    test_packet_2, "|", correction_offset=5
)
print(f"Test 2 -> {packet_id} {corrected_sensors}")

assert test_packet_2[1] == snapshot_2, (
    "SIDE EFFECT: Test 2 sensor readings were modified in place"
)
# This is the case that makes the id() check indispensable. The returned
# list is EQUAL in value to the original, because "ERROR" suppressed the
# offset - so == alone would pass even if the function had handed back the
# caller's own list. Only id() can tell the two situations apart.
assert corrected_sensors == original_list_2, (
    "Test 2 values should be unchanged when ERROR is present"
)
assert id(corrected_sensors) != id(original_list_2), (
    "ALIASING: Test 2 returned the caller's own list object"
)
print("Test 2 side-effect assertions passed.")


# =========================================================================
# TEST 3: the keyword argument omitted entirely, so the default applies
# =========================================================================
test_packet_3 = [503, [1.0, 2.0], "NOMINAL"]

packet_id, corrected_sensors = parse_payload(test_packet_3, "|")
print(f"Test 3 (default offset) -> {packet_id} {corrected_sensors}")


# =========================================================================
# TEST 4: positional-only parameters supplied by keyword - must fail
# =========================================================================
try:
    parse_payload(raw_packet=test_packet_1, delimiter="|")
except TypeError as error:
    print(f"Test 4 passed. TypeError raised as expected: {error}")


# =========================================================================
# TEST 5: the keyword-only parameter supplied positionally - must fail
# =========================================================================
try:
    parse_payload(test_packet_1, "|", 2)
except TypeError as error:
    print(f"Test 5 passed. TypeError raised as expected: {error}")


# =========================================================================
# SECTION 8: EDGE CASES
# =========================================================================
print()
print("--- Edge Cases ---")

# (i) Three or more status tokens, none of them an error.
edge_packet_1 = [505, [10.0, 20.0], "NOMINAL|CALIBRATED|LOW_POWER"]
packet_id, corrected_sensors = parse_payload(
    edge_packet_1, "|", correction_offset=1
)
print(f"(i)   three status tokens        -> {packet_id} "
      f"{corrected_sensors}")
print(f"      tokens split to            -> "
      f"{edge_packet_1[2].split('|')}")

# (ii) An empty sensor list.
edge_packet_2 = [504, [], "NOMINAL"]
packet_id, corrected_sensors = parse_payload(
    edge_packet_2, "|", correction_offset=3
)
print(f"(ii)  empty sensor list          -> {packet_id} "
      f"{corrected_sensors}")
assert corrected_sensors == [], "Empty input should give an empty list"
assert id(corrected_sensors) != id(edge_packet_2[1]), (
    "ALIASING: empty case returned the caller's own list object"
)
print("      still a brand-new object, and no error raised.")

# (iii) correction_offset explicitly 0 versus omitted altogether.
edge_packet_3 = [506, [4.5, 5.5], "NOMINAL"]
print(f"(iii) explicit correction_offset=0 -> "
      f"{parse_payload(edge_packet_3, '|', correction_offset=0)}")
print(f"      omitted entirely             -> "
      f"{parse_payload(edge_packet_3, '|')}")
assert (parse_payload(edge_packet_3, "|", correction_offset=0)
        == parse_payload(edge_packet_3, "|")), (
    "Explicit zero and omitted offset must behave identically"
)
print("      identical, so neither path is special-cased.")

print()
print("All assertions passed - parse_payload is side-effect free.")
print("NOTE: assert statements are stripped when Python runs with -O, so")
print("these checks are a development guarantee, not a runtime one.")
