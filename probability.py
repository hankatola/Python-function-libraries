# docstring
'''
    Contains the following probability/mathematical functions:
    nCr()               - permutations
    binomial()          - binomial probability
    negative_binomial() - negative binomial probability
    hypergeometric()    - hypergeometric probability
    poisson()           - poisson probability
    primes()            - returns prime numbers
    fibonacci()         - fibonacci numbers
    bernoulli()         - bernoulli numbers and/or specified row of Faulhaber's triangle
    summation()         - returns summation of 'n' numbers to the power of 'x'
'''

# function imports
from math import factorial
from math import exp
from math import sqrt
from math import floor
from math import log
from fractions import Fraction
import re

# Functions
def nCr(n,r):
    # docstring
    '''
        Out of a population of size 'n' return # of combinations of size 'r'
    '''
    combinations = factorial(n)/(factorial(r)*factorial(n-r))
    return combinations

def nPr(n,r):
    '''
        Out of a population of size 'n' return # of permutations of size 'r'
    '''
    permutations = factorial(n)/factorial(n-r)
    return permutations

def binomial(n,k,p,cumulative=False,get=False,precision=False):
    # docstring
    '''
        Out of a population of size 'n' choose 'k' where the probability of 'k' is 'p'
        precision defaults to 6 decimal places. Cumulative available.
    '''
    q = 1 - p
    # probability
    if cumulative == True:
        prob = 0
        for i in range (0,k+1):
            prob += nCr(n=n,r=i) * (p**i) * q**(n - i)
    else:
        prob = nCr(n=n,r=k) * (p**k) * (q**(n - k))
    #remaining parameters
    mean = p * n
    variance = mean * q
    # set precision
    if precision is False:
        precision = 6
    prob = round(prob,precision)
    mean = round(mean,precision)
    variance = round(variance,precision)
    answer = {'p(x)':prob,'mean':mean,'var':variance}
    # select chosen property, if requested
    if get:
        answer = getAnswer(get=get,answer=answer)
    return answer

def negative_binomial(r,k,p,cumulative=False,get=False,precision=False):
    '''
        probability of 'k' failures before the 'r'th success where the probability of
        success is 'p'. Precision defaults to 6 decimal places. Cumulative available.
    '''
    q = 1 - p
    x = r + k - 1
    y = r - 1
    # probability
    if cumulative == True:
        prob = 0
        for i in range (0,k+1):
            # x is the variable that stores k, which is the value we're iterating
            # through, so it must be redefined
            x = r + i - 1
            prob += nCr(n=x,r=y) * p**r * q**i
    else:
        prob = nCr(n=x,r=y) * p**r * q**k
    # remaining parameters
    mean = q / p
    variance = mean / p
    # set precision
    if precision is False:
        precision = 6
    prob = round(prob,precision)
    mean = round(mean,precision)
    variance = round(variance,precision)
    answer = {'p(x)':prob,'mean':mean,'var':variance}
    # return requested variable if specified
    if get:
        answer = getAnswer(get=get,answer=answer)
    return answer

def hypergeometric(N,n,r,k,cumulative=False,get=False,precision=False):
    # docstring
    '''
        Choosing 'n' out of a total population of 'N', returns the probability of
        returning 'k' target items out of a target population of 'r'. precision
        defaults to 6 decimal places. Cumulative available
    '''
    N_minus_r = N - r
    n_minus_k = n - k
    if cumulative == True:
        prob = 0
        for i in range (0,k+1):
             n_minus_k = n - i
             prob += (nCr(r,i) * nCr(N_minus_r,n_minus_k)) / nCr(N,n)
    else:
        prob = (nCr(r,k) * nCr(N_minus_r,n_minus_k)) / nCr(N,n)
    # remaining parameters
    mean = n * r / N
    variance = mean * (1 - r / N) * ((N - n) / (N - 1))
    # set precision
    if precision is False:
        precision = 6
    prob = round(prob,precision)
    mean = round(mean,precision)
    variance = round(variance,precision)
    answer = {'p(x)':prob,'mean':mean,'var':variance}
    # return requested variable, if specified
    if get:
        answer = getAnswer(get=get,answer=answer)
    return answer

def poisson(rate_lambda,k,cumulative=False,precision=False):
    '''
        P(x) of 'k' events happening given mean & variance 'rate_lambda'.
        Precision defaults to 6 decimal places, cumulative available
        mean = variance = rate_lambda
    '''
    if cumulative == True:
        prob = 0
        for i in range (0, k+1):
            prob += (rate_lambda**i * exp(-rate_lambda)) / factorial(i)
    else:
        prob = (rate_lambda**k * exp(-rate_lambda) ) / factorial(k)
    # set precision
    if precision is False:
        precision = 6
    prob = round(prob,precision)
    return prob

def primes(n,max=False):
    '''
        Uses the Sieve of Eratosthenes to generate a list of prime numbers <= 'n'.
        Returns the maximum prime number <= 'n' if 'max' == True
    '''
    # trying to use the Sieve of Eratosthenes: https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes
    #
    # create list of odd numbers beginning at 3 up to n, create second list of
    # the same size, but of all zeros. Use the two lists to create a dictionary
    # to track whether or not the numbers are composite
    l = [i for i in range(3,n+1,2)]
    z = [0] * len(l)
    z = dict(zip(l,z))
    # need a counter to make sure we start at the right place in the dict list
    # as we iterate through
    counter = 0
    # loop through and record the multiples of the primes. For each number 'a' in
    # list 'l', move in steps of 'a' through dict 'z' and indicate that each
    # number is composite. Each time we go through we must start at position
    # 'a' + counter to ensure we move through 'z' correctly.
    for a in l:
        for b in l[a+counter::a]:
            z[b] = 1
        counter += 1
    # delete everything in list 'l' that has a '1' stored in the dictionary -
    # i.e. is composite
    l[:] = [c for c in l if z[c] == 0]
    if n >= 2:
        l = [2] + l
    if max is not False:
        l = l[-1]
    return l

def fibonacci(n,position=False):
    # nth position fibonacci number is defined by
    '''
        returns the nth fibonacci number OR the position of fibonacci number 'n'
        when postion == True
    '''
    x = (1 + sqrt(5)) / 2
    y = (1 - sqrt(5)) / 2
    if position is False:
        n += 1
        answer = (x**n - y**n) / sqrt(5)
        answer = round(answer,0)
    else:
        answer = log(n * sqrt(5), x)
        answer = floor(answer) - 1
    return answer

def bernoulli(n,entireRow=False):
    '''
        Creates bernoulli numbers by making the Faulhaber Triangle. Returns bernoulli
        number by default, or last row if row == True.
    '''
    #   Academic paper describing process can be found at:
    #       https://www.research-collection.ethz.ch/bitstream/handle/20.500.11850/69248/eth-4937-01.pdf?sequence=1&isAllowed=y
    #   For the purposes of the algorithm, the triangle (here 't') has been flipped on the x-axis so that the bernoulli number
    #   ends up in the last column of the row, rather than the first. This switch means that the faulhaber coefficient in 
    #   [row(x),column(y)] = [x-1,y] * [x,y], rather than [x-1,y-1] * [x,y] as described in the paper. Also it makes more sense
    #   to me. 

    t = [0] * (n+1)
    row = 0
    for row in range(n+1):
        column = row + 1
        i = 0
        for column in range(column,1,-1):
            t[i] *= Fraction(row,column)
            i+=1
        t[row] = 1 - sum(t)

    if entireRow is False:
        return t[-1]
    else:
        return t

def summation(n,x=1):
    '''
        Returns the summation of the first 'n' numbers to the 'x'th power (if used)
        using Bernoulli's formula. See
            https://en.wikipedia.org/wiki/Faulhaber%27s_formula
        for description
    '''
    # uses final row of the Faulhaber triangle from the Bernoulli function.
    # Formula is summation of Bn_i * n ** (len(Bn) - i)
    Bn = bernoulli(x,entireRow=True)
    r = len(Bn)
    i = 0
    x = 0
    for j in Bn:
        x += j * n**(r - i)
        i += 1
    x = int(x)
    return round(x)

def solve_algebra(equation,solve_for='x'):
    ####################################
    #   Equation Class
    ####################################

    class equation():
        c = None    # equation Complete
        L = None    # equation - Left side
        R = None    # equation - Right side
        uR = None   # Right side unknowns
        uL = None   # Left side unknowns
        nR = None   # Right side numbers
        nL = None   # Left side numbers
        t = None    # Target variable to solve for
        # operations, left & right sides
        opsR = {'+':[],'-':[],'*':[],'/':[],'^':[],'(':[],')':[]}
        opsL = opsR
        # order of operations
        pemdas = {1:'(',2:'^',3:'*',4:'/',5:'+',6:'-'}
    
    ####################################
    #   Internal Functions
    ####################################

    def inventory(e,ops):
        # create dict, populate from eq, and delete blank entries
        ops = ops()
        for i in eq:
            ops[i] = findAll(i,eq)
        ops = dict([[k,v] for k,v in ops.items() if v])        
        return ops

    def clean(eq):
        # remove spaces, break into sides of equation, inventory operators in each side
        #eq.c = eq.c.replace(' ','')
        # break into sides of the equation
        equalsPos = eq.c.find('=')
        if equalsPos < 0 or equalsPos == len(eq) - 1:
            eq.R = eq.c
            eq.L = 'x'
        elif equalsPos == 0:
            eq.R = 'x'
            eq.L = eq.c[1:]
        else:
            eq.R = eq.c[:equalsPos]
            eq.L = eq.c[equalsPos+1:]
        return eq        

    ####################################
    #   Begin Program body
    ####################################

    eq = equation()
    eq.c = equation
    eq.t = solve_for
    clean(eq)
    
    print(eq)

    # to find all numbers, integer & decimal
    numbers = re.findall(r'[\d\.\d]+',eq)
    # maps operators and deletes blank entries from the dict
    ops = dict([[k,v] for k,v in ops.items() if v])
    # find position of first open/close (o/c) pair:
    c = ops[')'][0]
    o = max([i for i in ops['('] if i < ops[')'][c]])

# Internal Functions
def getAnswer(get,answer):
    # no docstring, internal library function
    # get request type
    if get == '1' or get[0].lower() == 'p':
        get = 'p(x)'
    elif get == '2' or get[0].lower() == 'm':
        get = 'mean'
    elif get == '3' or get[0].lower() == 'v':
        get = 'var'
    answer = answer[get]
    return answer

def findAll(target,area):
    #finds all instances of target in list 'area' and returns a list of positions of targets
    target = str(target)
    i = 0
    position = []
    for j in area:
        if str(j) == target:
            position.append(i)
        i+=1
    return position
