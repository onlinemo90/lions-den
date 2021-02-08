// Load Bootstrap Toasts------------------------------------------------------------------------------------------------
$('.toast').toast('show');
//----------------------------------------------------------------------------------------------------------------------

// Dynamic image & audio updating in subject forms----------------------------------------------------------------------
function setDynamicBlobDisplay(displayID, widgetID, audioControlID) {
	let reloadAudio = function(){ if (audioControlID){ $("#" + audioControlID)[0].load() } };
	var initialValue = document.getElementById(displayID).src;
	document.querySelector('#' + widgetID).addEventListener('change', function() {
		var file = document.getElementById(widgetID).files[0];
		var displayElement = document.getElementById(displayID);
		if (file){
			var reader  = new FileReader();
			reader.onload = function(e) {
				displayElement.src = e.target.result;
				reloadAudio();
			};
			reader.readAsDataURL(file);
		} else {
			displayElement.src = initialValue;
			reloadAudio();
		}
	});
};

if (document.getElementById("id_subject_image")){
	setDynamicBlobDisplay("id_subject_image_display", "id_subject_image");
}

if (document.getElementById("id_subject_audio")){
	setDynamicBlobDisplay("id_subject_audio_display", "id_subject_audio", "id_audio_control");
}
//----------------------------------------------------------------------------------------------------------------------

// Filtering Individuals List by Species--------------------------------------------------------------------------------
if (document.getElementById('select_species')){
	$('#select_species').on('change', function(){
		$.ajax({
			type: 'GET',
			url: document.URL,
			data: 'species_id=' + $(this).val(),
			success: function (response) {
				$('#subject-table').replaceWith(response);
			}
		});
	});
}
//----------------------------------------------------------------------------------------------------------------------

