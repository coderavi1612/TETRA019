import os
import json
import logging
from app.config import settings

def validate_startup_state() -> None:
    from app.core import DuelensLogger
    DuelensLogger.log("Startup", "START", "Starting comprehensive fail-fast validations...")

    # 1. Output directory permissions
    try:
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        # Test write permission
        test_file = os.path.join(settings.OUTPUT_DIR, ".startup_write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        DuelensLogger.log("Startup", "SUCCESS", "Output directory is writable.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Output directory {settings.OUTPUT_DIR} is not writable: {str(e)}", error=e)
        raise RuntimeError(f"Output directory not writable: {str(e)}")

    # 2. Schema / Specification Registry Validation
    try:
        from app.extractors.specification_registry import SpecificationRegistry
        SpecificationRegistry.load()
        DuelensLogger.log("Startup", "SUCCESS", "Specification registry loaded successfully.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Failed to load specification registry: {str(e)}", error=e)
        raise RuntimeError(f"Specification registry load failure: {str(e)}")

    # 3. JSON templates
    try:
        from app.extractors.template_loader import TemplateLoader
        TemplateLoader.load_all_templates()
        DuelensLogger.log("Startup", "SUCCESS", "Document JSON templates loaded successfully.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Failed to load JSON templates: {str(e)}", error=e)
        raise RuntimeError(f"JSON templates load failure: {str(e)}")

    # 4. Comparison Rules & Registry
    try:
        from app.verification import ComparisonRegistry
        ComparisonRegistry.load()
        DuelensLogger.log("Startup", "SUCCESS", "Comparison registry and rules loaded successfully.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Failed to load comparison registry/rules: {str(e)}", error=e)
        raise RuntimeError(f"Comparison rules validation failed: {str(e)}")

    # 5. Prompt templates
    try:
        from app.readiness.prompt_builder import PromptBuilder
        prompt_dir = PromptBuilder.get_prompt_dir()
        required_prompts = ["impact.md", "questions.md", "executive.md", "narrative.md"]
        for prompt in required_prompts:
            path = os.path.join(prompt_dir, prompt)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing required prompt template: {prompt}")
        DuelensLogger.log("Startup", "SUCCESS", "Readiness prompt templates verified.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Readiness prompt templates missing or invalid: {str(e)}", error=e)
        raise RuntimeError(f"Prompt templates validation failed: {str(e)}")

    # 6. Markdown templates
    try:
        import app.readiness.markdown as md_module
        md_dir = os.path.dirname(md_module.__file__)
        template_dir = os.path.join(md_dir, "templates")
        required_md_templates = ["header.md", "footer.md", "executive.md", "summary.md", "questions.md", "report.md"]
        for tmpl in required_md_templates:
            path = os.path.join(template_dir, tmpl)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing required Markdown template: {tmpl}")
        DuelensLogger.log("Startup", "SUCCESS", "Markdown report templates verified.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"Markdown templates missing or invalid: {str(e)}", error=e)
        raise RuntimeError(f"Markdown templates validation failed: {str(e)}")

    # 7. PDF / ReportLab templates
    try:
        from app.readiness.pdf import PdfReportAssembler
        DuelensLogger.log("Startup", "SUCCESS", "ReportLab PDF engine initialized.")
    except Exception as e:
        DuelensLogger.log("Startup", "ERROR", f"ReportLab initialization failed: {str(e)}", error=e)
        raise RuntimeError(f"PDF engine validation failed: {str(e)}")

    # 8. Gemini API configuration
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        DuelensLogger.log("Startup", "WARNING", "Gemini API key is not configured. The engine will run in MOCK fallback mode.")
    else:
        DuelensLogger.log("Startup", "SUCCESS", "Gemini API configuration verified.")

    DuelensLogger.log("Startup", "SUCCESS", "All fail-fast startup validations passed successfully!")
