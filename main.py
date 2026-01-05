import asyncio
import sys
from core.sandbox_controller import SandboxManager
from core.game_launcher import DotaLauncher
from ai.bot_ai import BotController
from network.coordinator import GameCoordinator


class Dota5Bot:
    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.game_launcher = DotaLauncher()
        self.bots = []
        self.coordinator = GameCoordinator()

    async def setup(self):
        """Настройка всей системы"""
        print("Настраиваю систему...")

        # 1. Запуск Sandboxie окон
        await self.sandbox_manager.launch_boxes(5)

        # 2. Запуск Dota 2 в каждом окне
        await self.game_launcher.launch_dota_in_boxes(5)

        # 3. Инициализация ботов
        for i in range(5):
            bot = BotController(bot_id=i)
            await bot.initialize()
            self.bots.append(bot)

        # 4. Подключение к координатору
        await self.coordinator.connect()

    async def run(self):
        """Основной цикл работы"""
        print("Запускаю ботов...")

        # Запускаем всех ботов параллельно
        tasks = []
        for bot in self.bots:
            task = asyncio.create_task(bot.run())
            tasks.append(task)

        # Запускаем координатор
        coordinator_task = asyncio.create_task(self.coordinator.sync_loop())
        tasks.append(coordinator_task)

        # Ожидаем завершения всех задач
        await asyncio.gather(*tasks)

    async def shutdown(self):
        """Корректное завершение"""
        print("Завершаю работу...")
        for bot in self.bots:
            await bot.shutdown()
        await self.coordinator.disconnect()
        await self.sandbox_manager.cleanup()


async def main():
    bot_system = Dota5Bot()

    try:
        await bot_system.setup()
        await bot_system.run()
    except KeyboardInterrupt:
        print("\nПолучен сигнал прерывания")
    finally:
        await bot_system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())