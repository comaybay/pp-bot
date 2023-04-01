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


def judge_pp_color(color: str, author):
    color = color.lower()

    if color == 'clear':
        return "you've drink more than the daily recommended value. But it's good that you are hydrated, just drink a little less next time!"

    elif color == 'yellow':
        return "if pp color is pale yellow or clear then it is healthy, else if it's to bright then you might have had too much B vitamins in your body"

    elif color in ['bright yellow', 'neon yellow']:
        return "you have had too much of B vitamins, B stands for Ball of course, stop having balls in your jaw"

    elif color in ['pale yellow', 'light yellow']:
        return "healthy pp color"

    elif color in ['red', 'light red', 'pink']:
        return "bruh that's blood in your urine, that or maybe you've been eating foods that have red pigments, or medications"

    elif color in ['orange', 'brown', 'dark orange']:
        return "you're dehydrated!! Please drink more water"

    elif color == 'dark brown':
        return "in most case you're dehydrated, or else you might have a liver problem or some sort of medical condition, please seek medical attention"

    elif color in ['cloudy', 'foamy', 'fizzy']:
        return "please seek medical attention, it could be a sign of kidney issue"

    elif color in ['blue', 'cyan']:
        return "stop drinking miku's pp"

    elif color == 'green':
        return "drink less kurokku's pp" if author.name != "Kurokku" else "drink less of your own piss kurokku."

    elif color in ['purple', 'indigo']:
        return "drink less fanta grape flavor"

    else:
        return "im not sure, here is a list of pp color that i can judge: clear, yellow, bright yellow, pale yellow, orange, dark brown, cloudy, blue, green, purple."
