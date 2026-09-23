"""
Program : SourceAuditor - a hand-built style and package-layout checker
Purpose : In Problem Set 8 I used pycodestyle, somebody else's tool. This
          module builds a small version of that tool myself, reading source
          code the way the interpreter does - as an Abstract Syntax Tree of
          syntactic structure rather than as a string of characters.

          SourceAuditor checks four things: whether consecutive top-level
          functions are separated by two blank lines (AST-based), whether
          any line is too long, whether any line carries trailing
          whitespace, and whether any type-annotation colon is missing the
          space after it. It also validates that an sdist-style directory
          really contains what its setup.py claims.

Author  : SOHAN SAHA
Date    : 23/09/2026
Course  : Coding for AI - Week 9, Problem Set 9

SUBMISSION NOTE: THE DECORATOR LINE-NUMBER PITFALL
-----------------------------------------------------------------------
FunctionDef.lineno points at the def keyword, never at a decorator sitting
above it. Because the blank lines a reader actually sees fall above the
decorator, measuring the gap from node.lineno silently overcounts it. I
built a case that separates the two readings rather than assuming they
agree: two top-level functions with exactly one blank line between them,
the second carrying an @staticmethod decorator. The first function ends on
line 2, the decorator sits on line 4 and the def on line 5. Measuring from
the decorator gives 4 - 2 - 1 = 1 blank line, correctly a violation;
measuring from the def gives 5 - 2 - 1 = 2 and wrongly passes. My
implementation uses node.decorator_list[0].lineno whenever that list is
non-empty, and running it on this example reports second_function as a
violation, confirming the decorator line is the one being measured from.
"""

import ast
import os

# =========================================================================
# HEADER DOCUMENTATION (Deliverable ii)
# =========================================================================
# WHY A PROPERTY SETTER PROTECTS AN ATTRIBUTE FOR AN OBJECT'S WHOLE LIFE,
# WHERE A CHECK WRITTEN INSIDE __init__ DOES NOT
#
# A check written directly in __init__ runs exactly once, at the moment the
# object is constructed. It inspects the value it was handed, and then it
# is finished forever. Nothing about having run that check leaves any trace
# on the object afterwards. The attribute it validated is an ordinary
# instance attribute, so any later assignment - auditor.target_path =
# "/some/other/path", written anywhere in the program, possibly months
# later by someone who never read __init__ - simply overwrites it. No code
# runs, no check happens, and the object is now holding a path that may not
# exist. The guarantee __init__ appeared to give quietly expired the
# instant construction ended.
#
# A property moves the guarantee from a moment in time to the attribute
# itself. Defining target_path with @property and @target_path.setter
# replaces the plain attribute with a pair of methods stored on the CLASS.
# From then on the name target_path is not a slot holding a value at all;
# it is a descriptor, and Python routes every read through the getter and
# every write through the setter. The real value is tucked away in
# _target_path, which the setter alone writes.
#
# The consequence is that validation is no longer something that happened,
# it is something that happens - on every single assignment, for as long as
# the object exists. Construction is not a special case: __init__ writes
# self.target_path = target_path, which is itself an assignment and so goes
# through the same setter as every later one. There is exactly one gate,
# and no way in through the side, so the object can never end up holding a
# path that does not exist no matter where in the program the assignment is
# written. That is a property the __init__-only check cannot offer at any
# price, because it has no way to be present at an assignment it never saw.
# =========================================================================

# Sample sources used by the self-test block below. These are module-level
# CONSTANTS - immutable strings, fixed at import - not mutable variables
# accumulating audit results, which is the thing Section 4 rules out. Every
# audit result lives on a SourceAuditor instance.

SAMPLE_FLAWED_SOURCE = "\n".join([
    "def search4letters(phrase:str, letters='ATCG'):",
    '    """Docstring with trailing whitespace below."""' + "   ",
    "    return set(letters).intersection(set(phrase))",
    "def another_function():",
    "    this_line_is_deliberately_way_too_long_to_fit_within_the_"
    "seventy_nine_column_limit = True",
    "    pass",
])

# Edge case (i): exactly one blank line - a borderline case, still a fail.
SAMPLE_ONE_BLANK_LINE = "\n".join([
    "def first_function():",
    "    pass",
    "",
    "def second_function():",
    "    pass",
])

# Edge case (ii): the decorator pitfall. One blank line sits above the
# decorator, so the decorator line says 1 blank line (violation) while the
# def line says 2 (no violation). The two readings genuinely disagree here.
SAMPLE_DECORATED_GAP = "\n".join([
    "def first_function():",
    "    pass",
    "",
    "@staticmethod",
    "def second_function():",
    "    pass",
])

# The same shape, correctly spaced, to prove the check is not simply
# flagging every decorated function it meets.
SAMPLE_DECORATED_CLEAN = "\n".join([
    "def first_function():",
    "    pass",
    "",
    "",
    "@staticmethod",
    "def second_function():",
    "    pass",
])

# Edge case (iv): a line holding only spaces has nothing meaningful
# "trailing", so it must not be flagged. Line 3 below is three spaces.
SAMPLE_WHITESPACE_ONLY_LINE = "\n".join([
    "def only_function():",
    "    value = 1",
    "   ",
    "    return value",
])


class SourceAuditor:
    """Inspect Python source text and sdist directories for compliance.

    Every piece of inspection state - the target path being audited and the
    most recent report produced - lives on the instance. Nothing is
    accumulated in module scope.
    """

    def __init__(self, target_path: str, /) -> None:
        self.target_path = target_path      # routed through the setter
        self._last_report = {}

    @property
    def target_path(self) -> str:
        """Return the validated path this auditor is pointed at."""
        return self._target_path

    @target_path.setter
    def target_path(self, value: str) -> None:
        """Validate on EVERY assignment, not only at construction."""
        if not os.path.exists(value):
            raise FileNotFoundError(
                f"Target path '{value}' does not exist.")
        self._target_path = value

    @property
    def last_report(self) -> dict:
        """Return the most recent audit report held by this instance."""
        return self._last_report

    def audit_module_structure(self, file_contents: str, /, *,
                               max_line_length: int = 79) -> dict:
        """Parse source code string, evaluate PEP 8 compliance rules,
        and return a summary dictionary of violations."""
        tree = ast.parse(file_contents)
        source_lines = file_contents.split("\n")
        self._last_report = {
            "spacing_violations":
                self._check_function_spacing(tree),
            "line_length_violations":
                self._check_line_length(
                    source_lines, max_line_length=max_line_length),
            "trailing_whitespace_violations":
                self._check_trailing_whitespace(source_lines),
            "colon_spacing_violations":
                self._check_colon_spacing(tree, source_lines),
        }
        return self._last_report

    def verify_sdist_layout(self, directory_path: str, /) -> bool:
        """Return True only if the directory is a plausible sdist.

        It must hold both setup.py and README.txt, AND at least one name in
        setup.py's py_modules list must correspond to a real .py file
        sitting in that same directory. setup.py is READ as a tree, never
        executed, so a hostile or broken setup.py cannot run any code here.
        """
        setup_path = os.path.join(directory_path, "setup.py")
        readme_path = os.path.join(directory_path, "README.txt")
        if not os.path.isfile(setup_path):
            return False
        if not os.path.isfile(readme_path):
            return False

        with open(setup_path, encoding="utf-8") as setup_handle:
            setup_tree = ast.parse(setup_handle.read())

        for node in ast.walk(setup_tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg != "py_modules":
                    continue
                try:
                    declared_modules = ast.literal_eval(keyword.value)
                except (ValueError, SyntaxError):
                    continue
                for module_name in declared_modules:
                    if os.path.isfile(os.path.join(
                            directory_path, f"{module_name}.py")):
                        return True
        return False

    # -- Requirement 1 ----------------------------------------------------

    @staticmethod
    def _check_function_spacing(tree: ast.Module, /) -> list:
        """Name every top-level function too close to the one before it.

        The gap is measured from the EFFECTIVE start line of the later
        function. For a decorated function that is the first decorator's
        line, not the def line, because the blank lines a reader sees are
        the ones above the decorator.
        """
        violations = []
        top_level = [node for node in tree.body
                     if isinstance(node, ast.FunctionDef)]
        for earlier, later in zip(top_level, top_level[1:]):
            effective_start = later.lineno
            if later.decorator_list:
                effective_start = later.decorator_list[0].lineno
            blank_lines = effective_start - earlier.end_lineno - 1
            if blank_lines < 2:
                violations.append(later.name)
        return violations

    # -- Requirement 2 ----------------------------------------------------

    @staticmethod
    def _check_line_length(source_lines: list, /, *,
                           max_line_length: int = 79) -> list:
        """Return the numbers of lines longer than the allowed width."""
        return [number
                for number, text in enumerate(source_lines, start=1)
                if len(text) > max_line_length]

    @staticmethod
    def _check_trailing_whitespace(source_lines: list, /) -> list:
        """Return the numbers of lines that end in stray whitespace.

        A blank or whitespace-only line is skipped: there is nothing
        meaningful for whitespace to be trailing behind.
        """
        return [number
                for number, text in enumerate(source_lines, start=1)
                if text.strip() and text != text.rstrip()]

    @staticmethod
    def _check_colon_spacing(tree: ast.Module, source_lines: list,
                             /) -> list:
        """Return the numbers of lines with a cramped annotation colon.

        The AST is used to find the annotations themselves, so only real
        type-annotation colons are examined. A dictionary literal, a slice
        and the colon that ends a def or if header are all left alone,
        which a plain text search for ':' could not manage.
        """
        violations = []
        for node in ast.walk(tree):
            annotation = None
            if isinstance(node, ast.arg) and node.annotation is not None:
                annotation = node.annotation
            elif isinstance(node, ast.AnnAssign):
                annotation = node.annotation
            if annotation is None:
                continue
            if annotation.col_offset == 0:
                continue
            text = source_lines[annotation.lineno - 1]
            if text[annotation.col_offset - 1] == ":":
                violations.append(annotation.lineno)
        return sorted(set(violations))


if __name__ == "__main__":
    # -- Requirement 4: the required self-test, chained as Section 4 asks --
    assert not SourceAuditor(__file__).audit_module_structure(
        open(__file__, encoding="utf-8").read()
    )["spacing_violations"], "Self-audit failed: spacing violations found."
    print("Self-audit passed: no top-level function spacing violations.")

    # The report lives on the instance, never in a module-level accumulator.
    auditor = SourceAuditor(__file__)

    print()
    print("=" * 62)
    print("SECTION 6 TRACE - auditing the deliberately flawed source")
    print("=" * 62)
    auditor.audit_module_structure(SAMPLE_FLAWED_SOURCE)
    for rule_name, line_numbers in auditor.last_report.items():
        print(f"{rule_name}: {line_numbers}")

    print()
    print("=" * 62)
    print("SECTION 7 EDGE CASES")
    print("=" * 62)

    print("(i)   exactly one blank line between two top-level functions")
    auditor.audit_module_structure(SAMPLE_ONE_BLANK_LINE)
    print(f"        spacing_violations -> "
          f"{auditor.last_report['spacing_violations']}")
    print("        one blank line is a fail; PEP 8 asks for at least two.")

    print()
    print("(ii)  a decorated function, one blank line above the decorator")
    auditor.audit_module_structure(SAMPLE_DECORATED_GAP)
    print(f"        spacing_violations -> "
          f"{auditor.last_report['spacing_violations']}")
    print("        measured from the decorator (line 4): 1 blank -> fail")
    print("        measured from the def (line 5):       2 blank -> pass")
    print("        the two readings disagree, and the decorator wins.")
    print("      the same shape, correctly spaced, is NOT flagged:")
    auditor.audit_module_structure(SAMPLE_DECORATED_CLEAN)
    print(f"        spacing_violations -> "
          f"{auditor.last_report['spacing_violations']}")

    print()
    print("(iv)  a line holding only spaces")
    auditor.audit_module_structure(SAMPLE_WHITESPACE_ONLY_LINE)
    print(f"        trailing_whitespace_violations -> "
          f"{auditor.last_report['trailing_whitespace_violations']}")
    print("        line 3 is three spaces and is correctly ignored.")

    # -- Edge case (iii): sdist layouts, built and removed on the fly -----
    print()
    print("(iii) sdist layout validation")
    for folder, wanted_files in (
        ("_demo_sdist_complete", ("setup.py", "README.txt", "demo_mod.py")),
        ("_demo_sdist_no_readme", ("setup.py", "demo_mod.py")),
        ("_demo_sdist_no_module", ("setup.py", "README.txt")),
    ):
        os.makedirs(folder, exist_ok=True)
        for wanted in wanted_files:
            with open(os.path.join(folder, wanted), "w",
                      encoding="utf-8") as handle:
                if wanted == "setup.py":
                    handle.write("from setuptools import setup\n\n"
                                 "setup(\n"
                                 "    name='demo',\n"
                                 "    py_modules=['demo_mod'],\n"
                                 ")\n")
        print(f"        {folder:<24} -> "
              f"{auditor.verify_sdist_layout(folder)}")
        for wanted in wanted_files:
            os.remove(os.path.join(folder, wanted))
        os.rmdir(folder)
    print("        only the complete layout passes; a missing README.txt")
    print("        or a py_modules entry with no matching .py file fails.")

    # -- The property setter, proved to still guard after construction ----
    print()
    print("=" * 62)
    print("THE PROPERTY SETTER, AFTER CONSTRUCTION")
    print("=" * 62)
    print(f"  constructed fine, target_path -> {auditor.target_path}")
    try:
        auditor.target_path = "/no/such/path/anywhere.py"
    except FileNotFoundError as error:
        print(f"  reassignment rejected -> FileNotFoundError: {error}")
    print("  an __init__-only check would have allowed that assignment.")
    print(f"  target_path is unchanged -> {auditor.target_path}")

    print()
    print("All checks completed.")
