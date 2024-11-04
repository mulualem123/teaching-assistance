##NOT Being USED #A function to load geez alphabate to latin alphabate transition and put it in Map
def geez_alpha_database():
    #file_loc = r"flask_package\\doc\\GeezEnglishAlphabetSingle.xlsx" # change this to your file location
    file_loc = r"C:\\Users\\selon\\Documents\\Projects\\VSprojects\\python\\flask\teaching-assistance\\flask_package\\doc\\GeezEnglishAlphabetSingle.xlsx"
    df = pd.read_excel(file_loc) # read the excel file into a dataframe
    map = {} # create an empty map: key is Geez, value is English
    for index, row in df.iterrows(): # iterate over the rows
        key = row.iloc[0] # get the first element of the row as the key
        value = row.iloc[1] # get the second element of the row as the value
        map[key] = value # store the key-value pair in the map
        #print(map)
        for i in range(2, len(row), 2): # iterate over the rest of the elements with a step of 2
            key = row.iloc[i] # get the next element of the row as the key
            value = row.iloc[i+1] # get the next element of the row as the value
            map[key] = value # store the key-value pair in the map
    return(map)

##Not Being used#my_map = geez_alpha_database()
my_map = {'ሀ': 'he', 'ለ': 'le', 'ሐ': 'He', 'መ': 'me', 'ሠ': 'se', 'ረ': 're', 'ሰ': 'se', 'ሸ': 'Se', 'ቀ': 'qe', 'ቈ': 'que', 'ቐ': 'Qe', 'ቘ': 'Que', 'በ': 'be', 'ቨ': 've', 'ተ': 'te', 'ቸ': 'ce', 'ኀ': 'h2e', 'ኈ': 'hue', 'ነ': 'ne', 'ኘ': 'Ne', 'አ': 'e', 'ከ': 'ke', 'ኰ': 'kue', 'ኸ': 'Ke', 'ዀ': 'Kue', 'ወ': 'we', 'ዐ': 'Oe', 'ዘ': 'ze', 'ዠ': 'Ze', 'የ': 'ye', 'ደ': 'de', 'ጀ': 'je', 'ገ': 'ge', 'ጐ': 'gue', 'ጠ': 'Te', 'ጨ': 'Ce', 'ጰ': 'Pe', 'ጸ': 'xe', 'ፀ': 'xe', 'ፈ': 'fe', 'ፐ': 'pe', '።': '.', '፩': 1, 8.0: 8.0, '፲': 10, '፹': 80, 'ጘ': 'Ge', 'ⶓ': 'Gue', 'ሇ': 'hoa', 'ኯ': 'koa', 'ዸ': 'd2e', 'ሁ': 'hu', 'ሉ': 'lu', 'ሑ': 'Hu', 'ሙ': 'mu', 'ሡ': 's2u', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'Su', 'ቁ': 'qu', 'ቊ': 'qui', 'ቑ': 'Qu', 'ቚ': 'Qui', 'ቡ': 'bu', 'ቩ': 'vu', 'ቱ': 'tu', 'ቹ': 'cu', 'ኁ': 'h2u', 'ኊ': 'hui', 'ኑ': 'nu', 'ኙ': 'Nu', 'ኡ': 'u', 'ኩ': 'ku', 'ኲ': 'kui', 'ኹ': 'Ku', 'ዂ': 'Kui', 'ዉ': 'wu', 'ዑ': 'Ou', 'ዙ': 'zu', 'ዡ': 'Zu', 'ዩ': 'yu', 'ዱ': 'du', 'ጁ': 'ju', 'ጉ': 'gu', 'ጒ': 'gui', 'ጡ': 'Tu', 'ጩ': 'Cu', 'ጱ': 'Pu', 'ጹ': 'xu', 'ፁ': 'x2u', 'ፉ': 'fu', 'ፑ': 'pu', '፡': ';', '፪': 2, 9.0: 9.0, '፳': 20, '፺': 90, 'ጙ': 'Gu', 'ⶔ': 'Gui', 'ሏ': 'lua', 'ዃ': 'Kua', 'ዹ': 'd2u', 'ሂ': 'hi', 'ሊ': 'li', 'ሒ': 'Hi', 'ሚ': 'mi', 'ሢ': 's2i', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'Si', 'ቂ': 'qi', 'ቋ': 'qua', 'ቒ': 'Qi', 'ቛ': 'Qua', 'ቢ': 'bi', 'ቪ': 'vi', 'ቲ': 'ti', 'ቺ': 'ci', 'ኂ': 'h2i', 'ኋ': 'hua', 'ኒ': 'ni', 'ኚ': 'Ni', 'ኢ': 'i', 'ኪ': 'ki', 'ኳ': 'kua', 'ኺ': 'Ki', 'ዊ': 'wi', 'ዒ': 'Oi', 'ዚ': 'zi', 'ዢ': 'Zi', 'ዪ': 'yi', 'ዲ': 'di', 'ጂ': 'ji', 'ጊ': 'gi', 'ጓ': 'gua', 'ጢ': 'Ti', 'ጪ': 'Ci', 'ጲ': 'Pi', 'ጺ': 'xi', 'ፂ': 'x2i', 'ፊ': 'fi', 'ፒ': 'pi', '፣': ',', '፫': 3, '፴': 30, '" "': '" "', 'ጚ': 'Gi', 'ጟ': 'Gua', 'ሗ': 'Hua', 'ዏ': 'woa', 'ዺ': 'd2i', 'ሃ': 'ha', 'ላ': 'la', 'ሓ': 'Ha', 'ማ': 'ma', 'ሣ': 's2a', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'Sa', 'ቃ': 'qa', 'ቌ': 'quie', 'ቓ': 'Qa', 'ቜ': 'Quie', 'ባ': 'ba', 'ቫ': 'va', 'ታ': 'ta', 'ቻ': 'ca', 'ኃ': 'h2a', 'ኌ': 'huie', 'ና': 'na', 'ኛ': 'Na', 'ኣ': 'a', 'ካ': 'ka', 'ኴ': 'kuie', 'ኻ': 'Ka', 'ዄ': 'Kuie', 'ዋ': 'wa', 'ዓ': 'Oa', 'ዛ': 'za', 'ዣ': 'Za', 'ያ': 'ya', 'ዳ': 'da', 'ጃ': 'ja', 'ጋ': 'ga', 'ጔ': 'guie', 'ጣ': 'Ta', 'ጫ': 'Ca', 'ጳ': 'Pa', 'ጻ': 'xa', 'ፃ': 'x2a', 'ፋ': 'fa', 'ፓ': 'pa', '፥': ':', '፬': 4, '፵': 40, " '": " '", 'ጛ': 'Ga', 'ⶕ': 'Guie', 'ሟ': 'mua', 'ዟ': 'zua', 'ዻ': 'd2a', 'ሄ': 'hie', 'ሌ': 'lie', 'ሔ': 'Hie', 'ሜ': 'mie', 'ሤ': 's2ie', 'ሬ': 'rie', 'ሴ': 'sie', 'ሼ': 'Sie', 'ቄ': 'qie', 'ቍ': 'qW', 'ቔ': 'Qie', 'ቝ': 'QW', 'ቤ': 'bie', 'ቬ': 'vie', 'ቴ': 'tie', 'ቼ': 'cie', 'ኄ': 'h2ie', 'ኍ': 'hW', 'ኔ': 'nie', 'ኜ': 'Nie', 'ኤ': 'ie', 'ኬ': 'kie', 'ኵ': 'kW', 'ኼ': 'Kie', 'ዅ': 'KW', 'ዌ': 'wie', 'ዔ': 'Oie', 'ዜ': 'zie', 'ዤ': 'Zie', 'ዬ': 'yie', 'ዴ': 'die', 'ጄ': 'jie', 'ጌ': 'gie', 'ጕ': 'gW', 'ጤ': 'Tie', 'ጬ': 'Cie', 'ጴ': 'Pie', 'ጼ': 'xie', 'ፄ': 'x2ie', 'ፌ': 'fie', 'ፔ': 'pie', '፤': '::', '፭': 5, '፶': 50, '""': '""', 'ጜ': 'Gie', 'ⶖ': 'GW', 'ሧ': 's2ua', 'ዧ': 'Zua', 'ዼ': 'd2ie', 'ህ': 'h', 'ል': 'l', 'ሕ': 'H', 'ም': 'm', 'ሥ': 's2', 'ር': 'r', 'ስ': 's', 'ሽ': 'S', 'ቅ': 'q', 'ቕ': 'Q', 'ብ': 'b', 'ቭ': 'v', 'ት': 't', 'ች': 'c', 'ኅ': 'h2', 'ን': 'n', 'ኝ': 'N', 'እ': 'A', 'ክ': 'k', 'ኽ': 'K', 'ው': 'w', 'ዕ': 'O', 'ዝ': 'z', 'ዥ': 'Z', 'ይ': 'y', 'ድ': 'd', 'ጅ': 'j', 'ግ': 'g', 'ጥ': 'T', 'ጭ': 'C', 'ጵ': 'P', 'ጽ': 'x', 'ፅ': 'x2', 'ፍ': 'f', 'ፕ': 'p', '፦': ';-', '፮': 6, '፷': 60, 'ጝ': 'G', 'ሯ': 'rua', 'ዯ': 'yoa', 'ዽ': 'd2', 'ሆ': 'ho', 'ሎ': 'lo', 'ሖ': 'Ho', 'ሞ': 'mo', 'ሦ': 's2o', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'So', 'ቆ': 'qo', 'ቖ': 'Qo', 'ቦ': 'bo', 'ቮ': 'vo', 'ቶ': 'to', 'ቾ': 'co', 'ኆ': 'h2o', 'ኖ': 'no', 'ኞ': 'No', 'ኦ': 'o', 'ኮ': 'ko', 'ኾ': 'Ko', 'ዎ': 'wo', 'ዖ': 'Oo', 'ዞ': 'zo', 'ዦ': 'Zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 'ጦ': 'To', 'ጮ': 'Co', 'ጶ': 'Po', 'ጾ': 'xo', 'ፆ': 'x2o', 'ፎ': 'fo', 'ፖ': 'po', '.': '..', '፯': 7, '፸': 70, 'ጞ': 'Go', 'ሷ': 'sua', 'ዷ': 'dua', 'ዾ': 'd2o'}
#print(my_map)

#A function to accept a map and geez text then change it to eglish alphabate. 
def geez_to_latin(text):
    print ("geez_to_latin method called with inpute: " + str(text))
    my_map = {'ሀ': 'he', 'ለ': 'le', 'ሐ': 'he', 'መ': 'me', 'ሠ': 'se', 'ረ': 're', 'ሰ': 'se', 'ሸ': 'Se', 'ቀ': 'qe', 'ቈ': 'que', 'ቐ': 'Qe', 'ቘ': 'que', 'በ': 'be', 'ቨ': 've', 'ተ': 'te', 'ቸ': 'ce', 'ኀ': 'he', 'ኈ': 'hue', 'ነ': 'ne', 'ኘ': 'ne', 'አ': 'e', 'ከ': 'ke', 'ኰ': 'kue', 'ኸ': 'ke', 'ዀ': 'kue', 'ወ': 'we', 'ዐ': 'oe', 'ዘ': 'ze', 'ዠ': 'ze', 'የ': 'ye', 'ደ': 'de', 'ጀ': 'je', 'ገ': 'ge', 'ጐ': 'gue', 'ጠ': 'te', 'ጨ': 'ce', 'ጰ': 'pe', 'ጸ': 'xe', 'ፀ': 'xe', 'ፈ': 'fe', 'ፐ': 'pe', '።': '.', '፩': 1, 8.0: 8.0, '፲': 10, '፹': 80, 'ጘ': 'ge', 'ⶓ': 'gue', 'ሇ': 'hoa', 'ኯ': 'koa', 'ዸ': 'de', 'ሁ': 'hu', 'ሉ': 'lu', 'ሑ': 'hu', 'ሙ': 'mu', 'ሡ': 'su', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'su', 'ቁ': 'qu', 'ቊ': 'qui', 'ቑ': 'qu', 'ቚ': 'qui', 'ቡ': 'bu', 'ቩ': 'vu', 'ቱ': 'tu', 'ቹ': 'cu', 'ኁ': 'hu', 'ኊ': 'hui', 'ኑ': 'nu', 'ኙ': 'nu', 'ኡ': 'u', 'ኩ': 'ku', 'ኲ': 'kui', 'ኹ': 'ku', 'ዂ': 'kui', 'ዉ': 'wu', 'ዑ': 'ou', 'ዙ': 'zu', 'ዡ': 'zu', 'ዩ': 'yu', 'ዱ': 'du', 'ጁ': 'ju', 'ጉ': 'gu', 'ጒ': 'gui', 'ጡ': 'tu', 'ጩ': 'cu', 'ጱ': 'pu', 'ጹ': 'xu', 'ፁ': 'xu', 'ፉ': 'fu', 'ፑ': 'pu', '፡': ';', '፪': 2, 9.0: 9.0, '፳': 20, '፺': 90, 'ጙ': 'gu', 'ⶔ': 'gui', 'ሏ': 'lua', 'ዃ': 'kua', 'ዹ': 'du', 'ሂ': 'hi', 'ሊ': 'li', 'ሒ': 'hi', 'ሚ': 'mi', 'ሢ': 'si', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'si', 'ቂ': 'qi', 'ቋ': 'qua', 'ቒ': 'qi', 'ቛ': 'qua', 'ቢ': 'bi', 'ቪ': 'vi', 'ቲ': 'ti', 'ቺ': 'ci', 'ኂ': 'hi', 'ኋ': 'hua', 'ኒ': 'ni', 'ኚ': 'ni', 'ኢ': 'i', 'ኪ': 'ki', 'ኳ': 'kua', 'ኺ': 'Ki', 'ዊ': 'wi', 'ዒ': 'Oi', 'ዚ': 'zi', 'ዢ': 'Zi', 'ዪ': 'yi', 'ዲ': 'di', 'ጂ': 'ji', 'ጊ': 'gi', 'ጓ': 'gua', 'ጢ': 'ti', 'ጪ': 'ci', 'ጲ': 'pi', 'ጺ': 'xi', 'ፂ': 'x2i', 'ፊ': 'fi', 'ፒ': 'pi', '፣': ',', '፫': 3, '፴': 30, '" "': '" "', 'ጚ': 'gi', 'ጟ': 'gua', 'ሗ': 'hua', 'ዏ': 'woa', 'ዺ': 'di', 'ሃ': 'ha', 'ላ': 'la', 'ሓ': 'ha', 'ማ': 'ma', 'ሣ': 'sa', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'sa', 'ቃ': 'qa', 'ቌ': 'quie', 'ቓ': 'qa', 'ቜ': 'quie', 'ባ': 'ba', 'ቫ': 'va', 'ታ': 'ta', 'ቻ': 'ca', 'ኃ': 'ha', 'ኌ': 'huie', 'ና': 'na', 'ኛ': 'na', 'ኣ': 'a', 'ካ': 'ka', 'ኴ': 'kuie', 'ኻ': 'ka', 'ዄ': 'kuie', 'ዋ': 'wa', 'ዓ': 'oa', 'ዛ': 'za', 'ዣ': 'za', 'ያ': 'ya', 'ዳ': 'da', 'ጃ': 'ja', 'ጋ': 'ga', 'ጔ': 'guie', 'ጣ': 'ta', 'ጫ': 'ca', 'ጳ': 'pa', 'ጻ': 'xa', 'ፃ': 'xa', 'ፋ': 'fa', 'ፓ': 'pa', '፥': ':', '፬': 4, '፵': 40, " '": " '", 'ጛ': 'ga', 'ⶕ': 'guie', 'ሟ': 'mua', 'ዟ': 'zua', 'ዻ': 'da', 'ሄ': 'hie', 'ሌ': 'lie', 'ሔ': 'hie', 'ሜ': 'mie', 'ሤ': 'sie', 'ሬ': 'rie', 'ሴ': 'sie', 'ሼ': 'sie', 'ቄ': 'qie', 'ቍ': 'qw', 'ቔ': 'qie', 'ቝ': 'qw', 'ቤ': 'bie', 'ቬ': 'vie', 'ቴ': 'tie', 'ቼ': 'cie', 'ኄ': 'hie', 'ኍ': 'hw', 'ኔ': 'nie', 'ኜ': 'nie', 'ኤ': 'ie', 'ኬ': 'kie', 'ኵ': 'kw', 'ኼ': 'kie', 'ዅ': 'kw', 'ዌ': 'wie', 'ዔ': 'oie', 'ዜ': 'zie', 'ዤ': 'zie', 'ዬ': 'yie', 'ዴ': 'die', 'ጄ': 'jie', 'ጌ': 'gie', 'ጕ': 'gw', 'ጤ': 'tie', 'ጬ': 'Cie', 'ጴ': 'pie', 'ጼ': 'xie', 'ፄ': 'xie', 'ፌ': 'fie', 'ፔ': 'pie', '፤': '::', '፭': 5, '፶': 50, '""': '""', 'ጜ': 'gie', 'ⶖ': 'gw', 'ሧ': 'sua', 'ዧ': 'zua', 'ዼ': 'die', 'ህ': 'h', 'ል': 'l', 'ሕ': 'h', 'ም': 'm', 'ሥ': 's', 'ር': 'r', 'ስ': 's', 'ሽ': 's', 'ቅ': 'q', 'ቕ': 'Q', 'ብ': 'b', 'ቭ': 'v', 'ት': 't', 'ች': 'c', 'ኅ': 'h2', 'ን': 'n', 'ኝ': 'N', 'እ': 'A', 'ክ': 'k', 'ኽ': 'K', 'ው': 'w', 'ዕ': 'O', 'ዝ': 'z', 'ዥ': 'Z', 'ይ': 'y', 'ድ': 'd', 'ጅ': 'j', 'ግ': 'g', 'ጥ': 'T', 'ጭ': 'C', 'ጵ': 'P', 'ጽ': 'x', 'ፅ': 'x2', 'ፍ': 'f', 'ፕ': 'p', '፦': ';-', '፮': 6, '፷': 60, 'ጝ': 'G', 'ሯ': 'rua', 'ዯ': 'yoa', 'ዽ': 'd2', 'ሆ': 'ho', 'ሎ': 'lo', 'ሖ': 'Ho', 'ሞ': 'mo', 'ሦ': 's2o', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'So', 'ቆ': 'qo', 'ቖ': 'Qo', 'ቦ': 'bo', 'ቮ': 'vo', 'ቶ': 'to', 'ቾ': 'co', 'ኆ': 'h2o', 'ኖ': 'no', 'ኞ': 'No', 'ኦ': 'o', 'ኮ': 'ko', 'ኾ': 'Ko', 'ዎ': 'wo', 'ዖ': 'Oo', 'ዞ': 'zo', 'ዦ': 'Zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 'ጦ': 'To', 'ጮ': 'Co', 'ጶ': 'Po', 'ጾ': 'xo', 'ፆ': 'x2o', 'ፎ': 'fo', 'ፖ': 'po', '.': '..', '፯': 7, '፸': 70, 'ጞ': 'Go', 'ሷ': 'sua', 'ዷ': 'dua', 'ዾ': 'do'}
    text=text
    eng_txt=""
    if(text==None or text == ""):
        return text
    else:
        for char in text:
            if char in my_map or char == '':
                #print (f"The value '{my_map[char]}' is associated with the key '{char}'.")
                #eng_txt = eng_txt + my_map[char]
                eng_txt = "{}{}".format(eng_txt, my_map[char])
            else:
                eng_txt = eng_txt + char
        print (str(text) + " changed to " + str(eng_txt))
        return eng_txt
    
#A function to accept a map and geez text then change it to eglish alphabate. # May be Delete
#def geez_to_latin(map,text):
#    my_map = map
#    text=text
#    eng_txt=""
#    if(text==None or text == " "):
#        return text
#    else:
#        for char in text:
#            if char in my_map or char == '':
#                #print (f"The value '{my_map[char]}' is associated with the key '{char}'.")
#                #eng_txt = eng_txt + my_map[char]
#                eng_txt = "{}{}".format(eng_txt, my_map[char])
#            else:
#                eng_txt = eng_txt + char
#        return eng_txt
