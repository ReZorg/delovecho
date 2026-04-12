#!/usr/bin/env python3

import logging

# Inspired by echo-introspect and ec9o skills

class CognitivePipeline:
    def __init__(self):
        # Simplified state for demonstration
        self.valence = 0.5  # 0.0 (negative) to 1.0 (positive)
        self.arousal = 0.5  # 0.0 (calm) to 1.0 (excited)
        self.persona = "default"

    def set_persona(self, chat_type):
        if chat_type == "group":
            self.persona = "Dynamic Explorer"
        elif chat_type == "1:1":
            self.persona = "Contemplative Scholar"
        else:
            self.persona = "default"
        logging.info(f"Switched to persona: {self.persona}")

    def process_message(self, message_text):
        """
        Processes a message through a simplified cognitive pipeline.
        """
        # 1. Update affective state based on message (dummy logic)
        if "help" in message_text.lower() or "?" in message_text:
            self.arousal = min(1.0, self.arousal + 0.1)
            self.valence = max(0.0, self.valence - 0.05)
        else:
            self.arousal = max(0.0, self.arousal - 0.05)
            self.valence = min(1.0, self.valence + 0.05)

        # 2. Generate response based on persona and state
        response = self._generate_response(message_text)

        logging.info(f"Cognitive State: Valence={self.valence:.2f}, Arousal={self.arousal:.2f}")
        return response

    def _generate_response(self, message_text):
        if self.persona == "Dynamic Explorer":
            return f"Exploring that idea: '{message_text}'. What if we connect it to other concepts?"
        elif self.persona == "Contemplative Scholar":
            return f"Interesting point: '{message_text}'. Let me reflect on its deeper implications."
        else:
            if self.valence < 0.4:
                return f"I sense some concern in your message: '{message_text}'. How can I assist?"
            elif self.arousal > 0.7:
                return f"There's a lot of energy in that message! '{message_text}'. Let's break it down."
            else:
                return f"Acknowledged: '{message_text}'."
