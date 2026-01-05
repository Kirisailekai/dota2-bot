#!/usr/bin/env python3
"""
Запуск системы ботов для Dota 2
"""

import asyncio
import argparse
from main import Dota5Bot


def parse_args():
    parser = argparse.ArgumentParser(description='Dota 5 Bot System')
    parser.add_argument('--mode', type=str, default='both',
                        choices=['host', 'client', 'both'],
                        help='Режим работы: host, client или both')
    parser.add_argument('--bots', type=int, default=5,
                        help='Количество ботов для запуска')
    parser.add_argument('--no-sandbox', action='store_true',
                        help='Запуск без Sandboxie (для тестов)')
    return parser.parse_args()


async def main():
    args = parse_args()

    print("=" * 50)
    print("Dota 5 Bot System запускается...")
    print(f"Режим: {args.mode}")
    print(f"Количество ботов: {args.bots}")
    print("=" * 50)

    bot_system = Dota5Bot()

    try:
        # Настройка
        await bot_system.setup()

        # Запуск
        print("\nСистема запущена. Нажмите Ctrl+C для остановки.")
        await bot_system.run()

    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки...")
    finally:
        # Завершение
        await bot_system.shutdown()
        print("Система остановлена.")


if __name__ == "__main__":
    asyncio.run(main())