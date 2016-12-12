'''
Parse input and run appropriate code.
Don't use this file for the actual work; only minimal code should be here.
We just parse input and call methods from other modules.
'''


# do NOT import ways. This should be done from other files
# simply import your modules and call the appropriate functions


from algorithms import a_star_time_with_information, ucs_time_with_information


def uc_time(source, target):
    return ucs_time_with_information(source, target)[0]

    
def a_star_time(source, target):
    return a_star_time_with_information(source, target)[0]
    

def dispatch(argv):
    from sys import argv
    source, target = int(argv[2]), int(argv[3])
    if argv[1] == 'uc_time':
        path = uc_time(source, target)
    elif argv[1] == 'a_star_time':
        path = a_star_time(source, target)
    print(' '.join(str(j) for j in path))


if __name__ == '__main__':
    from sys import argv
    dispatch(argv)
