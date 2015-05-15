# Step repository for GUI testing in NH eTake List using CoffeeScript
# (compiles into Odoo syntax)
# - Colin showed Ami this
# - Ami started using it
# - Ami is now a developer yayyyyy
login_page_has_loaded = {
  title: 'Login page loaded',
  element: '.oe_topbar_name'
}

# Check that the referral board has loaded
referral_board_loaded = {
  title: "Referral Board Loaded",
  element: '.oe_menu_text:contains("Referral Board")'
}

# Click the Clerk button on the patient kanban screen
click_on_clerk_patient_button = {
  title: "Clerk patient(click on 'Clerk'  button)",
  element: 'td.oe_kanban_column:nth-child(3) .oe_fold_column' +
    '.oe_kanban_record:first() button'
}

# Enter data into diagnosis for patient, assumes:
# - You're on the patient screen
enter_diagnosis = {
  title: "Enter Diagnosis",
  element: 'textarea[name=diagnosis]',
  sampleText: 'Test diagnosis'
}

# Enter data into Plan for patient, assumes:
# - You're on patient screen
enter_plan = {
  title: "Enter Plan",
  element: 'textarea[name=plan]',
  sampleText: 'Test plan'
}

# click the Create doctor task for patient, assumes:
# - You're on patient screen
click_create_doctor_task_button = {
  title: "Create Task",
  element: '.oe_button.oe_form_button:contains("Create Task")'
}

# Enter data for creating a doctor task, assumes:
# - You're on patient screen
create_doctor_task = {
  title: "Enter Task",
  element: '.oe_form_field.oe_form_field_char.oe_form_required',
  sampleText:'Test Tasks Name'
}

# Click on submit task button for doctor task, assumes:
# - You're on patient screen
# - You've entered data into doctor task form
submit_doctor_task = {
  title: "Submit Tasks",
  element: '.oe_button.oe_form_button.oe_highlight'
}

# Save form, assumes:
# - There's a form to save
save_form = {
  title: "Save",
  element: '.oe_form_button_save'
}

# Checking that patient has moved to clerking in progess stage, assumes:
# - Currently in kanban mode
check_patient_moved_to_clerking_in_progress = {
  title: "patient stage updated to 'clerking in progress stage' ",
  waitFor: 'td.oe_kanban_column:nth-child(4) div.oe_fold_' +
    'column.oe_kanban_record'.length + 1
}

'use strict'

# Tour to test Junior Doctor stuff
openerp.Tour.register({
  id: 'junior_doctor_able_to_create_diagnosis_plans_tasks',
  name: "Junior Doctor able to create diagnosis plan tasks",
  path: '/web?debug=',
  steps: [
    login_page_has_loaded,
    referral_board_loaded,
    click_on_clerk_patient_button,
    enter_diagnosis,
    enter_plan,
    click_create_doctor_task_button,
    create_doctor_task,
    submit_doctor_task,
    save_form,
    check_patient_moved_to_clerking_in_progress
  ]
})

