
from ethiopian_date import EthiopianDateConverter 


import datetime


# Instantiate the converter
converter = EthiopianDateConverter()

today = datetime.date.today()
year = today.year
month = today.month
day = today.day

ethiopian_date = converter.to_ethiopian(year, month, day)


# Testing the conversion of Gregorian Date to Ethiopian Date    
def test_gregorian_to_ethiopian():
    """Test if the function can convert a valid Gregorian date into an Ethiopian date"""
    assert converter.convertGregToEth("2018", "9","1")