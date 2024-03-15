from ethiopian_date import EthiopianDateConverter 




converter = EthiopianDateConverter()
today = converter.to_ethiopian_date(datetime.date.today())

# Testing the conversion of Gregorian Date to Ethiopian Date    
def test_gregorian_to_ethiopian():
    """Test if the function can convert a valid Gregorian date into an Ethiopian date"""
    assert converter.convertGregToEth("2018", "9","1")