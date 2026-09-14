from datetime import date

from example_adapter import ExampleRegulatorAdapter

from policygraph.models import PolicyStatus, Source, SourceKind
from policygraph.testing import assert_adapter_contract


def test_contract() -> None:
    source = Source(
        "example",
        "Example",
        "Example",
        "https://example.invalid/policy",
        SourceKind.WEB_PAGE,
        (),
        PolicyStatus.PROPOSAL,
        date(2026, 1, 1),
        content_path="sample.html",
    )
    assert_adapter_contract(ExampleRegulatorAdapter(), source)
