import datetime

from django import forms
from django.forms.models import modelformset_factory

from .models import Species, Individual, SpeciesAttribute, IndividualAttribute, AttributeCategory


class BaseModelForm(forms.ModelForm):
	""""
		Base class for Forms that is compatible with custom DBs
		If not binding to a model instance, provide a zoo_id argument
	"""
	def __init__(self, *args, **kwargs):
		if 'zoo_id' in kwargs:
			zoo_id = kwargs.pop('zoo_id')
		elif 'instance' in kwargs:
			zoo_id = kwargs['instance'].zoo.id
		else:
			raise Exception('zoo_id must be given to create zoo-related form')
		
		if 'instance' not in kwargs:
			super().__init__(*args, **kwargs)
			self.instance._state.db = zoo_id
		else:
			super().__init__(*args, **kwargs)


class BaseSubjectForm(BaseModelForm):
	def __init__(self, *args, **kwargs):
		# Stabilising HTML element ID generation to allow Javascript ID matching on field HTML elements
		kwargs['auto_id'] = 'id_subject_%s'
		if 'prefix' in kwargs:
			raise Exception("""
				A prefix is not allowed for SubjectForms.
				Unless you're trying to display multiple SubjectForms in one page, this shouldn't be needed.
			""")
		super().__init__(*args, **kwargs)
	
	def save(self, fields_to_delete=[]):
		for field in fields_to_delete:
			field_type = type(getattr(self.instance, field))
			setattr(self.instance, field, field_type())
		super().save()


class SpeciesForm(BaseSubjectForm):
	image = forms.FileField()
	audio = forms.FileField(required=False)
	
	class Meta:
		model = Species
		fields = ('name', 'image', 'audio')
		labels = {
			'name': 'Name',
			'image': 'Image',
			'audio': 'Audio'
		}


class IndividualForm(BaseSubjectForm):
	species = forms.ModelChoiceField(queryset=None) # set in __init__
	image = forms.FileField()
	weight = forms.CharField(required=False)
	place_of_birth = forms.CharField(required=False)
	size = forms.CharField(required=False)
	dob = forms.DateField(
		widget=forms.widgets.SelectDateWidget(
			years=list(range(datetime.date.today().year, datetime.date.today().year - 101, -1)),
			empty_label=''
		),
		required=False,
		label='Date of Birth'
	)
	
	class Meta:
		model = Individual
		fields = ['species', 'name', 'image', 'gender', 'dob', 'place_of_birth', 'size', 'weight']
		labels = {
			'species': 'Species',
			'name': 'Name',
			'image': 'Image',
			'gender': 'Gender',
			'weight': 'Weight',
			'place_of_birth': 'Place of Birth',
			'size': 'Size'
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Allow form to be used both for editing existing individuals and for creating new ones
		if 'instance' in kwargs:
			del self.fields['species']
		else:
			self.fields['species'] = forms.ModelChoiceField(empty_label='', queryset=Species.objects.using(kwargs['zoo_id']).order_by('name').all())


class AttributeCategoryForm(BaseModelForm):
	class Meta:
		model = AttributeCategory
		fields = ('name',)


def get_attributes_formset(subject, *args, **kwargs):
	SubjectAttribute = SpeciesAttribute if isinstance(subject, Species) else IndividualAttribute
	if len(subject.attributes.all()) > 0:
		# Define form for displaying/editing each attribute
		class SubjectAttributeForm(BaseModelForm):
			class Meta:
				model = SubjectAttribute
				fields = ('attribute',)
			
			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.fields['attribute'].label = self.instance.category.name
		
		
		# Define formset for multiple attributes
		BaseSubjectAttributesFormSet = forms.modelformset_factory(
			SubjectAttribute,
			form=SubjectAttributeForm,
			extra=0,
			can_delete=True,
			can_order=False
		)
		
		# Define formset for attributes specific to a subject (Species or Individual)
		class SubjectAttributesFormSet(BaseSubjectAttributesFormSet):
			def __init__(self, subject, *args, **kwargs):
				super().__init__(
					queryset=SubjectAttribute.objects.using(subject.zoo.id).filter(subject_id=subject.id).order_by('-category__priority').all(),
					form_kwargs={'zoo_id': subject.zoo.id},
					*args, **kwargs
				)
				
		return SubjectAttributesFormSet(subject, *args, **kwargs)
	return None


def get_attribute_categories_formset(zoo_id, *args, **kwargs):
	BaseAttributeCategoriesFormset = modelformset_factory(
		AttributeCategory,
		form=AttributeCategoryForm,
		extra=0,
		can_delete=True,
		can_order=True
	)
	
	class AttributeCategoriesFormset(BaseAttributeCategoriesFormset):
		def __init__(self, zoo_id, *args, **kwargs):
			super().__init__(
				queryset=AttributeCategory.objects.using(zoo_id).order_by('-priority').all(),
				form_kwargs={'zoo_id': zoo_id},
				*args, **kwargs
			)
		
		def save(self, commit=True):
			super().save(commit)
			
			def set_categories_priority(max_priority):
				current_priority = max_priority
				for form in self.ordered_forms:
					form.instance.priority = current_priority
					current_priority -= 1
					form.instance.save()
			
			set_categories_priority(3 * len(self.forms))
			set_categories_priority(len(self.forms))
	
	return AttributeCategoriesFormset(zoo_id, *args, **kwargs)


def get_new_attribute_form(subject, *args, **kwargs):
	used_categories = [attribute.category.id for attribute in subject.attributes.all()]
	category_queryset = AttributeCategory.objects.using(subject.zoo.id).exclude(id__in=used_categories)
	
	if len(category_queryset) > 0:
		class NewSubjectAttributeForm(BaseModelForm):
			class Meta:
				model = SpeciesAttribute if isinstance(subject, Species) else IndividualAttribute
				fields = ('category', 'attribute')
				labels = {'category': 'Header', 'attribute': 'Text'}
			
			def __init__(self, *args, **kwargs):
				super().__init__(zoo_id=subject.zoo.id, *args, **kwargs)
				self.fields['category'] = forms.ModelChoiceField(queryset=category_queryset, empty_label='')
			
			def save(self, commit=True):
				self.instance.subject = subject
				super().save(commit)
		
		return NewSubjectAttributeForm(*args, **kwargs)
	return None