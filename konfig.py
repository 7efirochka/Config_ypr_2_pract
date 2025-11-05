import toml
import requests
import json


with open('config.toml', 'r') as f:
    config = toml.load(f)

print("=== КОНФИГУРАЦИЯ ===")
for key, value in config.items():
    print(f"{key}: {value}")

package_name = config['package_name']
version = config['version']
test_mode = config['test_mode']



def get_dependencies(pkg, ver):
    if test_mode:

        test_deps = {
            'react': ['loose-envify', 'js-tokens'],
            'express': ['body-parser', 'cookie-parser'],
            'A': ['B', 'C'],
            'B': ['D']
        }
        return test_deps.get(pkg, [])
    else:

        url = f"https://registry.npmjs.org/{pkg}/{ver}"
        response = requests.get(url)
        data = response.json()
        deps = data.get('dependencies', {})
        return list(deps.keys())


print(f"\n=== ПРЯМЫЕ ЗАВИСИМОСТИ {package_name}@{version} ===")
direct_deps = get_dependencies(package_name, version)
for dep in direct_deps:
    print(f"📦 {dep}")


visited = set()
graph = {}
cycles = []


def dfs(current_pkg, path=None):
    if path is None:
        path = []

    if current_pkg in path:
        cycles.append(' -> '.join(path + [current_pkg]))
        return

    deps = get_dependencies(current_pkg, 'latest')
    graph[current_pkg] = deps
    visited.add(current_pkg)

    for dep in deps:
        if dep not in visited:
            dfs(dep, path + [current_pkg])


print(f"\n=== ПОЛНЫЙ ГРАФ ЗАВИСИМОСТЕЙ ===")
dfs(package_name)

for pkg, deps in graph.items():
    print(f"{pkg} -> {deps}")

if cycles:
    print(f"\n ЦИКЛЫ: {len(cycles)}")
    for cycle in cycles:
        print(f"  {cycle}")


if config.get('ascii_tree', False):
    print(f"\n=== ASCII ДЕРЕВО ===")


    def print_tree(pkg, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{pkg}")

        deps = graph.get(pkg, [])
        new_prefix = prefix + ("    " if is_last else "│   ")

        for i, dep in enumerate(deps):
            is_last_dep = i == len(deps) - 1
            print_tree(dep, new_prefix, is_last_dep)


    print_tree(package_name)