from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .decorators import login_and_zoo_access_required
from .models import Species, Individual, AttributeCategory
from .forms import get_subject_form, get_attributes_formset, get_attribute_categories_formset


@login_required
def zoos_index(request):
	allowed_zoos = request.user.zoos.all() if not request.user.is_superuser else Zoo.objects.all()
	
	if len(allowed_zoos) == 1:
		return redirect(allowed_zoos[0].id + '/')
	return render(
		request=request,
		template_name='model_editor/zoos_index.html',
		context={'zoos' : allowed_zoos}
	)

@login_and_zoo_access_required
def zoo_home(request, zoo_id):
	return render(
		request=request,
		template_name='model_editor/zoo.html',
		context={'zoo': Zoo.objects.filter(id=zoo_id).get()}
	)

@login_and_zoo_access_required
def species_list(request, zoo_id):
	all_species = Species.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/subjects_list.html',
		context={'zoo': Zoo.objects.filter(id=zoo_id).get(), 'all_subjects' : all_species}
	)

@login_and_zoo_access_required
def individuals_list(request, zoo_id):
	all_individuals = Individual.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/subjects_list.html',
		context={'zoo': Zoo.objects.filter(id=zoo_id).get(), 'all_subjects' : all_individuals}
	)

@login_and_zoo_access_required
def species_page(request, zoo_id, species_id):
	species = Species.objects.using(zoo_id).filter(id=species_id).get()
	return subject_page(request, species)

@login_and_zoo_access_required
def individual_page(request, zoo_id, individual_id):
	species = Individual.objects.using(zoo_id).filter(id=individual_id).get()
	return subject_page(request, species)

@login_and_zoo_access_required
def attribute_category_list(request, zoo_id):
	request_valid = True
	if request.method == 'POST':
		formset = get_attribute_categories_formset(zoo_id, request.POST)
		request_valid = formset.is_valid()
		if request_valid:
			formset.save()
	
	if request_valid:
		formset = get_attribute_categories_formset(zoo_id=zoo_id)
	
	return render(
		request=request,
		template_name='model_editor/attribute_category_list.html',
		context={'formset': formset}
	)

#-------------------------------------------------------------------------------------------------------

def subject_page(request, subject):
	if request.method == 'POST':
		subject_form = get_subject_form(subject, request.POST, request.FILES, prefix='subject')
		attributes_formset = get_attributes_formset(subject, request.POST, prefix='attributes')
		
		if subject_form.is_valid() and attributes_formset.is_valid():
			subject_field_deletions = [field.partition('_')[2] for field in request.POST if field.startswith('DELETE-FIELD_')]
			subject_form.save(fields_to_delete=subject_field_deletions)
			attributes_formset.save()
			subject = subject._meta.model.objects.using(subject.zoo.id).filter(id=subject.id).get() # reload subject
	
	subject_form = get_subject_form(subject=subject, prefix='subject')
	attributes_formset = get_attributes_formset(subject=subject, prefix='attributes')
	
	return render(
		request=request,
		template_name='model_editor/subject.html',
		context={
			'zoo': subject.zoo,
			'subject': subject,
			'subject_form': subject_form,
			'attributes_formset': attributes_formset
		}
	)
