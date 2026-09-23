"""
Program : The AI Social Media Auditor
Purpose : Audits unstructured text and user data in two independent halves.

          Task 1 - Word Frequency Counter. Walks a paragraph token by
          token, normalises each token to lower case and strips surrounding
          punctuation, then builds a frequency dictionary from scratch with
          setdefault. No collections.Counter is used anywhere.

          Task 2 - Follower Deduplicator. Converts two platforms' follower
          lists into sets and compares them with intersection, directional
          difference and symmetric difference, to report who follows on
          both platforms and who is unique to each one.

Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Problem Set 5.2

SUBMISSION NOTE: ACTUAL OUTPUT vs HAND-WORKED EXPECTATION
-----------------------------------------------------------
Running the script on my test paragraph produced a word_counts dictionary of
20 distinct keys. The five that occur more than once are ai with 4, is with 3,
the with 3, world with 3, and and with 2; every remaining key holds 1. That
matches the expectation I worked out by hand. The count of 4 for ai is the
whole point of normalisation: the raw tokens were "AI", "ai", "AI" and "AI,",
which without lowering and stripping would have produced three separate keys
holding 2, 1 and 1 instead of one correct key holding 4. For the follower
lists the script reported both_platforms as {u103, u104}, only_a as
{u101, u102, u105}, only_b as {u106, u107}, and the symmetric difference as
those five combined - again matching the table I worked out by hand.
"""

import string

# =========================================================================
# TASK 1: WORD FREQUENCY COUNTER
# =========================================================================
text = (
    "AI is changing the world. ai is powering new tools, and AI "
    "is helping researchers learn faster. The world loves AI, and the "
    "world depends on it more each year."
)

word_counts = {}

for raw_word in text.split():
    cleaned_word = raw_word.lower().strip(string.punctuation)

    # A token that was ONLY punctuation - a lone "--" used as a dash, say -
    # becomes the empty string once stripped. An empty string is a legal but
    # meaningless dictionary key, so it is skipped rather than counted.
    if not cleaned_word:
        continue

    word_counts.setdefault(cleaned_word, 0)
    word_counts[cleaned_word] += 1

print("=" * 58)
print("TASK 1: WORD FREQUENCY COUNTER")
print("=" * 58)
print(f"Source paragraph ({len(text.split())} raw tokens):")
print(f"  {text}")
print()
print(f"Distinct words after normalisation: {len(word_counts)}")
print()
print("word_counts dictionary (natural insertion order):")
print(word_counts)
print()
print("Alphabetical breakdown:")
for word in sorted(word_counts):
    print(f"  {word:<14}{word_counts[word]}")
print()
print("Repeated words only:")
for word in sorted(word_counts):
    if word_counts[word] > 1:
        print(f"  {word:<14}{word_counts[word]}")


# =========================================================================
# TASK 2: THE FOLLOWER DEDUPLICATOR
# =========================================================================
platform_a_followers = ["u101", "u102", "u103", "u104", "u105"]
platform_b_followers = ["u103", "u104", "u106", "u107"]

set_a = set(platform_a_followers)
set_b = set(platform_b_followers)

both_platforms = set_a & set_b      # intersection
only_a = set_a - set_b              # unique to Platform A
only_b = set_b - set_a              # unique to Platform B
either_only = set_a ^ set_b         # unique to exactly one platform

print()
print("=" * 58)
print("TASK 2: FOLLOWER DEDUPLICATOR")
print("=" * 58)
print(f"Platform A followers: {platform_a_followers}")
print(f"Platform B followers: {platform_b_followers}")
print()
print(f"Follows on both platforms (&) : {both_platforms}")
print(f"Unique to Platform A      (-) : {only_a}")
print(f"Unique to Platform B      (-) : {only_b}")
print(f"Unique to exactly one     (^) : {either_only}")
print()
print("Cross-check that ^ equals the union of the two differences:")
print(f"  (only_a | only_b) == either_only -> "
      f"{(only_a | only_b) == either_only}")


# =========================================================================
# EDGE-CASE VERIFICATION (Section 5)
# =========================================================================
print()
print("=" * 58)
print("EDGE-CASE VERIFICATION")
print("=" * 58)

# Cases 1 and 2: an empty paragraph, and a token that is only punctuation.
sample_texts = [
    ("empty paragraph", ""),
    ("punctuation-only tokens", "-- --- ... !!!"),
    ("punctuation mixed with words", "Data -- drives ... AI!"),
]

for label, sample_text in sample_texts:
    sample_counts = {}
    for raw_word in sample_text.split():
        cleaned_word = raw_word.lower().strip(string.punctuation)
        if not cleaned_word:
            continue
        sample_counts.setdefault(cleaned_word, 0)
        sample_counts[cleaned_word] += 1
    print(f"  {label}:")
    print(f"    split() gave {sample_text.split()}")
    print(f"    word_counts  {sample_counts}")

# Case 3: two follower lists with no overlap at all.
disjoint_a = {"u201", "u202"}
disjoint_b = {"u301", "u302"}
print()
print("  no overlap at all:")
print(f"    both_platforms {disjoint_a & disjoint_b} (empty set)")
print(f"    only_a         {disjoint_a - disjoint_b}")
print(f"    only_b         {disjoint_b - disjoint_a}")
print("    every user accounted for: "
      f"{(disjoint_a - disjoint_b) | (disjoint_b - disjoint_a) == disjoint_a | disjoint_b}")

# Case 4: two identical follower lists.
identical_a = {"u401", "u402", "u403"}
identical_b = {"u401", "u402", "u403"}
print()
print("  two identical lists:")
print(f"    both_platforms {identical_a & identical_b}")
print(f"    only_a         {identical_a - identical_b} (empty set)")
print(f"    only_b         {identical_b - identical_a} (empty set)")
print("    both_platforms is the full set of users: "
      f"{(identical_a & identical_b) == identical_a}")
