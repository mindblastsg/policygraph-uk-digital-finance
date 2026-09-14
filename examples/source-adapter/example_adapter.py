from pathlib import Path

from policygraph.adapters import LocalFixtureAdapter


class ExampleRegulatorAdapter(LocalFixtureAdapter):
    name = "example_regulator"
    supported_hosts = ("example.invalid",)

    def __init__(self) -> None:
        super().__init__(Path(__file__).parent / "fixtures")
