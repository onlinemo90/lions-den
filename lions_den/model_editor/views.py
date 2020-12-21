from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Species

@login_required
def zoo_home(request, zoo_id):
	all_species = Species.objects.using(zoo_id).all()
	return render(
		request=request,
		template_name='model_editor/zoo.html',
		context={'all_species' : all_species}
	)

@login_required
def species(request, zoo_id, species_id):
	species = Species.objects.using(zoo_id).filter(id=species_id).get()
	return render(
		request=request,
		template_name='model_editor/species.html',
		context={'species': species}
	)