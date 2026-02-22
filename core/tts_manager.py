# core/tts_manager.py
import pyttsx3
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self):
        logger.info("Initializing TTS Manager...")
        
        self.is_available = self._test_tts()
        
        if not self.is_available:
            logger.error("TTS is not available on this system")
            return
        
        self.speech_queue = queue.Queue()
        self.is_running = True
        
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        
        logger.info("TTS Manager initialized and ready")
    
    def _test_tts(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 0.9)
            
            engine.say("test")
            engine.runAndWait()
            engine.stop()
            
            logger.info("TTS test successful")
            return True
            
        except Exception as e:
            logger.error(f"TTS test failed: {e}")
            return False
    
    def _speak_text(self, text):
        try:
            logger.info(f"Speaking: '{text}'")
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 0.9)
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
            logger.info(f"Finished speaking: '{text}'")
            return True
            
        except Exception as e:
            logger.error(f"Error speaking text '{text}': {e}")
            return False
    
    def _process_queue(self):
        logger.debug("TTS worker thread started")
        
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=1)
                
                if text is None:
                    break
                
                self._speak_text(text)
                
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
                
            except Exception as e:
                logger.error(f"Error in TTS worker: {e}")
                time.sleep(0.1)
        
        logger.debug("TTS worker thread stopped")
    
    def speak(self, text):
        if not self.is_available:
            logger.warning("TTS not available, cannot speak")
            return
        
        if not text or not isinstance(text, str):
            return
        
        text = text.strip()
        if not text:
            return
        
        logger.info(f"Queueing speech: '{text}'")
        
        try:
            self.speech_queue.put(text, block=False)
        except queue.Full:
            logger.warning("TTS queue full, dropping speech")
        except Exception as e:
            logger.error(f"Error queueing speech: {e}")
    
    def speak_letter(self, letter):
        if letter and len(letter) == 1 and letter.isalpha():
            self.speak(f"letter {letter}")
    
    def speak_phrase(self, phrase):
        self.speak(phrase)
    
    def stop(self):
        logger.info("Stopping TTS...")
        
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break
    
    def cleanup(self):
        logger.info("Cleaning up TTS Manager...")
        self.is_running = False
        
        try:
            self.speech_queue.put(None, block=False)
        except:
            pass
        
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)