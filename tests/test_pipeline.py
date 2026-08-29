from datetime import date

from src.dashboard import MEETING_TARGETS, _review_id
from src.intelligence.deduplication import deduplicate
from src.intelligence.scoring import score_signal
from src.models.project_signal import ProjectSignal
from src.pipelines.normalize import normalize_fort_worth, normalize_frisco, parse_arcgis_date, parse_number
from src.storage.duckdb import radar_summary, save_signals, source_coverage


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


def test_normalize_constructs_address_and_rejects_non_company_label():
    raw = {"Permit_No":"PB-1", "Addr_No":14916, "Street_Name":"REYES", "Street_Suffix":"RD", "B1_SPECIAL_TEXT":"Fire Rebuild"}
    signal = normalize_fort_worth(raw, "https://example.test/0")
    assert signal.address == "14916 REYES RD"
    assert signal.builder == ""


def test_normalize_recognizes_builder_candidate():
    signal = normalize_fort_worth({"Permit_No":"PB-2", "B1_SPECIAL_TEXT":"M/I HOMES OF DFW LLC"}, "https://example.test/0")
    assert signal.builder == "M/I HOMES OF DFW LLC"


def test_generic_metro_code_is_not_used_as_project_or_builder():
    raw = {"Permit_No":"PB-3", "Addr_No":10, "Street_Name":"MAIN", "Street_Suffix":"ST", "Permit_SubType":"New", "Use_Type":"Single Family Residence", "B1_SPECIAL_TEXT":"METRO CODE"}
    signal = normalize_fort_worth(raw, "https://example.test/0")
    assert signal.project_name == "New / Single Family Residence — 10 MAIN ST"
    assert signal.builder == ""


def test_normalize_frisco_multifamily_and_square_feet():
    raw = {"Permit_No":"B25-1", "Permit_Subtype":"MNEW", "Type":"Multi-Family Residential", "Address":"5001 TEST DR", "Description":"554473 SF, FIELD NORTH", "Status":"ISSUED", "Issued_Date":"06/10/2026", "Project_Name":"Fields North", "Hyperlink":"https://example.test/permit"}
    signal = normalize_frisco(raw, "https://example.test/layer")
    assert signal.city == "Frisco"
    assert signal.project_type == "Multi-Family Residential / New"
    assert signal.square_feet == 554473
    assert signal.start_date == date(2026, 6, 10)


def test_scoring_is_bounded_and_explained():
    signal = ProjectSignal(source="x", source_project_id="1", project_name="New single family residence", address="1 Main", owner_developer="Builder", builder="Builder", start_date=date.today(), estimated_value=500000)
    scored = score_signal(signal, WEIGHTS)
    assert 80 <= scored.opportunity_score <= 100
    assert "construcción residencial nueva" in scored.reason_for_score


def test_remodel_scores_below_new_construction():
    new = ProjectSignal(source="x", source_project_id="1", project_name="House", project_type="Residential Building Permit / New / Single Family Residence", start_date=date.today())
    remodel = ProjectSignal(source="x", source_project_id="2", project_name="House remodel", project_type="Residential Building Permit / Remodel / Single Family Residence", start_date=date.today())
    assert score_signal(new, WEIGHTS).opportunity_score > score_signal(remodel, WEIGHTS).opportunity_score


def test_deduplication_uses_source_identity():
    a = ProjectSignal(source="x", source_project_id="1", project_name="A")
    b = ProjectSignal(source="x", source_project_id="1", project_name="B")
    assert len(deduplicate([a, b])) == 1


def test_presentation_metrics_report_observed_data_without_annualizing(tmp_path):
    path = tmp_path / "radar.duckdb"
    save_signals(path, [
        ProjectSignal(source="fort_worth", source_project_id="1", project_name="House", project_type="Residential Building Permit / New / Single Family Residence", start_date=date(2026, 8, 1)),
        ProjectSignal(source="frisco", source_project_id="2", project_name="Store", project_type="Commercial / New", start_date=date(2026, 8, 2)),
    ])

    assert radar_summary(path) == (2, 2, 1)
    assert source_coverage(path) == [
        ("fort_worth", 1, date(2026, 8, 1), date(2026, 8, 1)),
        ("frisco", 1, date(2026, 8, 2), date(2026, 8, 2)),
    ]


def test_meeting_references_keep_contractual_relationship_clear():
    targets = {target["name"]: target for target in MEETING_TARGETS}
    assert targets["Same Day Water Heaters"]["kind"] == "Contratista / cliente contractual"
    assert targets["The Home Depot · Home Services"]["kind"] == "Canal final / no cliente directo"
    assert targets["Frisco West WCID of Denton County"]["kind"] == "Entidad pública / inteligencia"


def test_review_ids_are_stable_and_do_not_expose_source_text():
    first = _review_id("meeting", "https://example.test/project")
    assert first == _review_id("meeting", "https://example.test/project")
    assert first != _review_id("meeting", "https://example.test/other")
    assert "example" not in first
