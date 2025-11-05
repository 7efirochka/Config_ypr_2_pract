import toml
import os
import sys
from typing import Dict, Any


class DependencyVisualizer:
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Конфигурационный файл {self.config_path} не найден")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)

            required_fields = ['package_name', 'repository_url', 'test_mode', 'version', 'ascii_tree']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Обязательный параметр '{field}' отсутствует в конфигурации")

            return config

        except toml.TomlDecodeError as e:
            raise ValueError(f"Ошибка синтаксиса TOML: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки конфигурации: {e}")

    def validate_config(self):
        errors = []
        if not isinstance(self.config['package_name'], str) or not self.config['package_name']:
            errors.append("package_name должен быть непустой строкой")

        repo_path = self.config['repository_url']
        if not isinstance(repo_path, str) or not repo_path:
            errors.append("repository_url должен быть непустой строкой")

        if not isinstance(self.config['test_mode'], bool):
            errors.append("test_mode должен быть true или false")

        version = self.config['version']
        if not isinstance(version, str) or not version:
            errors.append("version должен быть непустой строкой")

        if not isinstance(self.config['ascii_tree'], bool):
            errors.append("ascii_tree должен быть true или false")

        if errors:
            raise ValueError("Ошибки валидации конфигурации:\n- " + "\n- ".join(errors))

    def print_config(self):
        print("=== КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ ===")
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("=" * 40)

    def simulate_dependencies(self):

        if self.config['test_mode']:

            return {
                'numpy': ['python', 'setuptools'],
                'matplotlib': ['numpy', 'pillow', 'cycler'],
                'pillow': ['numpy'],
                'cycler': []
            }
        else:
            return {self.config['package_name']: ['dependency1', 'dependency2']}

    def print_ascii_tree(self, dependencies: Dict[str, list]):
        """Вывод зависимостей в виде ASCII-дерева"""
        if not self.config['ascii_tree']:
            return

        print("\n=== ДЕРЕВО ЗАВИСИМОСТЕЙ ===")

        def print_tree(package, deps, prefix="", is_last=True):
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{package}")

            new_prefix = prefix + ("    " if is_last else "│   ")
            for i, dep in enumerate(deps):
                is_last_dep = i == len(deps) - 1
                print_tree(dep, dependencies.get(dep, []), new_prefix, is_last_dep)


        main_package = self.config['package_name']
        print_tree(main_package, dependencies.get(main_package, []))


def create_sample_config():
    sample_config = {
        'package_name': 'matplotlib',
        'repository_url': 'https://github.com/matplotlib/matplotlib',
        'test_mode': True,
        'version': '3.7.1',
        'ascii_tree': True
    }

    with open('config.toml', 'w', encoding='utf-8') as f:
        toml.dump(sample_config, f)

    print("Создан пример конфигурационного файла: config.toml")


def main():
    try:
        if not os.path.exists('config.toml'):
            print("Конфигурационный файл не найден. Создаю пример...")
            create_sample_config()
            print("Отредактируйте config.toml и запустите приложение снова")
            return


        visualizer = DependencyVisualizer()
        visualizer.validate_config()
        visualizer.print_config()

        dependencies = visualizer.simulate_dependencies()


        if visualizer.config['ascii_tree']:
            visualizer.print_ascii_tree(dependencies)
        else:
            print(f"\nЗависимости: {dependencies}")

    except Exception as e:
        print(f" Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()