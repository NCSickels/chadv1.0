from typing import List, Set, Optional

from isla.derivation_tree import DerivationTree
from isla.language import SemPredEvalResult, StructuralPredicate, SemanticPredicate

"""
This module defines the function `predicates()` which returns an "internet_checksum"
semantic predicate relying on the function `internet_checksum(...)`. The other functions
are helper functions; they are all documented with docstrings and, if necessary,
inline comments.
"""


def hex_to_bytes(hex_str: str) -> List[int]:
    """
    Convert a hex string, e.g., `AB12`, to a list of integers representing the
    individual bytes (`[171, 18]` for the given example).

    :param hex_str: A hexadecimal number.
    :return: The bytes representex by `hex_str`.
    """
    return list(bytearray.fromhex(hex_str))


def int_to_hex(number: int) -> str:
    """
    Converts a number to a hex string, such that each byte is terminated by a space.

    :param number: The number to convert.
    :return: A hex string corresponding to `number`.
    """
    result = list(hex(number)[2:])
    if len(result) % 2 != 0:
        result.insert(0, "0")

    # add spaces
    for i in reversed(range(len(result))):
        if i > 0 and i % 2 == 0:
            result.insert(i, " ")

    return "".join(result)


def compute_checksum(header: DerivationTree, checksum_tree: DerivationTree) -> str:
    """
    Compute the checksum for `header`.

    :param header: The header derivation tree.
    :param checksum_tree: The checksum sub tree.
    :return: A string representing the checksum of header in HEX representation,
    each byte terminated by a space (e.g., `AB 12 `).
    """
    from pythonping import icmp

    # First, replace the checksum field with zeroes
    header_wo_checksum = replace_checksum_with_zeroes(header, checksum_tree)

    # Convert the header to bytes
    header_bytes = bytearray(reversed(hex_to_bytes(str(header_wo_checksum))))

    # Now, compute the actual checksum using the `icmp` package
    checksum_value = int_to_hex(icmp.checksum(header_bytes)).upper() + " "

    # The checksum consists of *two* bytes. If the result is of shape "AA " (the bytes
    # are terminated by a space), we add another "00 " to the front for the right
    # length.
    if len(checksum_value) < 6:
        assert len(checksum_value) == 3
        checksum_value = "00 " + checksum_value

    return checksum_value


def replace_checksum_with_zeroes(
    header: DerivationTree, checksum_tree: DerivationTree
) -> DerivationTree:
    """
    Replaces the checksum part in `header` by zeroes.

    :param header: The header derivation tree.
    :param checksum_tree: The checksum sub tree.
    :return: `header`, but with `checksum_tree` consisting only of zeroes.
    """
    import re

    zeroes = (
        "".join("0" for _ in range(len(re.sub(r"\s+", "", str(checksum_tree))))) + " "
    )

    zero_checksum = ("<checksum>", [(zeroes, [])])
    header_wo_checksum = header.replace_path(
        header.find_node(checksum_tree),
        DerivationTree.from_parse_tree(zero_checksum),
    )

    return header_wo_checksum


def internet_checksum(
    _,
    header: DerivationTree,
    checksum_tree: DerivationTree,
) -> SemPredEvalResult:
    """
    The actual function called by the `internet_checksum` predicate. Evaluates to
    "not ready" if the header derivation tree is incomplete (open), to "true" if the
    checksum is already correct, and to a correction (mapping from `checksum_tree` to
    a corrected tree) otherwise.

    :param _: Ignored.
    :param header: The ICMP header.
    :param checksum_tree: The existing checksum derivation sub tree.
    :return: The `SemPredEvalResult` (see description).
    """

    import re, string
    from isla.helpers import srange
    from isla.parser import PEGParser

    # If the header is not yet fully instantiated, we cannot compute
    # a checksum. Thus, signal "not ready" and wait until we are presented
    # a complete header.
    if not header.is_complete():
        return SemPredEvalResult(None)

    # Compute the correct value, check if checksum is already correct
    checksum_value = compute_checksum(header, checksum_tree)

    if re.sub(r"\s+", "", str(checksum_tree)) == re.sub(r"\s+", "", checksum_value):
        return SemPredEvalResult(True)

    # Compute a correction

    # Parse the computed checksum value in a derivation tree.
    checksum_grammar = {
        "<start>": ["<checksum>"],
        "<checksum>": ["<byte><byte>"],
        "<byte>": ["<zerof><zerof> "],
        "<zerof>": srange(string.digits + "ABCDEF"),
    }

    checksum_parser = PEGParser(checksum_grammar, start_symbol="<checksum>")
    new_checksum_tree = DerivationTree.from_parse_tree(
        list(checksum_parser.parse(checksum_value))[0]
    )

    # Return the correction mapping
    return SemPredEvalResult({checksum_tree: new_checksum_tree})


def predicates() -> Set[StructuralPredicate | SemanticPredicate]:
    """
    :return: The "internet_checksum" predicate.
    """

    return {
        SemanticPredicate("internet_checksum", 2, internet_checksum, binds_tree=False)
    }
