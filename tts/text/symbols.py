"""
Defines the set of symbols used in text input to the model.
"""


def get_symbols_and_space_id(cleaner: str):
    match cleaner:
        case 'japanese_cleaners':
            _pad        = '_'
            _punctuation = ',.!?-'
            _letters = 'AEINOQUabdefghijkmnoprstuvwyzʃʧ↓↑ '
        case 'japanese_cleaners2':
            _pad        = '_'
            _punctuation = ',.!?-~…'
            _letters = 'AEINOQUabdefghijkmnoprstuvwyzʃʧʦ↓↑ '
        case 'korean_cleaners':
            _pad        = '_'
            _punctuation = ',.!?…~'
            _letters = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄲㄸㅃㅆㅉㅏㅓㅗㅜㅡㅣㅐㅔ '
        case 'chinese_cleaners':
            _pad        = '_'
            _punctuation = '，。！？—…'
            _letters = 'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦㄧㄨㄩˉˊˇˋ˙ '
        case 'zh_ja_mixture_cleaners':
            _pad = '_'
            _punctuation = ',.!?-~…'
            _letters = 'AEINOQUabdefghijklmnoprstuvwyzʃʧʦɯɹəɥ⁼ʰ`→↓↑ '
        case 'sanskrit_cleaners':
            _pad = '_'
            _punctuation = '।'
            _letters = 'ँंःअआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलळवशषसहऽािीुूृॄेैोौ्ॠॢ '
        case 'cjks_cleaners':
            _pad = '_'
            _punctuation = ',.!?-~…'
            _letters = 'NQabdefghijklmnopstuvwxyzʃʧʥʦɯɹəɥçɸɾβŋɦː⁼ʰ`^#*=→↓↑ '
        case 'thai_cleaners':
            _pad = '_'
            _punctuation = '.!? '
            _letters = 'กขฃคฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤลวศษสหฬอฮฯะัาำิีึืุูเแโใไๅๆ็่้๊๋์'
        case 'cjke_cleaners2':
            _pad = '_'
            _punctuation = ',.!?-~…'
            _letters = 'NQabdefghijklmnopstuvwxyzɑæʃʑçɯɪɔɛɹðəɫɥɸʊɾʒθβŋɦ⁼ʰ`^#*=ˈˌ→↓↑ '
        case 'shanghainese_cleaners':
            _pad = '_'
            _punctuation = ',.!?…'
            _letters = 'abdfghiklmnopstuvyzøŋȵɑɔɕəɤɦɪɿʑʔʰ̩̃ᴀᴇ15678 '
        case 'chinese_dialect_cleaners':
            _pad = '_'
            _punctuation = ',.!?~…─'
            _letters = '#Nabdefghijklmnoprstuvwxyzæçøŋœȵɐɑɒɓɔɕɗɘəɚɛɜɣɤɦɪɭɯɵɷɸɻɾɿʂʅʊʋʌʏʑʔʦʮʰʷˀː˥˦˧˨˩̥̩̃̚ᴀᴇ↑↓∅ⱼ '
        case _:  # default: zh_ja_mixture_cleaners
            _pad = '_'
            _punctuation = ',.!?-~…'
            _letters = 'AEINOQUabdefghijklmnoprstuvwyzʃʧʦɯɹəɥ⁼ʰ`→↓↑ '
    symbols = [_pad] + list(_punctuation) + list(_letters)
    return symbols, symbols.index(" ")
