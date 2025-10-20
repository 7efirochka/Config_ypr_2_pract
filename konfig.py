import matplotlib as mpl


print(f"Version: {mpl.__version__}")
print(f"Location: {mpl.__file__}")
print(f"Author: {getattr(mpl, '__author__', 'Not specified')}")
print(f"License: {getattr(mpl, '__license__', 'Not specified')}")
print(f"Config directory: {mpl.get_configdir()}")
print(f"Cache directory: {mpl.get_cachedir()}")


dot_code = """
digraph MatplotlibDeps {
    rankdir=LR;
    node [shape=box];

    matplotlib -> numpy;
    matplotlib -> pillow;
    matplotlib -> cycler;
    matplotlib -> fonttools;
    matplotlib -> kiwisolver;
}
"""

with open('../matplotlib_simple.dot', 'w') as f:
    f.write(dot_code)
