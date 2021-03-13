import io
import base64
import functools

from abc import abstractmethod
from PIL import Image

from django.db import models

# File-like object classes----------------------------------------------------------------------------------------------
class BlobObject(io.BytesIO):
	def __init__(self, bytes, parent_field):
		super().__init__(bytes)
		self.parent_field = parent_field
	
	@classmethod
	def from_file(cls, bytes_file, parent_field):
		return cls(bytes_file.read(), parent_field)
	
	@property
	@abstractmethod
	def url(self):
		pass


class ImageBlob(BlobObject):
	@property
	def url(self):
		return f'data:image/{self.parent_field.format};base64,{base64.b64encode(self._get_normalised_img().getvalue()).decode()}'
	
	def _get_normalised_img(self):
		img = Image.open(self)
		img = self._adjust_rotation(img)
		width, height = img.size
		x_min, x_max, y_min, y_max = 0, width, 0, height
		aspect_ratio = self.parent_field.size[0] / self.parent_field.size[1]
		
		# Crop
		if width / height < aspect_ratio:  # image too tall
			new_width, new_height = width, round(width / aspect_ratio)
			y_min = round((height - new_height) // 2)
			y_max = y_min + new_height
		elif width / height > aspect_ratio:  # image too wide
			new_width, new_height = height * aspect_ratio, height
			x_min = round((width - new_width) // 2)
			x_max = x_min + new_width
		img = img.crop((x_min, y_min, x_max, y_max))
		
		# Scale
		img = img.resize(self.parent_field.size, Image.ANTIALIAS)
		
		# Output
		output_file = io.BytesIO()
		img.save(output_file, format=self.parent_field.format)
		return output_file
	
	def _adjust_rotation(self, img):
		"""
		Camera orientation is stored in the image metadata (EXIF data).
		PIL's Image.open() does not account for this, causing silent image rotation.

		Apply Image.transpose to ensure 0th row of pixels is at the visual
		top of the image, and 0th column is the visual left-hand side.
		Return the original image if unable to determine the orientation.

		As per CIPA DC-008-2012, the orientation field contains an integer,
		1 through 8. Other values are reserved.
		"""
		exif_orientation_tag = 0x0112
		exif_transpose_sequences = [  # Val  0th row  0th col
			[],  # 0    (reserved)
			[],  # 1   top      left
			[Image.FLIP_LEFT_RIGHT],  # 2   top      right
			[Image.ROTATE_180],  # 3   bottom   right
			[Image.FLIP_TOP_BOTTOM],  # 4   bottom   left
			[Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],  # 5   left     top
			[Image.ROTATE_270],  # 6   right    top
			[Image.FLIP_TOP_BOTTOM, Image.ROTATE_90],  # 7   right    bottom
			[Image.ROTATE_90],  # 8   left     bottom
		]
		
		try:
			seq = exif_transpose_sequences[img._getexif()[exif_orientation_tag]]
		except:
			return img
		else:
			return functools.reduce(type(img).transpose, seq, img)


class AudioBlob(BlobObject):
	@property
	def url(self):
		return f'data:audio/mp3;base64,{base64.b64encode(self.getvalue()).decode()}'

# Field classes---------------------------------------------------------------------------------------------------------
class DefaultCharField(models.CharField):
	def __init__(self, *args, **kwargs):
		if 'max_length' not in kwargs:
			kwargs['max_length'] = 16
		super().__init__(*args, **kwargs)


class BlobField(models.BinaryField):
	def from_db_value(self, value, expression, connection):
		return self.obj_class(bytes=value, parent_field=self) if value is not None else None
	
	def get_db_prep_value(self, value, connection, prepared=False):
		return value.read() if value else None
	
	def from_file(self, bytes_file):
		""" Used to emulate field display normalisation """
		return self.obj_class.from_file(bytes_file=bytes_file, parent_field=self)


class ImageBlobField(BlobField):
	obj_class = ImageBlob
	
	def __init__(self, size, format='PNG', *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.size = size
		self.format = format


class AudioBlobField(BlobField):
	obj_class = AudioBlob