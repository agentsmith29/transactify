from rest_framework import permissions
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets


from store.webmodels.StoreProduct import StoreProduct
from store.serializers.StoreProductSerializer import StoreProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = StoreProduct.objects.all()
    serializer_class = StoreProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        product = self.get_object()
        return Response(product.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)