from datetime import date

from src.intelligence.deduplication import deduplicate
from src.intelligence.scoring import score_signal
from src.models.project_signal import ProjectSignal
from src.pipelines.normalize import normalize_fort_worth, parse_arcgis_date, parse_number


WEIGHTS = {"dfw_geography":25,"residential_fit":25,"recent_or_upcoming":15,"attractive_value_or_size":10,"builder_identified":10,"plumbing_likelihood":10,"researchable":5,"small_remodel_penalty":-15,"inactive_penalty":-25}


def test_dates_and_money():
    assert parse_arcgis_date(1735689600000) == date(2025, 1, 1)
    assert parse_number("$1,250,000.50") == 1250000.50
    assert parse_number(None) is None


def test_normalize_incomplete_record():
    signal = normalize_fort_worth({"ObjectId": 7}, "https://example.test/0")
    assert signal.source_project_id == "7"
    assert signal.estimated_value is None
    assert signal.raw_payload == {"ObjectId": 7}


def test_scoring_is_bounded_and_explained():
    signal = ProjectSignal(source="x", source_project_id="1", project_name="New single family residence", address="1 Main", owner_developer="Builder", builder="Builder", start_date=date.today(), estimated_value=500000)
    scored = score_signal(signal, WEIGHTS)
    assert 80 <= scored.opportunity_score <= 100
    assert "fit residencial" in scored.reason_for_score


def test_deduplication_uses_source_identity():
    a = ProjectSignal(source="x", source_project_id="1", project_name="A")
    b = ProjectSignal(source="x", source_project_id="1", project_name="B")
    assert len(deduplicate([a, b])) == 1

