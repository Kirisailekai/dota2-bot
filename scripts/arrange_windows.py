#!/usr/bin/env python3
"""
Скрипт для управления расположением окон Dota 2 ботов
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.window_manager import WindowManager
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description='Управление окнами Dota 2 ботов')
    parser.add_argument('--layout', type=str, default='2x3',
                        choices=['2x3', 'custom', 'single'],
                        help='Тип расположения окон')
    parser.add_argument('--minimize', action='store_true',
                        help='Свернуть все окна')
    parser.add_argument('--restore', action='store_true',
                        help='Восстановить все окна')
    parser.add_argument('--front', action='store_true',
                        help='Вывести окна на передний план')
    parser.add_argument('--save', action='store_true',
                        help='Сохранить текущие положения окон')
    parser.add_argument('--continuous', action='store_true',
                        help='Непрерывно поддерживать расположение окон')

    args = parser.parse_args()

    wm = WindowManager()

    if args.minimize:
        print("Сворачиваю все окна...")
        wm.minimize_all()

    elif args.restore:
        print("Восстанавливаю все окна...")
        wm.restore_all()

    elif args.front:
        print("Вывожу окна на передний план...")
        wm.bring_to_front()

    elif args.save:
        print("Сохраняю положения окон...")
        wm.save_window_positions()

    elif args.continuous:
        print("Режим непрерывного поддержания расположения окон")
        print("Нажмите Ctrl+C для выхода")
        try:
            while True:
                windows = wm.arrange_windows_grid(args.layout)
                if windows:
                    print(f"Управляю {len(windows)} окнами")
                time.sleep(5)  # Проверяем каждые 5 секунд
        except KeyboardInterrupt:
            print("\nЗавершение работы...")

    else:
        # Стандартное расположение окон
        print(f"Располагаю окна в сетке {args.layout}...")
        windows = wm.arrange_windows_grid(args.layout)
        if windows:
            print(f"Успешно расположено {len(windows)} окон")
            wm.set_window_titles(["1", "2", "3", "4", "5"])
        else:
            print("Не удалось найти окна Dota 2")


if __name__ == "__main__":
    main()