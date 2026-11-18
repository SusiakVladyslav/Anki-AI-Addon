import copy
from unittest.mock import patch, MagicMock
import pytest

from ankiaddon.gui import profile_configuration
from ankiaddon.gui.profile_configuration import DialogMode, ProfileConfigurationDialog

SAMPLE_PROFILE_NAME = "Korean Vocab Profile"

SAMPLE_SETTINGS = {
    "selected_card_type": "Korean Vocab",
    "selected_fields": ["Korean", "English"],
    "selected_fields_settings": {
        "Korean": {
            "strip_html": True,
            "strip_brackets": False,
            "convert_cloze": False,
            "strip_non_ascii": False,
        },
        "English": {
            "strip_html": True,
            "strip_brackets": False,
            "convert_cloze": False,
            "strip_non_ascii": False,
        },
    },
    "selected_model": "gpt-6-luna",
    "generate_as_new_cards": True,
    "deck_for_generated_cards": "Korean Deck",
    "add_tag_to_generated_cards": True,
    "tag_name_for_generated_cards": "ai_enhanced",
    "prompt_text": "Enhance these cards",
}

SAMPLE_PROFILE = {SAMPLE_PROFILE_NAME: SAMPLE_SETTINGS}


@pytest.fixture
def dialog_logic_deps():
    """
    Refactor-proof fixture for business logic tests (validation, saving, dirty-state).
    Mocks _collect_profile_settings and load_profile_settings directly so tests do not
    depend on internal child widget names or tab hierarchy.
    """
    profile_configuration.aqt.qt.QDialogButtonBox.reset_mock()
    with (
        patch.object(profile_configuration, "PromptTextEditLayout"),
        patch.object(profile_configuration, "ProfileCreationSettings"),
        patch.object(profile_configuration, "gui_utils") as mock_gui_utils,
        patch.object(profile_configuration, "notifications") as mock_notifications,
        patch.object(profile_configuration.ProfileConfigurationDialog, "_collect_profile_settings") as mock_collect,
        patch.object(profile_configuration.ProfileConfigurationDialog, "load_profile_settings") as mock_load,
    ):
        mock_collect.return_value = copy.deepcopy(SAMPLE_PROFILE)
        yield {
            "collect": mock_collect,
            "load": mock_load,
            "gui_utils": mock_gui_utils,
            "notifications": mock_notifications,
        }


def test_init_create_mode(dialog_logic_deps):
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    assert isinstance(dialog.mode, DialogMode.Create)
    assert dialog.original_profile_name is None
    assert not hasattr(dialog, "save_button")
    dialog_logic_deps["load"].assert_not_called()

    print("BUTTON BOX CALLS:", dialog.commit_buttons_box.mock_calls)

    dialog.commit_buttons_box.rejected.connect.assert_called_once_with(dialog.reject)
    dialog.commit_buttons_box.accepted.connect.assert_called_once_with(dialog._insert_profile_settings)


def test_init_edit_mode(dialog_logic_deps):
    settings = copy.deepcopy(SAMPLE_SETTINGS)
    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=settings)
    )

    assert isinstance(dialog.mode, DialogMode.Edit)

    dialog.save_button.setEnabled.assert_called_once_with(False)
    dialog.commit_buttons_box.accepted.connect.assert_called_once_with(dialog._update_profile_settings)
    dialog.commit_buttons_box.rejected.connect.assert_called_once_with(dialog.reject)
    dialog_logic_deps["load"].assert_called_once_with(
        profile_name=SAMPLE_PROFILE_NAME,
        profile_settings=settings,
    )


def test_on_widget_settings_changed_toggles_save_button(dialog_logic_deps):
    settings = copy.deepcopy(SAMPLE_SETTINGS)
    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=settings)
    )
    dialog.config = copy.deepcopy(SAMPLE_PROFILE)
    dialog.save_button.setEnabled.reset_mock()

    modified_profile = copy.deepcopy(SAMPLE_PROFILE)
    modified_profile[SAMPLE_PROFILE_NAME]["prompt_text"] = "Modified prompt text"
    dialog_logic_deps["collect"].return_value = modified_profile

    dialog._on_widget_settings_changed()
    dialog.save_button.setEnabled.assert_called_once_with(True)

    dialog.save_button.setEnabled.reset_mock()
    dialog_logic_deps["collect"].return_value = copy.deepcopy(SAMPLE_PROFILE)

    dialog._on_widget_settings_changed()
    dialog.save_button.setEnabled.assert_called_once_with(False)


def test_reject_closes_immediately_when_no_unsaved_changes(dialog_logic_deps):
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    with patch.object(profile_configuration.aqt.qt.QDialog, "reject") as mock_super_reject:
        dialog.reject()

        dialog_logic_deps["notifications"].confirm_unsaved_changes_discard.assert_not_called()
        mock_super_reject.assert_called_once()


@pytest.mark.parametrize("user_confirms_discard", [True, False])
def test_reject_prompts_when_unsaved_changes_exist(dialog_logic_deps, user_confirms_discard):
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    modified_profile = copy.deepcopy(SAMPLE_PROFILE)
    modified_profile[SAMPLE_PROFILE_NAME]["prompt_text"] = "Unsaved edit"
    dialog_logic_deps["collect"].return_value = modified_profile
    dialog_logic_deps["notifications"].confirm_unsaved_changes_discard.return_value = user_confirms_discard

    with patch.object(profile_configuration.aqt.qt.QDialog, "reject") as mock_super_reject:
        dialog.reject()

        dialog_logic_deps["notifications"].confirm_unsaved_changes_discard.assert_called_once_with(parent=dialog)
        if user_confirms_discard:
            mock_super_reject.assert_called_once()
        else:
            mock_super_reject.assert_not_called()


def test_insert_profile_settings_empty_name_shows_warning(dialog_logic_deps):
    dialog_logic_deps["collect"].return_value = {"": copy.deepcopy(SAMPLE_SETTINGS)}
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    dialog._insert_profile_settings()

    dialog_logic_deps["notifications"].profile_name_cant_be_empty_warning.assert_called_once_with(
        parent=dialog.parent
    )
    dialog_logic_deps["gui_utils"].insert_profile_settings_in_config.assert_not_called()


def test_insert_profile_settings_name_too_long_shows_warning(dialog_logic_deps):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = True
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    dialog._insert_profile_settings()

    dialog_logic_deps["notifications"].profile_name_is_too_long_warning.assert_called_once_with(
        SAMPLE_PROFILE_NAME, parent=dialog.parent
    )
    dialog_logic_deps["gui_utils"].insert_profile_settings_in_config.assert_not_called()


def test_insert_profile_settings_no_fields_selected_shows_warning(dialog_logic_deps):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = False
    no_fields_profile = copy.deepcopy(SAMPLE_PROFILE)
    no_fields_profile[SAMPLE_PROFILE_NAME]["selected_fields"] = []
    dialog_logic_deps["collect"].return_value = no_fields_profile

    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())
    dialog._insert_profile_settings()

    dialog_logic_deps["notifications"].no_fields_were_selected.assert_called_once_with(parent=dialog.parent)
    dialog_logic_deps["gui_utils"].insert_profile_settings_in_config.assert_not_called()


@pytest.mark.parametrize("insert_succeeded", [True, False])
def test_insert_profile_settings_save_flow(dialog_logic_deps, insert_succeeded):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = False
    dialog_logic_deps["gui_utils"].insert_profile_settings_in_config.return_value = insert_succeeded
    dialog = ProfileConfigurationDialog(mode=DialogMode.Create())

    with patch.object(dialog, "accept") as mock_accept:
        dialog._insert_profile_settings()

        dialog_logic_deps["gui_utils"].insert_profile_settings_in_config.assert_called_once_with(SAMPLE_PROFILE)
        if insert_succeeded:
            mock_accept.assert_called_once()
            dialog_logic_deps["notifications"].profile_was_successfully_created.assert_called_once_with(
                profile_name=SAMPLE_PROFILE_NAME,
                parent=dialog.parent,
            )
        else:
            mock_accept.assert_not_called()
            dialog_logic_deps["notifications"].profile_was_successfully_created.assert_not_called()


def test_update_profile_settings_empty_name_shows_warning(dialog_logic_deps):
    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=copy.deepcopy(SAMPLE_SETTINGS))
    )
    dialog_logic_deps["collect"].return_value = {"": copy.deepcopy(SAMPLE_SETTINGS)}

    dialog._update_profile_settings()

    dialog_logic_deps["notifications"].profile_name_cant_be_empty_warning.assert_called_once_with(
        parent=dialog.parent
    )
    dialog_logic_deps["gui_utils"].update_profile_settings_name.assert_not_called()


def test_update_profile_settings_name_too_long_shows_warning(dialog_logic_deps):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = True
    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=copy.deepcopy(SAMPLE_SETTINGS))
    )

    dialog._update_profile_settings()

    dialog_logic_deps["notifications"].profile_name_is_too_long_warning.assert_called_once_with(
        SAMPLE_PROFILE_NAME, parent=dialog.parent
    )
    dialog_logic_deps["gui_utils"].update_profile_settings_name.assert_not_called()


def test_update_profile_settings_no_fields_selected_shows_warning(dialog_logic_deps):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = False
    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=copy.deepcopy(SAMPLE_SETTINGS))
    )
    no_fields_profile = copy.deepcopy(SAMPLE_PROFILE)
    no_fields_profile[SAMPLE_PROFILE_NAME]["selected_fields"] = []
    dialog_logic_deps["collect"].return_value = no_fields_profile

    dialog._update_profile_settings()

    dialog_logic_deps["notifications"].no_fields_were_selected.assert_called_once_with(parent=dialog.parent)
    dialog_logic_deps["gui_utils"].update_profile_settings_name.assert_not_called()


@pytest.mark.parametrize(
    "edited_name, name_was_edited",
    [
        (SAMPLE_PROFILE_NAME, False),
        ("Renamed Korean Vocab Profile", True),
    ],
)
def test_update_profile_settings_success(dialog_logic_deps, edited_name, name_was_edited):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = False
    dialog_logic_deps["gui_utils"].update_profile_settings_name.return_value = True

    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=copy.deepcopy(SAMPLE_SETTINGS))
    )

    dialog.original_profile_name = SAMPLE_PROFILE_NAME
    dialog.profile_settings_changed = MagicMock()

    updated_profile = {edited_name: copy.deepcopy(SAMPLE_SETTINGS)}
    dialog_logic_deps["collect"].return_value = updated_profile

    with patch.object(dialog, "accept") as mock_accept:
        dialog._update_profile_settings()

        if name_was_edited:
            dialog_logic_deps["gui_utils"].update_profile_settings_name.assert_called_once_with(
                updated_profile,
                profile_name_was_edited=True,
                original_profile_name=SAMPLE_PROFILE_NAME,
            )
        else:
            dialog_logic_deps["gui_utils"].update_profile_settings_name.assert_called_once_with(
                updated_profile,
                profile_name_was_edited=False,
            )

        dialog.profile_settings_changed.emit.assert_called_once_with(updated_profile)
        mock_accept.assert_called_once()
        dialog_logic_deps["notifications"].profile_was_successfully_edited.assert_called_once_with(
            edited_name, parent=dialog.parent
        )


def test_update_profile_settings_aborts_if_config_write_fails(dialog_logic_deps):
    dialog_logic_deps["gui_utils"].profile_name_is_too_long.return_value = False
    dialog_logic_deps["gui_utils"].update_profile_settings_name.return_value = False

    dialog = ProfileConfigurationDialog(
        mode=DialogMode.Edit(profile_name=SAMPLE_PROFILE_NAME, profile_settings=copy.deepcopy(SAMPLE_SETTINGS))
    )
    dialog.original_profile_name = SAMPLE_PROFILE_NAME
    dialog.profile_settings_changed = MagicMock()

    with patch.object(dialog, "accept") as mock_accept:
        dialog._update_profile_settings()

        dialog.profile_settings_changed.emit.assert_not_called()
        mock_accept.assert_not_called()
        dialog_logic_deps["notifications"].profile_was_successfully_edited.assert_not_called()
