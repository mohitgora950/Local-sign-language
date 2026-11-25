"""Interruptible speech. say() replaces whatever is being said; stop() silences at once."""
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)

SVS_ASYNC = 1
SVS_PURGE = 2


def _windows_voice_factory():
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    voice = win32com.client.Dispatch("SAPI.SpVoice")
    voice.Rate = 0
    voice.Volume = 100
    return voice, pythoncom.CoUninitialize


class SpeechController:
    def __init__(self, voice_factory=_windows_voice_factory):
        self._factory = voice_factory
        self._q = queue.Queue()
        self._gen = 0                     # bumped by say()/stop(); older speech is dropped
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    # ---- called from the webcam thread (never blocks) ----
    def say(self, word):
        with self._lock:
            self._gen += 1
            gen = self._gen
        self._q.put((gen, word))
        logger.info("Queued speech: %s", word)

    def stop(self):
        with self._lock:
            self._gen += 1
        self._drain()

    def close(self):
        self.stop()
        self._q.put(None)
        self._thread.join(timeout=3)

    def _drain(self):
        try:
            while True:
                self._q.get_nowait()
                self._q.task_done()
        except queue.Empty:
            pass

    # ---- worker thread ----
    def _run(self):
        cleanup = None
        try:
            voice, cleanup = self._factory()
            logger.info("Speech engine ready.")
            while True:
                item = self._q.get()
                try:
                    if item is None:
                        break
                    gen, word = item
                    if gen != self._gen:          # stale (hand left / newer gesture)
                        continue
                    logger.info("Speaking: %s", word)
                    voice.Speak(word, SVS_ASYNC)
                    while not voice.WaitUntilDone(30):
                        if gen != self._gen:      # interrupted
                            voice.Speak("", SVS_ASYNC | SVS_PURGE)
                            logger.info("Speech interrupted.")
                            break
                except Exception:
                    logger.exception("Speech error")
                finally:
                    self._q.task_done()
        except Exception:
            logger.exception("Speech worker could not initialize.")
        finally:
            if cleanup:
                cleanup()