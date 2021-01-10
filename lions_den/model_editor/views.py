from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .decorators import login_and_zoo_access_required
from .zoos import zoos
from .models import Species, Individual
from .forms import get_subject_form, get_attributes_formset


@login_required
def zoos_index(request):
	#TODO: move this permission-check logic into a User model method
	if request.user.is_superuser:
		allowed_zoos = zoos.values()
	else:
		allowed_zoos = [zoos[user_group.name] for user_group in request.user.groups.all() if user_group.name in zoos]
	
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
		context={'zoo': zoos[zoo_id]}
	)

@login_and_zoo_access_required
def species_list(request, zoo_id):
	all_species = Species.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/species_list.html',
		context={'zoo': zoos[zoo_id], 'all_species' : all_species}
	)

@login_and_zoo_access_required
def species_page(request, zoo_id, species_id):
	species = Species.objects.using(zoo_id).filter(id=species_id).get()
	return subject(request, species)

@login_and_zoo_access_required
def individual(request, zoo_id, individual_id):
	species = Individual.objects.using(zoo_id).filter(id=individual_id).get().individuals.first()
	return subject(request, species)

#-------------------------------------------------------------------------------------------------------

def subject(request, subject):
	if request.method == 'POST':
		species_form = get_subject_form(subject, request.POST, request.FILES, prefix='subject')
		attributes_formset = get_attributes_formset(subject, request.POST, prefix='attributes')
		
		if species_form.is_valid():
			species_form.save()
		if attributes_formset.is_valid():
			attributes_formset.save()
	else:
		species_form = get_subject_form(subject=subject, prefix='subject')
		attributes_formset = get_attributes_formset(subject=subject, prefix='attributes')
	
	return render(
		request=request,
		template_name='model_editor/subject.html',
		context={
			'zoo': zoos[subject.zoo.id],
			'subject': subject,
			'subject_form': species_form,
			'attributes_formset': attributes_formset
		}
	)

@login_and_zoo_access_required
def attributes_list(request, zoo_id):
	all_attributes = Species.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/attributes_list.html',
		context={'zoo': zoos[zoo_id], 'all_attributes' : all_attributes}
	)
