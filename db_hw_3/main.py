from dataclasses import dataclass
from datetime import datetime

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_hw_3.populate import random_int

from .models import OneTimeTicket, Passenger, Ride, Route, TicketUse, WeeklyTicket

app = FastAPI()

engine = create_engine("sqlite:///db.sqlite")
Session = sessionmaker(bind=engine)
session = Session()


@dataclass
class RideData:
    licensePlate: str
    routeNo: int
    startTime: datetime

    @staticmethod
    def from_orm(ride: Ride) -> "RideData":
        return RideData(
            licensePlate=ride.licensePlate,
            routeNo=ride.routeNo,
            startTime=ride.startTime,
        )


@app.get("/rides_after_date")
def rides_after_date(date: datetime) -> list[RideData]:
    rides = session.query(Ride).filter(Ride.startTime > date).all()
    return [RideData.from_orm(ride) for ride in rides]


@dataclass
class ScheduleBusData:
    licensePlate: str
    routeNo: int
    licenseID: str
    startTime: datetime


@app.post("/schedule_bus")
def schedule_bus(data: ScheduleBusData):
    session.add(Ride(**data.__dict__))
    session.commit()


@dataclass
class BuyWeeklyTicketData:
    issueDate: datetime
    passengerID: int


@app.post("/buy_weekly_ticket")
def buy_weekly_ticket(data: BuyWeeklyTicketData) -> int:
    ticket_id = random_int()
    session.add(WeeklyTicket(**data.__dict__, ticketID=ticket_id))
    session.commit()
    return ticket_id


@dataclass
class BuyOneTimeTicketData:
    issueDate: datetime
    passengerID: int


@app.post("/buy_one_time_ticket")
def buy_one_time_ticket(data: BuyOneTimeTicketData) -> int:
    ticket_id = random_int()
    session.add(OneTimeTicket(**data.__dict__, ticketID=ticket_id))
    session.commit()
    return ticket_id


@dataclass
class ChangePassengerNameData:
    passengerID: int
    name_firstName: str
    name_lastName: str


@app.post("/change_passenger_name")
def change_passenger_name(data: ChangePassengerNameData):
    passenger = (
        session.query(Passenger)
        .filter(Passenger.passengerID == data.passengerID)
        .first()
    )
    passenger.name_firstName = data.name_firstName
    passenger.name_lastName = data.name_lastName
    session.commit()


@dataclass
class UsageData:
    routeNo: int
    tickets_sold: int


@app.get("/tickets_used")
def tickets_used() -> list[UsageData]:
    return [
        UsageData(
            routeNo=route.routeNo,
            tickets_sold=session.query(Ride)
            .filter(Ride.routeNo == route.routeNo)
            .count(),
        )
        for route in session.query(Route).all()
    ]


@dataclass
class DriverScheduleData:
    startTime: datetime
    routeNo: int


@app.get("/driver_schedule")
def driver_schedule(licenseID: str, date: datetime) -> list[DriverScheduleData]:
    return [
        DriverScheduleData(startTime=ride.startTime, routeNo=ride.routeNo)
        for ride in session.query(Ride)
        .filter(Ride.licenseID == licenseID, Ride.startTime > date)
        .all()
    ]


@dataclass
class TicketData:
    ticketID: int
    issueDate: datetime


@dataclass
class PassengerTicketsData:
    one_time: list[TicketData]
    weekly: list[TicketData]


@app.get("/passenger_tickets")
def passenger_tickets(passenger_id: int) -> PassengerTicketsData:
    return PassengerTicketsData(
        one_time=[
            TicketData(ticketID=ticket.ticketID, issueDate=ticket.issueDate)
            for ticket in session.query(OneTimeTicket)
            .filter(OneTimeTicket.passengerID == passenger_id)
            .all()
        ],
        weekly=[
            TicketData(ticketID=ticket.ticketID, issueDate=ticket.issueDate)
            for ticket in session.query(WeeklyTicket)
            .filter(WeeklyTicket.passengerID == passenger_id)
            .all()
        ],
    )


@dataclass
class ValidateWeeklyTicketData:
    ticketID: int
    rideID: int


@app.post("/validate_weekly_ticket")
def validate_weekly_ticket(data: ValidateWeeklyTicketData):
    ticket = (
        session.query(WeeklyTicket)
        .filter(WeeklyTicket.ticketID == data.ticketID)
        .first()
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.issueDate > datetime.now():
        raise HTTPException(status_code=400, detail="Ticket not valid")
    session.add(TicketUse(w_ticketID=data.ticketID, rideID=data.rideID))
    session.commit()


@dataclass
class ValidateOneTimeTicketData:
    ticketID: int
    rideID: int


@app.post("/validate_one_time_ticket")
def validate_one_time_ticket(data: ValidateOneTimeTicketData):
    ticket = (
        session.query(OneTimeTicket)
        .filter(OneTimeTicket.ticketID == data.ticketID)
        .first()
    )
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if (
        session.query(TicketUse).filter(TicketUse.o_ticketID == data.ticketID).first()
        is not None
    ):
        raise HTTPException(status_code=400, detail="Ticket already used")
    session.add(TicketUse(o_ticketID=data.ticketID, rideID=data.rideID))
    session.commit()
