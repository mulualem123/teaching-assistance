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

#Not Being used#my_map = geez_alpha_database()
my_map = {'ሀ': 'ha', 'ለ': 'le', 'ሐ': 'he', 'መ': 'me', 'ሠ': 'se', 'ረ': 're', 'ሰ': 'se', 'ሸ': 'Se', 'ቀ': 'qe', 'ቈ': 'que', 'ቐ': 'qe', 'ቘ': 'Que', 'በ': 'be', 'ቨ': 've', 'ተ': 'te', 'ቸ': 'ce', 'ኀ': 'he', 'ኈ': 'hue', 'ነ': 'ne', 'ኘ': 'nhe', 'አ': 'a', 'ከ': 'ke', 'ኰ': 'kue', 'ኸ': 'Ke', 'ዀ': 'kue', 'ወ': 'we', 'ዐ': 'Oe', 'ዘ': 'ze', 'ዠ': 'Ze', 'የ': 'ye', 'ደ': 'de', 'ጀ': 'je', 'ገ': 'ge', 'ጐ': 'gue', 'ጠ': 'te', 'ጨ': 'ce', 'ጰ': 'pe', 'ጸ': 'tse', 'ፀ': 'tse', 'ፈ': 'fe', 'ፐ': 'pe', '።': '.', '፩': 1, 8.0: 8.0, '፲': 10, '፹': 80, 'ጘ': 'ge', 'ⶓ': 'gue', 'ሇ': 'hoa', 'ኯ': 'koa', 'ዸ': 'de', 
'ሁ': 'hu', 'ሉ': 'lu', 'ሑ': 'hu', 'ሙ': 'mu', 'ሡ': 'su', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'Su', 'ቁ': 'qu', 'ቊ': 'qui', 'ቑ': 'qu', 'ቚ': 'qui', 'ቡ': 'bu', 'ቩ': 'vu', 'ቱ': 'tu', 'ቹ': 'cu', 'ኁ': 'ḥu', 'ኊ': 'hui', 'ኑ': 'nu', 'ኙ': 'nhu', 'ኡ': 'u', 'ኩ': 'ku', 'ኲ': 'kui', 'ኹ': 'ku', 'ዂ': 'kui', 'ዉ': 'wu', 'ዑ': 'Ou', 'ዙ': 'zu', 'ዡ': 'zu', 'ዩ': 'yu', 'ዱ': 'du', 'ጁ': 'ju', 'ጉ': 'gu', 'ጒ': 'gui', 'ጡ': 'tu', 'ጩ': 'cu', 'ጱ': 'pu', 'ጹ': 'tsu', 'ፁ': 'tsu', 'ፉ': 'fu', 'ፑ': 'pu', '፡': ';', '፪': 2, 9.0: 9.0, '፳': 20, '፺': 90, 'ጙ': 'gu', 'ⶔ': 'gui', 'ሏ': 'lua', 'ዃ': 'Kua', 'ዹ': 'du', 
'ሂ': 'hi', 'ሊ': 'li', 'ሒ': 'hi', 'ሚ': 'mi', 'ሢ': 'si', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'Si', 'ቂ': 'qi', 'ቋ': 'qua', 'ቒ': 'Qi', 'ቛ': 'Qua', 'ቢ': 'bi', 'ቪ': 'vi', 'ቲ': 'ti', 'ቺ': 'ci', 'ኂ': 'hi', 'ኋ': 'hua', 'ኒ': 'ni', 'ኚ': 'nhi', 'ኢ': 'i', 'ኪ': 'ki', 'ኳ': 'kua', 'ኺ': 'ki', 'ዊ': 'wi', 'ዒ': 'Oi', 'ዚ': 'zi', 'ዢ': 'Zi', 'ዪ': 'yi', 'ዲ': 'di', 'ጂ': 'ji', 'ጊ': 'gi', 'ጓ': 'gua', 'ጢ': 'ti', 'ጪ': 'Ci', 'ጲ': 'Pi', 'ጺ': 'tsi', 'ፂ': 'tsi', 'ፊ': 'fi', 'ፒ': 'pi', '፣': ',', '፫': 3, '፴': 30, '" "': '" "', 'ጚ': 'gi', 'ጟ': 'gua', 'ሗ': 'hua', 'ዏ': 'woa', 'ዺ': 'd2i', 
'ሃ': 'ha', 'ላ': 'la', 'ሓ': 'ha', 'ማ': 'ma', 'ሣ': 'sa', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'Sa', 'ቃ': 'qa', 'ቌ': 'quie', 'ቓ': 'Qa', 'ቜ': 'Quie', 'ባ': 'ba', 'ቫ': 'va', 'ታ': 'ta', 'ቻ': 'ca', 'ኃ': 'ha', 'ኌ': 'huie', 'ና': 'na', 'ኛ': 'nha', 'ኣ': 'a', 'ካ': 'ka', 'ኴ': 'kuie', 'ኻ': 'Ka', 'ዄ': 'kuie', 'ዋ': 'wa', 'ዓ': 'Oa', 'ዛ': 'za', 'ዣ': 'zha', 'ያ': 'ya', 'ዳ': 'da', 'ጃ': 'ja', 'ጋ': 'ga', 'ጔ': 'guie', 'ጣ': 'ta', 'ጫ': 'Ca', 'ጳ': 'Pa', 'ጻ': 'tsa', 'ፃ': 'tsa', 'ፋ': 'fa', 'ፓ': 'pa', '፥': ':', '፬': 4, '፵': 40, " '": " '", 'ጛ': 'ga', 'ⶕ': 'guie', 'ሟ': 'mua', 'ዟ': 'zua', 'ዻ': 'd2a', 
'ሄ': 'hie', 'ሌ': 'lie', 'ሔ': 'hie', 'ሜ': 'mie', 'ሤ': 'sie', 'ሬ': 'rie', 'ሴ': 'sie', 'ሼ': 'Sie', 'ቄ': 'qie', 'ቍ': 'qW', 'ቔ': 'Qie', 'ቝ': 'QW', 'ቤ': 'bie', 'ቬ': 'vie', 'ቴ': 'tie', 'ቼ': 'cie', 'ኄ': 'hie', 'ኍ': 'hw', 'ኔ': 'nie', 'ኜ': 'nhie', 'ኤ': 'ie', 'ኬ': 'kie', 'ኵ': 'kw', 'ኼ': 'kie', 'ዅ': 'kw', 'ዌ': 'wie', 'ዔ': 'oie', 'ዜ': 'zie', 'ዤ': 'zhie', 'ዬ': 'yie', 'ዴ': 'de', 'ጄ': 'jie', 'ጌ': 'gie', 'ጕ': 'gw', 'ጤ': 'tie', 'ጬ': 'cie', 'ጴ': 'pie', 'ጼ': 'tsie', 'ፄ': 'tsie', 'ፌ': 'fie', 'ፔ': 'pie', '፤': '::', '፭': 5, '፶': 50, '""': '""', 'ጜ': 'gie', 'ⶖ': 'gw', 'ሧ': 'sua', 'ዧ': 'zua', 'ዼ': 'de', 
'ህ': 'h', 'ል': 'l', 'ሕ': 'h', 'ም': 'm', 'ሥ': 's', 'ር': 'r', 'ስ': 's', 'ሽ': 'S', 'ቅ': 'q', 'ቕ': 'q', 'ብ': 'b', 'ቭ': 'v', 'ት': 't', 'ች': 'c', 'ኅ': 'h', 'ን': 'n', 'ኝ': 'nh', 'እ': 'e', 'ክ': 'k', 'ኽ': 'kh', 'ው': 'w', 'ዕ': 'O', 'ዝ': 'z', 'ዥ': 'zh', 'ይ': 'y', 'ድ': 'd', 'ጅ': 'j', 'ግ': 'g', 'ጥ': 't', 'ጭ': 'c', 'ጵ': 'p', 'ጽ': 'ts', 'ፅ': 'ts', 'ፍ': 'f', 'ፕ': 'p', '፦': ';-', '፮': 6, '፷': 60, 'ጝ': 'G', 'ሯ': 'rua', 'ዯ': 'yoa', 'ዽ': 'd', 
'ሆ': 'ho', 'ሎ': 'lo', 'ሖ': 'ho', 'ሞ': 'mo', 'ሦ': 'so', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'So', 'ቆ': 'qo', 'ቖ': 'qo', 'ቦ': 'bo', 'ቮ': 'vo', 'ቶ': 'to', 'ቾ': 'co', 'ኆ': 'ho', 'ኖ': 'no', 'ኞ': 'nho', 'ኦ': 'o', 'ኮ': 'ko', 'ኾ': 'ko', 'ዎ': 'wo', 'ዖ': 'Oo', 'ዞ': 'zo', 'ዦ': 'Zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 'ጦ': 'to', 'ጮ': 'Co', 'ጶ': 'po', 'ጾ': 'tso', 'ፆ': 'tso', 'ፎ': 'fo', 'ፖ': 'po', '.': '..', '፯': 7, '፸': 70, 'ጞ': 'go', 'ሷ': 'sua', 'ዷ': 'dua', 'ዾ': 'd2o'}
print(my_map)
# my_map = {
#     # Basic consonants (1st order ä)
#     'ሀ': 'hä', 'ለ': 'lä', 'መ': 'mä', 'ሠ': 'sä', 'ረ': 'rä', 'ሰ': 'sä', 'ሸ': 'ša',
#     'ቀ': 'qä', 'በ': 'bä', 'ተ': 'tä', 'ቸ': 'čä', 'ኀ': 'ḥä', 'ነ': 'nä', 'አ': 'ʾä',  
#     'ከ': 'kä', 'ወ': 'wä', 'ዘ': 'zä', 'የ': 'yä', 'ደ': 'dä', 'ጀ': 'ǧä', 'ገ': 'gä',
#     'ጠ': 'ṭä', 'ጨ': 'č̣ä', 'ጰ': 'p̣ä', 'ጸ': 'ṣä', 'ፀ': 'ṣ́ä', 'ፈ': 'fä', 'ፐ': 'pä',

#     # Second order (u)
#     'ሁ': 'hu', 'ሉ': 'lu', 'ሙ': 'mu', 'ሡ': 'su', 'ሩ': 'ru', 'ሱ': 'su', 'ሹ': 'šu',
#     'ቁ': 'qu', 'ቡ': 'bu', 'ቱ': 'tu', 'ቹ': 'ču', 'ኁ': 'ḥu', 'ኑ': 'nu', 'ኡ': 'ʾu', 
#     'ኩ': 'ku', 'ዉ': 'wu', 'ዙ': 'zu', 'ዩ': 'yu', 'ዱ': 'du','ጁ': 'ju', 'ጉ': 'gu',
#     'ጡ': 'ṭu', 'ጩ': 'č̣u', 'ጱ': 'p̣u', 'ጹ': 'ṣu', 'ፁ': 'ṣ́u', 'ፉ': 'fu', 'ፑ': 'pu',

#     # Third order (i)
#     'ሂ': 'hi', 'ሊ': 'li', 'ሚ': 'mi', 'ሢ': 'si', 'ሪ': 'ri', 'ሲ': 'si', 'ሺ': 'ši',
#     'ቂ': 'qi', 'ቢ': 'bi', 'ቲ': 'ti', 'ቺ': 'či', 'ኂ': 'ḥi', 'ኒ': 'ni', 'ኢ': 'ʾi', 
#     'ኪ': 'ki', 'ዊ': 'wi', 'ዚ': 'zi', 'ዪ': 'yi', 'ዲ': 'di','ጂ': 'ji', 'ጊ': 'gi', 
#     'ጢ': 'ṭi', 'ጪ': 'č̣i', 'ጲ': 'p̣i', 'ጺ': 'ṣi','ፂ': 'ṣi', 'ፊ': 'fi', 'ፒ': 'pi',

#     # Fourth order (a)
#     'ሃ': 'ha', 'ላ': 'la', 'ማ': 'ma', 'ሣ': 's2a', 'ራ': 'ra', 'ሳ': 'sa', 'ሻ': 'ša',
#     'ቃ': 'qa', 'ባ': 'ba', 'ታ': 'ta', 'ቻ': 'ča', 'ኃ': 'ḥa', 'ና': 'na', 'ኣ': 'ʾa', 
#     'ካ': 'ka', 'ዋ': 'wa', 'ዛ': 'za', 'ያ': 'ya', 'ዳ': 'da','ጃ': 'ja', 'ጋ': 'ga', 
#     'ጣ': 'ṭa', 'ጫ': 'č̣a', 'ጳ': 'p̣a', 'ጻ': 'ṣa', 'ፃ': 'ṣa', 'ፋ': 'fa', 'ፓ': 'pa',

#     # Fifth order (e)
#     'ሄ': 'he', 'ሌ': 'le', 'ሜ': 'me', 'ሤ': 'se', 'ሬ': 're', 'ሴ': 'se', 'ሼ': 'še',
#     'ቄ': 'qe', 'ቤ': 'be', 'ቴ': 'te', 'ቼ': 'če', 'ኄ': 'ḥe', 'ኔ': 'ne', 'ኤ': 'ʾe', 
#     'ኬ': 'ke', 'ዌ': 'we', 'ዜ': 'ze', 'ዬ': 'ye', 'ዴ': 'de','ጄ': 'jie', 'ጌ': 'ge', 
#     'ጤ': 'ṭe', 'ጬ': 'č̣e', 'ጴ': 'p̣e', 'ጼ': 'ṣe','ፄ': 'ṣe', 'ፌ': 'fe', 'ፔ': 'pe',

#     # Sixth order (ə)
#     'ህ': 'hə', 'ል': 'lə', 'ም': 'mə', 'ሥ': 'sə','ር': 'rə', 'ስ': 'sə', 'ሽ': 'šə',
#     'ቅ': 'qə', 'ብ': 'bə', 'ት': 'tə', 'ች': 'čə', 'ኅ': 'ḥə', 'ን': 'nə', 'እ': 'ʾə', 
#     'ክ': 'kə', 'ው': 'wə', 'ዝ': 'zə', 'ይ': 'yə', 'ድ': 'də','ጅ': 'jə','ግ': 'gə', 
#     'ጥ': 'ṭə', 'ጭ': 'č̣ə', 'ጵ': 'p̣ə', 'ጽ': 'ṣə', 'ፅ': 'ṣə', 'ፍ': 'fə', 'ፕ': 'pə',

#     # Seventh order (o)
#     'ሆ': 'ho', 'ሎ': 'lo', 'ሞ': 'mo', 'ሦ': 'so', 'ሮ': 'ro', 'ሶ': 'so', 'ሾ': 'šo',
#     'ቆ': 'qo', 'ቦ': 'bo', 'ቶ': 'to', 'ቾ': 'čo', 'ኆ': 'ḥo', 'ኖ': 'no', 'ኦ': 'ʾo', 
#     'ኮ': 'ko', 'ዎ': 'wo', 'ዞ': 'zo', 'ዮ': 'yo', 'ዶ': 'do', 'ጆ': 'jo', 'ጎ': 'go', 
#     'ጦ': 'ṭo', 'ጮ': 'č̣o', 'ጶ': 'p̣o', 'ጾ': 'ṣo', 'ፆ': 'x2o', 'ፎ': 'fo', 'ፖ': 'po',

#     # Numerals
#     '፩': 1, '፪': 2, '፫': 3, '፬': 4, '፭': 5, '፮': 6, '፯': 7, '፰': 8, '፱': 9, '፲': 10, '፳': 20, '፴': 30, '፵': 40, '፶': 50, '፷': 60, '፸': 70

# }

#A function to accept a map and geez text then change it to eglish alphabate. 
def geez_to_latin(text: str) -> str:
    """Transliterate Ge'ez/Amharic script to a Latin (phonetic) approximation.

    This is a single implementation (no nested functions) that:
    - handles None/empty inputs safely,
    - maps punctuation/numerals explicitly,
    - decomposes Unicode Ethiopic syllables into base consonant + vowel order,
    - falls back to a module-level `my_map` for exceptional single-char mappings,
    - returns a string (or the original input for non-string inputs).
    """
    # Defensive checks
    if text is None:
        return text
    if not isinstance(text, str):
        return text
    if text == "":
        return text

    # explicit minor mappings (punctuation, numerals, spacing)
    explicit = {
        '\u1361': '.',  # Ethiopic wordspace (rare)
        '።': '.', '፣': ',', '፥': ':', '፦': ';', '፨': '?', '፡': ' ',
        '፩': '1', '፪': '2', '፫': '3', '፬': '4', '፭': '5', '፮': '6', '፯': '7', '፰': '8', '፱': '9', '፲': '10'
    }

    # vowel forms order for Ethiopic syllabary (approximate phonetic values)
    # Unicode syllables are organized in groups of 8 forms (orders 0..7)
    order_vowel = ['ä', 'u', 'i', 'a', 'e', 'ə', 'o', 'wa']


    # base consonant transliteration for the first form of each consonant (compact map)
    # base_map = {
    #     'ሀ': 'h', 'ለ': 'l', 'ሐ': 'ḥ', 'መ': 'm', 'ሠ': 'ś', 'ረ': 'r', 'ሰ': 's', 'ሸ': 'sh',
    #     'ቀ': 'q', 'ቐ': "q'", 'በ': 'b', 'ተ': 't', 'ቸ': 'č', 'ኀ': 'h', 'ነ': 'n', 'ኘ': 'ñ',
    #     'አ': "ʾ", 'ከ': 'k', 'ኸ': 'kh', 'ዀ': 'k', 'ወ': 'w', 'ዐ': "ʿ", 'ዘ': 'z', 'ዠ': 'ž',
    #     'የ': 'y', 'ደ': 'd', 'ጀ': 'j', 'ገ': 'g', 'ጠ': 'ṭ', 'ጨ': 'č', 'ጰ': 'p', 'ጸ': 'ṣ',
    #     'ፈ': 'f', 'ፐ': 'p'
    # }jdflkjfkldf

    base_map = {
        'ሀ': 'h',   # hä
        'ለ': 'l',   # lä
        'ሐ': 'ḥ',   # ḥä
        'መ': 'm',   # mä
        'ሠ': 'ś',   # śä
        'ረ': 'r',   # rä
        'ሰ': 's',   # sä
        'ሸ': 'š',   # šä

        'ቀ': 'q',   # qä
        'ቐ': "qʼ",  # ejective q
        'በ': 'b',   # bä
        'ተ': 't',   # tä
        'ቸ': 'č',   # čä

        'ኀ': 'ḥ',   # ḥä
        'ነ': 'n',   # nä
        'ኘ': 'ñ',   # ñä
        'አ': "ʾ",   # glottal stop ä
        'ከ': 'k',   # kä
        'ኸ': 'kh',  # khä
        'ዀ': 'kʷ',  # labialized k

        'ወ': 'w',   # wä
        'ዐ': "ʿ",   # pharyngeal ä
        'ዘ': 'z',   # zä
        'ዠ': 'ž',   # žä
        'የ': 'y',   # yä
        'ደ': 'd',   # dä
        'ጀ': 'j',   # jä
        'ገ': 'g',   # gä

        'ጠ': 'ṭ',   # ṭä
        'ጨ': 'č̣',  # emphatic č
        'ጰ': 'pʼ',  # ejective p
        'ጸ': 'ṣ',   # ṣä
        'ፈ': 'f',   # fä
        'ፐ': 'p'    # pä
    }

    

    out = []
    for ch in text:
        # explicit map
        if ch in explicit:
            out.append(explicit[ch])
            continue

        cp = ord(ch)
        # Ethiopic syllables block U+1200..U+137F
        if 0x1200 <= cp <= 0x137F:
            index = cp - 0x1200
            order = index % 8
            base_cp = cp - order
            base_char = chr(base_cp)
            base = base_map.get(base_char)
            vowel = order_vowel[order]
            if base is None:
                # unknown base: fallback to raw character
                out.append(ch)
            else:
                # assemble transliteration, handle glottal/semivowel bases
                if base in ("ʾ", "ʿ"):
                    out.append(vowel if vowel != 'ə' else 'a')
                else:
                    out.append(base + vowel)
            continue

        # try simple direct mapping from any remaining hardcoded transliterations in module (if available)
        try:
            if 'my_map' in globals() and isinstance(my_map, dict) and ch in my_map:
                out.append(str(my_map[ch]))
                continue
        except Exception:
            pass

        # default: passthrough
        out.append(ch)

    return ''.join(out)
