def prettify_timetable(data):
    response = {}
    temp = []
    i = 1
    for d in data:
        d = dict(d)
        if d["day"] != i:
            i = i + 1
            temp = []
        day = {
            "period": d["period"],
            "batch": d["batch"],
            "subject": {
                "code": d["sub_code"],
                "name": d["sub_name"]
            },
            "teacher": {
                "id": d["teacher_id"],
                "abbr": d['abbr'],
                "name": d['teacher_name'],
            },
            "room": {
                "id": d['room_Id'],
                "name": d['room_name'],
                "is_lab": d['room_is_lab'],
                "building": d['Building']
            }
        }
        temp.append(day)
        response.update({i: temp})
    return response
