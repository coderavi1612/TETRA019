import os
import json
from typing import Dict, List, Any
from app.verification.schemas.verification import VerificationManifest

class ManifestBuilder:
    @staticmethod
    def save_manifest(manifest: VerificationManifest, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        manifest_path = os.path.join(output_dir, "verification_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.model_dump(), f, indent=2, default=str)
