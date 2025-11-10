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

test_deps = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['B', 'E'],
    'D': [],
    'E': ['F'],
    'F': [],

        'react': ['loose-envify', 'js-tokens'],
        'express': ['body-parser', 'cookie-parser'],

        'matplotlib': ['numpy', 'pillow', 'cycler'],
        'numpy': ['python', 'setuptools'],
        'pillow': ['numpy'],
        'cycler': []
}

def get_dependencies(pkg, ver):
    if test_mode:
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

print(f"\n=== ОБРАТНЫЕ ЗАВИСИМОСТИ {package_name} ===")
reverse_deps = {}
for pkg, deps in test_deps.items():
    for dep in deps:
        if dep not in reverse_deps:
            reverse_deps[dep] = []
        reverse_deps[dep].append(pkg)

if package_name in reverse_deps:
    for dep in reverse_deps[package_name]:
        print(f"🔙 {dep} -> {package_name}")
else:
    print("Никто не зависит от этого пакета")

visited = set()
graph = {}
cycles = []


def dfs(current_pkg, path=None):
    if path is None:
        path = []

    if current_pkg in path:
        cycles.append(' -> '.join(path + [current_pkg]))
        return

    if current_pkg == package_name:
        deps = get_dependencies(current_pkg, version)
    else:
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

print(f"\n=== MERMAID ДИАГРАММА ===")
print("```mermaid")
print("graph TD")
for pkg, deps in graph.items():
    for dep in deps:
        print(f"    {pkg} --> {dep}")
print("```")

print(f"\n=== ИНФОРМАЦИЯ О ГРАФЕ ===")
print(f"Всего узлов: {len(graph)}")
print(f"Всего связей: {sum(len(deps) for deps in graph.values())}")
if cycles:
    print(f"Обнаружено циклов: {len(cycles)}")
    for cycle in cycles:
        print(f"  🔁 {cycle}")