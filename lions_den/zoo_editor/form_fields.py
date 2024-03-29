from django import forms
from django.core import validators


class BlobClearableFileInput(forms.ClearableFileInput):
	subwidget_template_name = None  # needs to be defined in subclass
	template_name = 'zoo_editor/widgets/blob_clearable_file_input.html'
	initial_text = ''
	input_text = ''
	
	def get_context(self, name, value, attrs):
		context = super().get_context(name, value, attrs)
		context['widget'].update({
			'subwidget_template_name': self.subwidget_template_name,
			'subwidget_id': context['widget']['attrs']['id'] + '-display',
		})
		return context


class ImageBlobClearableFileInput(BlobClearableFileInput):
	subwidget_template_name = 'zoo_editor/widgets/image_subwidget.html'


class AudioBlobClearableFileInput(BlobClearableFileInput):
	subwidget_template_name = 'zoo_editor/widgets/audio_subwidget.html'


class ImageBlobField(forms.FileField):
	widget = ImageBlobClearableFileInput
	default_validators = [validators.validate_image_file_extension]


class AudioBlobField(forms.FileField):
	widget = AudioBlobClearableFileInput