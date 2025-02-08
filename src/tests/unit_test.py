"""Unit tests for the Chad Python service."""


class ChadUnitTest:
    """Unit tests for the Chad Python service."""

    def __init__(self, token: str) -> None:
        self.token = token

    def run_unit_tests(self) -> None:
        """Run the unit tests."""
        match self.token:
            case "all":
                self._all_unit_tests()
            case "ui":
                self.ui_unit_tests()
            case "modules":
                self._modules_unit_tests()
            case "connections":
                self._connections_unit_tests()
            case "live_capture":
                self._live_capture_unit_tests()
            case "logger":
                self._logger_unit_tests()
            case _:
                raise ValueError(f"Invalid token: {self.token}")

    def _all_unit_tests(self) -> None:
        """Run all unit tests."""
        self.ui_unit_tests()
        self._modules_unit_tests()
        self._connections_unit_tests()
        self._live_capture_unit_tests()
        self._logger_unit_tests()

    def ui_unit_tests(self) -> None:
        pass

    def _modules_unit_tests(self) -> None:
        pass

    def _connections_unit_tests(self) -> None:
        pass

    def _live_capture_unit_tests(self) -> None:
        pass

    def _logger_unit_tests(self) -> None:
        """Run the logger unit tests."""
        from tests.test_logger import test_logger

        test_logger()
