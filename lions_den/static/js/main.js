// Prepare for Ajax-----------------------------------------------------------------------------------------------------
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
//----------------------------------------------------------------------------------------------------------------------

// Dynamic image & audio updating in subject forms----------------------------------------------------------------------
function setDynamicBlobDisplay(displayID, widgetID, audioControlID, updateFunction) {
	let reloadAudio = function(){ if (audioControlID){ $("#" + audioControlID)[0].load() } };
	var initialValue = document.getElementById(displayID).src;
	document.querySelector('#' + widgetID).addEventListener('change', function() {
		var file = document.getElementById(widgetID).files[0];
		var displayElement = document.getElementById(displayID);
		if (file){
			var reader  = new FileReader();
			reader.onload = updateFunction;
			reader.readAsDataURL(file);
		} else {
			displayElement.src = initialValue;
			reloadAudio();
		}
	});
}

function setDynamicImageDisplay(displayID, widgetID, audioControlID){
	return setDynamicBlobDisplay(displayID, widgetID, null,
		function(e){
			var file = document.getElementById(widgetID).files[0];
			let formdata = new FormData();
			if (formdata) {
				formdata.append("image", file);
				$.ajax({
					url: document.URL,
					type: "POST",
					data: formdata,
					processData: false,
					contentType: false,
					success: function(data){ document.getElementById(displayID).src = data['image_src'] },
					error: function() {}
				});
			}
		}
	)
}

function setDynamicAudioDisplay(displayID, widgetID, audioControlID){
	return setDynamicBlobDisplay(displayID, widgetID, null,
		function(e){
			$("#" + audioControlID)[0].load();
			document.getElementById(displayID).src = e.target.result;
		}
	)
}

if (document.getElementById("id_subject_image")){
	setDynamicImageDisplay("id_subject_image-display", "id_subject_image");
}

if (document.getElementById("id_subject_audio")){
	setDynamicAudioDisplay("id_subject_audio-display", "id_subject_audio", "id_subject_audio-display_controls");
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