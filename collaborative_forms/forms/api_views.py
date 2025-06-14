from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Form, FormResponse
from .serializers import FormSerializer, FormResponseSerializer

class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return Form.objects.filter(creator=self.request.user)
        return Form.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def response(self, request, pk=None):
        form = self.get_object()
        try:
            response = form.response
            serializer = FormResponseSerializer(response)
            return Response(serializer.data)
        except FormResponse.DoesNotExist:
            return Response({'data': {}})
