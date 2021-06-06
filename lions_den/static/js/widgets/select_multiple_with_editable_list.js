document.addEventListener("DOMContentLoaded", function(){
	let multiSelectFormId = 'SELECT_MULTIPLE_WITH_EDITABLE_LIST';
	$('div#' + multiSelectFormId).each(function(){
		var container = $(this);
		var hiddenInput = $('select[multiple]', container);

		// Populate members list and non-members select
		hiddenInput.find('option').each(function(){ // Loop each option of the hidden select
			// Non-members select
			let selectOption = document.createElement('option');
			selectOption.text = $(this).html();
			selectOption.value = $(this).val();

			// Members list
			let memberListItem = $('li[value=GROUP_LIST_ITEM_TEMPLATE]', container).clone();
			memberListItem.val($(this).val());
			memberListItem.html(memberListItem.html().replaceAll('[MEMBER_NAME]', $(this).html()));

			if ($(this).prop('selected')){
				memberListItem.removeAttr('hidden'); // un-hide from list
				selectOption.setAttributeNode(document.createAttribute('hidden')); // hide from select
			}

			// Add elements
			$('.NON_MEMBERS_SELECT', container).append(selectOption);
			$('.MEMBERS_LIST', container).append(memberListItem);
		});

		// Set onclick of button for adding members to group
		$('.ADD_MEMBER_BUTTON', this).click(function(){
			memberId = $('.NON_MEMBERS_SELECT', container).val();
			if (memberId){
				$('option[value=' + memberId + ']', hiddenInput).attr('selected', true); // select in hidden form field
				$('.MEMBERS_LIST li[value=' + memberId + ']', container).prop('hidden', false); // show in members list
				$('.NON_MEMBERS_SELECT option[value=' + memberId + ']', container).prop('hidden', true); // hide from non-members select

				$('.NON_MEMBERS_SELECT', container).prop('selectedIndex', 0); // reset selection
			}
		});

		// Set onclick of button for removing members to group
		$('.REMOVE_MEMBER_BUTTON', this).click(function(){
			let memberId = $(this).parent().val();
			$('option[value=' + memberId + ']', hiddenInput).attr('selected', false); // unselect in hidden form field
			$('.MEMBERS_LIST li[value=' + memberId + ']', container).prop('hidden', true); // hide from members list
			$('.NON_MEMBERS_SELECT option[value=' + memberId + ']', container).prop('hidden', false); // show in non-members select
		});
	});
});