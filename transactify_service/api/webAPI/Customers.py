from store.webmodels.Customer import Customer
from store.serializers.CustomerSerializer import CustomerSerializer

from rest_framework import permissions
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from transactify_service.HttpResponses import HTTPResponses

class CustomerViewSet(viewsets.ModelViewSet):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, we also provide an extra `highlight` action.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        customer = self.get_object()
        return Response(customer.highlighted)

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to provide a custom not found response.
        """
        customer = self.get_object_or_none()
        if customer is None:
            return HTTPResponses.HTTP_STATUS_CUSTOMER_NOT_FOUND(kwargs.get('pk'))
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    def get_object_or_none(self):
        """
        Helper method to return the object or None if not found.
        """
        try:
            return self.get_object()
        except Exception:
            return None

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
