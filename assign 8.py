"""
Program : DNA Marker Finder
Purpose : Two connected exercises in bio-informatics.

          Task 1 - search4letters. A parameterised function with a type
          hinted signature and a default argument, called three ways:
          positionally, by keyword, and relying on the default.

          Task 2 - analyze_sequence. An experiment in what actually happens
          to an object when it is passed into a function, using id() to
          watch whether two names refer to one object or to two, and
          contrasting MUTATING an object with REASSIGNING a name.

Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Problem Set 6

SUBMISSION NOTE: MY ANSWER TO THE DISCOVERY CHALLENGE (Section 3.2)
--------------------------------------------------------------------
Written before reading the provided answer.

My prediction: the function never received a copy of the list. When
analyze_sequence(dna_database, 'CGAT') is called, the parameter name
sequence_list is bound to the very same list object that dna_database
already names - two names, one object - which is why I expect all three
printed IDs to be identical. The method .append() then changes that one
object in place rather than building a new one, so the change is visible
through whichever name you happen to look through afterwards. A return
statement would only be needed if the function had constructed something
new that the caller could not otherwise reach; here nothing new was
created, so there is nothing to hand back. I expect the global list to
read ['AATCCG', 'TGGCTA', 'CGAT'] once the call finishes.

Having now read the provided answer, my prediction was correct: the model
is call by object reference, and running the script confirmed that all three
IDs matched and that the global list gained 'CGAT' with no return statement.
"""

# =========================================================================
# HEADER DOCUMENTATION (Deliverable 2)
# =========================================================================
# WHAT "CALL BY OBJECT REFERENCE" MEANS
#
# Every value in Python lives as an object somewhere in memory, and a
# variable is not a box holding that value - it is a name tied to the
# object. Passing an argument into a function does one thing only: it ties
# a second name, the parameter name, to the object the caller's name was
# already tied to. Nothing is copied and nothing is duplicated. For the
# duration of the call there are simply two names for one object, which is
# why id() reports the same number on both sides of the call boundary.
#
# Everything else follows from that. If the function calls a method that
# changes the object itself - .append() on a list, for instance - there is
# only one object to change, so the caller sees the change through its own
# name afterwards. If instead the function assigns to the parameter name,
# that assignment reties the LOCAL name to some different object and leaves
# the original object, and the caller's name, completely untouched.
#
# WHY THIS IS NOT "PASS BY VALUE"
#
# In a pass-by-value language the callee receives a private copy of the
# value, so nothing it does can ever be seen by the caller. If Python
# worked that way, the .append() below would modify a copy and the global
# list would still hold two elements at the end. It holds three. So Python
# is not passing values.
#
# WHY THIS IS NOT "PASS BY REFERENCE" EITHER
#
# In a genuine pass-by-reference language - C++ with an & parameter, say -
# the callee receives an alias for the caller's VARIABLE, not just for its
# object. Assigning to the parameter there would reach back and rebind the
# caller's variable too. The rebinding experiment below proves Python does
# not do this: inside analyze_sequence_rebind the local name is pointed at
# a brand new list, its ID changes accordingly, and the caller's
# dna_database is left exactly as it was.
#
# So Python sits between the two. What is passed is a reference to an
# object, and that reference is itself passed by value: the callee gets its
# own name, which it may repoint freely without consequence, but that name
# starts out aimed at the caller's actual object, which it may change in
# place with consequences visible everywhere. Mutation crosses the call
# boundary; rebinding does not.
# =========================================================================


# =========================================================================
# TASK 1: BUILDING search4letters
# =========================================================================
def search4letters(phrase: str, letters: str = 'ATCG') -> set:
    """Return the set of target 'letters' found in a supplied 'phrase'."""
    # set(letters) creates a unique pool of target markers
    # set(phrase) represents the genetic material to analyze
    return set(letters).intersection(set(phrase))


print("=" * 62)
print("TASK 1: search4letters")
print("=" * 62)

positional_result = search4letters('TGGACC', 'GC')
keyword_result = search4letters(letters='CG', phrase='TGGACC')
default_result = search4letters('TGGACC')

print(f"search4letters('TGGACC', 'GC')                 -> "
      f"{positional_result}")
print(f"search4letters(letters='CG', phrase='TGGACC')  -> "
      f"{keyword_result}")
print(f"search4letters('TGGACC')                       -> "
      f"{default_result}")
print()
print("The first two calls bind the SAME values to the SAME parameters;")
print("only the notation differs, so the results are equal:")
print(f"  positional_result == keyword_result -> "
      f"{positional_result == keyword_result}")
print("The third call supplies no second argument, so letters falls back")
print("to its default of 'ATCG'.")


# =========================================================================
# TASK 2: TRACKING MEMORY REFERENCES
# =========================================================================
def analyze_sequence(sequence_list, marker):
    """Append a marker to the caller's list, MUTATING the shared object."""
    print(f"  Inside Function (Start) - ID: {id(sequence_list)} | "
          f"Data: {sequence_list}")

    # In-place modification (mutating the shared object)
    sequence_list.append(marker)

    print(f"  Inside Function (End)   - ID: {id(sequence_list)} | "
          f"Data: {sequence_list}")


# ------------------------------------------------------------------
# 3.1  The Core Demonstration - passing the original list
# ------------------------------------------------------------------
print()
print("=" * 62)
print("TASK 2 / 3.1: THE CORE DEMONSTRATION (mutating the original)")
print("=" * 62)

dna_database = ['AATCCG', 'TGGCTA']
global_id_before = id(dna_database)

print(f"Global Scope (Before)   - ID: {id(dna_database)} | "
      f"Data: {dna_database}")
analyze_sequence(dna_database, 'CGAT')
print(f"Global Scope (After)    - ID: {id(dna_database)} | "
      f"Data: {dna_database}")

print()
print("All three IDs are the same number, and the global list changed")
print("even though analyze_sequence has no return statement.")


# ------------------------------------------------------------------
# 3.3  The Slice Experiment - passing a shallow copy
# ------------------------------------------------------------------
print()
print("=" * 62)
print("TASK 2 / 3.3: THE SLICE EXPERIMENT (passing a shallow copy)")
print("=" * 62)

dna_database = ['AATCCG', 'TGGCTA']

print(f"Global Scope (Before)   - ID: {id(dna_database)} | "
      f"Data: {dna_database}")
analyze_sequence(dna_database[:], 'CGAT')
print(f"Global Scope (After)    - ID: {id(dna_database)} | "
      f"Data: {dna_database}")

print()
print("This time the ID printed inside the function does NOT match the")
print("global ID: dna_database[:] built a new list object. The function")
print("appended to that new object, and the original is untouched.")


# ------------------------------------------------------------------
# 3.4  Bonus Experiment - mutation versus reassignment
# ------------------------------------------------------------------
def analyze_sequence_rebind(sequence_list, marker):
    """Rebind the LOCAL name instead of mutating the shared object."""
    print(f"  Inside (Start) - ID: {id(sequence_list)} | "
          f"Data: {sequence_list}")

    # REBINDS the local name to an entirely new list
    sequence_list = sequence_list + [marker]

    print(f"  Inside (End)   - ID: {id(sequence_list)} | "
          f"Data: {sequence_list}")


print()
print("=" * 62)
print("TASK 2 / 3.4: BONUS - MUTATION vs REASSIGNMENT")
print("=" * 62)

dna_database = ['AATCCG', 'TGGCTA']

print(f"Global Scope (Before)   - ID: {id(dna_database)} | "
      f"Data: {dna_database}")
analyze_sequence_rebind(dna_database, 'CGAT')
print(f"Global Scope (After)    - ID: {id(dna_database)} | "
      f"Data: {dna_database}")

print()
print("No slicing was used, yet the global is unchanged. The ID at the")
print("START matches the global - the same object did arrive - but the ID")
print("at the END differs, because sequence_list + [marker] built a new")
print("list and the local name was pointed at that instead.")


# =========================================================================
# SECTION 4: EDGE CASES
# =========================================================================
print()
print("=" * 62)
print("SECTION 4: EDGE CASES")
print("=" * 62)

# Case 1: an empty phrase.
print("1. search4letters with an empty phrase")
print(f"     search4letters('')   -> {search4letters('')}")
print(f"     is it an empty set?  -> {search4letters('') == set()}")
print("     The intersection of any set with an empty set is empty, so")
print("     this returns an empty set rather than raising an error.")

# Case 2: mixing positional and keyword arguments in one call.
print()
print("2. Mixing positional and keyword arguments in the same call")
mixed_result = search4letters('TGGACC', letters='GC')
print(f"     search4letters('TGGACC', letters='GC') -> {mixed_result}")
print(f"     identical to using keywords for both?  -> "
      f"{mixed_result == keyword_result}")
print("     But a positional argument may never follow a keyword one.")
print("     The offending form is rejected while the file is being")
print("     compiled, before a single line of it runs:")
try:
    compile("search4letters(phrase='TGGACC', 'GC')", "<demo>", "eval")
except SyntaxError as error:
    print(f"     SyntaxError: {error.msg}")

# Case 3: appending to a sliced list more than once.
print()
print("3. Appending to a list passed as a slice, repeatedly")
dna_database = ['AATCCG', 'TGGCTA']
print(f"     global before  : {dna_database}")
for call_number in (1, 2, 3):
    analyze_sequence(dna_database[:], f'MARK{call_number}')
print(f"     global after 3 : {dna_database}")
print(f"     still 2 items and unchanged -> "
      f"{dna_database == ['AATCCG', 'TGGCTA']}")
print("     Each call sliced a fresh, independent copy, so no change ever")
print("     accumulated in the global list.")
print()
print("     NOTE: the IDs above may repeat between calls. That is not a")
print("     shared object - each temporary copy is discarded as soon as")
print("     the call ends, and CPython is free to reuse the address it")
print("     just freed. The proof of independence is the unchanged global")
print("     list, not the ID numbers.")

print()
print("=" * 62)
print("REMINDER ON id() VALUES")
print("=" * 62)
print("The specific numbers above are memory addresses. They will differ")
print("on every run and on every machine. What matters is the PATTERN:")
print("whether the same number appears in several places (one object) or")
print("whether it changes (a new object was created).")
print()
print(f"Sanity check - the ID captured at the very start of 3.1 was")
print(f"{global_id_before}, which is a plain integer: {type(global_id_before)}")
