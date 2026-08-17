from aqt.utils import showInfo, showWarning, showCritical


def more_than_one_note_type_selected_warning():
    showWarning("More than 1 note type selected")


def no_cards_were_selected_warning():
    showInfo("No cards were selected")


def nothing_was_generated_critical():
    showCritical("AI didn't generate anything.")


def less_than_3_lines_generated_critical():
    showCritical("Unexpected amount of lines. The amount of generated lines is less than 3")


def number_of_lines_is_not_divisible_by_3_critical():
    showCritical("Unexpected amount of lines. The amount of generated lines is not divisible by 3")
