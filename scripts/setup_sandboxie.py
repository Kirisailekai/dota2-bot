# scripts/setup_sandboxie.py
"""
Настройка Sandboxie
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_sandboxie():
    """Настройка Sandboxie для ботов"""
    from core.sandbox_controller import SandboxController

    controller = SandboxController()

    print("Настройка Sandboxie...")

    # 1. Проверка установки
    if not controller.check_sandboxie_installed():
        print("❌ Sandboxie не установлен!")
        print("Установите Sandboxie-Plus с официального сайта")
        return False

    print(f"✓ Sandboxie найден: {controller.sandboxie_path}")

    # 2. Создание конфигурационных файлов
    print("\nСоздание конфигурационных файлов...")

    config_template = """[DefaultBox]
Enabled=y
AutoRecover=y
BlockNetworkFiles=y
Template=OpenBluetooth
Template=OpenClipboard
Template=OpenCOM
Template=OpenDNS
Template=OpenDrives
Template=OpenSmartCard
Template=FileCopy
Template=AutoRecoverIgnore
Template=WindowsRasMan
Template=LingerPrograms
Template=Chrome_Phishing_DirectAccess
Template=Firefox_Phishing_DirectAccess
Template=SkipHook
Template=qWave
Template=BlockPorts

[InternetAccess]
Enabled=y

[Dota2]
Enabled=y
"""

    for i in range(1, 6):
        config_path = Path(f"config/sandbox_configs/DOTA_BOT_{i}.ini")
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w') as f:
            f.write(config_template)

        print(f"  ✓ Создан конфиг: {config_path}")

    print("\n✅ Настройка завершена!")
    print("\nЧто нужно сделать вручную:")
    print("1. Откройте Sandboxie-Plus")
    print("2. Создайте 5 песочниц с именами DOTA_BOT_1 ... DOTA_BOT_5")
    print("3. Для каждой песочницы:")
    print("   - В настройках добавьте 'Full Access' к папке с проектом")
    print("   - Настройте автозапуск Steam")

    return True


if __name__ == "__main__":
    setup_sandboxie()