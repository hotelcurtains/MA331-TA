"""
Author: Daniel Detore
Date: 2026-5-11
Description: Outputs a pivoted (more readable) attendence schedule and prints basic info. For use with output from Canvas's "Roll Call" section.
Version: 1.0
Contact: ddetore@stevens.edu
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

usage = \
f"""Usage: [python] {sys.argv[0]} <ATTENDANCE_REPORT.csv|-h>
    Get attendance report from Canvas -> any course -> Roll Call -> gear icon
    then enter a date range and your email -> 'Run Report' -> and download
    from your email. This program pivots the result to get attendance (0 or 1)
    by student per class date."""

if __name__ == "__main__":
    report = ""
    if len(sys.argv) == 2:
        if sys.argv[1] == "-h":
            print(usage)
            exit(0)
        else:
            report = sys.argv[1]
    else:
        print(usage)
        exit(1)
    
    
    df = pd.read_csv(report, usecols=[10,11,12], header=0)
    
    # only keep last record; in case of mistaken inputs you fixed later
    df.drop_duplicates(subset=["Student Name", "Class Date"], keep="last", inplace=True, ignore_index=True)
    
    # assume only either present or absent. rewrite as factors if you count other types (late, excused, etc)
    df["Attendance"] = np.where(df["Attendance"] == "present", 1, 0)

    # pivot to table of attendance of student vs day
    df = df.pivot(columns="Class Date", index="Student Name", values="Attendance")
    # nan = not entered = assume absent
    df = df.fillna(0)
    df = df.astype(int)
    # sort by last name, with first name as tiebreaker
    df = df.sort_index(
        key=lambda x: x.str.split().str[-1].str.lower() + " " +
        x.str.split().str[0].str.lower()
    )

    # add sum column at left
    df.insert(0, "total attendances", np.sum(df, axis=1))

    original_filename = os.path.basename(report)
    original_filename = original_filename[:original_filename.rfind(".csv")]
    new_filename = f"./PIVOTED_{original_filename}.csv"
    df.to_csv(new_filename)
    print(f"saved pivoted table to: {new_filename}")

    print("details...")
    print(f"          # of students: {df.shape[0]}")
    # subtract 1 since we added sum row
    print(f"           # of records: {df.shape[1]-1}")
    print(f"     average attendance: {np.average(df["total attendances"]):.3f}")
    print(f" worst/best per-student: [{np.min(df["total attendances"])}, {np.max(df["total attendances"])}]")
    daysums = np.sum(df.drop(columns="total attendances"), axis=0)
    print(f"  worst/best attendance: [{daysums.min()}, {daysums.max()}]")
    dayrank = np.argsort(daysums)
    print(f"worst/best overall days: [{dayrank.idxmin()}, {dayrank.idxmax()}]")
    




