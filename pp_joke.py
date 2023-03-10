def judge_pp(size: float):
    if size <= 1.5:
        return "micro pp, F."

    elif size <= 10:
        return "small pp"

    elif size <= 13:
        return "average pp"

    elif size <= 16:
        return "long pp"

    elif size <= 20:
        return "johnny sins level pp"

    elif size <= 30:
        return "fantasy pp"

    else:
        return "no way pp"
