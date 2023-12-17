from channels.generic.websocket import AsyncWebsocketConsumer
from celery.result import AsyncResult
import json
import asyncio

class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        task_id = text_data_json['task_id']    
        while True:
            status = await self.check_task_status(task_id)
            if status == 'SUCCESS':
                await self.send(text_data=json.dumps({
                    'status': status,
                    'task_id': task_id
                }))
                break
            else:
                await self.send(text_data=json.dumps({
                    'status': status
                }))
    
            await asyncio.sleep(5)

    async def check_task_status(self, task_id):
        res = AsyncResult(task_id)
        if res.ready():
            return res.status
        return res.status
