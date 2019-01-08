# docstring
'''
    Contains the following TVM business functions:
    rates()     - returns interest rates [i,d,v,delta]
    solve_r()   - solves for unknown interest rates
    pv()        - returns present value of future cash flows
    fv()        - returns future value of present cash flows
    solve_t()   - solves for unknown time
    solve_q()   - solves for unknown payment amount
'''

# imports
from math import exp
from math import log
from mpmath import polyroots
from mpmath import ctx_mp_python

# Functions
def rates(r,r_is=False,get=False,q_per_t=False):
    # docstring
    '''
        Function Description:
            -   Gets associated rates given input rate and (optional) type (r_is) and returns
                all assocated rates as a dictionary of form:
                    {'i':i,'d':d,'v':v,'delta':delta}
            -   If 'get' is passed to function it returns singular requested value. i.e. if get = 'delta'
                function returns only delta instead of a dict.
            -   adjusts answers to equivalent rates compounded per period if called

        Calculation assumptions:
            All returned values are rounded to 10 decimal places.
            Where (Future Value = FV) and (Present Value = PV) and (time = t)
                i:      FV = PV * (1 + i)^t
                d:      PV = FV * (1 - d)^t
                v:      PV = FV * v^t
                delta:  FV = PV * exp(delta * t)
            Adjusted rates per period 'i_t' are equivalent to:
                i_t     = (1+i)^(1/q_per_t) - 1

        Variable/argument Description:
            r:      mandatory primary argument
            r_is:   Optional. What type of rate 'r' is. Default assumes 'r' is an interest rate 'i'
            get:    Optional. The specific associated rate to return. Default returns all rates
            q_per_t:
                    adjust returned rates for a different compounding period. i.e. if given rate r
                    is annual but desired rate get is monthly, then q_per_t should be passed as 12,
                    and the returned rate r will be adjusted to the different compounding period and
                    can be used as such immediately. In this case q_per_t returns the q_per_t'th root
                    of r. So returned rate r will be r ** (1/q_per_t).

                    Conversely, if r needs to be adjusted to a biannual effective rate, then q_per_t
                    should be passed as 0.5

        Acceptable argument inputs:
            r:
                Decimal or float: .01 = 1%, 1 = 100%
            r_is & get:
                interest rate i, pass:
                    nothing OR 1 OR a string that starts with 'i'
                discount rate d, pass:
                    2 OR a string that starts with 'd'
                discount rate v, pass:
                    3 OR a string that starts with 'v'
                continuously compounded force of interest, pass:
                    4 OR a string that starts with 'de', 'c', or 'f'
            q_per_t:
                Decimal or float
    '''

    # internal functions
    def interest(r):
        # calculates associated rates if r is an interest rate
        i = r
        d = i/(1+i)
        v = 1-d
        delta = exp(i)-1
        rates = {'i':i,'d':d,'v':v,'delta':delta}
        return rates

    def discount(r):
        # calculates associated rates if r is a discount rate
        d = r
        i = d/(1-d)
        v = 1-d
        delta = exp(i)-1
        rates = {'i':i,'d':d,'v':v,'delta':delta}
        return rates

    def getV(r):
        # calculates associated rates if r is a discount factor
        v = r
        d = 1-v
        i = 1/v - 1
        delta = exp(i)-1
        rates = {'i':i,'d':d,'v':v,'delta':delta}
        return rates

    def delta(r):
        # calculates associated rates if r is a continuously compounded interest
        # rate
        delta = r
        i = log(1+delta)
        d = i/(1+i)
        v = 1-d
        rates = {'i':i,'d':d,'v':v,'delta':delta}
        return rates

    def roundValues(answer):
        # rounds all dict values to 10 decimal places
        answer['i'] = round(answer['i'],10)
        answer['d'] = round(answer['d'],10)
        answer['v'] = round(answer['v'],10)
        answer['delta'] = round(answer['delta'],10)
        return answer

    # Function Body
    #   if r_is has been specified then determine its type, else it's assumed to
    #   be an interest rate 'i'
    if r_is:
        r_is = get_rType(str(r_is))
    else:
        r_is = 'i'

    #   given r_is, call the appropriate rate calculation function
    if r_is == 'i':
        answer = interest(r)
    elif r_is == 'd':
        answer = discount(r)
    elif r_is == 'v':
        answer = getV(r)
    else:
        answer = delta(r)

    #   round the resulting values to 10 decimal places
    answer = roundValues(answer)

    #   if adjust was requested, recalculate i & redo function
    if q_per_t:
        i = (1 + answer['i'])**(1 / q_per_t) - 1
        answer = rates(r=i)

    #   if a specific value was requested via get then return that, else returns
    #   all calcualted values via the dict
    if get:
        get = get_rType(str(get))
        answer = answer[get]

    return answer

def solve_r(pv=False,q=False,t=False,fv=False,annuity_due=False,get=False,q_per_t=False):
    # docstring
    '''
       Function Description:
            Solves for interest rates [i,d,v,delta] based on payments described by either pv, q, t, and fv
            Use get to return a specific interest rate, otherwise function returns a dict of all four based
            on the output of the function rates().

        Calculation assumptions:
            pv and fv are assumed to be the opposite of q, i.e. if pv = 3, q = 1, and t = 4, then the
            annuity payment stream is assumed to be either [-3,1,1,1,1] or [3,-1,-1,-1,-1] - both of which
            return the same interest rate (in this case ~12.6%).

            t multiplies q, so if t = 2 and q = 1, then the annuity stream is assumed to be [1,1]. However
            if q = [1,2] and t = 2, then the annuity stream is assumed to be [1,2,1,2]. t has no affect on
            pv or fv.

            annuity payments q are evenly spaced for the duration of the annuity.

            There is no bottom limit to negative interest rates.

        Variable/argument Description:
            pv:
                present value of future funds/first annuity payment made to opposite to q
            q:
                annuity payments equally spaced out over time
            t:
                the number of times the annuity payments are made. If q is a list and t is passed,
                then the pattern q is assumed to be repeated t times, all the payments of which are
                made at evenly spaced intervals.
            fv:
                accumulated value of funds/final annuity payment made opposite to q
            annuity_due:
                annuity payments are assumed to be immediate, i.e. begin one period t from inception. If
                that is not the case, i.e. annuity payments begin immediately upon inception, then the annuity
                due on inception, and thus an annuity-due. Annuities-due are atypical.
            get:
                return a rate either i, d, v, or delta. See rates() function for descriptions of each. This
                function returns i by default
            q_per_t:
                return rate r adjusted for different compounding period than calculated. So if the annuity payments
                passed are actually monthly but you're looking for an annual effective rate, then pass q_per_t as 12.
                Conversely if the annuity payments as described are biannual, then pass q_per_t as 0.5 to return the
                effective annual interest rate.

                See the description in the rates() function for further explanation, but be advised that it this functions
                inversely here as opposed to there. i.e. passing 12 in this function will mean that the returned rate
                r is r ** 12 as opposed to r ** (1/12)

        Acceptable argument inputs:
            q:
                int, float, or a list of either or both
            get:
                interest rate i, pass:
                    nothing OR 1 OR a string that starts with 'i'
                discount rate d, pass:
                    2 OR a string that starts with 'd'
                discount rate v, pass:
                    3 OR a string that starts with 'v'
                continuously compounded force of interest, pass:
                    4 OR a string that starts with 'de', 'c', or 'f'
            t:
                int only
            annuity_due:
                True or False
            all others:
                int or float
    '''

    # Function Body
    #   If q is False, the answer is easier
    if q == False:
        #   account for the possibility that we are only given fv
        if pv == False:
            pv = 1
        if fv == False:
            fv = 1

        #   simple rate calculation
        r = (fv / pv) ** (1 / t) - 1
    else:
        # need to create a list of payments (q).
        if isinstance(q,list) == False:
            q = [q]
        if t != False:
            q *= t
        if pv != False and annuity_due == True:
            q[0] = q[0]-pv
        elif pv != False:
            q = [-pv] + q
        if fv != False and annuity_due == False:
            q[-1] = q[-1] - fv
        elif fv != False and annuity_due == True:
            q.append(-fv)

        #   find the roots of the polynomial as created above
        real = []
        for i in polyroots(q):
            # we only want real numbers
            if isinstance(i,ctx_mp_python.mpf):
                real.append(i)
        # we want the positive zero, if it exists, and we can't take the max of a null list
        if real == []:
            real = [1]
        r = max(real)
        #   make r a percentage
        r = float(r - 1)

        #   payments q must have ins and outs. If it is all outs or all ins then q is free money and no investment was
        #   made to make a return. Therefore test for lack of investment and return an error value (0) if no
        #   investment was ever made.
        if max(q) < 0 or min(q) > 0:
            r = 0

    # q_per_t functions inversely in this function to all other functions.
    if q_per_t != False:
        q_per_t = 1 / q_per_t
    r = rates(r=r,get=get,q_per_t=q_per_t)

    return r

def pv(r,t=False,r_is=False,q=False,fv=False,q_per_t=False,annuity_due=False,cash_today=False,precision=False):
    # docstring
    '''
        Function Description:
            Returns Present Value (pv) of given arguments. Unlike most other PV functions,
            this one does not check for positive/negative values for pv, fv, and payments (q).
            Returns pv of fixed fv amounts as well as annuities immediate and due.
            Precision up to 16 decimal places, default is 2.
            q may be a single payment amount or a list of payments. If given as a list it must
            not skip periods, i.e. if an interest period has no payment then there must be a 0

        Calculation assumptions:
            Annuity payment are level/regular and interest rates do not change

        Variable/Argument Description:
            r       = given interest rate
            r_is    = optional, defaults to 'i'. "r is" either 'i','d','v','delta'
            t       = given time period. Usually years.
            q       = individual annuity payment amount OR cash flow stream
            q_per_t = how many annuity payments per period t. If rate 'r' is annual
                    but payments 'q' are monthly, this variable should be 12
            fv      = future value, or in the case of annuity payments, the final payment
                    that exchanges hands. i.e. the final payment is the sum of fv + q_final
            annuity_due = True if annuity due, defaults to False
            cash_today  = any cash exchanging hands today
            precision   = decimal places of answer, defaults to 2

        Acceptable Argument inputs:
            r           : float. 1% should be entered as .01
            r_is        : see rates docstring for description
            annuity_due : True or False
            precision   : integer <= 16
            q           : float/integer or list of float/integers
            all others  : float or integer
    '''

    # Function Body
    #   if 'r_is' has been specified then determine its type, else it's assumed to
    #   be an interest rate 'i'
    if r_is:
        r_is = get_rType(str(r_is))
    else:
        r_is = 'i'

    #   establish t
    if not t:
        t = 1

    #   get the appropriate rates per payment period
    if q_per_t:
        iRates = rates(r=r,r_is=r_is,q_per_t=q_per_t)
        t = t * q_per_t
    else:
        iRates = rates(r=r,r_is=r_is)
        q_per_t = 1

    #   assign 0 to all unused/uncalled arguments for math
    if fv == False and q == False:
        fv = 1
        precision = 16
    if q == False:
        q = 0
    if cash_today == False:
        cash_today = 0

    #   Calculate values via irregular annuity stream or standard PV
    if isinstance(q,list):
        #   calculate pv via array method - we have an irregular annuity stream

        #   variable declarations
        pmts = []
        t = 1
        if annuity_due == True:
            t = 0

        #   payment loop
        for payment in q:
            pv_pmt = payment * iRates['v']**t
            pmts.append(pv_pmt)
            t += 1

        #   present value of annuities
        presVal = sum(pmts)
        #   t was iterated 1 higher than necessary as loop ended, needs to be reset
        #   so that final fv adjustment is accurate
        t -= 1

    else:
        # calculate pv via traditional method: q is annuity or single cashflow
        #   calculate present value of annuity + future value + cash today
        if annuity_due == False:
            presVal = q * (1 - iRates['v']**t) / iRates['i']
        else:
            presVal = q * (1 - iRates['v']**t) / iRates['d']

    #   final step:
    presVal += fv * iRates['v']**t
    presVal += cash_today

    #   round
    if precision == False:
        precision = 2
    precision = min(precision,16)

    presVal = round(presVal,precision)

    return presVal

def fv(r,t=False,r_is=False,q=False,pv=False,q_per_t=False,annuity_due=False,future_cash=False,precision=False):
    # docstring
    '''
        Function Description:
            Returns Future Value (fv) of given arguments. Unlike most other FV functions,
            this one does not check for positive/negative values for pv, fv, and payments (q).
            Returns fv of fixed amounts as well as annuities immediate and due.
            Precision up to 16 decimal places, default is 2

        Calculation assumptions:
            Annuity payment are level/regular and interest rates do not change

        Variable/Argument Description:
            r       = given interest rate
            r_is    = optional, defaults to 'i'. "r is" either 'i','d','v','delta'
            t       = given time period. Usually years. Optional/not needed if q is a list
            q       = individual annuity payment amount OR list of payments
            q_per_t = how many annuity payments per period t. Would be 12 if payments
                    were Monthly but given rate 'r' is annual
            pv      = present value
            annuity_due = True if annuity due, defaults to False
            cash_today  = any cash exchanging hands today

        Acceptable Argument inputs:
            r       : float. 1% should be entered as .01
            r_is    : see rates docstring for description
            annuity_due: True or False
            all others: float or integer
    '''

    # Function Body
    #   if 'r_is' has been specified then determine its type, else it's assumed to
    #   be an interest rate 'i'
    if r_is:
        r_is = get_rType(str(r_is))
    else:
        r_is = 'i'

    #   get the appropriate rates per payment period
    if q_per_t:
        iRates = rates(r=r,r_is=r_is,q_per_t=q_per_t)
        t = t * q_per_t
    else:
        iRates = rates(r=r,r_is=r_is)
        q_per_t = 1

    #   assign 0 to all unused/uncalled arguments for math
    if pv == False and q == False:
        pv = 1
        precision = 16
    if q == False:
        q = 0
    if future_cash == False:
        future_cash = 0

    #   cash-flow stream or traditional annuity stream
    if isinstance(q,list):
        #   payments are a list - need to be calculated individually

        #   reverse list so that normal loop can just iterate through without
        #   needing to worry about finding the total range of the list
        q.reverse()
        pmts = []
        t_list = 0
        # accumulation starts immediately if annuity_due == True
        if annuity_due == True:
            t_list = 1
        # pmt loop
        for i in q:
            pmt = i * (1 + iRates['i'])**t_list
            pmts.append(pmt)
            t_list+=1
        #   re-reverse the list to set back to original order
        q.reverse()

        futVal = sum(pmts)

    else:
        #   payments are not a list - standard calculations apply
        #   calculate future value of annuity + pv + future cash
        if annuity_due == False:
            futVal = q * ((1 + iRates['i'])**t - 1) / iRates['i']
        else:
            futVal = q * ((1 + iRates['i'])**t - 1) / iRates['d']

    futVal += pv * (1 + iRates['i'])**t
    futVal += future_cash

    #   round
    if precision == False:
        precision = 2
    precision = min(precision,16)

    futVal = round(futVal,precision)

    return futVal

def solve_t(r,pv=False,r_is=False,q=False,q_per_t=False,fv=False,annuity_due=False,precision=False):
    # docstring
    '''
        Function Description:
            Solves for the number of periods of time 't' given an interest rate and at least
            one of the following: present value (pv), future value (fv), or payments (q). If
            pv is not given, pv defaults to 1. Function is not currently designed to handle
            all three values (pv, fv, and q) at once, and will return an answer of 0.
            Precision up to 16 decimal places (default is 10)

        Calculation assumptions:
            Annuity payment are level and interest rates do not change

        Variable/Argument Description:
            r       = given interest rate
            r_is    = optional, defaults to 'i'. "r is" either 'i','d','v','delta'
            q       = individual annuity payment amount
            q_per_t = how many annuity payments per period t. Would be 12 if payments
                    were Monthly but given rate 'r' is annual
            pv      = present value
            annuity_due = True if annuity due, defaults to False
            cash_today  = any cash exchanging hands today

        Acceptable Argument inputs:
            r       : float. 1% should be entered as .01
            r_is    : see rates docstring for description
            annuity_due: True or False
            all others: float or integer
    '''

    # Function Body
    #   if 'r_is' has been specified then determine its type, else it's assumed to
    #   be an interest rate 'i'
    if r_is:
        r_is = get_rType(str(r_is))
    else:
        r_is = 'i'

    #   get the appropriate rates per payment period
    if q_per_t:
        iRates = rates(r=r,r_is=r_is,q_per_t=q_per_t)
    else:
        iRates = rates(r=r,r_is=r_is)

    # denominator
    denominator = log(1 + iRates['i'])

    # numerator
    if pv == False:
        pv = 1
    if (q == False and fv == False) or (pv == fv):
        numerator = denominator
    elif q == False and fv != False:
        numerator = log(fv / pv)
    elif q != False and fv == False and annuity_due == False:
        numerator = -log(1 - iRates['i'] * pv / q)
    elif q != False and fv == False and annuity_due == True:
        numerator = -log(1 - iRates['d'] * pv / q)
    else:
        numerator = 0

    #   round
    if precision == False:
        precision = 10
    precision = min(precision,16)

    t = round(numerator / denominator, precision)

    return t

def solve_q(r,t,r_is=False,pv=False,fv=False,q_per_t=False,annuity_due=False,sinking_fund=False,precision=False):
    # docstring
    '''
       Function Description:
            Returns payment amount (q) given specified arguments.
            Max precision is 10^-16

        Calculation assumptions:
            Annuity payment are level and interest rates do not change.
            If pv and fv are not specified then pv is set to 1.
            If sinking_fund == True, payments q are accumulated, otherwise (by default)
                payments are discounted.

        Variable/Argument Description:
            r       = given interest rate
            r_is    = optional, defaults to 'i'. "r is" either 'i','d','v','delta'
            t       = given time period. Usually years.
            q_per_t = how many annuity payments per period t. Would be 12 if payments
                    were Monthly but given rate 'r' is annual
            pv      = present value
            fv      = future value
            annuity_due = True if annuity due, defaults to False

        Acceptable Argument inputs:
            r       : float. 1% should be entered as .01
            r_is    : see rates docstring for description
            annuity_due: True or False
            all others: float or integer
    '''

    # Function Body
    #   if 'r_is' has been specified then determine its type, else it's assumed to
    #   be an interest rate 'i'
    if r_is:
        r_is = get_rType(str(r_is))
    else:
        r_is = 'i'

    #   get the appropriate rates per payment period
    if q_per_t:
        iRates = rates(r=r,r_is=r_is,q_per_t=q_per_t)
        t *= q_per_t
    else:
        iRates = rates(r=r,r_is=r_is)
        q_per_t = 1

    #   account for annuity_due
    if annuity_due == False:
        r = iRates['i']
    else:
        r = iRates['d']

    #   calculate the numerator
    if fv == False and pv == False:
        numerator = 1
        precision = 16
    elif sinking_fund == False and fv == False and pv:
        numerator = pv
    elif sinking_fund == False and fv != False and pv != False:
        numerator = fv * iRates['v'] ** t - pv
    elif sinking_fund == True and fv != False and pv == False:
        numerator = fv
    else:
        numerator = fv - pv * (1 + iRates['i']) ** t

    #   calculate the denominator
    if sinking_fund == False:
        denominator = (1 - iRates['v']**t) / r
    else:
        denominator = ((1 + iRates['i'])**t - 1) / r

    #   round
    if precision == False:
        precision = 2
    precision = min(precision,16)

    pmt = round(numerator / denominator, precision)

    return pmt

def get_rType(x):
    # No docstring
    # Internal library function. Cleans & determines what type of value is being passed
    # as 'r'. I.e. users may pass i (interest rate), d (discount), v (discount rate), or
    # delta (continuously compounding interest rate)
    if x=='1' or x[0].lower()=='i':
        x = 'i'
    elif x=='4' or x[0:2].lower()=='de' or x[0].lower()=='c' or x[0].lower()=='f':
        x = 'delta'
    elif x=='2' or x[0].lower()=='d':
        x = 'd'
    elif x=='3' or x[0].lower()=='v':
        x = 'v'
    return x
