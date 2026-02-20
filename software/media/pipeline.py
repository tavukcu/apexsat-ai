#!/usr/bin/env python3
"""
APEXSAT AI - GStreamer Medya Pipeline Yöneticisi

DVB-S2 TS demux → Video/Audio decode → Display/PVR/Timeshift
Amlogic V4L2 donanım hızlandırma destekli.
"""

import os
import time
import signal
import threading
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Callable

# GStreamer import (cihazda yüklü olacak)
try:
    import gi
    gi.require_version("Gst", "1.0")
    gi.require_version("GstVideo", "1.0")
    from gi.repository import Gst, GLib, GstVideo
    GST_AVAILABLE = True
except (ImportError, ValueError):
    GST_AVAILABLE = False
    print("⚠️  GStreamer bulunamadı - simülasyon modunda")


# ─── Sabitler ────────────────────────────────────────────────────────────────

PVR_DEFAULT_PATH = Path("/media/pvr")
TIMESHIFT_BUFFER_PATH = Path("/tmp/timeshift")
TIMESHIFT_BUFFER_SIZE = 2 * 1024 * 1024 * 1024  # 2GB


class PlaybackState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()
    BUFFERING = auto()
    RECORDING = auto()
    TIMESHIFT = auto()
    ERROR = auto()


class VideoCodec(Enum):
    H264 = "h264"
    H265 = "h265"
    MPEG2 = "mpeg2"
    VP9 = "vp9"
    AV1 = "av1"


class AudioCodec(Enum):
    AAC = "aac"
    AC3 = "ac3"
    EAC3 = "eac3"
    DTS = "dts"
    MP2 = "mp2"
    MP3 = "mp3"


@dataclass
class StreamInfo:
    """Akış bilgisi."""
    video_pid: int = 0
    audio_pid: int = 0
    pcr_pid: int = 0
    pmt_pid: int = 0
    video_codec: str = "h264"
    audio_codec: str = "aac"
    width: int = 0
    height: int = 0
    framerate: float = 0.0
    is_hd: bool = False
    is_4k: bool = False
    has_subtitle: bool = False
    subtitle_pid: int = 0
    audio_tracks: list = None

    def __post_init__(self):
        if self.audio_tracks is None:
            self.audio_tracks = []


@dataclass
class PVRRecording:
    """PVR kayıt bilgisi."""
    filename: str
    channel_name: str
    start_time: float
    duration: int = 0     # dakika, 0=süresiz
    file_path: str = ""
    file_size: int = 0
    is_active: bool = False


# ─── GStreamer Pipeline Yöneticisi ───────────────────────────────────────────

class MediaPipeline:
    """
    DVB medya oynatma pipeline'ı.

    Pipeline mimarisi:
    ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
    │ DVB Src │───▶│ TS Demux │───▶│ H.264/265 │───▶│ Video    │
    │ (tuner) │    │          │    │  Decoder   │    │  Sink    │
    └─────────┘    │          │    └───────────┘    └──────────┘
                   │          │    ┌───────────┐    ┌──────────┐
                   │          │───▶│ AAC/AC3   │───▶│ Audio    │
                   │          │    │  Decoder   │    │  Sink    │
                   └──────────┘    └───────────┘    └──────────┘
    """

    def __init__(self, adapter_num: int = 0, frontend_num: int = 0):
        self.adapter_num = adapter_num
        self.frontend_num = frontend_num
        self.state = PlaybackState.STOPPED
        self.pipeline = None
        self.main_loop = None
        self._loop_thread = None
        self._on_state_change: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._pvr_recordings: list[PVRRecording] = []
        self._current_stream: Optional[StreamInfo] = None

        if GST_AVAILABLE:
            Gst.init(None)

    def _get_video_decoder_element(self, codec: str) -> str:
        """Video codec'e göre decoder element seç (HW hızlandırma öncelikli)."""
        # Amlogic V4L2 donanım decoder'lar
        hw_decoders = {
            "h264": "v4l2h264dec",    # Amlogic HW H.264
            "h265": "v4l2h265dec",    # Amlogic HW H.265/HEVC
            "mpeg2": "v4l2mpeg2dec",  # Amlogic HW MPEG-2
            "vp9": "v4l2vp9dec",      # Amlogic HW VP9
            "av1": "v4l2av1dec",      # Amlogic HW AV1 (S905X5+)
        }

        # Yazılım fallback decoder'lar
        sw_decoders = {
            "h264": "avdec_h264",
            "h265": "avdec_h265",
            "mpeg2": "avdec_mpeg2video",
            "vp9": "avdec_vp9",
            "av1": "avdec_av1",
        }

        # Önce HW decoder dene
        hw = hw_decoders.get(codec, "")
        if hw and GST_AVAILABLE:
            factory = Gst.ElementFactory.find(hw)
            if factory:
                return hw

        # SW fallback
        return sw_decoders.get(codec, "decodebin")

    def _get_audio_decoder_element(self, codec: str) -> str:
        """Audio codec'e göre decoder element seç."""
        decoders = {
            "aac": "avdec_aac",
            "ac3": "avdec_ac3",
            "eac3": "avdec_eac3",
            "dts": "avdec_dts",
            "mp2": "avdec_mp2float",
            "mp3": "avdec_mp3",
        }
        return decoders.get(codec, "decodebin")

    def build_live_tv_pipeline(self, stream: StreamInfo) -> str:
        """
        Canlı TV izleme pipeline'ı oluştur.

        Returns:
            GStreamer pipeline açıklama string'i
        """
        self._current_stream = stream
        video_dec = self._get_video_decoder_element(stream.video_codec)
        audio_dec = self._get_audio_decoder_element(stream.audio_codec)

        # DVB kaynak
        dvb_src = (
            f"dvbsrc adapter={self.adapter_num} frontend={self.frontend_num} "
            f"pids={stream.video_pid}:{stream.audio_pid}:{stream.pcr_pid}:{stream.pmt_pid}"
        )

        pipeline_str = (
            f"{dvb_src} ! tsdemux name=demux "

            # Video dalı
            f"demux. ! queue max-size-buffers=0 max-size-time=3000000000 ! "
            f"{video_dec} ! videoconvert ! "
            f"videoscale ! autovideosink name=videosink sync=true "

            # Audio dalı
            f"demux. ! queue max-size-buffers=0 max-size-time=3000000000 ! "
            f"{audio_dec} ! audioconvert ! audioresample ! "
            f"autoaudiosink name=audiosink sync=true"
        )

        return pipeline_str

    def build_pvr_pipeline(self, stream: StreamInfo, output_path: str) -> str:
        """
        PVR kayıt pipeline'ı (canlı TV + kayıt).

        TS'yi doğrudan dosyaya yazar (re-encode yok).
        """
        pids = f"{stream.video_pid}:{stream.audio_pid}:{stream.pcr_pid}:{stream.pmt_pid}"
        dvb_src = f"dvbsrc adapter={self.adapter_num} frontend={self.frontend_num} pids={pids}"

        video_dec = self._get_video_decoder_element(stream.video_codec)
        audio_dec = self._get_audio_decoder_element(stream.audio_codec)

        pipeline_str = (
            f"{dvb_src} ! tee name=t "

            # Kayıt dalı (raw TS)
            f"t. ! queue ! filesink location={output_path} "

            # Oynatma dalı
            f"t. ! queue ! tsdemux name=demux "
            f"demux. ! queue ! {video_dec} ! videoconvert ! autovideosink sync=true "
            f"demux. ! queue ! {audio_dec} ! audioconvert ! autoaudiosink sync=true"
        )

        return pipeline_str

    def build_timeshift_pipeline(self, stream: StreamInfo) -> str:
        """
        Timeshift pipeline'ı (canlı TV duraklatma/geri sarma).

        Ring buffer ile döngüsel kayıt yapar.
        """
        TIMESHIFT_BUFFER_PATH.mkdir(parents=True, exist_ok=True)
        ts_file = str(TIMESHIFT_BUFFER_PATH / "timeshift.ts")

        pids = f"{stream.video_pid}:{stream.audio_pid}:{stream.pcr_pid}:{stream.pmt_pid}"
        dvb_src = f"dvbsrc adapter={self.adapter_num} frontend={self.frontend_num} pids={pids}"

        video_dec = self._get_video_decoder_element(stream.video_codec)
        audio_dec = self._get_audio_decoder_element(stream.audio_codec)

        pipeline_str = (
            f"{dvb_src} ! tee name=t "

            # Timeshift buffer'a yaz
            f"t. ! queue ! filesink location={ts_file} "

            # Oynatma (filesrc ile buffer'dan oku)
            f"t. ! queue ! tsdemux name=demux "
            f"demux. ! queue ! {video_dec} ! videoconvert ! autovideosink sync=true "
            f"demux. ! queue ! {audio_dec} ! audioconvert ! autoaudiosink sync=true"
        )

        return pipeline_str

    def build_iptv_pipeline(self, url: str) -> str:
        """
        IPTV/OTT oynatma pipeline'ı.

        HLS, MPEG-DASH, RTSP ve UDP multicast destekli.
        """
        if url.startswith("udp://"):
            source = f"udpsrc uri={url} caps=\"video/mpegts\""
        elif url.startswith("rtsp://"):
            source = f"rtspsrc location={url} latency=200"
        elif url.endswith(".m3u8") or "m3u8" in url:
            source = f"souphttpsrc location={url} ! hlsdemux"
        else:
            source = f"uridecodebin uri={url} name=decoder"

        pipeline_str = (
            f"{source} ! tsdemux name=demux "
            f"demux. ! queue ! decodebin ! videoconvert ! autovideosink sync=true "
            f"demux. ! queue ! decodebin ! audioconvert ! autoaudiosink sync=true"
        )

        return pipeline_str

    def build_file_playback_pipeline(self, filepath: str) -> str:
        """Dosya oynatma pipeline'ı (PVR kayıtları, USB medya)."""
        pipeline_str = (
            f"filesrc location={filepath} ! "
            f"decodebin name=decoder "
            f"decoder. ! queue ! videoconvert ! autovideosink sync=true "
            f"decoder. ! queue ! audioconvert ! autoaudiosink sync=true"
        )
        return pipeline_str

    # ─── Pipeline Kontrol ────────────────────────────────────────────────

    def play(self, pipeline_str: str):
        """Pipeline'ı başlat."""
        if not GST_AVAILABLE:
            print(f"▶️  [SİMÜLASYON] Pipeline başlatıldı")
            print(f"   {pipeline_str[:100]}...")
            self.state = PlaybackState.PLAYING
            return

        try:
            self.pipeline = Gst.parse_launch(pipeline_str)

            # Bus mesajlarını dinle
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message::eos", self._on_eos)
            bus.connect("message::error", self._on_bus_error)
            bus.connect("message::state-changed", self._on_bus_state_changed)
            bus.connect("message::buffering", self._on_buffering)

            self.pipeline.set_state(Gst.State.PLAYING)
            self.state = PlaybackState.PLAYING
            print("▶️  Pipeline başlatıldı")

            # GLib main loop
            self.main_loop = GLib.MainLoop()
            self._loop_thread = threading.Thread(target=self.main_loop.run, daemon=True)
            self._loop_thread.start()

        except Exception as e:
            print(f"❌ Pipeline hatası: {e}")
            self.state = PlaybackState.ERROR

    def stop(self):
        """Pipeline'ı durdur."""
        if self.pipeline and GST_AVAILABLE:
            self.pipeline.set_state(Gst.State.NULL)
        if self.main_loop:
            self.main_loop.quit()

        self.state = PlaybackState.STOPPED
        self.pipeline = None
        print("⏹️  Pipeline durduruldu")

    def pause(self):
        """Pipeline'ı duraklat."""
        if self.pipeline and GST_AVAILABLE:
            self.pipeline.set_state(Gst.State.PAUSED)
        self.state = PlaybackState.PAUSED
        print("⏸️  Duraklatıldı")

    def resume(self):
        """Duraklamayı kaldır."""
        if self.pipeline and GST_AVAILABLE:
            self.pipeline.set_state(Gst.State.PLAYING)
        self.state = PlaybackState.PLAYING
        print("▶️  Devam ediyor")

    def seek(self, position_ns: int):
        """Belirtilen pozisyona atla (nanosaniye)."""
        if self.pipeline and GST_AVAILABLE:
            self.pipeline.seek_simple(
                Gst.Format.TIME,
                Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                position_ns
            )
            print(f"⏩ Pozisyon: {position_ns / Gst.SECOND:.1f}s")

    def get_position(self) -> float:
        """Mevcut pozisyonu saniye cinsinden al."""
        if self.pipeline and GST_AVAILABLE:
            success, position = self.pipeline.query_position(Gst.Format.TIME)
            if success:
                return position / Gst.SECOND
        return 0.0

    def get_duration(self) -> float:
        """Toplam süreyi saniye cinsinden al."""
        if self.pipeline and GST_AVAILABLE:
            success, duration = self.pipeline.query_duration(Gst.Format.TIME)
            if success:
                return duration / Gst.SECOND
        return 0.0

    def set_volume(self, volume: float):
        """Ses seviyesini ayarla (0.0 - 1.0)."""
        if self.pipeline and GST_AVAILABLE:
            audio_sink = self.pipeline.get_by_name("audiosink")
            if audio_sink:
                audio_sink.set_property("volume", max(0.0, min(1.0, volume)))

    def set_mute(self, mute: bool):
        """Ses kıs/aç."""
        if self.pipeline and GST_AVAILABLE:
            audio_sink = self.pipeline.get_by_name("audiosink")
            if audio_sink:
                audio_sink.set_property("mute", mute)

    # ─── PVR (Kayıt) ────────────────────────────────────────────────────

    def start_recording(self, stream: StreamInfo, channel_name: str,
                        duration_min: int = 0) -> Optional[PVRRecording]:
        """PVR kaydı başlat."""
        PVR_DEFAULT_PATH.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_name = channel_name.replace(" ", "_").replace("/", "-")
        filename = f"{safe_name}_{timestamp}.ts"
        filepath = PVR_DEFAULT_PATH / filename

        recording = PVRRecording(
            filename=filename,
            channel_name=channel_name,
            start_time=time.time(),
            duration=duration_min,
            file_path=str(filepath),
            is_active=True,
        )

        pipeline_str = self.build_pvr_pipeline(stream, str(filepath))
        self.play(pipeline_str)
        self.state = PlaybackState.RECORDING

        self._pvr_recordings.append(recording)
        print(f"🔴 Kayıt başladı: {filename}")

        if duration_min > 0:
            timer = threading.Timer(duration_min * 60, self._stop_recording_timer, [recording])
            timer.daemon = True
            timer.start()
            print(f"   ⏱️  Zamanlayıcı: {duration_min} dakika")

        return recording

    def stop_recording(self):
        """Aktif kaydı durdur."""
        for rec in self._pvr_recordings:
            if rec.is_active:
                rec.is_active = False
                rec.file_size = os.path.getsize(rec.file_path) if os.path.exists(rec.file_path) else 0
                print(f"⏹️  Kayıt durduruldu: {rec.filename} ({rec.file_size / 1024 / 1024:.1f} MB)")

        self.stop()

    def _stop_recording_timer(self, recording: PVRRecording):
        """Zamanlayıcı ile kayıt durdurma."""
        print(f"⏱️  Kayıt süresi doldu: {recording.filename}")
        self.stop_recording()

    def list_recordings(self) -> list[PVRRecording]:
        """Kayıt listesini al."""
        return self._pvr_recordings

    # ─── Timeshift ───────────────────────────────────────────────────────

    def start_timeshift(self, stream: StreamInfo):
        """Timeshift başlat (canlı TV duraklatma)."""
        pipeline_str = self.build_timeshift_pipeline(stream)
        self.play(pipeline_str)
        self.state = PlaybackState.TIMESHIFT
        print("⏯️  Timeshift aktif")

    # ─── Bus Callback'leri ───────────────────────────────────────────────

    def _on_eos(self, bus, msg):
        print("📺 Yayın sonu (EOS)")
        self.stop()

    def _on_bus_error(self, bus, msg):
        err, debug = msg.parse_error()
        print(f"❌ Pipeline hatası: {err.message}")
        print(f"   Debug: {debug}")
        self.state = PlaybackState.ERROR
        if self._on_error:
            self._on_error(err.message)

    def _on_bus_state_changed(self, bus, msg):
        if msg.src == self.pipeline:
            old, new, pending = msg.parse_state_changed()
            if self._on_state_change:
                self._on_state_change(old.value_nick, new.value_nick)

    def _on_buffering(self, bus, msg):
        percent = msg.parse_buffering()
        if percent < 100:
            self.state = PlaybackState.BUFFERING
            if self.pipeline:
                self.pipeline.set_state(Gst.State.PAUSED)
        else:
            self.state = PlaybackState.PLAYING
            if self.pipeline:
                self.pipeline.set_state(Gst.State.PLAYING)


# ─── Pipeline Şablonları (CLI test için) ─────────────────────────────────────

PIPELINE_TEMPLATES = {
    "dvb_live_basic": (
        "dvbsrc adapter=0 ! tsdemux ! decodebin ! autovideosink"
    ),
    "dvb_live_hd": (
        "dvbsrc adapter=0 pids=101:201:101:1001 ! "
        "tsdemux name=demux "
        "demux. ! queue ! v4l2h264dec ! videoconvert ! autovideosink "
        "demux. ! queue ! avdec_aac ! audioconvert ! alsasink"
    ),
    "dvb_live_4k_hevc": (
        "dvbsrc adapter=0 pids=301:401:301:3001 ! "
        "tsdemux name=demux "
        "demux. ! queue max-size-time=5000000000 ! v4l2h265dec ! "
        "videoconvert ! video/x-raw,width=3840,height=2160 ! autovideosink "
        "demux. ! queue ! avdec_aac ! audioconvert ! alsasink"
    ),
    "dvb_record_ts": (
        "dvbsrc adapter=0 pids=101:201:101:1001 ! "
        "tee name=t "
        "t. ! queue ! filesink location=/media/pvr/recording.ts "
        "t. ! queue ! tsdemux name=demux "
        "demux. ! queue ! decodebin ! autovideosink "
        "demux. ! queue ! decodebin ! autoaudiosink"
    ),
    "iptv_hls": (
        "souphttpsrc location=URL ! hlsdemux ! "
        "tsdemux name=demux "
        "demux. ! queue ! decodebin ! autovideosink "
        "demux. ! queue ! decodebin ! autoaudiosink"
    ),
    "iptv_udp": (
        "udpsrc uri=udp://239.0.0.1:5000 caps=\"video/mpegts\" ! "
        "tsdemux name=demux "
        "demux. ! queue ! decodebin ! autovideosink "
        "demux. ! queue ! decodebin ! autoaudiosink"
    ),
    "file_playback": (
        "filesrc location=FILE ! decodebin name=dec "
        "dec. ! queue ! videoconvert ! autovideosink "
        "dec. ! queue ! audioconvert ! autoaudiosink"
    ),
    "ai_upscale_sd_to_hd": (
        "dvbsrc adapter=0 ! tsdemux name=demux "
        "demux. ! queue ! decodebin ! videoconvert ! "
        "video/x-raw,format=RGB ! "
        "tensor_converter ! tensor_filter framework=tensorflow-lite "
        "model=/opt/apexsat/models/realesrgan_x2.tflite ! "
        "tensor_decoder mode=direct_video ! videoconvert ! "
        "autovideosink "
        "demux. ! queue ! decodebin ! audioconvert ! autoaudiosink"
    ),
    "test_pattern": (
        "videotestsrc pattern=smpte ! videoconvert ! autovideosink "
        "audiotestsrc wave=sine freq=440 ! audioconvert ! autoaudiosink"
    ),
}


# ─── Ana Program ─────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="APEXSAT AI - Medya Pipeline Yöneticisi")
    parser.add_argument("--template", choices=PIPELINE_TEMPLATES.keys(),
                        help="Pipeline şablonu")
    parser.add_argument("--custom", type=str, help="Özel pipeline string")
    parser.add_argument("--adapter", type=int, default=0, help="DVB adaptör")
    parser.add_argument("--url", type=str, help="IPTV URL")
    parser.add_argument("--file", type=str, help="Dosya yolu")
    parser.add_argument("--record", action="store_true", help="Kayıt modu")
    parser.add_argument("--list-templates", action="store_true", help="Şablonları listele")

    args = parser.parse_args()

    if args.list_templates:
        print("\n📋 Pipeline Şablonları:")
        print("─" * 60)
        for name, pipeline in PIPELINE_TEMPLATES.items():
            print(f"\n🔹 {name}:")
            print(f"   {pipeline}")
        return

    pipeline = MediaPipeline(args.adapter)

    if args.template:
        pipeline_str = PIPELINE_TEMPLATES[args.template]
        if args.url:
            pipeline_str = pipeline_str.replace("URL", args.url)
        if args.file:
            pipeline_str = pipeline_str.replace("FILE", args.file)

        print(f"\n▶️  Pipeline: {args.template}")
        print(f"   {pipeline_str[:100]}...\n")
        pipeline.play(pipeline_str)

        try:
            print("Çıkmak için Ctrl+C basın...")
            while pipeline.state == PlaybackState.PLAYING:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n")
            pipeline.stop()

    elif args.custom:
        pipeline.play(args.custom)
    else:
        # Test modu
        print("=" * 50)
        print("  APEXSAT AI - Medya Pipeline Testi")
        print("=" * 50)

        stream = StreamInfo(
            video_pid=101, audio_pid=201, pcr_pid=101, pmt_pid=1001,
            video_codec="h264", audio_codec="aac",
            width=1920, height=1080, is_hd=True
        )

        print("\n📺 Canlı TV Pipeline:")
        pipe_str = pipeline.build_live_tv_pipeline(stream)
        print(f"   {pipe_str[:100]}...")

        print("\n🔴 PVR Kayıt Pipeline:")
        pipe_str = pipeline.build_pvr_pipeline(stream, "/media/pvr/test.ts")
        print(f"   {pipe_str[:100]}...")

        print("\n⏯️  Timeshift Pipeline:")
        pipe_str = pipeline.build_timeshift_pipeline(stream)
        print(f"   {pipe_str[:100]}...")

        print("\n🌐 IPTV Pipeline (HLS):")
        pipe_str = pipeline.build_iptv_pipeline("https://example.com/stream.m3u8")
        print(f"   {pipe_str[:100]}...")

        print("\n✅ Pipeline test tamamlandı")


if __name__ == "__main__":
    main()
