# install.py
import subprocess
import sys


def install_requirements():
    """Автоматическая установка зависимостей"""
    requirements = [
        "opencv-python",
        "pyautogui",
        "pydirectinput",
        "numpy",
        "pillow",
        "psutil",
        "pywin32",
        "pynput",
        "keyboard",
        "steam",
        "websockets"
    ]

    for package in requirements:
        print(f"Устанавливаю {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    print("\nВсе зависимости установлены!")


if __name__ == "__main__":
    install_requirements()