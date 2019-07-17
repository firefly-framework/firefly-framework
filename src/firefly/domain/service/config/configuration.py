from __future__ import annotations

import os
from abc import ABC, abstractmethod

import firefly.domain as ffd
from dotenv import load_dotenv


class Configuration(ABC):
    def __init__(self):
        self._config: dict = {}
        self._load_config()

    @property
    def all(self):
        return self._config

    @property
    def contexts(self):
        return self._config.get('contexts', {})

    @property
    def extensions(self):
        return self._config.get('extensions', {})

    def _load_config(self):
        self._load_environment_vars()

        try:
            original_dir = self._move_to_project_root()
        except ffd.ProjectConfigNotFound:
            self._config = {}
            return

        with open('firefly.yml', 'r') as fp:
            self._config = self.load(fp.read())
        os.chdir(original_dir)

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

    @abstractmethod
    def load(self, data: str):
        pass

    @abstractmethod
    def save(self, data: dict):
        pass
