from typing import Protocol, List, Dict, Any


class AwardAvailabilityAdapter(Protocol):
    def search_awards(self, query: Dict[str, Any]) -> List[Dict[str, Any]]: ...


class CashAirfareAdapter(Protocol):
    def search_cash_fares(self, query: Dict[str, Any]) -> List[Dict[str, Any]]: ...


class HotelPricingAdapter(Protocol):
    def search_hotels(self, query: Dict[str, Any]) -> List[Dict[str, Any]]: ...
