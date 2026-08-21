"""
Program : Temporal Profile Analyzer
Purpose : Ingests a user's name and age, computes temporal metrics against a
          2045 reference year, and reports an AI Era Readiness Score.
Author  : Sohan Saha
Date    : 3rd Aug 2026
"""

import datetime

SINGULARITY_YEAR = 2045
MAX_REASONABLE_AGE = 120


def main():
    """Run the interactive Temporal Profile Analyzer."""
    user_full_name = input("Enter your full name: ").strip()

    # Edge case 1: name is empty or was only whitespace before stripping.
    if not user_full_name:
        print("Error: A name cannot be empty or whitespace only. Exiting.")
        return

    name_length = len(user_full_name)
    formatted_name = user_full_name.title()

    user_age = input("Enter your current age in whole years: ").strip()

    # Edge case 2: guard the int() conversion instead of letting it raise.
    if not user_age.isdigit():
        print(f"Error: '{user_age}' is not a whole number. Age must be digits "
              f"only, for example 20. Exiting.")
        return

    current_age = int(user_age)

    # Edge case 3: 0 is accepted; absurd values are rejected as out of range.
    if current_age > MAX_REASONABLE_AGE:
        print(f"Error: Age must be between 0 and {MAX_REASONABLE_AGE}. Exiting.")
        return

    current_year = datetime.date.today().year
    age_in_2045 = current_age + (SINGULARITY_YEAR - current_year)

    readiness_score = ((name_length * 10) + age_in_2045) / 2

    print("\n--- Temporal Profile Report ---")
    print(f"Stored Record         : {formatted_name}")
    print(f"Identifier Byte-Count : {name_length}")
    print(f"Current Year          : {current_year}")
    print(f"Projected Age in {SINGULARITY_YEAR} : {age_in_2045}")
    print(f"AI Readiness Score    : {readiness_score:.2f}")

    # Challenge task: repeat the name once per unit of the age's first digit.
    first_digit = int(user_age[0])

    if first_digit == 0:
        print("Name Echo             : (age begins with 0 - no repetition)")
    else:
        print(f"Name Echo             : {formatted_name * first_digit}")


if __name__ == "__main__":
    main()
