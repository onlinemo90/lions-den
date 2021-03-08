import io
import base64
import enum

from django.db import models

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .utils.qrcode_creator import create_request_qrcode


class Gender(enum.Enum):
	MALE = 'M'
	FEMALE = 'F'


class BlobField(models.BinaryField):
	def from_db_value(self, value, expression, connection):
		return io.BytesIO(value) if value is not None else io.BytesIO()
	
	def get_db_prep_value(self, value, connection, prepared=False):
		return value.read() if value is not None else None


class DefaultCharField(models.CharField):
	def __init__(self, *args, **kwargs):
		if 'max_length' not in kwargs:
			kwargs['max_length'] = 16
		super().__init__(*args, **kwargs)


class AbstractBaseModel(models.Model):
	id = models.AutoField(db_column='_id', primary_key=True)
	
	class Meta:
		abstract = True
	
	@property
	def zoo(self):
		assert self._state.db is not None, f'{self} does not belong to any zoo'
		return Zoo.objects.filter(id=self._state.db).first()


class ZooSubject(AbstractBaseModel):
	name = DefaultCharField()
	image = BlobField(editable=True, null=True, blank=False)
	
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
	
	def __str__(self):
		return self.name
	
	def has_max_attributes(self):
		return len(self.attributes.all()) == len(AttributeCategory.objects.using(self.zoo.id).all())
	
	def qr_code(self):
		if isinstance(self, Species):
			type_str = 'species'
		elif isinstance(self, Individual):
			type_str = 'individual'
		elif isinstance(self, Group):
			type_str = 'group'
		else:
			return None
		
		return create_request_qrcode(
			zoo=self.zoo,
			request = {
				'zoo': self.zoo.id,
				'type': type_str,
				'id': self.id
			}
		)


class Species(ZooSubject):
	audio = BlobField(editable=True, null=True, blank=True)
	weight = DefaultCharField()
	size = DefaultCharField()
	
	class Meta:
		db_table = 'SPECIES'


class Individual(ZooSubject):
	species = models.ForeignKey(Species, related_name='individuals', on_delete=models.CASCADE)  # If the species is deleted, so are the related individuals
	dob = models.DateField()
	place_of_birth = DefaultCharField()
	image = BlobField(editable=True, null=True, blank=False)
	gender = DefaultCharField(
		choices=([(None, '')] + [(gender.value, gender.name.title()) for gender in Gender]),
		blank=True, null=True
	)
	
	class Meta:
		db_table = 'INDIVIDUAL'


class Group(ZooSubject): # Added just for QR Code support
	pass


class AttributeCategory(AbstractBaseModel):
	name = DefaultCharField()
	position = models.PositiveIntegerField(unique=True)
	
	class Meta: db_table = 'ATTRIBUTE_CATEGORY'
	
	def __str__(self): return self.name
	
	def save(self):
		# If adding a new category, set the priority to above current highest
		if self._state.adding:
			highest_position = AttributeCategory.objects.using(self.zoo.id).all().aggregate(highest=models.Max('position'))['highest']
			self.position = highest_position + 1 if highest_position else 1
		super().save()


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


