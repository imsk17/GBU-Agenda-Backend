import logging
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import exc
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.database import get_db
from api.utility import prettify_timetable

timetable = APIRouter()

LOGGER = logging.getLogger(__name__)


@timetable.get("/ping")
async def ping():
    return JSONResponse({"message": "pong"}, status_code=200)


@timetable.get("/schools")
def schools(db: Session = Depends(get_db)):
    try:
        data = db.execute("SELECT Name as name, FullName as full_name, id as id FROM School")
        return [dict(d) for d in data]
    except exc.SQLAlchemyError as err:
        LOGGER.error("INFO:     Database Error Occurred.")
        return JSONResponse({"error": err}, status_code=500)


@timetable.get("/sections")
async def sections(school: str, db: Session = Depends(get_db)):
    try:
        data = db.execute(f"""
        SELECT Section.Id as section_id, Section.Name as section_name,
        Section.Semester as semester, Program.id as program_id,
        Program.Code as program_code, Program.Name as program_name,
        Program.school, Program.IsActive as is_active 
        FROM Section 
        INNER JOIN Program on Section.Program=Program.id WHERE school is '{school}'
        """)
        return [dict(d) for d in data]
    except exc.SQLAlchemyError as err:
        LOGGER.error("INFO:     Database Error Occurred.")
        return JSONResponse({"error": err}, status_code=500)


@timetable.get("/teachers")
async def teachers(teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        data = db.execute(f"""
        SELECT id,abbr, school, name,isActive as is_active, department FROM Teacher WHERE id is '{teacher_id}'
        """)
        return [dict(d) for d in data][0]
    except exc.SQLAlchemyError as err:
        LOGGER.error("INFO:     Database Error Occurred.")
        return JSONResponse({"error": err}, status_code=500)


@timetable.get("/subjects")
async def subject(subject: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        data = db.execute(f"""
        SELECT Subject.id as sub_id , Subject.name as sub_name, Subject.code as sub_code,
        Subject.IsLab as is_lab, Subject.L, Subject.T, Subject.P, M_Department.Code
        as dept_code, M_Department.name as dept_name, M_Department.SchoolCode as school
        FROM Subject INNER JOIN M_Department on M_Department.Id = Subject.dept WHERE Subject.code is '{subject}'
        """)
        return [dict(d) for d in data][0]
    except exc.SQLAlchemyError as err:
        LOGGER.error("INFO:     Database Error Occurred.")
        return JSONResponse({"error": err}, status_code=500)


@timetable.get("/timetable")
async def teachers(section: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        data = db.execute(f"""
        SELECT tt_period as period, tt_day as day, M_Time_Table.Batch_Id as batch,
        Subject.code as sub_code, Subject.name as sub_name, Subject.isLab as is_lab, Subject.L as l, Subject.T as t, Subject.P as p,
        Teacher.id as teacher_id, Teacher.abbr, Teacher.school as teacher_school, TRIM(Teacher.department, ' ') as teacher_dept,
        Teacher.name as teacher_name, Teacher.isActive as teacher_is_active,
        M_Room.room_id, TRIM(M_Room.Name, ' ') as room_name, M_Room.isLab as room_is_lab, M_Room.building
        FROM M_Time_Table
        INNER JOIN CSF on M_Time_Table.csf_id=CSF.csf_id
        INNER JOIN Subject ON Subject.code=subject_code
        INNER JOIN CSF_Faculty ON CSF_Faculty.csf_id=M_Time_Table.csf_id
        INNER JOIN Teacher ON CSF_Faculty.faculty_id=Teacher.id
        INNER JOIN M_Room ON M_Room.room_id=M_Time_Table.room_id
        WHERE M_Time_Table.section_id='{section}'
        ORDER BY tt_day, tt_period
        """)
        response = prettify_timetable(data)
        return {'days': response}
    except exc.SQLAlchemyError as err:
        LOGGER.error("INFO:     Database Error Occurred.")
        return JSONResponse({"error": err}, status_code=500)
