from django import forms
from django.core import validators

from .widgets import ImageBlobClearableFileInput, AudioBlobClearableFileInput


class ImageBlobField(forms.FileField):
	widget = ImageBlobClearableFileInput
	default_validators = [validators.validate_image_file_extension]


class AudioBlobField(forms.FileField):
	widget = AudioBlobClearableFileInput
