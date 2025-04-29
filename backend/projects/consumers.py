from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import DiscussionComment, Member

class DiscussionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope['user']
        self.comment_group = f'comments_{self.project_id}'
        
        if await self.verify_membership():
            await self.accept()
            await self.channel_layer.group_add(
                self.comment_group,
                self.channel_name
            )
        else:
            await self.close()

    @database_sync_to_async
    def verify_membership(self):
        if isinstance(self.user, AnonymousUser):
            return False
        return Member.objects.filter(
            project_id=self.project_id,
            user=self.user
        ).exists()

    async def receive_json(self, content):
        action = content.get('action')
        try:
            if action == 'create':
                await self.handle_create(content)
            elif action == 'update':
                await self.handle_update(content)
            elif action == 'delete':
                await self.handle_delete(content)
        except Exception as e:
            await self.send_json({'error': str(e)})

    async def handle_create(self, content):
        comment = await self.create_comment(content)
        await self.broadcast('create', comment)

    async def handle_update(self, content):
        comment = await self.update_comment(content)
        await self.broadcast('update', comment)

    async def handle_delete(self, content):
        comment_id = await self.delete_comment(content)
        await self.broadcast('delete', {'id': comment_id})

    @database_sync_to_async
    def create_comment(self, data):
        return DiscussionComment.objects.create(
            discussion_id=data['discussion_id'],
            member_id=data['member_id'],
            text=data['text'],
            temp_id=data.get('temp_id')
        )

    @database_sync_to_async
    def update_comment(self, data):
        comment = DiscussionComment.objects.get(id=data['id'])
        comment.text = data['text']
        comment.save()
        return comment

    @database_sync_to_async
    def delete_comment(self, data):
        comment = DiscussionComment.objects.get(id=data['id'])
        comment_id = comment.id
        comment.delete()
        return comment_id

    async def broadcast(self, action, data):
        await self.channel_layer.group_send(
            self.comment_group,
            {
                'type': 'send_message',
                'action': action,
                'data': data
            }
        )

    async def send_message(self, event):
        await self.send_json({
            'action': event['action'],
            'data': event['data']
        })