from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import exc
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.database import get_db
from api.utility import prettify_timetable

timetable = APIRouter()


@timetable.get("/ping")
async def ping():
    return JSONResponse({"message": "pong"}, status_code=200)


@timetable.get("/schools")
def schools(db: Session = Depends(get_db)):
    try:
        data = db.execute(
            "SELECT Name as name, FullName as full_name, id as id FROM School")
        return [dict(d) for d in data]
    except exc.SQLAlchemyError as err:
        print("failed to fetch schools from database")
        return JSONResponse({"error": "failed to fetch schools from database"}, status_code=500)


@timetable.get("/sections")
async def sections(school: str, db: Session = Depends(get_db)):
    if " " in school:
        return JSONResponse({"error": "Invalid School ID"}, status_code=400)
    try:
        data = db.execute("""
        SELECT Section.Id as section_id, Section.Name as section_name,
        Section.Semester as semester, Program.id as program_id,
        Program.Code as program_code, Program.Name as program_name,
        Program.school, Program.IsActive as is_active 
        FROM Section 
        INNER JOIN Program on Section.Program=Program.id WHERE school = :school AND is_active = 1 AND Section.ShowTimeTable = 1
        """, {"school": school})
        return [dict(d) for d in data]
    except exc.SQLAlchemyError as err:
        print(f"failed to fetch sections from database {e}")
        return JSONResponse({"error": "failed to fetch sections from database"}, status_code=500)


@timetable.get("/teachers")
async def teachers(teacher_id: int = None, db: Session = Depends(get_db)):
    try:
        data = db.execute("""
        SELECT id,abbr, school, name,isActive as is_active, department FROM Teacher WHERE id = :id
        """, {"id": teacher_id})
        t = [dict(d) for d in data]
        if t.__len__() > 0:
            return t.pop()
        else:
            return JSONResponse({"error": "no teacher with that id found"}, status_code=404)
    except exc.SQLAlchemyError as err:
        print(f"failed to fetch teachers from database {err}")
        return JSONResponse({"error": "failed to fetch teachers from database"}, status_code=500)


@timetable.get("/subjects")
async def subject(subject: str, db: Session = Depends(get_db)):
    if " " in subject:
        return JSONResponse({"error": "Invalid Subject ID"}, status_code=400)
    try:
        data = db.execute("""
        SELECT Subject.id as sub_id , Subject.name as sub_name, Subject.code as sub_code,
        Subject.IsLab as is_lab, Subject.L, Subject.T, Subject.P, AV.Code
        as dept_code, AV.dept as dept_name, AV.school as school
        FROM Subject INNER JOIN ATView AV on Subject.code = AV.Code WHERE Subject.code = :subject
        """, {"subject": subject})
        s = [dict(d) for d in data]
        if s.__len__() > 0:
            return s.pop()
        else:
            return JSONResponse({"error": "no subject with that id found"}, status_code=404)
        return [dict(d) for d in data].pop()
    except exc.SQLAlchemyError as err:
        print(f"failed to fetch subject from database {e}")
        return JSONResponse({"error": "failed to fetch subject from database"}, status_code=500)


@timetable.get("/timetable")
async def timetables(section: int = None, db: Session = Depends(get_db)):
    try:
        data = db.execute("""
        SELECT tt_period as period, tt_day as day, M_Time_Table.Batch_Id as batch,
        Subject.code as sub_code, Subject.name as sub_name, Subject.isLab as is_lab, Subject.L as l,  Subject.T as t, Subject.P as p,
        Teacher.id as teacher_id, Teacher.abbr, Teacher.school as teacher_school, TRIM(Teacher.department,  ' ') as teacher_dept,
        Teacher.name as teacher_name, Teacher.isActive as teacher_is_active,
        M_Room.room_id, TRIM(M_Room.Name, ' ') as room_name, M_Room.isLab as room_is_lab, M_Room.building
        FROM M_Time_Table
        INNER JOIN CSF on M_Time_Table.csf_id=CSF.csf_id
        INNER JOIN Subject ON Subject.code=subject_code
        INNER JOIN CSF_Faculty ON CSF_Faculty.csf_id=M_Time_Table.csf_id
        INNER JOIN Teacher ON CSF_Faculty.faculty_id=Teacher.id
        INNER JOIN M_Room ON M_Room.room_id=M_Time_Table.room_id
        WHERE M_Time_Table.section_id= :section_id AND M_Time_Table.SessionId = (SELECT Id FROM Session WHERE (CurrentActive = 1))
        ORDER BY tt_day, tt_period
        """, {"section_id": section})
        show = db.execute(f"SELECT * FROM Section WHERE Id = '{section}'")
        for i in show:
            show = dict(i)
        response = prettify_timetable(data)
        return {'days': response, "show_tt": show["ShowTimeTable"]}
    except exc.SQLAlchemyError as err:
        print(f"failed to fetch subject from database {e}")
        return JSONResponse({"error": "failed to fetch subject from database"}, status_code=500)
