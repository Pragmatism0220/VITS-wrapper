import sys
import toml
from pathlib import Path
from colorama import Back, Style
from colorama import init as colorama_init


def load_config() -> bool:
    global TTS_LOCAL, TTS_CONFIG_PATH, TTS_MODEL_PATH, TTS_LANGUAGE, TTS_EMOTION, TTS_PHONEME_LENGTH,\
        TTS_SPEECH_SPEED, TTS_MULTI_SPEAKERS, TTS_MULTI_SPEAKERS_SID
    config_toml_file = 'config.toml'

    try:
        config = toml.load(Path.cwd().joinpath(config_toml_file).as_posix())

        TTS_LOCAL = config['tts']['local']
        if not isinstance(TTS_LOCAL, bool):
            print(Style.BRIGHT + Back.RED + u'"tts.local"参数错误！是否启用自定义VITS模型选项只能为true或false。')
            return False

        if not TTS_LOCAL:
            TTS_CONFIG_PATH = config['tts']['config_path']
            TTS_MODEL_PATH = config['tts']['model_path']
            TTS_LANGUAGE = config['tts']['language']
            TTS_EMOTION = config['tts']['emotion']
            TTS_PHONEME_LENGTH = config['tts']['phoneme_length']
            TTS_SPEECH_SPEED = config['tts']['speech_speed']

            # tts
            if not isinstance(TTS_CONFIG_PATH, str):
                print(Style.BRIGHT + Back.RED + u'"tts.config_path"参数错误！配置文件路径必须为非空字符串。')
                return False
            elif not Path(TTS_CONFIG_PATH).resolve().is_file():
                print(Style.BRIGHT + Back.RED + u'"tts.config_path"配置文件路径不存在！')
                return False
            if not isinstance(TTS_MODEL_PATH, str):
                print(Style.BRIGHT + Back.RED + u'"tts.model_path"参数错误！模型文件路径必须为非空字符串。')
                return False
            elif not Path(TTS_MODEL_PATH).resolve().is_file():
                print(Style.BRIGHT + Back.RED + u'"tts.model_path"模型文件路径不存在！')
                return False
            if not isinstance(TTS_LANGUAGE, str):
                print(Style.BRIGHT + Back.RED + u'"tts.language"参数错误！语言参数只能为VITS的指定前后缀或空字符串。')
                return False
            if not (isinstance(TTS_EMOTION, float) and (0.1 <= TTS_EMOTION <= 1)):
                print(Style.BRIGHT + Back.RED + u'"tts.emotion"参数错误！感情变化程度参数必须为处在[0.1, 1]区间内的数值。')
                return False
            if not (isinstance(TTS_PHONEME_LENGTH, float) and (0.1 <= TTS_PHONEME_LENGTH <= 1)):
                print(Style.BRIGHT + Back.RED + u'"tts.phoneme_length"参数错误！音素发音长度参数必须为处在[0.1, 1]区间内的数值。')
                return False
            if not (isinstance(TTS_SPEECH_SPEED, float) and (0.1 <= TTS_SPEECH_SPEED <= 2)):
                print(Style.BRIGHT + Back.RED + u'"tts.speech_speed"参数错误！语速参数必须为处在[0.1, 2]区间内的数值。')
                return False

            TTS_MULTI_SPEAKERS = config['tts']['multi_speakers']
            if not isinstance(TTS_MULTI_SPEAKERS, bool):
                print(Style.BRIGHT + Back.RED + u'"tts.multi_speakers"参数错误！是否为多人模型选项只能为true或false。')
                return False
            if TTS_MULTI_SPEAKERS:
                TTS_MULTI_SPEAKERS_SID = config['tts']['multi_speakers_sid']
                if not (isinstance(TTS_MULTI_SPEAKERS_SID, int) and TTS_MULTI_SPEAKERS_SID >= 0):
                    print(Style.BRIGHT + Back.RED + u'"tts.multi_speakers_sid"参数错误！多人模型ID必须为大于等于0的整数。')
                    return False
            else:
                TTS_MULTI_SPEAKERS_SID = 0
        else:
            # use pyttsx3 as TTS engine
            pass

    except FileNotFoundError:
        print(Style.BRIGHT + Back.RED + u'未找到 %s 配置文件！' % config_toml_file)
        return False
    except KeyError:
        print(Style.BRIGHT + Back.RED + u'%s 配置文件参数命名错误！' % config_toml_file)
        return False

    return True


if __name__ == '__main__':
    colorama_init(autoreset=True)

    TTS_LOCAL = False
    TTS_CONFIG_PATH = ''
    TTS_MODEL_PATH = ''
    TTS_LANGUAGE = None
    TTS_EMOTION = 0.5
    TTS_PHONEME_LENGTH = 0.668
    TTS_SPEECH_SPEED = 1.4
    TTS_MULTI_SPEAKERS = False
    TTS_MULTI_SPEAKERS_SID = 0

    if not load_config():
        sys.exit(-1)

    # TTS(text-to-speech)语音引擎；特别地，可通过设置is_local=True来指定使用pyttsx3作为语音引擎
    from tts.engine import TTS

    tts_engine = TTS(
        is_local=TTS_LOCAL,
        config_path=TTS_CONFIG_PATH,
        model_path=TTS_MODEL_PATH,
        is_multi_speakers=TTS_MULTI_SPEAKERS,
        multi_speakers_sid=TTS_MULTI_SPEAKERS_SID,
        lang=TTS_LANGUAGE,
        emotion=TTS_EMOTION,
        phoneme_length=TTS_PHONEME_LENGTH,
        speech_speed=TTS_SPEECH_SPEED,
    )

    tts_engine.say(u'我姓云，单名一个堇字。有道是闻名不如见面，日后还请多多赏光，常来听戏。', print_=True)
    while input_text := input(u'云堇 说：'):
        tts_engine.say(input_text)
