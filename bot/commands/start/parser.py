def parse_argument(args: list):
    function = str(args[0]).replace('/start', '').strip() # getting function

    available_function = ['game', 'gift', 'ref']

    if function not in available_function:
        return None, None
    
    return function, args[1]
