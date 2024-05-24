from dataclasses import dataclass
from datetime import datetime
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    Bus,
    BusCharacteristic,
    Driver,
    OneTimeTicket,
    Passenger,
    Ride,
    Route,
    Stop,
    StopEnRoute,
    TicketUse,
    WeeklyTicket,
)

engine = create_engine("sqlite:///db.sqlite")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def random_name() -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10)).capitalize()


def random_date() -> datetime:
    return datetime.now()


def random_bool() -> bool:
    return random.choice([True, False])


def random_int() -> int:
    return random.randint(0, 10000000)


def random_string() -> str:
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))


def random_coordinates() -> str:
    return f"{random_int()},{random_int()}"


def random_license_plate() -> str:
    return (
        "".join(random.choices("AB", k=2))
        + "".join(random.choices("0123456789", k=4))
        + "".join(random.choices("AB", k=2))
    )


def random_route_no() -> int:
    return random.randint(0, 10000000)


def random_model_id() -> int:
    return random.randint(0, 10000000)


def random_passenger_id() -> int:
    return random.randint(0, 10000000)


def random_stop_order() -> int:
    return random.randint(0, 10000000)


@dataclass
class DriverData:
    licenseID: int
    name_firstName: str
    name_lastName: str

    @staticmethod
    def random() -> "DriverData":
        return DriverData(
            licenseID=random_int(),
            name_firstName=random_name(),
            name_lastName=random_name(),
        )


@dataclass
class BusData:
    licensePlate: str
    characteristics_model_id: int
    working: bool

    @staticmethod
    def random(characteristics_model_id: int) -> "BusData":
        return BusData(
            licensePlate=random_license_plate(),
            characteristics_model_id=characteristics_model_id,
            working=random_bool(),
        )


@dataclass
class RouteData:
    routeNo: int

    @staticmethod
    def random() -> "RouteData":
        return RouteData(routeNo=random_route_no())


@dataclass
class StopData:
    stopID: int
    stopName: str
    stopCoordinates: str

    @staticmethod
    def random() -> "StopData":
        return StopData(
            stopID=random_int(),
            stopName=random_name(),
            stopCoordinates=random_coordinates(),
        )


@dataclass
class RideData:
    rideID: int
    licensePlate: str
    routeNo: int
    licenseID: int
    startTime: datetime

    @staticmethod
    def random(licensePlate: str, routeNo: int, licenseID: int) -> "RideData":
        return RideData(
            rideID=random_int(),
            licensePlate=licensePlate,
            routeNo=routeNo,
            licenseID=licenseID,
            startTime=random_date(),
        )


@dataclass
class TicketUseData:
    useID: int
    rideID: int
    w_ticketID: int | None
    o_ticketID: int | None

    @staticmethod
    def random(w_ticketID: int | None, o_ticketID: int | None) -> "TicketUseData":
        # Only one of the two can be set
        o_ticketID = o_ticketID if w_ticketID is None else None

        return TicketUseData(
            useID=random_int(),
            rideID=random_int(),
            w_ticketID=w_ticketID,
            o_ticketID=o_ticketID,
        )


@dataclass
class OneTimeTicketData:
    ticketID: int
    issueDate: datetime
    passengerID: int

    @staticmethod
    def random(passengerID: int) -> "OneTimeTicketData":
        return OneTimeTicketData(
            ticketID=random_int(), issueDate=random_date(), passengerID=passengerID
        )


@dataclass
class WeeklyTicketData:
    ticketID: int
    issueDate: datetime
    passengerID: int

    @staticmethod
    def random(passengerID: int) -> "WeeklyTicketData":
        return WeeklyTicketData(
            ticketID=random_int(), issueDate=random_date(), passengerID=passengerID
        )


@dataclass
class PassengerData:
    passengerID: int
    name_firstName: str
    name_lastName: str

    @staticmethod
    def random() -> "PassengerData":
        return PassengerData(
            passengerID=random_passenger_id(),
            name_firstName=random_name(),
            name_lastName=random_name(),
        )


@dataclass
class BusCharacteristicsData:
    model_id: int
    size: int

    @staticmethod
    def random() -> "BusCharacteristicsData":
        return BusCharacteristicsData(model_id=random_model_id(), size=random_int())


@dataclass
class StopEnRouteData:
    stopID: int
    routeID: int
    stopOrder: int

    @staticmethod
    def random(stopID: int, routeID: int) -> "StopEnRouteData":
        return StopEnRouteData(
            stopID=stopID, routeID=routeID, stopOrder=random_stop_order()
        )


def populate():
    drivers = [Driver(**DriverData.random().__dict__) for _ in range(10)]
    bus_characteristics = [
        BusCharacteristic(**BusCharacteristicsData.random().__dict__) for _ in range(10)
    ]
    buses = [
        Bus(**BusData.random(random.choice(bus_characteristics).model_id).__dict__)
        for _ in range(10)
    ]
    routes = [Route(**RouteData.random().__dict__) for _ in range(10)]
    stops = [Stop(**StopData.random().__dict__) for _ in range(10)]
    rides = [
        Ride(
            **RideData.random(
                random.choice(buses).licensePlate,
                random.choice(routes).routeNo,
                random.choice(drivers).licenseID,
            ).__dict__
        )
        for _ in range(10)
    ]
    passengers = [Passenger(**PassengerData.random().__dict__) for _ in range(10)]
    stops_en_route = [
        StopEnRoute(
            **StopEnRouteData.random(
                random.choice(stops).stopID, random.choice(routes).routeNo
            ).__dict__
        )
    ]
    one_time_tickets = [
        OneTimeTicket(
            **OneTimeTicketData.random(random.choice(passengers).passengerID).__dict__
        )
        for _ in range(10)
    ]
    weekly_tickets = [
        WeeklyTicket(
            **WeeklyTicketData.random(random.choice(passengers).passengerID).__dict__
        )
        for _ in range(10)
    ]
    ticket_uses = [
        TicketUse(
            **TicketUseData.random(
                random.choice(one_time_tickets).ticketID,
                random.choice(weekly_tickets).ticketID,
            ).__dict__
        )
        for _ in range(10)
    ]

    session.add_all(drivers)
    session.add_all(bus_characteristics)
    session.add_all(buses)
    session.add_all(routes)
    session.add_all(stops)
    session.add_all(rides)
    session.add_all(passengers)
    session.add_all(stops_en_route)
    session.add_all(one_time_tickets)
    session.add_all(weekly_tickets)
    session.add_all(ticket_uses)

    session.commit()


if __name__ == "__main__":
    random.seed(0)
    populate()
