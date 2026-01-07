import subprocess
import sys
import os
from pathlib import Path
import ctypes
import winreg
import urllib.request
import tempfile
import json


class SandboxieSetup:
    def __init__(self):
        self.sandboxie_path = self.find_sandboxie()
        self.config_file = Path("config/sandboxie_config.json")
        self.load_config()

    def load_config(self):
        """Загрузка конфигурации"""
        default_config = {
            "sandboxie_path": r"C:\Program Files\Sandboxie-Plus",
            "sandboxie_exe": "Start.exe",
            "sandboxie_ctl": "SandboxieCtl.exe",
            "sandboxie_plus": "SandboxiePlus.exe",
            "sandboxes": ["DOTA_BOT_1", "DOTA_BOT_2", "DOTA_BOT_3", "DOTA_BOT_4", "DOTA_BOT_5"],
            "border_colors": ["#00FF00", "#0000FF", "#00FFFF", "#FF00FF", "#FFFF00"],
            "window_positions": [
                (0, 0, 1280, 720),
                (1280, 0, 1280, 720),
                (0, 720, 1280, 720),
                (1280, 720, 1280, 720),
                (2560, 0, 1280, 1080)
            ]
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except:
                pass

        self.config = default_config
        self.save_config()

        # Обновляем путь к Sandboxie
        if not self.sandboxie_path:
            self.sandboxie_path = Path(self.config["sandboxie_path"])

    def save_config(self):
        """Сохранение конфигурации"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def find_sandboxie(self):
        """Поиск установленного Sandboxie-Plus"""
        possible_paths = [
            r"C:\Program Files\Sandboxie-Plus",
            r"C:\Program Files (x86)\Sandboxie-Plus",
            r"C:\Program Files\Sandboxie",
            r"C:\Program Files (x86)\Sandboxie"
        ]

        for path in possible_paths:
            p = Path(path)
            if p.exists():
                # Проверяем наличие ключевых файлов
                if (p / "Start.exe").exists() or (p / "SandboxiePlus.exe").exists():
                    print(f"✓ Найден Sandboxie: {p}")
                    return p

        print("✗ Sandboxie не найден")
        return None

    def is_admin(self):
        """Проверка прав администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def generate_configs(self):
        """Генерация конфигурационных файлов для Sandboxie-Plus"""
        print("\n1. Генерация конфигураций...")

        config_dir = Path("config/sandbox_configs")
        config_dir.mkdir(exist_ok=True)

        for i, (sandbox_name, color) in enumerate(zip(
                self.config["sandboxes"],
                self.config["border_colors"]
        ), 1):
            config_content = f"""[{sandbox_name}]
Enabled=y
ConfigLevel=9
BorderColor={color},ttl
AutoRecover=y
BlockNetworkFiles=y
FileRootPath=%USER%\\Desktop\\Sandboxes\\{sandbox_name}
BoxNameTitle=y
BorderSize=4,4,4,4

; Steam paths
OpenFilePath=%SteamPath%\\steam.exe
OpenFilePath=%SteamPath%\\steamapps\\common\\dota 2 beta
OpenFilePath=%SteamPath%\\userdata

; Network and Graphics
OpenPipe=Steam*
OpenWinClass=Valve001
OpenWinClass=SDL_app
OpenClsid={{5C6698D9-7BE4-4122-8EC5-291D84DBD4A0}}
OpenClsid={{60B0E4A0-EDCF-11CF-BC10-00AA00AC74F6}}
OpenClsid={{22D6F304-B0F6-11D0-94AB-0080C74C7E95}}

; Performance
Template=Direct3D
Template=OpenGL
Template=WindowsRas

; Recovery
RecoverFolder=%Desktop%\\Sandbox-{sandbox_name}-Recovered
LingerProcess=steam.exe
LingerProcess=dota2.exe
"""

            config_file = config_dir / f"{sandbox_name}.ini"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            print(f"✓ Создан конфиг: {sandbox_name}.ini")

        return True

    def create_sandboxes(self):
        """Создание песочниц через Sandboxie-Plus"""
        print("\n2. Создание песочниц...")

        # Проверяем наличие SandboxieCtl
        sandboxie_ctl = self.sandboxie_path / "SandboxieCtl.exe"
        if not sandboxie_ctl.exists():
            print("✗ SandboxieCtl.exe не найден")
            return False

        for sandbox_name in self.config["sandboxes"]:
            try:
                # Создаем песочницу
                result = subprocess.run(
                    [str(sandboxie_ctl), "add", sandbox_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    print(f"✓ Создана песочница: {sandbox_name}")
                else:
                    # Песочница может уже существовать
                    if "already exists" in result.stderr:
                        print(f"⚠ Песочница {sandbox_name} уже существует")
                    else:
                        print(f"✗ Ошибка создания {sandbox_name}: {result.stderr}")

            except subprocess.TimeoutExpired:
                print(f"✗ Таймаут при создании {sandbox_name}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")

        return True

    def configure_sandboxie_plus(self):
        """Настройка Sandboxie-Plus"""
        print("\n3. Настройка Sandboxie-Plus...")

        # Копируем конфиги
        config_dir = Path("config/sandbox_configs")
        if not config_dir.exists():
            print("✗ Папка с конфигами не найдена")
            return False

        try:
            import shutil
            # Копируем все .ini файлы
            for config_file in config_dir.glob("*.ini"):
                dest = self.sandboxie_path / config_file.name
                shutil.copy(config_file, dest)
                print(f"✓ Скопирован: {config_file.name}")

            # Также копируем в папку Sandboxie.ini если нужно
            main_config = self.sandboxie_path / "Sandboxie.ini"
            if not main_config.exists():
                # Создаем базовый конфиг
                with open(main_config, 'w') as f:
                    f.write("[GlobalSettings]\n")
                    f.write("Template=AutoRecover\n")
                    f.write("Template=WindowsRas\n")
                    f.write("Template=BlockPorts\n")
                print("✓ Создан основной конфиг Sandboxie.ini")

            return True

        except Exception as e:
            print(f"✗ Ошибка копирования конфигов: {e}")
            return False

    def test_sandboxie_plus(self):
        """Тестирование работы Sandboxie-Plus"""
        print("\n4. Тестирование Sandboxie-Plus...")

        if not self.sandboxie_path:
            print("✗ Sandboxie-Plus не найден")
            return False

        # Проверяем, какой исполняемый файл существует
        exe_files = ["Start.exe", "SandboxiePlus.exe"]
        sandboxie_exe = None

        for exe in exe_files:
            exe_path = self.sandboxie_path / exe
            if exe_path.exists():
                sandboxie_exe = exe_path
                print(f"✓ Найден исполняемый файл: {exe}")
                break

        if not sandboxie_exe:
            print("✗ Не найден исполняемый файл Sandboxie")
            return False

        # Тестируем запуск в песочнице
        test_cmd = [
            str(sandboxie_exe),
            "/box:DOTA_BOT_1",
            "cmd.exe",
            "/c",
            "echo Sandboxie-Plus Test OK && timeout 3"
        ]

        try:
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if "Sandboxie-Plus Test OK" in result.stdout:
                print("✓ Sandboxie-Plus работает корректно")
                return True
            else:
                print(f"✗ Sandboxie-Plus не работает: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("✓ Sandboxie-Plus запущен (таймаут ожидания)")
            return True
        except Exception as e:
            print(f"✗ Ошибка тестирования: {e}")
            return False

    def create_desktop_shortcuts(self):
        """Создание ярлыков на рабочем столе"""
        print("\n5. Создание ярлыков...")

        try:
            # Находим исполняемый файл
            exe_path = self.sandboxie_path / "Start.exe"
            if not exe_path.exists():
                exe_path = self.sandboxie_path / "SandboxiePlus.exe"

            if not exe_path.exists():
                print("✗ Не найден исполняемый файл для создания ярлыков")
                return False

            # Создаем ярлыки
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()

            for i, sandbox_name in enumerate(self.config["sandboxes"], 1):
                shortcut_path = os.path.join(desktop, f"DOTA Bot {i}.lnk")

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortcut(shortcut_path)
                shortcut.TargetPath = str(exe_path)
                shortcut.Arguments = f'/box:{sandbox_name} "C:\\Program Files (x86)\\Steam\\steam.exe" -applaunch 570 -windowed -w 1024 -h 768 -novid'
                shortcut.WorkingDirectory = "C:\\Program Files (x86)\\Steam"
                shortcut.IconLocation = "C:\\Program Files (x86)\\Steam\\steam.exe,0"
                shortcut.Description = f"DOTA 2 Bot {i} - {sandbox_name}"
                shortcut.save()

                print(f"✓ Создан ярлык: DOTA Bot {i}.lnk")

            return True

        except Exception as e:
            print(f"⚠ Не удалось создать ярлыки: {e}")
            print("Создайте ярлыки вручную через Sandboxie-Plus UI")
            return False

    def setup_complete(self):
        """Запуск полной настройки"""
        print("=" * 60)
        print("Настройка Sandboxie-Plus для Dota 2 Bot System")
        print("=" * 60)

        # Проверяем Sandboxie-Plus
        if not self.sandboxie_path:
            print("\n✗ Sandboxie-Plus не найден!")
            return

        print(f"\n✓ Sandboxie-Plus найден: {self.sandboxie_path}")

        # Генерируем конфиги
        self.generate_configs()

        # Настраиваем Sandboxie-Plus
        self.configure_sandboxie_plus()

        # Создаем песочницы
        self.create_sandboxes()

        # Тестируем
        self.test_sandboxie_plus()

        # Создаем ярлыки
        self.create_desktop_shortcuts()

        print("\n" + "=" * 60)
        print("Настройка Sandboxie-Plus завершена!")
        print("\nСледующие шаги:")
        print("1. Откройте Sandboxie-Plus UI и проверьте созданные песочницы")
        print("2. Добавьте аккаунты Steam в config/accounts.json")
        print("3. Запустите тест: python test_launch.py")
        print("4. Проверьте работу в main.py")
        print("\nПримечание: Для первого запуска Dota 2 в песочнице")
        print("может потребоваться ввод Steam Guard кода.")
        print("=" * 60)


def main():
    setup = SandboxieSetup()
    setup.setup_complete()


if __name__ == "__main__":
    main()