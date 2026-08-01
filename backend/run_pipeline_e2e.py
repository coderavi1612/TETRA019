import os
import sys
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.pipeline.orchestrator import DuelensPipeline, PipelineStage
from app.config import settings
from app.core.logging import setup_logging

def main():
    setup_logging()
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline_e2e.py <company_id>")
        sys.exit(1)
        
    company_id = sys.argv[1].strip()
    
    print(f"Triggering E2E pipeline run for company: {company_id}...")
    start_time = time.time()
    
    try:
        # Run parsing, extraction, verification and readiness stages synchronously
        results = DuelensPipeline.run(company_id=company_id, stage=PipelineStage.FULL)
        elapsed = time.time() - start_time
        
        print("\n=== PIPELINE RUN RESULTS ===")
        print(f"Status: COMPLETED successfully in {elapsed:.2f} seconds!")
        
        # Check generated output files
        extracted_dir = os.path.join(settings.OUTPUT_DIR, company_id, "extracted")
        if os.path.exists(extracted_dir):
            print("\nGenerated Extraction Files:")
            for filename in sorted(os.listdir(extracted_dir)):
                file_path = os.path.join(extracted_dir, filename)
                size_kb = os.path.getsize(file_path) / 1024
                print(f" - {filename} ({size_kb:.2f} KB)")
        else:
            print("\nWARNING: Extracted output directory not found!")
            
        manifests_dir = os.path.join(settings.OUTPUT_DIR, company_id, "manifests")
        manifest_path = os.path.join(manifests_dir, "artifacts_manifest.json")
        if os.path.exists(manifest_path):
            print(f"\nArtifact Manifest generated at: {manifest_path}")
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                print(f"Artifacts registered in manifest: {len(manifest_data.get('artifacts', []))}")
        else:
            print(f"\nWARNING: Artifact manifest not found!")
            
    except Exception as e:
        print(f"\nERROR: Pipeline execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
