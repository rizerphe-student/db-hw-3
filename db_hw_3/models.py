from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, VARCHAR
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Driver(Base):
    __tablename__ = "drivers"
    licenseID = Column(String, primary_key=True)
    name_firstName = Column(String, nullable=False)
    name_lastName = Column(String, nullable=False)


class BusCharacteristic(Base):
    __tablename__ = "bus_characteristics"
    model_id = Column(BigInteger, primary_key=True)
    size = Column(Integer, nullable=False)


class Bus(Base):
    __tablename__ = "buses"
    licensePlate = Column(VARCHAR(8), primary_key=True)
    characteristics_model_id = Column(
        BigInteger, ForeignKey("bus_characteristics.model_id"), nullable=False
    )
    working = Column(Boolean, nullable=False)


class Route(Base):
    __tablename__ = "routes"
    routeNo = Column(Integer, primary_key=True)


class Stop(Base):
    __tablename__ = "stops"
    stopID = Column(Integer, primary_key=True)
    stopName = Column(String, nullable=False)
    stopCoordinates = Column(String, nullable=False)


class Ride(Base):
    __tablename__ = "rides"
    rideID = Column(BigInteger, primary_key=True)
    licensePlate = Column(VARCHAR(8), ForeignKey("buses.licensePlate"), nullable=False)
    routeNo = Column(Integer, ForeignKey("routes.routeNo"), nullable=False)
    licenseID = Column(String, ForeignKey("drivers.licenseID"), nullable=False)
    startTime = Column(DateTime, nullable=False)


class TicketUse(Base):
    __tablename__ = "ticket_uses"
    useID = Column(Integer, primary_key=True)
    rideID = Column(BigInteger, nullable=False)
    w_ticketID = Column(Integer, nullable=True)
    o_ticketID = Column(Integer, nullable=True)
    ForeignKeyConstraint(["rideID"], ["rides.rideID"])
    ForeignKeyConstraint(["w_ticketID"], ["weeklytickets.ticketID"])
    ForeignKeyConstraint(["o_ticketID"], ["onetimetickets.ticketID"])


class OneTimeTicket(Base):
    __tablename__ = "onetimetickets"
    ticketID = Column(Integer, primary_key=True)
    issueDate = Column(TIMESTAMP, nullable=False)
    passengerID = Column(Integer, ForeignKey("passengers.passengerID"), nullable=False)


class WeeklyTicket(Base):
    __tablename__ = "weeklytickets"
    ticketID = Column(Integer, primary_key=True)
    issueDate = Column(TIMESTAMP, nullable=False)
    passengerID = Column(Integer, ForeignKey("passengers.passengerID"), nullable=False)


class Passenger(Base):
    __tablename__ = "passengers"
    passengerID = Column(Integer, primary_key=True)
    name_firstName = Column(String, nullable=False)
    name_lastName = Column(String, nullable=False)


class StopEnRoute(Base):
    __tablename__ = "stops_en_route"
    stopID = Column(Integer, ForeignKey("stops.stopID"), primary_key=True)
    routeID = Column(BigInteger, ForeignKey("routes.routeNo"), primary_key=True)
    stopOrder = Column(Integer, nullable=False)
