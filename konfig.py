
import toml
import os
import sys
import requests
import json
from typing import Dict, Any, List
from urllib.parse import urljoin


class NpmDependencyVisualizer:
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.npm_registry_url = "https://registry.npmjs.org/"

    def load_config(self) -> Dict[str, Any]:

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


        version = self.config['version']
        if not isinstance(version, str) or not version:
            errors.append("version должен быть непустой строкой")

        if errors:
            raise ValueError("Ошибки валидации конфигурации:\n- " + "\n- ".join(errors))

    def get_npm_package_info(self, package_name: str, version: str = "latest") -> Dict[str, Any]:

        try:
            url = urljoin(self.npm_registry_url, f"{package_name}/{version}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка получения данных из npm реестра: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ошибка парсинга JSON ответа: {e}")

    def get_dependencies(self, package_info: Dict[str, Any]) -> Dict[str, str]:

        try:
            dependencies = {}


            if 'dependencies' in package_info:
                dependencies.update(package_info['dependencies'])


            if 'versions' in package_info and self.config['version'] in package_info['versions']:
                version_data = package_info['versions'][self.config['version']]
                if 'dependencies' in version_data:
                    dependencies.update(version_data['dependencies'])

            return dependencies

        except Exception as e:
            raise RuntimeError(f"Ошибка извлечения зависимостей: {e}")

    def print_dependencies(self, dependencies: Dict[str, str]):

        print(f"\n=== ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА {self.config['package_name']}@{self.config['version']} ===")

        if not dependencies:
            print("Зависимости не найдены")
            return

        for dep_name, dep_version in dependencies.items():
            print(f"📦 {dep_name}: {dep_version}")

        print(f"\nВсего зависимостей: {len(dependencies)}")

    def print_config(self):
        """Вывод конфигурации"""
        print("=== КОНФИГУРАЦИЯ ===")
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("=" * 40)


def create_sample_config():

    sample_config = {
        'package_name': 'react',
        'repository_url': 'https://github.com/facebook/react',
        'test_mode': False,
        'version': '18.2.0',
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


        visualizer = NpmDependencyVisualizer()
        visualizer.validate_config()
        visualizer.print_config()


        print(f"\nПолучение информации о пакете {visualizer.config['package_name']}...")
        package_info = visualizer.get_npm_package_info(
            visualizer.config['package_name'],
            visualizer.config['version']
        )


        dependencies = visualizer.get_dependencies(package_info)

        visualizer.print_dependencies(dependencies)


        with open('package_info.json', 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, ensure_ascii=False)
        print(f"\n Полная информация о пакете сохранена в package_info.json")

    except Exception as e:
        print(f" Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()