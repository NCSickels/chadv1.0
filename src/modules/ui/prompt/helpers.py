"""Helper functions for the prompt module."""


def get_tokens(text: str) -> list:
    """Tokenize the input text."""
    tokens = text.split(" ")
    return tokens
