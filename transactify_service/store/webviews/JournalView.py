
from django.shortcuts import render
from django.views import View

from transactify_service.settings import CONFIG


class JournalView(View):
    template_name = 'store/journal.html'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.journal_content = ""
        file_content = CONFIG.webservice.JOURNAL_FILE
        try:
            with open(file_content, 'r') as f:
                self.journal_content = f.read()
        except Exception as e:
            self.journal_content = f"No file found: {file_content}. Have you already issued a journal command?"

    def get(self, request):
        return render(request, self.template_name, {'title': 'Journal',
                                                    'journal_content': self.journal_content})

    def post(self, request):
        return render(request, self.template_name, {'title': 'Journal',
                                                    'journal_content': self.journal_content})