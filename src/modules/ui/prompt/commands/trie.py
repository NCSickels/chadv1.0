"""
Trie data structure implementation for efficient prefix-based search.

Used for autocomplete and prefix-based searching.
"""


class TrieNode:
    """
    Node in the Trie data structure.

    Attributes:
        children (dict): Dictionary of child nodes.
        end_of_word (bool): Flag to indicate if the node is the end of a word.
    """

    def __init__(self):
        self.children = {}
        self.end_of_word = False


class Trie:
    """
    Trie data structure for efficient prefix-based search.

    Attributes:
        root (TrieNode): The root node of the Trie.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end_of_word = True

    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.end_of_word

    def startswith(self, prefix: str) -> list:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._get_all(node, prefix)

    def _get_all(self, node: TrieNode, prefix: str) -> list:
        words = []
        if node.end_of_word:
            words.append(prefix)
        for char, child_node in node.children.items():
            words.extend(self._get_all(child_node, prefix + char))
        return words
