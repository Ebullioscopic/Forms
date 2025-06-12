import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Form, FormResponse, ActiveUser, FieldLock
from django.conf import settings
#User = get_user_model()

class FormCollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.share_code = self.scope['url_route']['kwargs']['share_code']
        self.room_group_name = f'form_{self.share_code}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to active users
        await self.add_active_user()
        
        # Send current form data
        await self.send_form_data()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': await self.get_user_data(self.user),
            }
        )

    async def disconnect(self, close_code):
        # Remove user from active users
        await self.remove_active_user()
        
        # Release any field locks
        await self.release_user_locks()
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': await self.get_user_data(self.user),
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'field_change':
            await self.handle_field_change(data)
        elif action == 'field_focus':
            await self.handle_field_focus(data)
        elif action == 'field_blur':
            await self.handle_field_blur(data)

    async def handle_field_change(self, data):
        field_id = data.get('field_id')
        value = data.get('value')
        
        # Update form response
        await self.update_form_response(field_id, value)
        
        # Broadcast change to other users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'field_changed',
                'field_id': field_id,
                'value': value,
                'user': await self.get_user_data(self.user),
            }
        )

    async def handle_field_focus(self, data):
        field_id = data.get('field_id')
        
        # Try to acquire field lock
        success = await self.acquire_field_lock(field_id)
        
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'field_locked',
                    'field_id': field_id,
                    'user': await self.get_user_data(self.user),
                }
            )

    async def handle_field_blur(self, data):
        field_id = data.get('field_id')
        
        # Release field lock
        await self.release_field_lock(field_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'field_unlocked',
                'field_id': field_id,
                'user': await self.get_user_data(self.user),
            }
        )

    # WebSocket message handlers
    async def field_changed(self, event):
        if event['user']['id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'field_changed',
                'field_id': event['field_id'],
                'value': event['value'],
                'user': event['user'],
            }))

    async def field_locked(self, event):
        if event['user']['id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'field_locked',
                'field_id': event['field_id'],
                'user': event['user'],
            }))

    async def field_unlocked(self, event):
        await self.send(text_data=json.dumps({
            'type': 'field_unlocked',
            'field_id': event['field_id'],
            'user': event['user'],
        }))

    async def user_joined(self, event):
        if event['user']['id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user': event['user'],
            }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
        }))

    # Database operations
    @database_sync_to_async
    def add_active_user(self):
        form = Form.objects.get(share_code=self.share_code)
        ActiveUser.objects.get_or_create(form=form, user=self.user)

    @database_sync_to_async
    def remove_active_user(self):
        ActiveUser.objects.filter(
            form__share_code=self.share_code,
            user=self.user
        ).delete()

    @database_sync_to_async
    def get_user_data(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'avatar_color': user.avatar_color,
        }

    @database_sync_to_async
    def send_form_data(self):
        try:
            form = Form.objects.prefetch_related('fields', 'response').get(share_code=self.share_code)
            response_data = {}
            if hasattr(form, 'response'):
                response_data = form.response.data
            
            active_users = list(ActiveUser.objects.filter(form=form).select_related('user'))
            field_locks = list(FieldLock.objects.filter(form=form).select_related('locked_by'))
            
            asyncio.create_task(self.send(text_data=json.dumps({
                'type': 'form_data',
                'form': {
                    'title': form.title,
                    'description': form.description,
                    'fields': [
                        {
                            'id': f'field_{field.id}',
                            'label': field.label,
                            'type': field.field_type,
                            'options': field.options,
                            'required': field.is_required,
                        }
                        for field in form.fields.all()
                    ]
                },
                'response_data': response_data,
                'active_users': [
                    {
                        'id': au.user.id,
                        'username': au.user.username,
                        'avatar_color': au.user.avatar_color,
                    }
                    for au in active_users
                ],
                'field_locks': [
                    {
                        'field_id': fl.field_id,
                        'locked_by': {
                            'id': fl.locked_by.id,
                            'username': fl.locked_by.username,
                        }
                    }
                    for fl in field_locks
                ]
            })))
        except Form.DoesNotExist:
            asyncio.create_task(self.close())

    @database_sync_to_async
    def update_form_response(self, field_id, value):
        form = Form.objects.get(share_code=self.share_code)
        response, created = FormResponse.objects.get_or_create(form=form)
        response.data[field_id] = value
        response.last_edited_by = self.user
        response.save()

    @database_sync_to_async
    def acquire_field_lock(self, field_id):
        form = Form.objects.get(share_code=self.share_code)
        try:
            FieldLock.objects.create(form=form, field_id=field_id, locked_by=self.user)
            return True
        except:
            return False

    @database_sync_to_async
    def release_field_lock(self, field_id):
        FieldLock.objects.filter(
            form__share_code=self.share_code,
            field_id=field_id,
            locked_by=self.user
        ).delete()

    @database_sync_to_async
    def release_user_locks(self):
        FieldLock.objects.filter(
            form__share_code=self.share_code,
            locked_by=self.user
        ).delete()
