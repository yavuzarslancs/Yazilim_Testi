from django.db import models

class JavaFile(models.Model):
    file_name = models.CharField(null=True, blank=True,max_length=255)
    javadoc_comment_count = models.IntegerField(null=True, blank=True)
    other_comment_count = models.IntegerField(null=True, blank=True)
    code_line_count = models.IntegerField(null=True, blank=True)
    loc = models.IntegerField(null=True, blank=True)
    function_count = models.IntegerField(null=True, blank=True)
    comment_deviation_percentage = models.FloatField(null=True, blank=True)
    repo_url = models.URLField(default="https://default.url")
    def __str__(self):
        return self.file_name
