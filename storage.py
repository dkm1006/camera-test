from typing import Literal
from dataclasses import dataclass, asdict
from datetime import datetime

import pandas as pd

import sample


@dataclass
class ParkingData:
    currently_parked: int
    total_parked: int
    total_turned_back: int
    hourly_parked: list[tuple[int]]
    hourly_left: list[tuple[int]]
    hourly_turned_back: list[tuple[int]]

    def to_dict(self):
        return asdict(self)


@dataclass
class Crossing:
    crossed_at: datetime
    # in and out are crossing the gate, 
    # turnback means someone was outside and never went in, 
    # recorded at the time of disappearance
    direction: Literal['in', 'out', 'turnback']
    category: Literal['car', 'person']


def load_parking_data(db) -> ParkingData:
    """Obtains data from the database"""
    df = sample.df
    hourly_data = df.groupby([df['crossed_at'].dt.hour, 'direction']).size().unstack(fill_value=0)
    totals = hourly_data.sum().to_dict()
    hourly_data = hourly_data
    return ParkingData(
        currently_parked=totals['in']-totals['out'],
        total_parked=totals['in'],
        total_turned_back=totals['turnback'],
        hourly_parked=hourly_data['in'].to_dict(),
        hourly_left=hourly_data['out'].to_dict(),
        hourly_turned_back=hourly_data['turnback'].to_dict(),
    )

def load_parking_data_raw():
    df = sample.df
    hourly_data = df.groupby([df['crossed_at'].dt.hour, 'direction']).size().unstack(fill_value=0)
    totals = hourly_data.sum()
    return hourly_data, totals

def store_crossing(crossing: Crossing):
    """Stores data about a crossing in the database"""
    pass