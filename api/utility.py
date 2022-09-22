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
            "period": [d["period"]],
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


def remove_class(classes: list, to_remove: dict) -> list:
    for (k, v) in to_remove.items():
        (batch, sub_code) = k.split(",")
        index = 0
        for (idx, cls) in enumerate(classes):
            if (cls['batch'] == int(batch) and cls['subject']['code'] == sub_code):
                print(f'Got a Hit got {k}')
                index += 1
                print(f'Incremented index to {index}')
                if (index <= 1):
                    cls['period'] = list(v)
                    print(f'Changing into List {cls["period"]}')
                else:
                    print(f'Removing {cls}')
                    classes.pop(idx)


def combine_periods(data: dict):
    for day, classes in data.items():
        periods = dict[str, set]()
        for cls in classes:
            key = f"{cls['batch']},{cls['subject']['code']}"
            if periods.get(key) == None:
                period = set()
                period.add(cls['period'][0])
                periods[key] = period
            else:
                periods[key].add(
                    cls["period"][0])
        remove_class(classes, periods)
    return data
