from pathlib import Path

from src.utils.config import settings


def repo_root() -> Path:
    return settings.project_root


def data_dir() -> Path:
    return settings.data_dir


def raw_dir() -> Path:
    return settings.raw_dir


def processed_dir() -> Path:
    return settings.processed_dir


def models_dir() -> Path:
    return settings.models_dir


def configs_dir() -> Path:
    return settings.configs_dir


def notebook_dir() -> Path:
    return settings.notebook_dir


def submission_dir() -> Path:
    return settings.submission_dir
