from speechkit import speechkit
import speech_recognition as sr
# import pygame
import simpleaudio as sa


'''
def playaudiofunction_(io_vaw):
    """
    Function to play audio, that can be changed on different devices
    :param io_vaw: byte array vaw audio
    """
    pygame.init()
    pygame.mixer.music.load(io_vaw)
    pygame.mixer.music.play()

    while True:
        if not pygame.mixer.get_busy():
            return 1
'''


def playaudiofunction(
        io_vaw,
        num_channels=1,
        bytes_per_sample=2,
        sample_rate=44100):
    """
    Function to play audio, that can be changed on different devices
    : param io_vaw: byte array vaw audio
    """
    play_obj = sa.play_buffer(
        io_vaw,
        num_channels,
        bytes_per_sample,
        sample_rate,
    )
    play_obj.wait_done()
    return 1


class SynthesizedSpeech:
    def __init__(self, text, speech):
        """
        Creates one sentence with method to syntethize and play
        : param text: string text to syntheze
        : param speech: object of Speech class
        """
        self.speech = speech
        self.text = text
        self.audio_data = None

    def syntethize(self):
        """
        Creates buffer io wav file that next can be plaeyed
        """
        self.audio_data = self.speech.synthesizeAudio.synthesize_stream(
                self.text, lpcm=True)

    def play(self):
        """
        Plays created wav with speakers
        """
        if self.audio_data is None:
            raise Exception(
                "Audio did not synthesized, please run \"synthesize\" first.")
        self.speech.playaudiofunction(
            self.audio_data.read(), sample_rate=48000)


class RecognizeSpeech:
    def __init__(self, io_vaw, speech):
        """
        Recognizes text from given bytesio vaw
        : param io_vaw: bytesio array with audio vaw
        : param speech: object of Speech class
        """

        self.io_vaw = io_vaw
        self.speech = speech

    def recognize(self):
        """
        Starting streaming to yandex api and return recognize text
        """

        return self.speech.recognizeShortAudio.recognize(
                self.io_vaw, self.speech.catalog)


class Speech:
    def __init__(self,
                 api_key,
                 catalog,
                 playaudiofunction,
                 timeout_speech=10,
                 phrase_time_limit=15):
        """
        Class that realase speech recognition and synthesize methods
        :param api_key: string Yandex API key
        :param catalog: string Yandex catalog
        :param playaudiofunction: function to play vaw bytesio
        :param timeout_speech: parameter is the maximum number of seconds that this will wait for a phrase
        :param phrase_time_limit: parameter is the maximum number of seconds that this will allow a phrase to continue
        """

        self.synthesizeAudio = speechkit.SynthesizeAudio(
            api_key, catalog)
        self.recognizeShortAudio = speechkit.RecognizeShortAudio(
            api_key)
        self.playaudiofunction = playaudiofunction
        self.recognizer = sr.Recognizer()
        self.catalog = catalog
        self.timeout_speech = timeout_speech
        self.phrase_time_limit = phrase_time_limit

    def create_speech(self, text: str):
        """
        Creates inctance of SynthesizedSpeech to be used for synth later
        """
        return SynthesizedSpeech(text, self)

    def read_audio(self):
        """
        Starting reading audio and if there is audio creates instance of RecognizeSpeech or None
        """
        try:
            with sr.Microphone() as source:
                data = self.recognizer.listen(
                    source,
                    timeout=self.timeout_speech,
                    phrase_time_limit=self.phrase_time_limit,
                )
                data_sound = data.get_raw_data(convert_rate=48000)
                return RecognizeSpeech(data_sound, self)
        except self.recognizer.WaitTimeoutError:
            return None

    def adjust_for_ambient_noise(self, duration=3):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
