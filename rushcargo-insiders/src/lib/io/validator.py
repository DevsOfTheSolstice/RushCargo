# String Input Validator
def checkString(input: str, isAlpha: bool = True, isDigit: bool = True, isSpecial: bool = False) -> bool:
    # Nothing to Check
    if isAlpha and isDigit and isSpecial:
      return True
    
    for i in input:
        # Check if the Given Character is an Alphabetical Character
        if isAlpha and i.isalpha():
            continue
        
        # Check if the Given Character is a Digit
        if isDigit and i.isdigit():
            continue
        
        if not isSpecial: 
          return False
            
    return True