from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class GithubRepoForm(forms.Form):
    repo_url = forms.CharField(label='GitHub Repository URL', max_length=1000, validators=[URLValidator()])

    def clean_repo_url(self):
        url = self.cleaned_data.get('repo_url')
        if "github.com" not in url:
            raise ValidationError("Lütfen geçerli bir GitHub URL'si giriniz.")
        return url
