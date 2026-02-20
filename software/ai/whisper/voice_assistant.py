#!/usr/bin/env python3
"""
APEXSAT AI - APEX Voice Sesli Asistan

Wake word algılama → Ses tanıma (Whisper) → Komut işleme → TTS yanıt

Kullanım:
    python3 voice_assistant.py                    # Sesli asistanı başlat
    python3 voice_assistant.py --test-stt FILE    # STT testi (ses dosyası)
    python3 voice_assistant.py --test-commands     # Komut parser testi
"""

import json
import os
import re
import subprocess
import sys
import time
import wave
import struct
import threading
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Callable


# ─── Sabitler ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
WHISPER_BIN = Path("/opt/apexsat/whisper/bin/whisper-cli")
WHISPER_MODEL = Path("/opt/apexsat/whisper/models/ggml-small.bin")
PIPER_BIN = Path("/opt/apexsat/piper/piper")
PIPER_MODEL = Path("/opt/apexsat/piper/models/tr_TR-dfki-medium.onnx")

WAKE_WORDS = ["apex", "hey apex", "apeks", "hey apeks"]
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 500    # Sessizlik eşiği
SILENCE_DURATION = 1.5     # Sessizlik süresi (saniye) - komut sonu algılama
MAX_RECORD_DURATION = 10   # Maksimum kayıt süresi (saniye)


class AssistantState(Enum):
    IDLE = auto()           # Beklemede (wake word dinliyor)
    LISTENING = auto()      # Komut dinliyor
    PROCESSING = auto()     # Komut işleniyor
    SPEAKING = auto()       # Yanıt veriliyor
    ERROR = auto()


class IntentType(Enum):
    CHANNEL_CHANGE = "channel_change"
    CHANNEL_SEARCH = "channel_search"
    VOLUME_CONTROL = "volume_control"
    RECORDING = "recording"
    EPG_QUERY = "epg_query"
    APP_LAUNCH = "app_launch"
    SEARCH = "search"
    SYSTEM = "system"
    PLAYBACK = "playback"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    type: IntentType
    action: str
    params: dict
    confidence: float = 1.0
    raw_text: str = ""


@dataclass
class VoiceCommand:
    text: str
    intent: Intent
    response: str = ""


# ─── Wake Word Algılama ─────────────────────────────────────────────────────

class WakeWordDetector:
    """
    'APEX' veya 'Hey APEX' wake word algılama.

    Basit enerji tabanlı algılama + Whisper ile doğrulama.
    Üretim versiyonunda OpenWakeWord veya Porcupine kullanılacak.
    """

    def __init__(self, wake_words: list[str] = None):
        self.wake_words = [w.lower() for w in (wake_words or WAKE_WORDS)]
        self.is_active = False
        self._callback: Optional[Callable] = None

    def check_text(self, text: str) -> bool:
        """Metinde wake word var mı kontrol et."""
        text_lower = text.lower().strip()
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                return True
        return False

    def extract_command(self, text: str) -> str:
        """Wake word'den sonraki komutu çıkar."""
        text_lower = text.lower().strip()
        for wake_word in sorted(self.wake_words, key=len, reverse=True):
            idx = text_lower.find(wake_word)
            if idx >= 0:
                command = text[idx + len(wake_word):].strip()
                # Başındaki virgül, nokta gibi işaretleri temizle
                command = command.lstrip(",. ")
                return command
        return text


# ─── Ses Tanıma (STT - Speech to Text) ──────────────────────────────────────

class SpeechToText:
    """Whisper.cpp tabanlı ses tanıma."""

    def __init__(self, model_path: Path = WHISPER_MODEL,
                 whisper_bin: Path = WHISPER_BIN,
                 language: str = "tr"):
        self.model_path = model_path
        self.whisper_bin = whisper_bin
        self.language = language

    def transcribe_file(self, audio_path: str) -> str:
        """Ses dosyasını metne çevir."""
        if not self.whisper_bin.exists():
            print(f"⚠️  Whisper bulunamadı: {self.whisper_bin}")
            return self._simulate_transcription(audio_path)

        try:
            result = subprocess.run(
                [
                    str(self.whisper_bin),
                    "-m", str(self.model_path),
                    "-l", self.language,
                    "-f", audio_path,
                    "--no-timestamps",
                    "-t", "4",  # 4 thread
                ],
                capture_output=True, text=True, timeout=30
            )

            text = result.stdout.strip()
            # Whisper çıktısından temiz metni al
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("[")]
            return " ".join(lines)

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️  Whisper hatası: {e}")
            return ""

    def transcribe_buffer(self, audio_data: bytes) -> str:
        """Ses buffer'ını metne çevir (PCM 16-bit, 16kHz, mono)."""
        temp_path = "/tmp/apexsat_voice.wav"

        # WAV dosyası oluştur
        with wave.open(temp_path, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)

        return self.transcribe_file(temp_path)

    def _simulate_transcription(self, audio_path: str) -> str:
        """Simülasyon modu (Whisper yüklü değilken test)."""
        simulated_texts = [
            "apex trt 1'e geç",
            "apex sesi aç",
            "apex şimdi ne var",
            "apex bu programı kaydet",
            "apex youtube aç",
            "apex haber kanallarını göster",
        ]
        import random
        return random.choice(simulated_texts)


# ─── Metin-Ses Dönüşümü (TTS - Text to Speech) ─────────────────────────────

class TextToSpeech:
    """Piper TTS tabanlı Türkçe ses sentezi."""

    def __init__(self, piper_bin: Path = PIPER_BIN,
                 model_path: Path = PIPER_MODEL):
        self.piper_bin = piper_bin
        self.model_path = model_path

    def speak(self, text: str, output_path: str = "/tmp/apexsat_tts.wav"):
        """Metni sese çevir ve oynat."""
        if not self.piper_bin.exists():
            print(f"🔊 [TTS SİMÜLASYON]: {text}")
            return

        try:
            # Piper ile ses oluştur
            process = subprocess.Popen(
                [
                    str(self.piper_bin),
                    "--model", str(self.model_path),
                    "--output_file", output_path,
                ],
                stdin=subprocess.PIPE,
                capture_output=True
            )
            process.communicate(input=text.encode("utf-8"), timeout=10)

            # Ses dosyasını oynat
            self._play_audio(output_path)

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️  TTS hatası: {e}")
            print(f"🔊 [YAZI]: {text}")

    def _play_audio(self, filepath: str):
        """Ses dosyasını oynat."""
        players = ["aplay", "paplay", "pw-play", "ffplay -nodisp -autoexit"]
        for player in players:
            try:
                subprocess.run(
                    player.split() + [filepath],
                    capture_output=True, timeout=10
                )
                return
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        print(f"⚠️  Ses oynatıcı bulunamadı")


# ─── Doğal Dil İşleme (NLU) ─────────────────────────────────────────────────

class IntentParser:
    """
    Türkçe komut parser - rule-based intent recognition.

    Üretim versiyonunda TinyLlama/Phi-2 ile değiştirilecek.
    """

    # Kanal adı → numara eşleşmeleri
    CHANNEL_MAP = {
        "trt 1": 1, "trt bir": 1, "trt1": 1,
        "trt 2": 2, "trt iki": 2,
        "trt haber": 3, "trt spor": 4,
        "trt world": 5, "trt belgesel": 6,
        "trt müzik": 7, "trt çocuk": 8,
        "trt 4k": 9,
        "atv": 10, "a tv": 10,
        "a haber": 11, "a spor": 12,
        "show tv": 13, "show": 13,
        "habertürk": 14, "haberturk": 14,
        "bloomberg ht": 15,
        "star tv": 16, "star": 16,
        "ntv": 17,
        "kanal d": 18,
        "cnn türk": 19, "cnn turk": 19,
        "fox tv": 20, "fox": 20, "now tv": 20,
        "tv8": 21, "tv 8": 21,
        "beyaz tv": 22, "beyaz": 22,
        "tv360": 23, "tv 360": 23,
        "halk tv": 24, "halk": 24,
        "tele1": 25, "tele 1": 25,
        "tgrt haber": 26, "tgrt": 26,
        "ulusal kanal": 27,
        "diyanet tv": 28,
        "trt arabi": 29, "trt kurdi": 30,
    }

    # Intent kalıpları
    PATTERNS = {
        IntentType.CHANNEL_CHANGE: [
            r"(.+?)(?:'?[aeiıoöuü]?[yn]?[ae]) (?:geç|aç|değiştir|getir)",
            r"(.+?) (?:kanalına geç|kanalını aç)",
            r"(?:kanal|channel)\s*(\d+)",
            r"(\d+)\s*(?:numaralı|nolu) kanal",
        ],
        IntentType.CHANNEL_SEARCH: [
            r"(.+?) kanallarını (?:göster|listele|bul)",
            r"(.+?) kanalları",
            r"(?:göster|listele|bul) (.+?) kanalları",
        ],
        IntentType.VOLUME_CONTROL: [
            r"ses(?:i)? (?:aç|yükselt|arttır)",
            r"ses(?:i)? (?:kıs|azalt|düşür|kapat)",
            r"sessiz(?:e al)?|mute|sustur",
            r"ses(?:i)? (%?\d+)",
        ],
        IntentType.RECORDING: [
            r"(?:bunu |bu programı )?(?:kaydet|kayda al|kayıt (?:başlat|yap))",
            r"kaydı (?:durdur|bitir|kapat)",
            r"(.+?) (?:kaydet|kayda al)",
        ],
        IntentType.EPG_QUERY: [
            r"(?:şimdi|şu an) ne (?:var|yayınlanıyor|çalıyor)",
            r"(?:bu akşam|bu gece|yarın|bugün) ne var",
            r"(.+?)(?:'?[dtk]?[ae]) (?:şimdi )?ne var",
            r"program (?:rehberi|listesi|akışı)",
        ],
        IntentType.APP_LAUNCH: [
            r"(youtube|netflix|kodi|iptv|ayarlar|medya) (?:aç|başlat|göster)",
            r"(youtube|netflix|kodi|iptv|ayarlar|medya)(?:'[aeiıoöuü]|[aeiıoöuü]) (?:geç|aç)",
        ],
        IntentType.SEARCH: [
            r"(.+?) (?:ara|bul|filmleri|dizileri)",
            r"(?:ara|bul) (.+)",
        ],
        IntentType.PLAYBACK: [
            r"(?:duraklat|pause|bekle)",
            r"(?:devam et|devam|oynat|play|başlat)",
            r"(?:geri sar|geri al|rewind)",
            r"(?:ileri sar|ileri al|forward)",
            r"(?:durdur|kapat|stop)",
        ],
        IntentType.SYSTEM: [
            r"(?:güncelleme|update) (?:kontrol et|var mı|bak)",
            r"ayarları? aç",
            r"(?:kapat|shutdown|yeniden başlat|restart|reboot)",
            r"(?:saat kaç|tarih ne|hava durumu)",
        ],
    }

    def parse(self, text: str) -> Intent:
        """Metni analiz edip Intent çıkar."""
        text_lower = text.lower().strip()

        if not text_lower:
            return Intent(IntentType.UNKNOWN, "", {}, 0.0, text)

        # Her intent türünü kontrol et
        for intent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    return self._build_intent(intent_type, match, text_lower, text)

        # Doğrudan kanal adı kontrolü
        for ch_name, ch_num in self.CHANNEL_MAP.items():
            if ch_name in text_lower:
                return Intent(
                    IntentType.CHANNEL_CHANGE,
                    "change",
                    {"channel_name": ch_name, "channel_number": ch_num},
                    0.8,
                    text
                )

        return Intent(IntentType.UNKNOWN, "unknown", {"text": text_lower}, 0.0, text)

    def _build_intent(self, intent_type: IntentType, match: re.Match,
                       text_lower: str, raw_text: str) -> Intent:
        """Eşleşmeden Intent nesnesi oluştur."""
        params = {}

        if intent_type == IntentType.CHANNEL_CHANGE:
            captured = match.group(1) if match.lastindex else ""
            # Kanal numarası mı, isim mi?
            if captured and captured.isdigit():
                params["channel_number"] = int(captured)
                params["action"] = "change_by_number"
            else:
                ch_name = captured.strip().lower()
                params["channel_name"] = ch_name
                params["channel_number"] = self.CHANNEL_MAP.get(ch_name, 0)
                params["action"] = "change_by_name"
            return Intent(intent_type, "change", params, 0.9, raw_text)

        elif intent_type == IntentType.VOLUME_CONTROL:
            if any(w in text_lower for w in ["aç", "yükselt", "arttır"]):
                params["action"] = "up"
            elif any(w in text_lower for w in ["kıs", "azalt", "düşür"]):
                params["action"] = "down"
            elif any(w in text_lower for w in ["sessiz", "mute", "sustur"]):
                params["action"] = "mute"
            elif any(w in text_lower for w in ["kapat"]):
                params["action"] = "mute"
            else:
                params["action"] = "set"
                # Sayı varsa ses seviyesini al
                num_match = re.search(r"(\d+)", text_lower)
                if num_match:
                    params["level"] = int(num_match.group(1))
            return Intent(intent_type, params.get("action", "up"), params, 0.9, raw_text)

        elif intent_type == IntentType.RECORDING:
            if any(w in text_lower for w in ["durdur", "bitir", "kapat"]):
                params["action"] = "stop"
            else:
                params["action"] = "start"
            return Intent(intent_type, params["action"], params, 0.9, raw_text)

        elif intent_type == IntentType.EPG_QUERY:
            params["query"] = text_lower
            if "bu akşam" in text_lower:
                params["time"] = "evening"
            elif "yarın" in text_lower:
                params["time"] = "tomorrow"
            else:
                params["time"] = "now"
            return Intent(intent_type, "query", params, 0.85, raw_text)

        elif intent_type == IntentType.APP_LAUNCH:
            app = match.group(1) if match.lastindex else ""
            params["app"] = app.strip()
            return Intent(intent_type, "launch", params, 0.9, raw_text)

        elif intent_type == IntentType.PLAYBACK:
            if any(w in text_lower for w in ["duraklat", "pause", "bekle"]):
                action = "pause"
            elif any(w in text_lower for w in ["devam", "oynat", "play", "başlat"]):
                action = "resume"
            elif any(w in text_lower for w in ["geri"]):
                action = "rewind"
            elif any(w in text_lower for w in ["ileri"]):
                action = "forward"
            else:
                action = "stop"
            return Intent(intent_type, action, params, 0.9, raw_text)

        elif intent_type == IntentType.SEARCH:
            query = match.group(1) if match.lastindex else text_lower
            params["query"] = query.strip()
            return Intent(intent_type, "search", params, 0.8, raw_text)

        elif intent_type == IntentType.SYSTEM:
            if "güncelleme" in text_lower or "update" in text_lower:
                params["action"] = "check_update"
            elif "ayar" in text_lower:
                params["action"] = "open_settings"
            elif any(w in text_lower for w in ["kapat", "shutdown"]):
                params["action"] = "shutdown"
            elif any(w in text_lower for w in ["yeniden", "restart", "reboot"]):
                params["action"] = "restart"
            else:
                params["action"] = "info"
            return Intent(intent_type, params["action"], params, 0.85, raw_text)

        return Intent(intent_type, "unknown", params, 0.5, raw_text)


# ─── Yanıt Üretici ──────────────────────────────────────────────────────────

class ResponseGenerator:
    """Komut yanıtları üret (TTS için Türkçe metin)."""

    RESPONSES = {
        IntentType.CHANNEL_CHANGE: {
            "change": "{channel_name} kanalına geçiliyor",
            "not_found": "Kanal bulunamadı: {channel_name}",
        },
        IntentType.CHANNEL_SEARCH: {
            "found": "{count} kanal bulundu",
            "not_found": "Kanal bulunamadı",
        },
        IntentType.VOLUME_CONTROL: {
            "up": "Ses yükseltildi",
            "down": "Ses kısıldı",
            "mute": "Ses kapatıldı",
            "unmute": "Ses açıldı",
        },
        IntentType.RECORDING: {
            "start": "Kayıt başlatıldı",
            "stop": "Kayıt durduruldu",
        },
        IntentType.EPG_QUERY: {
            "now": "Şu anda {channel} kanalında {program} yayınlanıyor",
            "evening": "Bu akşam için program rehberi gösteriliyor",
        },
        IntentType.APP_LAUNCH: {
            "launch": "{app} açılıyor",
        },
        IntentType.PLAYBACK: {
            "pause": "Duraklatıldı",
            "resume": "Devam ediyor",
            "rewind": "Geri sarılıyor",
            "forward": "İleri sarılıyor",
            "stop": "Durduruldu",
        },
        IntentType.SYSTEM: {
            "check_update": "Güncelleme kontrol ediliyor",
            "open_settings": "Ayarlar açılıyor",
            "shutdown": "Cihaz kapatılıyor",
            "restart": "Cihaz yeniden başlatılıyor",
        },
        IntentType.UNKNOWN: {
            "unknown": "Anlayamadım, tekrar söyler misiniz?",
        },
    }

    def generate(self, intent: Intent) -> str:
        """Intent'e göre yanıt metni üret."""
        responses = self.RESPONSES.get(intent.type, {})
        template = responses.get(intent.action, responses.get("unknown", "Tamam"))

        try:
            return template.format(**intent.params)
        except (KeyError, IndexError):
            return template


# ─── Ana Sesli Asistan Sınıfı ───────────────────────────────────────────────

class APEXVoiceAssistant:
    """APEX Voice - Ana sesli asistan sınıfı."""

    def __init__(self):
        self.state = AssistantState.IDLE
        self.wake_word = WakeWordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.intent_parser = IntentParser()
        self.response_gen = ResponseGenerator()
        self._on_command: Optional[Callable[[VoiceCommand], None]] = None
        self._running = False

    def set_command_handler(self, handler: Callable[[VoiceCommand], None]):
        """Komut işleyici callback'i ayarla."""
        self._on_command = handler

    def process_text(self, text: str) -> VoiceCommand:
        """Metin komutunu işle (test ve yazılı komut için)."""
        # Wake word kontrolü
        if self.wake_word.check_text(text):
            command_text = self.wake_word.extract_command(text)
        else:
            command_text = text

        # Intent algıla
        intent = self.intent_parser.parse(command_text)

        # Yanıt üret
        response = self.response_gen.generate(intent)

        cmd = VoiceCommand(text=command_text, intent=intent, response=response)

        # Callback çağır
        if self._on_command:
            self._on_command(cmd)

        return cmd

    def process_audio(self, audio_data: bytes) -> VoiceCommand:
        """Ses verisini işle."""
        self.state = AssistantState.PROCESSING

        # STT
        text = self.stt.transcribe_buffer(audio_data)
        if not text:
            self.state = AssistantState.IDLE
            return VoiceCommand("", Intent(IntentType.UNKNOWN, "", {}, 0.0))

        # Komut işle
        cmd = self.process_text(text)

        # TTS yanıt
        if cmd.response:
            self.state = AssistantState.SPEAKING
            self.tts.speak(cmd.response)

        self.state = AssistantState.IDLE
        return cmd

    def start(self):
        """Sesli asistanı başlat (mikrofon dinleme döngüsü)."""
        self._running = True
        self.state = AssistantState.IDLE

        print("=" * 50)
        print("  🎙️  APEX Voice Sesli Asistan")
        print("  'APEX' diyerek aktive edin")
        print("  Ctrl+C ile çıkış")
        print("=" * 50)

        try:
            while self._running:
                # Mikrofon dinleme (gerçek cihazda ALSA/PulseAudio ile)
                # PoC aşamasında stdin'den metin komut kabul et
                try:
                    user_input = input("\n🎤 Komut (veya 'q' çıkış): ").strip()
                    if user_input.lower() in ("q", "quit", "exit", "çıkış"):
                        break
                    if user_input:
                        cmd = self.process_text(user_input)
                        self._print_result(cmd)
                except EOFError:
                    break

        except KeyboardInterrupt:
            pass

        self._running = False
        print("\n👋 APEX Voice kapatıldı")

    def stop(self):
        """Asistanı durdur."""
        self._running = False

    def _print_result(self, cmd: VoiceCommand):
        """Komut sonucunu yazdır."""
        intent = cmd.intent
        print(f"\n  📝 Metin: {cmd.text}")
        print(f"  🎯 Intent: {intent.type.value} → {intent.action}")
        print(f"  📊 Güven: {intent.confidence:.0%}")
        if intent.params:
            print(f"  📦 Parametreler: {json.dumps(intent.params, ensure_ascii=False)}")
        print(f"  💬 Yanıt: {cmd.response}")


# ─── Ana Program ─────────────────────────────────────────────────────────────

def test_commands():
    """Komut parser test senaryoları."""
    assistant = APEXVoiceAssistant()

    test_cases = [
        "APEX, TRT 1'e geç",
        "APEX, sesi aç",
        "APEX, sesi kıs",
        "hey apex sessize al",
        "APEX, şimdi ne var?",
        "APEX, bu akşam ne var TRT'de?",
        "APEX, bunu kaydet",
        "APEX, kaydı durdur",
        "APEX, YouTube aç",
        "APEX, Netflix'e geç",
        "APEX, haber kanallarını göster",
        "APEX, Kemal Sunal filmleri ara",
        "APEX, güncelleme kontrol et",
        "APEX, ayarları aç",
        "APEX, duraklat",
        "APEX, devam et",
        "APEX, geri sar",
        "APEX, kanal 5",
        "APEX, Kanal D'ye geç",
        "APEX, Star TV aç",
        "burada bir şey söylüyorum ama apex kelimesi yok",
    ]

    print("=" * 60)
    print("  APEX Voice - Komut Parser Testi")
    print("=" * 60)

    passed = 0
    for text in test_cases:
        cmd = assistant.process_text(text)
        status = "✅" if cmd.intent.type != IntentType.UNKNOWN or "apex" not in text.lower() else "❌"
        if status == "✅":
            passed += 1

        print(f"\n{status} \"{text}\"")
        print(f"   → {cmd.intent.type.value}: {cmd.intent.action} "
              f"({cmd.intent.confidence:.0%})")
        if cmd.intent.params:
            print(f"   → Params: {json.dumps(cmd.intent.params, ensure_ascii=False)}")
        print(f"   → Yanıt: {cmd.response}")

    print(f"\n{'=' * 60}")
    print(f"  Sonuç: {passed}/{len(test_cases)} test geçti")
    print(f"{'=' * 60}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="APEXSAT AI - APEX Voice Sesli Asistan")
    parser.add_argument("--test-commands", action="store_true", help="Komut parser testi")
    parser.add_argument("--test-stt", type=str, help="STT testi (ses dosyası)")
    parser.add_argument("--interactive", action="store_true", help="İnteraktif mod")

    args = parser.parse_args()

    if args.test_commands:
        test_commands()
    elif args.test_stt:
        stt = SpeechToText()
        text = stt.transcribe_file(args.test_stt)
        print(f"📝 Sonuç: {text}")
    else:
        assistant = APEXVoiceAssistant()
        assistant.start()


if __name__ == "__main__":
    main()
