
function setupNestedCheckBox(){
    var main_checkbox = document.getElementById('mainBox');
    var sub_checkboxes = document.querySelectorAll('input.subBox');
    updateMainCheckBox(main_checkbox, sub_checkboxes);

    for (var i = 0; i < sub_checkboxes.length; i++) {
        sub_checkboxes[i].addEventListener('change', function () { updateMainCheckBox(main_checkbox, sub_checkboxes) });
    }
    main_checkbox.addEventListener('change', function () { updateNestedCheckBoxes(main_checkbox, sub_checkboxes) });
}

function updateNestedCheckBoxes(main_checkbox, sub_checkboxes){
    for (var i = 0; i < sub_checkboxes.length; i++) {
        sub_checkboxes[i].checked = main_checkbox.checked;
    }
}

function updateMainCheckBox(main_checkbox, sub_checkboxes) {
    var checked_cnt = 0;
    for (var i = 0; i < sub_checkboxes.length; i++) {
        if (sub_checkboxes[i].checked) {
            checked_cnt++;
        }
        main_checkbox.checked = checked_cnt > 0;
        main_checkbox.indeterminate = main_checkbox.checked && (checked_cnt < sub_checkboxes.length);
    }
}


