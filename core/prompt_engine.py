class PromptEngine:
    def build_prompt(self, selected_text, user_prompt):
        """
        Build the final prompt for the AI model.
        """

        selected_text = selected_text.strip() if selected_text else ""
        user_prompt = user_prompt.strip() if user_prompt else ""

        # Chat mode (no selected text)
        if not selected_text:
            return user_prompt

        # Selected text mode
        prompt = f"""You are a helpful AI assistant.

Selected Text:
--------------------
{selected_text}
--------------------

User Request:
{user_prompt}

Provide a clear and helpful response.
"""

        return prompt