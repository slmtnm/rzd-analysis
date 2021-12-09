from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any
from utils import date_str, str_date
from enum import Enum


class CarType(Enum):
    COUPE = 'Купе'
    PLAZKART = 'Плац'
    LUX = 'Люкс'
    SEAT = 'Сид'


@dataclass
class Car:
    tariff: int
    type: str
    type_loc: str
    free_seats: int

    def as_dict(self) -> dict[str, str | int]:
        return {
            'tariff': self.tariff,
            'type': self.type,
            'type_loc': self.type_loc,
            'free_seats': self.free_seats,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Car:
        return cls(
            tariff=int(d['tariff']),
            type=d['type'],
            type_loc=d['type_loc'],
            free_seats=int(d['free_seats']),
        )


@dataclass
class Train:
    from_code: int
    where_code: int

    start_date: date
    finish_date: date

    number: str
    cars: list[Car]

    def as_dict(self) -> dict[str, Any]:
        return {
            'from_code': self.from_code,
            'where_code': self.where_code,
            'start_date': date_str(self.start_date),
            'finish_date': date_str(self.finish_date),
            'number': self.number,
            'cars': [c.as_dict() for c in self.cars],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Train:
        return cls(
            from_code=int(d['from_code']),
            where_code=int(d['where_code']),
            start_date=str_date(d['start_date']),
            finish_date=str_date(d['finish_date']),
            number=d['number'],
            cars=[Car.from_dict(c) for c in d['cars']],
        )


@dataclass
class Route:
    from_code: int
    where_code: int
    trains: list[Train]
    date: date

    def as_dict(self) -> dict[str, Any]:
        return {
            'from_code': self.from_code,
            'where_code': self.where_code,
            'trains': [t.as_dict() for t in self.trains],
            'date': date_str(self.date),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Route:
        return cls(
            from_code=int(d['from_code']),
            where_code=int(d['where_code']),
            trains=[Train.from_dict(t) for t in d['trains']],
            date=str_date(d['date']),
        )
