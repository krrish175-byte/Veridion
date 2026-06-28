"""Base error hierarchy for the Veridion platform."""


class VeridionError(Exception):
    """Root exception for all Veridion domain errors.

    Domain-specific subclasses (e.g. ``EvidenceProviderError``,
    ``VerificationError``, ``ReasoningEngineError``) will be added in the
    tasks that introduce their respective modules — they are **not** created
    here.
    """
