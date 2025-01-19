""" DB Model to store the traceback to an error"""
from django.db import models

class LogTraceback(models.Model):
    """Model to store the traceback to an error"""
    traceback = models.TextField()
    line_no = models.IntegerField()
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"