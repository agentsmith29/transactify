from django.views.generic import ListView
from terminal.webmodels.StoreLogs import StoreLog

class StoreLogListView(ListView):
    model = StoreLog
    template_name = 'hwcontroller/view_logs.html'
    context_object_name = 'logs'
    paginate_by = 10  # Paginate the logs (10 per page)

    def get_queryset(self):
        """Custom queryset to order logs by timestamp (most recent first)."""
        return StoreLog.objects.all().order_by('-timestamp')
