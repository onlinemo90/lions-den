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
		return io.BytesIO(value) if value is not None else None
	
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


class SubjectManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().order_by('name')


class Subject(AbstractBaseModel):
	name = DefaultCharField()
	image = BlobField(editable=True, null=True, blank=False)
	
	objects = SubjectManager()
	
	class Meta:
		abstract = True
	
	def __str__(self):
		return self.name
	
	@property
	def attribute_model(self):
		raise NotImplementedError()
	
	@property
	def form(self):
		raise NotImplementedError()
	

class Species(Subject):
	audio = BlobField(editable=True, null=True, blank=True)
	weight = DefaultCharField()
	size = DefaultCharField()
	
	class Meta:
		db_table = 'SPECIES'
	
	@property
	def attribute_model(self):
		return SpeciesAttribute
	
	@property
	def form(self):
		from .forms import SpeciesForm
		return SpeciesForm
	
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


class Individual(Subject):
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
	
	@property
	def attribute_model(self):
		return IndividualAttribute
	
	@property
	def form(self):
		from .forms import IndividualForm
		return IndividualForm


class Group(Subject):
	audio = BlobField(editable=True, null=True, blank=True)
	species = models.ManyToManyField(Species, related_name='groups', related_query_name='group', db_table='GROUPS_SPECIES')
	individuals = models.ManyToManyField(Individual, related_name='groups', related_query_name='group', db_table='GROUPS_INDIVIDUALS')
	
	class Meta:
		db_table = '_GROUP_'
	
	def __str__(self):
		return self.name
	
	@property
	def attribute_model(self):
		return GroupAttribute
	
	@property
	def form(self):
		from .forms import GroupForm
		return GroupForm
	
	@property
	def non_member_species(self):
		return Species.objects.using(self.zoo.id).exclude(id__in=self.species.values_list('id', flat=True))
	
	def non_member_individuals(self):
		return Individual.objects.using(self.zoo.id).exclude(id__in=self.individuals.values_list('id', flat=True))
	


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


class GroupAttribute(AbstractAttribute):
	subject = models.ForeignKey(Group, related_name='attributes', on_delete=models.CASCADE)
	
	class Meta: db_table = 'GROUPS_ATTRIBUTES'