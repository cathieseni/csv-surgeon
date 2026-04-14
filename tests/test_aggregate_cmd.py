"""Integration tests for the aggregate sub-command."""
import csv
import io
from pathlib import Path

import pytest

from csv_surgeon.commands.aggregate_cmd import run


CSV_CONTENT = """name,score,dept
Alice,90,eng
Bob,70,eng
Carol,80,hr
Dave,70,hr
"""


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT)
    return p


class _Args:
    """Minimal namespace mimic."""
    def __init__(self, file, aggs, output=None):
        self.file = file
        self.aggs = aggs
        self.output = output


def test_run_stdout(csv_file, capsys):
    args = _Args(csv_file, ["score:sum", "name:count"])
    rc = run(args)
    assert rc == 0
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = {r["metric"]: r["value"] for r in reader}
    assert rows["score__sum"] == "310.0"
    assert rows["name__count"] == "4"


def test_run_output_file(csv_file, tmp_path):
    out = tmp_path / "out.csv"
    args = _Args(csv_file, ["score:mean"], output=out)
    rc = run(args)
    assert rc == 0
    assert out.exists()
    reader = csv.DictReader(out.open())
    rows = {r["metric"]: r["value"] for r in reader}
    assert rows["score__mean"] == "77.5"


def test_run_missing_file(tmp_path):
    args = _Args(tmp_path / "nope.csv", ["score:sum"])
    rc = run(args)
    assert rc == 1


def test_run_invalid_spec(csv_file):
    args = _Args(csv_file, ["score_sum"])  # missing colon
    rc = run(args)
    assert rc == 1


def test_run_unknown_aggregator(csv_file):
    args = _Args(csv_file, ["score:median"])
    rc = run(args)
    assert rc == 1
