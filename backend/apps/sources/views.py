from rest_framework.response import Response
from rest_framework.views import APIView

from . import services


class SourcesView(APIView):
    def get(self, request):
        return Response(services.get_sources())
