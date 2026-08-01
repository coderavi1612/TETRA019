from typing import Dict, List
from app.verification.schemas.issue import Evidence
from app.verification.schemas.comparison import NormalizedValue

class EvidenceBuilder:
    @staticmethod
    def build_evidence(canonical_field: str, docs: Dict[str, NormalizedValue]) -> List[Evidence]:
        evidence_list = []
        for doc_type, val in docs.items():
            if val.value is not None:
                evidence_list.append(Evidence(
                    document=doc_type,
                    value=val.value,
                    canonical_path=val.canonical_path,
                    source_block_id=val.source_block_id,
                    page=val.page,
                    slide=val.slide,
                    sheet=val.sheet,
                    snippet=val.extracted_text_snippet
                ))
        return evidence_list
