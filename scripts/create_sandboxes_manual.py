# scripts/create_sandboxes_manual.py
"""
Создание песочниц вручную
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def create_all_sandboxes():
    """Создание всех 5 песочниц"""
    from core.sandbox_controller import SandboxController

    controller = SandboxController()

    print("Создание песочниц для ботов...")

    for i in range(1, 6):
        sandbox_name = f"DOTA_BOT_{i}"
        print(f"Создание песочницы {sandbox_name}...")

        if controller.is_sandbox_exists(sandbox_name):
            print(f"  Песочница {sandbox_name} уже существует")
        else:
            success = controller.create_sandbox_through_ui(sandbox_name)
            if success:
                print(f"  ✓ Песочница {sandbox_name} создана")
            else:
                print(f"  ✗ Ошибка создания песочницы {sandbox_name}")

    print("\nГотово!")


if __name__ == "__main__":
    create_all_sandboxes()