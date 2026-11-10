from aqt.browser import Browser
from aqt.utils import showInfo, showWarning, showCritical, askUser

from . import ui_constants
from ..utils import constants


def show_successful_notes_creation(creation_deck: str, amount_of_notes: int, parent: Browser) -> None:
    showInfo(
        f"{amount_of_notes} new notes were successfully created!\n"
        f'You can find them in the deck "{creation_deck}"',
        parent=parent
    )


def show_successful_notes_replacement(parent: Browser) -> None:
    showInfo(
        f"Selected notes were successfully enhanced!\n",
        parent=parent
    )


def successful_notes_generation(
        time_spent: float,
        input_tokens: int,
        output_tokens: int,
        money_spent_on_input: float,
        money_spent_on_output: float,
        total_money_spent: float,
        ai_model: str,
        parent: Browser
) -> None:

    showInfo(
        f"Notes were successfully generated!\n"
        f"Time spent: {time_spent:.3f} seconds\n"
        f"\n"
        f"Input tokens used: {input_tokens}\n"
        f"Output tokens used: {output_tokens}\n"
        f"\n"
        f"Money spent on input {money_spent_on_input:.5f}$\n"
        f"Money spent on output {money_spent_on_output:.5f}$\n"
        f"Total money spent {total_money_spent:.5f}$\n"
        f"\n"
        f"Model: {ai_model}",
        parent=parent
    )

def profile_name_is_too_long_warning(profile_name: str, parent) -> None:
    showWarning(f'Profile name "{profile_name}" is longer than {ui_constants.PROFILE_NAME_MAX_LENGTH} characters. '
                f'Please write a shorter profile name.', parent=parent)

def profile_name_cant_be_empty_warning(parent) -> None:
    showWarning("Profile name cannot be empty. Please enter valid profile name.", parent=parent)

def profile_was_successfully_created(profile_name: str, parent) -> None:
    showInfo(f'Profile "{profile_name}" was successfully created', parent=parent)

def profile_was_successfully_edited(profile_name: str, parent) -> None:
    showInfo(f'Profile "{profile_name}" was successfully edited', parent=parent)

def confirm_unsaved_changes_discard(parent) -> bool:
    return askUser(
        "You have unsaved changes. Discard them and close?",
        parent=parent,
        title="Unsaved Changes"
    )

def confirm_profile_deletion(profile_name: str, parent) -> bool:
    return askUser(
            text=f'Are you sure you want to delete profile "{profile_name}"?',
            parent=parent,
            title="Confirm Deletion"
    )

def profile_was_successfully_deleted(profile_name: str, parent) -> None:
    showInfo(f"Profile {profile_name} was successfully deleted", parent=parent)

def too_many_notes_were_selected_warning(parent):
    showWarning(
        f"You have selected more than {constants.MAX_NOTES_TO_APPLY} notes.\n"
        f"Please select no more than {constants.MAX_NOTES_TO_APPLY} notes to apply a profile.",
        parent=parent
    )

def profile_with_such_name_already_exists(profile_name: str, parent=None) -> None:
    showInfo(
        f'Profile with name "{profile_name}" already exist. Please try a different name.',
        parent=parent
    )

def config_not_found_error(parent=None) -> None:
    showCritical("Config not found", parent=parent)

def more_than_one_note_type_selected_warning() -> None:
    showWarning("More than 1 note type selected")

def no_fields_were_selected(parent=None) -> None:
    showInfo(
        "You didn't select any card field.\n"
        "Please, select at least 1 card field.",
        parent=parent
    )


def no_cards_were_selected_warning() -> None:
    showWarning("No cards were selected")


def nothing_was_generated_critical(browser: Browser) -> None:
    showCritical("AI didn't generate anything.", parent=browser)


def less_than_3_lines_generated_critical(browser: Browser) -> None:
    showCritical("Unexpected amount of lines. The amount of generated lines is less than 3", parent=browser)


def number_of_lines_is_not_divisible_by_3_critical(browser: Browser) -> None:
    showCritical("Unexpected amount of lines. The amount of generated lines is not divisible by 3", parent=browser)


def successful_ingestion_of_generated_korean_sentences_info(
        time_spent: float,
        input_tokens: int,
        output_tokens: int,
        money_spent_on_input: float,
        money_spent_on_output: float,
        total_money_spent: float,
        model: str,
        browser: Browser) -> None:
    showInfo(
        f"AI response written successfully!\n"
        f"Time spent: {time_spent:.3f} seconds\n"
        f"\n"
        f"Input tokens used: {input_tokens}\n"
        f"Output tokens used: {output_tokens}\n"
        f"\n"
        f"Money spent on input {money_spent_on_input:.5f}$\n"
        f"Money spent on output {money_spent_on_output:.5f}$\n"
        f"Total money spent {total_money_spent:.5f}$\n"
        f"\n"
        f"Model: {model}",
        parent=browser
    )


def unknown_generation_error_critical(browser: Browser, e: Exception) -> None:
    showWarning(f"An unknown generation error occurred. Error message: {e}", parent=browser)
