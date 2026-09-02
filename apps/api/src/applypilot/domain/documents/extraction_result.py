from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceSegment:
    citation: str
    text: str


@dataclass(frozen=True)
class ExtractionResult:
    text: str
    segments: tuple[EvidenceSegment, ...]
    page_count: int | None = None
    paragraph_count: int | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
