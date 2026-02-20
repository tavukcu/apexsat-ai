import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        Text {
            text: "⚙️ Ayarlar"
            font.pixelSize: Theme.fontTitle
            color: Theme.textPrimary
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 4
            clip: true

            model: ListModel {
                ListElement { icon: "📡"; title: "Uydu Ayarları"; desc: "Uydu tarama, DiSEqC, LNB ayarları" }
                ListElement { icon: "🌐"; title: "Ağ Ayarları"; desc: "WiFi, Ethernet, IPTV bağlantıları" }
                ListElement { icon: "🖥️"; title: "Görüntü Ayarları"; desc: "Çözünürlük, HDR, AI upscaling" }
                ListElement { icon: "🔊"; title: "Ses Ayarları"; desc: "Audio çıkış, Dolby, ses dili" }
                ListElement { icon: "🎙️"; title: "Sesli Asistan"; desc: "APEX Voice ayarları, wake word" }
                ListElement { icon: "🤖"; title: "AI Ayarları"; desc: "Öneri motoru, super resolution, NPU" }
                ListElement { icon: "🔴"; title: "PVR Ayarları"; desc: "Kayıt dizini, timeshift, zamanlayıcı" }
                ListElement { icon: "🔒"; title: "Ebeveyn Kontrolü"; desc: "PIN, yaş sınırı, kanal kilidi" }
                ListElement { icon: "🌍"; title: "Dil ve Bölge"; desc: "Menü dili, altyazı dili, saat dilimi" }
                ListElement { icon: "📦"; title: "Sistem Güncelleme"; desc: "OTA güncelleme, sürüm bilgisi" }
                ListElement { icon: "ℹ️"; title: "Hakkında"; desc: "APEXSAT AI v1.0 - Dinçer Tavukçuluk" }
            }

            delegate: Rectangle {
                width: parent ? parent.width : 0
                height: 72
                radius: Theme.radiusM
                color: settArea.containsMouse || ListView.isCurrentItem
                       ? Theme.bgCardHover : Theme.bgCard

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingM
                    spacing: Theme.spacingM

                    Text { text: model.icon; font.pixelSize: 32 }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text { text: model.title; font.pixelSize: Theme.fontBody; color: Theme.textPrimary }
                        Text { text: model.desc; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary }
                    }

                    Text { text: "▶"; font.pixelSize: Theme.fontBody; color: Theme.textMuted }
                }

                MouseArea { id: settArea; anchors.fill: parent; hoverEnabled: true }
            }
        }
    }
}
