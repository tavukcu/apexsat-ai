PIPER_TTS_VERSION = 2023.11.14-2
PIPER_TTS_SITE = https://github.com/rhasspy/piper/archive/refs/tags/$(PIPER_TTS_VERSION).tar.gz
PIPER_TTS_LICENSE = MIT
PIPER_TTS_INSTALL_TARGET = YES

PIPER_TTS_DEPENDENCIES = onnxruntime

$(eval $(cmake-package))
