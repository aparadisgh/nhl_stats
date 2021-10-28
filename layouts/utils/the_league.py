# -*- coding: utf-8 -*-
"""Function libray to retreive important Fantasy Hockey dates

This module ...
"""
import datetime

def get_next_monday():
    today = datetime.datetime.today()
    day_of_the_week = today.weekday()
    days_to_monday = 7-day_of_the_week

    if day_of_the_week == 0:
        start_date = today.strftime('%Y-%m-%d')
    else:
        start_date = today + datetime.timedelta(days=days_to_monday)

    return start_date
