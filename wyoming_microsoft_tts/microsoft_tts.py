"""Microsoft TTS."""

import logging
import tempfile
import time
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk

_LOGGER = logging.getLogger(__name__)


class MicrosoftTTS:
    """Class to handle Microsoft TTS."""

    def __init__(self, args) -> None:
        """Initialize."""
        _LOGGER.debug("Initialize Microsoft TTS")
        self.args = args
        self.output_format = args.output_format
        self.speech_config = speechsdk.SpeechConfig(
            subscription=args.subscription_key, region=args.service_region
        )

        output_dir = str(tempfile.TemporaryDirectory())
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir

    def synthesize(self, text, voice=None):
        """Synthesize text to speech."""
        _LOGGER.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice

        self.speech_config.speech_synthesis_voice_name = voice
        if self.output_format:
            self.speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat[self.output_format]
            )
        file_name = self.output_dir / f"{time.monotonic_ns()}.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(file_name))

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            _LOGGER.debug(f"Speech synthesized for text [{text}]")
            return str(file_name)

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            _LOGGER.warning(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                _LOGGER.warning(f"Error details: {cancellation_details.error_details}")
