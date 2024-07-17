from googletrans import Translator 

#check given text what language it is
def check_language_type(my_text):
    try:
        translator = Translator()
        result = translator.detect(my_text)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "No connection"
    else:
        translator = Translator()
        result = translator.detect(my_text)
        print(result.lang)
        return result.lang
        #result = translator.translate('እንዴት ነህ?', dest='en')
        #print(result.text)
 
#Translation from geez/tigrigna to english    
def translate_tig_eng(my_text):
    try:
        translator = Translator()
        result = translator.translate(my_text, dest='en')
    except Exception as e:
        print(f"An error occurred: {e}")
        return "No Connection"
    else:
        translator = Translator()
        result = translator.translate(my_text, dest='en')
        return (result.text)       