from datetime import datetime, timedelta


def get_date(datestring: str = "") -> datetime:
    return datetime.strptime(datestring, "%Y-%m-%d") if datestring else datetime.today()


def delta_week(date: datetime, delta: int = 0) -> datetime:
    return date + timedelta(weeks=delta)


def get_year(datestring: str = "") -> int:
    return delta_week(get_date(datestring), -33).strftime("%Y")
