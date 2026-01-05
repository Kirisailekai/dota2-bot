import asyncio
import websockets
import json
from typing import Dict, Any


class GameCoordinator:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.bots_state = {}
        self.connected = False

    async def connect(self):
        """Подключение к серверу координации"""
        try:
            uri = f"ws://{self.host}:{self.port}"
            self.websocket = await websockets.connect(uri)
            self.connected = True
            print(f"Подключен к координатору на {uri}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    async def send_state(self, bot_id: int, state: Dict[str, Any]):
        """Отправка состояния бота"""
        if not self.connected or not self.websocket:
            return

        message = {
            'type': 'bot_state',
            'bot_id': bot_id,
            'state': state,
            'timestamp': asyncio.get_event_loop().time()
        }

        await self.websocket.send(json.dumps(message))

    async def receive_commands(self):
        """Получение команд от координатора"""
        try:
            async for message in self.websocket:
                data = json.loads(message)

                if data['type'] == 'global_command':
                    # Общая команда для всех ботов
                    return data['command']
                elif data['type'] == 'bot_command':
                    # Команда для конкретного бота
                    if data['bot_id'] == self.bot_id:
                        return data['command']

        except websockets.exceptions.ConnectionClosed:
            print("Соединение с координатором разорвано")
            self.connected = False

    async def sync_loop(self):
        """Цикл синхронизации"""
        while self.connected:
            try:
                # Здесь будет логика синхронизации
                await asyncio.sleep(0.1)  # 10 FPS синхронизации
            except Exception as e:
                print(f"Ошибка синхронизации: {e}")
                await asyncio.sleep(1)

    async def disconnect(self):
        """Отключение от координатора"""
        if self.websocket:
            await self.websocket.close()
        self.connected = False