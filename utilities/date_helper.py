from datetime import datetime, date

def get_month_label(month):
    if month == 1:
        return 'Jan'
    elif month == 2:
        return 'Feb'
    elif month == 3:
        return 'Mar'
    elif month == 4:
        return 'Apr'
    elif month == 5:
        return 'May'
    elif month == 6:
        return 'Jun'
    elif month == 7:
        return 'Jul'
    elif month == 8:
        return 'Aug'
    elif month == 9:
        return 'Sep'
    elif month == 10:
        return 'Oct'
    elif month == 11:
        return 'Nov'
    elif month == 12:
        return 'Dec'
    else:
        return ''  

def get_next_month(month):
    if month >= 12:
        return 1
    else:
        return month + 1

def get_year_of_next_month(month, year):
    if month >= 12:
        return year + 1
    else:
        return year
    
def get_previous_month(month):
    if month <= 1:
        return 12
    else:
        return month - 1

def get_year_of_previous_month(month, year):
    if month <= 1:
        return year - 1
    else:
        return year

def get_last_year_date():
    dtnow = datetime.utcnow()
    if dtnow.month < 12:
        return date(dtnow.year-1, dtnow.month + 1, 1)
    return date(dtnow.year, 1, 1)

def get_month_index(dt):
    last_year = get_last_year_date()
    if dt < last_year or dt > date.today():
        return -1
    return (dt.month + 12 - last_year.month)%12
