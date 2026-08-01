import os
from typing import Dict, Any, Tuple
from app.core import sha256_string

class PromptBuilder:
    @staticmethod
    def get_prompt_dir() -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts", "v1")

    @classmethod
    def build_prompt(cls, prompt_name: str, variables: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Loads the prompt template file prompt_name + ".md", formats it with variables,
        and returns a tuple of (formatted_prompt_text, template_sha256_hash, version_tag).
        """
        prompt_dir = cls.get_prompt_dir()
        file_path = os.path.join(prompt_dir, f"{prompt_name}.md")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Calculate template hash using unified helper
        template_hash = sha256_string(template_content)

        # Format variables into the template
        try:
            formatted_prompt = template_content.format(**variables)
        except KeyError as e:
            raise KeyError(f"Missing required format variable '{str(e)}' in prompt template '{prompt_name}.md'")

        from app.core.version import PROMPT_VERSION
        return formatted_prompt, template_hash, PROMPT_VERSION
