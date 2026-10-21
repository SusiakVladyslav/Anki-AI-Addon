import aqt.utils
from aqt import mw
from aqt.operations import QueryOp
from anki.notes import Note
from aqt.browser import Browser

from typing import Any

from ..ai.openai_requests import send_open_ai_request, AiOutput
from.func_utils import calculate_spent_money

class ProfileService:
    def __init__(self, browser, profile_settings):
        self.profile_settings: dict[str, Any] = profile_settings
        self.browser: Browser = browser

        self.prompt: str = self.profile_settings["prompt_text"]
        self.ai_model: str = self.profile_settings["selected_model"]

        self.selected_fields = self.profile_settings["selected_fields"]

        self.selected_card_type = self.profile_settings["selected_card_type"]
        self.generate_as_new_cards: bool = self.profile_settings["generate_as_new_cards"]
        self.deck_for_generated_cards: str | None = self.profile_settings["deck_for_generated_cards"]
        self.add_tag_to_generated_cards: bool = self.profile_settings["add_tag_to_generated_cards"]
        self.tag_name_for_generated_cards: str | None = self.profile_settings["tag_name_for_generated_cards"]

    def apply_profile(self, parent, input_data, selected_notes):

        op = QueryOp(
            parent=parent,
            op = lambda _: send_open_ai_request(input_data=input_data, prompt=self.prompt, model=self.ai_model, selected_fields=self.selected_fields),
            success=lambda ai_output, notes=selected_notes: self._apply_results_to_notes(ai_output=ai_output, notes=notes),
        )

        op.with_progress("AI is generating sentences...").run_in_background()

    def _apply_results_to_notes(self, ai_output: AiOutput, notes):
        generated_notes = ai_output.output_json["generated_notes"]
        if self.generate_as_new_cards:
            self._create_new_notes(generated_notes)
        else:
            self._replace_existing_notes(generated_notes, notes)

        self.on_successful_notes_enhancement_dialog(ai_output)

    def _create_new_notes(self, generated_notes:list[dict[str, str]]):
        deck_id = mw.col.decks.id_for_name(self.deck_for_generated_cards)
        note_type = mw.col.models.by_name(self.selected_card_type)

        for generated_note in generated_notes:
            new_note = mw.col.new_note(note_type)

            for field_name, field_data in generated_note.items():
                new_note[field_name] = field_data

                if self.add_tag_to_generated_cards:
                    new_note.add_tag(self.tag_name_for_generated_cards) # if tag_name contains space it will add a tag for each word instead of just 1 tag

            mw.col.add_note(new_note, deck_id)

    @staticmethod
    def _replace_existing_notes(generated_notes: list[dict[str, str]], selected_notes: list[Note]):
        for note, note_dict in zip(selected_notes, generated_notes):
            for field_name, field_data in note_dict.items():
                note[field_name] = field_data

            note.col.update_note(note)


    def on_successful_notes_enhancement_dialog(self, ai_output: AiOutput):
        self.browser.onSearchActivated()
        if self.browser.editor.note:
            self.browser.editor.loadNote()

        money_spent_on_input, money_spent_on_output, total_money_spent = (
            calculate_spent_money(ai_output.input_tokens, ai_output.output_tokens, self.ai_model)
        )

        aqt.utils.showInfo(
            f"Notes were successfully enhanced!\n"
            f"Time spent: {ai_output.time_spent:.3f} seconds\n"
            f"\n"
            f"Input tokens used: {ai_output.input_tokens}\n"
            f"Output tokens used: {ai_output.output_tokens}\n"
            f"\n"
            f"Money spent on input {money_spent_on_input:.5f}$\n"
            f"Money spent on output {money_spent_on_output:.5f}$\n"
            f"Total money spent {total_money_spent:.5f}$\n"
            f"\n"
            f"Model: {self.ai_model}",
            parent=self.browser
        )
