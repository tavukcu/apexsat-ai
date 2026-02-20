#!/usr/bin/env python3
"""
APEXSAT AI - Qt/QML UI Launcher

Kullanım:
    python3 main.py                    # UI'ı başlat
    python3 main.py --fullscreen       # Tam ekran
    python3 main.py --resolution 1280x720  # Özel çözünürlük
"""

import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtQml import QQmlApplicationEngine
    from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, pyqtProperty
    QT_AVAILABLE = True
except ImportError:
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtQml import QQmlApplicationEngine
        from PyQt6.QtCore import QUrl, QObject
        QT_AVAILABLE = True
    except ImportError:
        QT_AVAILABLE = False


class APEXSATBackend(QObject):
    """QML'den erişilebilen Python backend."""

    channelChanged = pyqtSignal(int, str, arguments=["channelNum", "channelName"])
    volumeChanged = pyqtSignal(int, arguments=["volume"])

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_channel = 1
        self._volume = 50

    @pyqtSlot(int, str)
    def changeChannel(self, num, name):
        """Kanal değiştir."""
        self._current_channel = num
        print(f"📺 Kanal değiştirildi: {num} - {name}")
        self.channelChanged.emit(num, name)

    @pyqtSlot(int)
    def setVolume(self, level):
        """Ses seviyesini ayarla."""
        self._volume = max(0, min(100, level))
        print(f"🔊 Ses: {self._volume}")
        self.volumeChanged.emit(self._volume)

    @pyqtSlot(str)
    def processVoiceCommand(self, command):
        """Sesli komutu işle."""
        print(f"🎙️ Sesli komut: {command}")

    @pyqtSlot(result=str)
    def getVersion(self):
        return "APEXSAT AI v1.0"


def main():
    if not QT_AVAILABLE:
        print("❌ PyQt5/PyQt6 bulunamadı!")
        print("   Yüklemek için: pip install PyQt5 PyQt5-sip")
        print("")
        print("   UI dosyaları oluşturuldu:")
        print(f"   - {SCRIPT_DIR}/main.qml")
        print(f"   - {SCRIPT_DIR}/qml/ (bileşenler)")
        print("")
        print("   Qt Creator ile açmak için: qtcreator main.qml")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setOrganizationName("DincerTavukculuk")
    app.setApplicationName("APEXSAT AI")

    engine = QQmlApplicationEngine()

    # Backend'i QML'e expose et
    backend = APEXSATBackend()
    engine.rootContext().setContextProperty("backend", backend)

    # QML import path
    engine.addImportPath(str(SCRIPT_DIR / "qml"))

    # Ana QML dosyasını yükle
    qml_file = SCRIPT_DIR / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        print("❌ QML yüklenemedi!")
        sys.exit(1)

    print("✅ APEXSAT AI UI başlatıldı")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
