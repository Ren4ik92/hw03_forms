import datetime


def year(request):
    now = datetime.date.today()
    year = now.year
    return {
        'year': year
    }
