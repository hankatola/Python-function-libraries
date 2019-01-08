# docstring
'''
    Contains the following date functions:
    date()      - returns system date and creates dates from inputs
    datedif()   - returns numeric differences between dates
    year()      - returns today's year or year of input date
    month()     - returns today's month or month of input date
    day()       - returns today's day of month or day of input date
    julian()    - returns the julian date of today or the given date
    weekNum()   - returns the week number of today or the given date
    dateMath()  - adds years, months, weeks, and days to today or given date
    eoMonth()   - returns the end of the month
'''

# needed other libraries
from dateutil import relativedelta
from numpy import nan
from math import floor
import dateutil.parser
import datetime


# Functions
def date(date1=False,month=False,day=False):
    # docstring
    '''
      Returns a date given any one of the following inputs where month and day are not called:
            text format ('July 19, 2012')
            date format ('07/19/2012', etc...)
            yyymmdd format (20120719)
        Acceptable inputs:
            date1:
                '7/19/2012' or 'July 19 2012' or 'Jul. the 19th, 2012' etc... (basically any reasonable date format)
                '20120719' or 20120719 (YYYYMMDD)
                '201207' or 201207 (returns beginning of month)
                2012 or '2012' (returns beginning of year)
            Month:
                MM or 'MM' - no other acceptable inputs ()
            Day:
                DD or 'DD' - no other acceptable inputs
    '''
    # function
    if date1 == False:
        date = datetime.datetime.now()
    elif date1 is None or date1 is 0 or date1 is '' or date1 is nan or date1 is 'nan' or date1 is '':
        date = ''
    elif len(str(date1)) > 4 and month == False and day == False:
        date = dateutil.parser.parse(str(date1))
    elif len(str(date1)) == 4 and month == False and day == False:
        date = datetime.datetime(int(date1),1,1)
    elif month != False and day == False:
        date = datetime.datetime(int(date1),int(month),1)
    else:
        date = datetime.datetime(int(date1),int(month),int(day))
    return date

def datedif(compare,today=False,period='m',exact=False):
    # docstring
    '''
        Returns absolute value of elapsed period between two dates. Return values
        will be either an integer or float, depending on whether or not exact is
        called. Days is inherently exact, so including an exact argument in the
        function will not make any difference.

        Acceptable inputs:
            compare & today
                see date1 under date() function for list of acceptable inputs. If you need
                to use date2 or date3 for date() function, call date() directly before
                and use its results as today and/or compare
                today defaults to today() if left blank
            period: defaults to months if not called
                'm' or 'months' or 12 or '2' or 'Monthly', etc... all return months
                'y' or 'years' or '1' or 1 or 'annual', etc... all return years
                'w' or 'weeks' or '3' or '52' etc...
                'd' or 'days' or '4' or '365', etc... all returns days
            exact: defaults to no
                False, 0, 'no', 'not exact', etc... all returns False
                anything else (True, 1, '1', 'yes', 'exact', etc...) returns True
    '''
    # sub-functions
    def datedif_months(today,compare):
        # returns the datedif in months regardless of date input type
        diff        = relativedelta.relativedelta(today, compare)
        months      = diff.years * 12 + diff.months
        return months

    def datedif_months_exact(today,compare):
        if (today.year == compare.year) and (today.month == compare.month):
            x           = julian(today) - 1
            y           = julian(compare) - 1
            z           = x - y
            eoMonth     = dateMath(date(date1=today.year,month=today.month),days=-1).day
            months      = z / eoMonth
        else:
            dayStart    = date(today.year,today.month)
            yayStart    = date(compare.year,compare.month)
            daysActual  = datedif_days(today,compare)
            monthStart  = datedif_months(dayStart,yayStart)
            daysStart   = datedif_days(dayStart,yayStart)
            months      = daysActual * monthStart / daysStart
        return months

    def datedif_years(today,compare):
        # returns the datedif in years regardless of data type
        diff        = relativedelta.relativedelta(today,compare)
        years       = diff.years
        return years

    def datedif_years_exact(today, compare):
        # returns the exact number of elapsed years in decimal form
        if today.year == compare.year:
            frac1       = (julian(today) - 1) / julian(date(today.year,12,31))
            frac2       = (julian(compare) - 1) / julian(date(compare.year,12,31))
            years       = frac1 - frac2
        else:
            dayStart    = date(today.year)
            yayStart    = date(compare.year)
            daysActual  = datedif_days(today,compare)
            startDays   = datedif_days(dayStart, yayStart)
            yearsApart  = datedif_years(dayStart, yayStart)
            years       = daysActual * yearsApart / startDays
        return years

    def datedif_days(today,compare):
        # returns the datedif in days regardless of data type
        days        = (today - compare).days
        return days

    def datedif_weeks(today,compare):
        days        = datedif_days(today,compare)
        weeks       = days // 7
        return weeks

    def datedif_weeks_exact(today,compare):
        days        = datedif_days(today,compare)
        weeks       = days / 7
        return weeks

    # set defaults - no reason to call date function if it's already a date
    if today == False:
        today = date()
    if type(today) != datetime.datetime:
        today = date(today)
    if type(compare) != datetime.datetime:
        compare = date(compare)
    period = str(period)

    # determine period
    if((period[0].lower()=='m') or (period=='2') or (period=='12')):
        period='m'
    elif((period=='1') or (period[0].lower()=='y') or (period[0].lower()=='a')):
        period='y'
    elif((period=='3') or (period=='52') or (period[0].lower()=='w')):
        period='w'
    else:
        period='d'
    # if exact is not default, it's probably True
    if (exact==False or str(exact)[0]=='0' or str(exact)[0]=='n'):
        exact=False
    else:
        exact=True

    # call the correct sub-function
    if period == 'm' and exact == False:
        difference = datedif_months(today,compare)
    elif period == 'm' and exact == True:
        difference = datedif_months_exact(today,compare)
    elif period == 'y' and exact == False:
        difference = datedif_years(today,compare)
    elif period == 'y' and exact == True:
        difference = datedif_years_exact(today,compare)
    elif period == 'w' and exact == False:
        difference = datedif_weeks(today,compare)
    elif period == 'w' and exact == True:
        difference = datedif_weeks_exact(today,compare)
    else:
        difference = datedif_days(today,compare)
    # take the absolute value of the answer - no negative differences allowed
    difference = abs(difference)
    return difference

def year(varIn=False):
    # docstring
    'Returns the year of today or the given date'
    if varIn == False:
        temp = date()
    else:
        temp = date(varIn)
    year = temp.year
    return year

def month(varIn=False):
    # docstring
    'Returns the month of today or the given date'
    if varIn == False:
        temp = date()
    else:
        temp = date(varIn)
    month = temp.month
    return month

def day(varIn=False):
    # docstring
    '''Returns today's day of the month, or the day of the month of the
    included argument (must be a recognizable as a date in one field)
    '''
    if varIn == False:
        temp = date()
    else:
        temp = date(varIn)
    day = temp.day
    return day

def julian(varIn=False):
    # docstring
    '''
        Returns the julian date of today - i.e. the day of the year, or
        the julian date of the included argument
    '''
    if varIn == False:
        mid = date()
        start = year()
    else:
        mid = date(varIn)
        start = date(mid.year)
    julian = datedif(mid,start,period='Days',exact=False) + 1
    return julian

def dateMath(date1=False,years=0,months=0,weeks=0,days=0):
    #docstring
    '''
       Inputs:
            date1 = False       Optional, defaults to today if omitted
            years = 0           Optional
            months = 0          Optional
            weeks = 0           Optional
            days = 0            Optional

        Description:
            adds/subtracts years, months, or days from the given date. Order of operations is (years & months), (weeks & days). If
            target month has fewer days than beginning month, i.e. 20170131 + 1 month (there is no day 31 in February),
            formula defaults to the last day of the answer month. So the formula would return 20170228 in a non leap-year.

            All inputs must be integers
    '''
    if date1 == False:
        date1 = date()
    if type(date1) != datetime.datetime:
        date1 = date(date1)
    stYr = date1.year
    stMo = date1.month
    stDy = date1.day

    #   year & month
    start_date = stYr + (stMo - 1) / 12
    add_date = years + months / 12
    end_date = start_date + add_date

    nwYr = floor(end_date)
    nwMo = round((end_date - nwYr) * 12 + 1,0)

    end_date = date(nwYr,nwMo,stDy) + datetime.timedelta(days = days, weeks = weeks)
    answer = end_date
    return answer

def weekNum(varIn=False):
    ''' returns the weekNum of today or the date passed by to the function'''
    if varIn == False:
        temp = date()
    else:
        temp = date(varIn)
    return weekNum

def eoMonth(varIn=False):
    ''' 
        returns the last day of the month as a date of either this month or the
        date passed to the function
    '''
    if varIn == False:
        temp = date()
    else:
        temp = date(varIn)
    ans_year = dateMath(temp,months=1).year
    ans_mnth = dateMath(temp,months=1).month
    ans_date = dateMath(date1 = ans_year,month=ans_mnth)

    eom = dateMath(date1=ans_date,days=-1)
    return eom
