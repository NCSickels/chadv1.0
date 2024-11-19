import os


def generate_tree(root_dir, prefix=""):
    """
    Generates a visual representation of the directory tree structure.
    Args:
        root_dir (str): The root directory from which to generate the tree.
        prefix (str, optional): The prefix to use for each line of the tree. Defaults to "".
    Returns:
        list: A list of strings, each representing a line in the directory tree.
    """
    tree = []
    contents = sorted(os.listdir(root_dir))
    pointers = [("├── ", "│   "), ("└── ", "    ")]

    for index, name in enumerate(contents):
        path = os.path.join(root_dir, name)
        if index == len(contents) - 1:
            tree.append(prefix + pointers[1][0] + name)
            if os.path.isdir(path):
                tree.extend(generate_tree(path, prefix + pointers[1][1]))
        else:
            tree.append(prefix + pointers[0][0] + name)
            if os.path.isdir(path):
                tree.extend(generate_tree(path, prefix + pointers[0][1]))

    return tree


def print_tree(root_dir, output_file=None):
    """
    Prints the directory tree structure starting from the given root directory.

    Args:
        root_dir (str): The root directory from which to generate the tree structure.
        output_file (str, optional): The file path where the tree structure should be written. 
                                     If None, the tree structure is not written to a file.

    Returns:
        None
    """
    print(root_dir)
    tree = generate_tree(root_dir)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(root_dir + '\n')
            for line in tree:
                f.write(line + '\n')
    for line in tree:
        print(line)


if __name__ == "__main__":
    root_directory = os.getcwd()
    output_file = "directory_tree.txt"
    print_tree(root_directory, output_file)
