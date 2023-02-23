import tempfile
import warnings
import pyttsx3
import torch
import numpy as np
from tts import utils, commons
from pathlib import Path
from tts.models import SynthesizerTrn
from tts.text import init_symbols, text_to_sequence
from torch import no_grad, LongTensor
from typing import Tuple, Dict, Union, Optional

with warnings.catch_warnings():
    warnings.simplefilter('ignore')  # Ignore pydub warning if ffmpeg is not installed
    from pydub import AudioSegment
    from pydub.playback import play as pydub_play_audio


class TTS:
    __device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __init__(self, is_local: bool = False, config_path: str = '', model_path: str = '',
                 is_multi_speakers: bool = False, multi_speakers_sid: int = 0,
                 lang: Optional[str] = None, emotion: float = 0.6, phoneme_length: float = 0.668, speech_speed: float = 1.2):
        self.__engine = None
        
        self.__is_local = is_local

        if self.__is_local:
            self.__engine = pyttsx3.init()
        else:
            self.__config_path = config_path
            self.__model_path = model_path
            self.__is_multi_speakers = is_multi_speakers
            self.__multi_speakers_sid = multi_speakers_sid

            self.lang = lang
            self.emotion = emotion
            self.phoneme_length = phoneme_length
            self.speech_speed = speech_speed

            self.__hps_ms = utils.get_hparams_from_file(Path(self.__config_path))
            self.__cleaners = self.__hps_ms.data.text_cleaners[0]

            init_symbols(self.__cleaners)
            from tts.text import symbols

            self.__net_g_ms = SynthesizerTrn(
                len(symbols),
                self.__hps_ms.data.filter_length // 2 + 1,
                self.__hps_ms.train.segment_size // self.__hps_ms.data.hop_length,
                n_speakers=self.__hps_ms.data.n_speakers if self.__is_multi_speakers else 0,
                **self.__hps_ms.model)
            self.__net_g_ms.eval().to(TTS.__device)
            utils.load_checkpoint(Path(self.__model_path), self.__net_g_ms, None)

    def generate(self, input_text: str = ''):
        """
        输入要语音播报的文本，返回wav文件的路径位置。
        """
        if self.__engine is None:
            o1, o2 = self.__tts_fn(input_text)
            res = TTS.__postprocess(o2)
            if res.get('is_file', False) and 'name' in res:
                return res['name']

    def say(self, input_text: str = '', print_: Union[str, bool, None] = None):
        if self.__is_local:
            if print_ is not None:
                if isinstance(print_, bool) and print_:
                    print(input_text)
                elif isinstance(print_, str):
                    print(print_)
            self.__engine.say(input_text)
            self.__engine.runAndWait()
        else:
            audio_file = self.generate(input_text=input_text)
            if print_ is not None:
                if isinstance(print_, bool) and print_:
                    print(input_text)
                elif isinstance(print_, str):
                    print(print_)
            self.play_audio(audio_file=audio_file)

    @staticmethod
    def play_audio(audio_file: str):
        pydub_play_audio(AudioSegment.from_wav(audio_file))
        Path(audio_file).unlink()

    @staticmethod
    def __get_text(input_text, hps):
        text_norm = text_to_sequence(input_text, hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm

    def __tts_fn(self, input_text):
        input_text = input_text.replace('\n', ' ').replace('\r', '').replace(' ', '')
        match self.__cleaners:
            case 'zh_ja_mixture_cleaners':
                match self.lang:
                    case 'ZH':  # 中文
                        input_text = f'[ZH]{input_text}[ZH]'
                    case 'JA':  # 日语
                        input_text = f'[JA]{input_text}[JA]'
            case 'cjks_cleaners':
                match self.lang:
                    case 'ZH':  # 中文
                        input_text = f'[ZH]{input_text}[ZH]'
                    case 'JA':  # 日语
                        input_text = f'[JA]{input_text}[JA]'
                    case 'KO':  # 韩语
                        input_text = f'[KO]{input_text}[KO]'
                    case 'SA':  # 天城文
                        input_text = f'[SA]{input_text}[SA]'
                    case 'EN':  # 英语
                        input_text = f'[EN]{input_text}[EN]'
            case 'cjke_cleaners' | 'cjke_cleaners2':
                match self.lang:
                    case 'ZH':  # 中文
                        input_text = f'[ZH]{input_text}[ZH]'
                    case 'JA':  # 日语
                        input_text = f'[JA]{input_text}[JA]'
                    case 'KO':  # 韩语
                        input_text = f'[KO]{input_text}[KO]'
                    case 'EN':  # 英语
                        input_text = f'[EN]{input_text}[EN]'
            case 'chinese_dialect_cleaners':
                match self.lang:
                    case 'ZH':  # 中文
                        input_text = f'[ZH]{input_text}[ZH]'
                    case 'JA':  # 日语
                        input_text = f'[JA]{input_text}[JA]'
                    case 'SH':  # 上海话（方言）
                        input_text = f'[SH]{input_text}[SH]'
                    case 'GD':  # 广东话（粤语，方言）
                        input_text = f'[GD]{input_text}[GD]'
                    case 'EN':  # 英语
                        input_text = f'[EN]{input_text}[EN]'
            case _:
                pass
        stn_tst = TTS.__get_text(input_text, self.__hps_ms)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(TTS.__device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(TTS.__device)
            sid = LongTensor([self.__multi_speakers_sid]).to(TTS.__device) if self.__is_multi_speakers else None
            audio = self.__net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=self.emotion,
                                          noise_scale_w=self.phoneme_length,
                                          length_scale=self.speech_speed)[0][0, 0].data.cpu().float().numpy()

        return 'Success', (22050, audio)

    @staticmethod
    def __abspath(path: Union[str, Path]) -> Path:
        """Returns absolute path of a str or Path path, but does not resolve symlinks."""
        if Path(path).is_symlink():
            return Path.cwd() / path
        else:
            return Path(path).resolve()

    @staticmethod
    def __audio_to_file(sample_rate, data, filename):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            data = TTS.__convert_to_16_bit_wav(data)
        audio = AudioSegment(
            data.tobytes(),
            frame_rate=sample_rate,
            sample_width=data.dtype.itemsize,
            channels=(1 if len(data.shape) == 1 else data.shape[1]),
        )
        file = audio.export(filename, format='wav')
        file.close()  # type: ignore

    @staticmethod
    def __convert_to_16_bit_wav(data):
        # Based on: https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html
        warning = 'Trying to convert audio automatically from {} to 16-bit int format.'
        if data.dtype in [np.float64, np.float32, np.float16]:
            warnings.warn(warning.format(data.dtype))
            data = data / np.abs(data).max()
            data = data * 32767
            data = data.astype(np.int16)
        elif data.dtype == np.int32:
            warnings.warn(warning.format(data.dtype))
            data = data / 65538
            data = data.astype(np.int16)
        elif data.dtype == np.int16:
            pass
        elif data.dtype == np.uint16:
            warnings.warn(warning.format(data.dtype))
            data = data - 32768
            data = data.astype(np.int16)
        elif data.dtype == np.uint8:
            warnings.warn(warning.format(data.dtype))
            data = data * 257 - 32768
            data = data.astype(np.int16)
        else:
            raise ValueError(
                'Audio data cannot be converted automatically from '
                f'{data.dtype} to 16-bit int format.'
            )
        return data

    @staticmethod
    def __postprocess(y: Union[Tuple[int, np.ndarray], str, None]) -> Union[str, Dict, None]:
        """
        Parameters:
            y: audio data in either of the following formats: a tuple of (sample_rate, data), or None.
        Returns:
            base64 url data
        """
        if y is None:
            return None
        if isinstance(y, tuple):
            sample_rate, data = y
            file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            TTS.__audio_to_file(sample_rate, data, file.name)
            file_path = str(TTS.__abspath(file.name))
            return {'name': file_path, 'data': None, 'is_file': True}
        return None
