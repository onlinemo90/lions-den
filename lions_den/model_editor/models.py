import io
import base64
import enum
from PIL import Image

from django.db import models

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .utils.qrcode_creator import create_request_qrcode


class Gender(enum.Enum):
	MALE = 'M'
	FEMALE = 'F'


class BlobField(models.BinaryField):
	def from_db_value(self, value, expression, connection):
		return io.BytesIO(value) if value is not None else None
	
	def get_db_prep_value(self, value, connection, prepared=False):
		return value.read() if value is not None else None


class ImageBlobField(BlobField):
	def __init__(self, size, format='PNG', *args, **kwargs):
		self.size = size
		self.format = format
		super().__init__(*args, **kwargs)
	
	def get_db_prep_value(self, value, connection, prepared=False):
		value = self.normalise_image(value)
		return value.read() if value is not None else None
	
	def normalise_image(self, img):
		img = Image.open(img)
		width, height = img.size
		x_min, x_max, y_min, y_max = 0, width, 0, height
		aspect_ratio = self.size[0] / self.size[1]
		
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
		img = img.resize(self.size, Image.ANTIALIAS)
		
		# Output
		output = io.BytesIO()
		img.save(output, format=self.format)
		output.seek(0)
		return output
		

class DefaultCharField(models.CharField):
	def __init__(self, *args, **kwargs):
		if 'max_length' not in kwargs:
			kwargs['max_length'] = 16
		super().__init__(*args, **kwargs)


class AbstractBaseModel(models.Model):
	id = models.AutoField(db_column='_id', primary_key=True)
	
	class Meta:
		abstract = True
	
	def __getattribute__(self, name):
		try:
			return super().__getattribute__(name)
		except AttributeError:
			try:
				blob_field = name.removesuffix('_str')
				return base64.b64encode(super().__getattribute__(blob_field).read()).decode()
			except:
				return super().__getattribute__(name)  # raise original exception
	
	@property
	def zoo(self):
		assert self._state.db is not None, f'{self} does not belong to any zoo'
		return Zoo.objects.filter(id=self._state.db).first()


class Species(AbstractBaseModel):
	name = DefaultCharField()
	image = ImageBlobField(size=(256, 192), editable=True, null=True, blank=False)
	audio = BlobField(editable=True, null=True, blank=True)
	
	class Meta:
		db_table = 'SPECIES'
	
	def __str__(self):
		return self.name
	
	@property
	def qrcode(self):
		return create_request_qrcode(
			zoo=self.zoo,
			request='I|' + str(self.id)
		)


class Individual(AbstractBaseModel):
	species = models.ForeignKey(Species, related_name='individuals', on_delete=models.CASCADE)  # If the species is deleted, so are the related individuals
	name = DefaultCharField()
	dob = models.DateField()
	place_of_birth = DefaultCharField()
	weight = DefaultCharField()
	image = ImageBlobField(size=(256, 192), editable=True, null=True, blank=False)
	size = DefaultCharField()
	gender = DefaultCharField(
		choices=([(None, '')] + [(gender.value, gender.name.title()) for gender in Gender]),
		blank=True, null=True
	)
	
	class Meta:
		db_table = 'INDIVIDUAL'
	
	def __str__(self):
		return self.name


class AttributeCategory(AbstractBaseModel):
	name = DefaultCharField()
	priority = models.PositiveIntegerField(unique=True)
	
	class Meta: db_table = 'ATTRIBUTE_CATEGORY'
	
	def __str__(self): return self.name


class AbstractAttribute(AbstractBaseModel):
	category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE)
	attribute = models.TextField()
	
	class Meta: abstract = True
	
	def __str__(self): return f'{self.category} -> {self.attribute}'


class SpeciesAttribute(AbstractAttribute):
	subject = models.ForeignKey(Species, related_name='attributes', on_delete=models.CASCADE)
	
	class Meta: db_table = 'SPECIES_ATTRIBUTES'


class IndividualAttribute(AbstractAttribute):
	subject = models.ForeignKey(Individual, related_name='attributes', on_delete=models.CASCADE)
	
	class Meta: db_table = 'INDIVIDUALS_ATTRIBUTES'


