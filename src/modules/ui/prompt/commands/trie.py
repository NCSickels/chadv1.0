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

    Methods:
        insert(word): Inserts a word into the Trie.
        search(word): Searches for a word in the Trie.
        startswith(prefix): Returns all words in the Trie that start with the given prefix.
        _get_all(node, prefix): Helper method to get all words in the Trie starting from a given node.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.end_of_word

    def startswith(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._get_all(node, prefix)

    def _get_all(self, node, prefix):
        words = []
        if node.end_of_word:
            words.append(prefix)
        for char, child_node in node.children.items():
            words.extend(self._get_all(child_node, prefix + char))
        return words
