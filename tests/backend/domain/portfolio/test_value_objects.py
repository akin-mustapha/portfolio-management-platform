import pytest

from v2.backend.domain.portfolio.value_objects import Ticker, Currency, Broker


class TestTicker:
    def test_valid_ticker_is_uppercased(self):
        t = Ticker("aapl")
        assert str(t) == "AAPL"

    def test_empty_ticker_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            Ticker("")

    def test_ticker_equality(self):
        assert Ticker("aapl") == Ticker("AAPL")

    def test_ticker_is_immutable(self):
        t = Ticker("AAPL")
        with pytest.raises((AttributeError, TypeError)):
            t.value = "MSFT"


class TestCurrency:
    def test_valid_currency_is_uppercased(self):
        c = Currency("gbp")
        assert str(c) == "GBP"

    def test_empty_currency_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            Currency("")

    def test_currency_wrong_length_raises(self):
        with pytest.raises(ValueError, match="3 characters"):
            Currency("GB")

    def test_four_char_currency_raises(self):
        with pytest.raises(ValueError, match="3 characters"):
            Currency("GBPP")

    def test_currency_equality(self):
        assert Currency("usd") == Currency("USD")


class TestBroker:
    def test_valid_broker_stores_value(self):
        b = Broker("Trading212")
        assert str(b) == "Trading212"

    def test_empty_broker_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            Broker("")

    def test_broker_equality(self):
        assert Broker("Trading212") == Broker("Trading212")

    def test_different_brokers_not_equal(self):
        assert Broker("Trading212") != Broker("IBKR")
