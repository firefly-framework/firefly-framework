from __future__ import annotations

import os
import re

import firefly.domain as ffd
import yaml
from dotenv import load_dotenv
from firefly.domain.entity.core.configuration import Configuration


class YamlConfigurationFactory(ffd.ConfigurationFactory):
    def __call__(self) -> Configuration:
        return Configuration(_config=self._load_config())

    @staticmethod
    def _parse(data: str):
        path_matcher = re.compile(r'\$\{([^}^{]+)\}')

        def path_constructor(loader, node):
            value = node.value
            match = path_matcher.match(value)
            env_var = match.group()[2:-1]
            if env_var not in os.environ:
                raise ffd.ConfigurationError(f'Environment variable {env_var} is used in config, but is not set')
            return os.environ.get(env_var) + value[match.end():1]

        yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
        yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)

        return yaml.safe_load(data)

    def _load_config(self) -> dict:
        self._load_environment_vars()

        try:
            original_dir = self._move_to_project_root()
        except ffd.ProjectConfigNotFound:
            return {}

        with open('firefly.yml', 'r') as fp:
            config = self._parse(fp.read())
        os.chdir(original_dir)

        return config

    def _load_environment_vars(self):
        stage = os.environ.get('STAGE', 'local')
        dir_ = self._move_to_project_root()
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), f'.env.{stage}'))
        os.chdir(dir_)

    @staticmethod
    def _move_to_project_root() -> str:
        original_dir = os.getcwd()
        os.chdir(os.environ.get('PWD'))
        while not os.path.exists('firefly.yml'):
            if os.path.realpath(os.getcwd()) == os.path.realpath('..'):
                break
            os.chdir('..')

        if not os.path.exists('firefly.yml'):
            raise ffd.ProjectConfigNotFound()

        return original_dir
