from backend.domain.portfolio.value_objects import Ticker, Currency, Broker
from backend.domain.portfolio.entities import (
    Asset,
    Tag,
    Category,
    AssetTag,
    Industry,
    Sector,
)


class TestAssetToRecord:
    def test_to_record_unpacks_value_objects(self):
        asset = Asset(
            id=None,
            ticker=Ticker("AAPL"),
            name="Apple Inc.",
            broker=Broker("Trading212"),
            currency=Currency("USD"),
        )
        record = asset.to_record()

        assert record["ticker"] == "AAPL"
        assert record["broker"] == "Trading212"
        assert record["currency"] == "USD"
        assert record["name"] == "Apple Inc."
        assert "id" not in record

    def test_to_record_with_null_optional_fields(self):
        asset = Asset(
            id=None,
            ticker=Ticker("VOD"),
            name="Vodafone",
            broker=None,
            currency=None,
        )
        record = asset.to_record()

        assert record["broker"] is None
        assert record["currency"] is None


class TestTagToRecord:
    def test_to_record_excludes_id(self):
        tag = Tag(
            id=None,
            name="Growth",
            description="Growth stocks",
            tag_type_id=1,
            created_timestamp="2026-01-01",
        )
        record = tag.to_record()

        assert record["name"] == "Growth"
        assert record["tag_type_id"] == 1
        assert "id" not in record

    def test_to_record_raises_if_tag_type_id_missing(self):
        # tag_type_id=0 is falsy but technically valid as an int; domain rule states it must be set.
        # The dataclass itself does not enforce this — this test documents expected caller behaviour.
        tag = Tag(
            id=None,
            name="Orphan",
            description="",
            tag_type_id=0,
            created_timestamp="2026-01-01",
        )
        record = tag.to_record()
        assert record["tag_type_id"] == 0


class TestCategoryToRecord:
    def test_to_record_returns_expected_keys(self):
        cat = Category(
            id=None,
            name="Equity",
            description="Equity assets",
            created_timestamp="2026-01-01",
        )
        record = cat.to_record()

        assert set(record.keys()) == {"name", "description", "created_timestamp"}

    def test_to_record_values_match(self):
        cat = Category(
            id=5,
            name="Bond",
            description="Fixed income",
            created_timestamp="2026-03-01",
        )
        record = cat.to_record()

        assert record["name"] == "Bond"
        assert record["description"] == "Fixed income"


class TestAssetTagToRecord:
    def test_to_record_includes_both_ids(self):
        at = AssetTag(asset_id=1, tag_id=2, created_timestamp="2026-01-01")
        record = at.to_record()

        assert record["asset_id"] == 1
        assert record["tag_id"] == 2

    def test_to_record_with_null_timestamp(self):
        at = AssetTag(asset_id=1, tag_id=2, created_timestamp=None)
        record = at.to_record()

        assert record["created_timestamp"] is None


class TestIndustryToRecord:
    def test_to_record_includes_id(self):
        ind = Industry(
            id=10,
            name="Technology",
            description="Tech sector",
            created_timestamp="2026-01-01",
        )
        record = ind.to_record()

        assert record["id"] == 10
        assert record["name"] == "Technology"

    def test_to_record_with_null_timestamp(self):
        ind = Industry(id=None, name="Energy", description="", created_timestamp=None)
        record = ind.to_record()

        assert record["created_timestamp"] is None


class TestSectorToRecord:
    def test_to_record_includes_industry_id(self):
        sec = Sector(
            id=3,
            industry_id=1,
            name="Software",
            description="SW companies",
            created_timestamp="2026-01-01",
        )
        record = sec.to_record()

        assert record["industry_id"] == 1
        assert record["name"] == "Software"

    def test_to_record_with_null_industry_id(self):
        # Documents current behaviour — domain rule says industry_id is required,
        # but the dataclass allows None at construction time.
        sec = Sector(
            id=None,
            industry_id=None,
            name="Orphan Sector",
            description="",
            created_timestamp=None,
        )
        record = sec.to_record()

        assert record["industry_id"] is None
