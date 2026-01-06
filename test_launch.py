#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы инфраструктуры
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.sandbox_controller import SandboxManager
from core.process_monitor import ProcessMonitor
from config.accounts_manager import AccountsManager


async def test_single_window():
    """Тест запуска одного окна"""
    print("\n" + "=" * 50)
    print("ТЕСТ: Запуск одного окна Dota 2")
    print("=" * 50)

    # Инициализация
    sandbox_mgr = SandboxManager()
    accounts_mgr = AccountsManager()

    # Проверяем аккаунты
    accounts = accounts_mgr.load_accounts()
    if not accounts:
        print("❌ Аккаунты не настроены!")
        print("Запустите accounts_mgr.create_accounts_template()")
        return False

    print(f"✅ Найдено {len(accounts)} аккаунтов")

    # Запускаем одно окно
    try:
        process = await sandbox_mgr.launch_box(
            box_name="TestBox1",
            config_type="default",
            account_id=1
        )

        print("✅ Окно запущено")
        print(f"   PID: {process.pid}")
        print(f"   Аккаунт: {accounts[0].login}")

        # Мониторинг
        monitor = ProcessMonitor(sandbox_mgr)
        await monitor.add_process("TestBox1", psutil.Process(process.pid))

        # Проверяем 30 секунд
        print("\n⏳ Мониторинг 30 секунд...")
        for i in range(30):
            status = await monitor.check_process("TestBox1")
            print(f"   {i + 1}/30 - Статус: {status}")
            await asyncio.sleep(1)

        # Очистка
        print("\n🧹 Очистка...")
        await sandbox_mgr.cleanup()

        print("\n✅ Тест завершен успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_resources_allocation():
    """Тест распределения ресурсов"""
    print("\n" + "=" * 50)
    print("ТЕСТ: Распределение ресурсов системы")
    print("=" * 50)

    sandbox_mgr = SandboxManager()

    # Анализ системы
    import psutil
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024 ** 3)

    print(f"Система:")
    print(f"  CPU ядер: {cpu_count}")
    print(f"  RAM: {memory_gb:.1f} GB")

    # Рекомендации
    print("\nРекомендации для 5 окон:")
    if memory_gb < 16:
        print("  ⚠️  Мало RAM! Используйте low_memory профили")
        print("  Рассмотрите запуск только 3 окон")
    elif memory_gb < 32:
        print("  ✅ Достаточно для 5 окон на средних настройках")
    else:
        print("  ✅ Отлично! Можно использовать высокие настройки")

    return True


async def main():
    """Основная функция тестирования"""
    print("Тестирование инфраструктуры Dota 5 Bot System")
    print("Разработчик 1: Инфраструктура\n")

    tests = [
        ("Анализ системы", test_resources_allocation),
        ("Запуск одного окна", test_single_window),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'=' * 60}")
            print(f"Запуск теста: {test_name}")
            print(f"{'=' * 60}")

            success = await test_func()
            results.append((test_name, success))

        except Exception as e:
            print(f"❌ Тест упал с ошибкой: {e}")
            results.append((test_name, False))

    # Вывод результатов
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)

    for test_name, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{test_name:30} {status}")

    # Итог
    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nИТОГО: {passed}/{total} тестов пройдено")

    if passed == total:
        print("\n🎉 Вся инфраструктура готова к работе!")
    else:
        print("\n⚠️  Требуется доработка инфраструктуры")


if __name__ == "__main__":
    asyncio.run(main())