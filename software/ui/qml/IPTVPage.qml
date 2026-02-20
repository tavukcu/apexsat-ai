import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        Text {
            text: "🌐 IPTV / OTT"
            font.pixelSize: Theme.fontTitle
            color: Theme.textPrimary
        }

        // Platform kartları
        GridView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 280
            cellHeight: 160
            clip: true

            model: ListModel {
                ListElement { name: "M3U Playlist"; icon: "📋"; desc: "M3U/M3U8 playlist yükle"; color: "#2196F3" }
                ListElement { name: "Xtream Codes"; icon: "🔗"; desc: "Xtream API bağlantısı"; color: "#4CAF50" }
                ListElement { name: "YouTube"; icon: "▶️"; desc: "YouTube video ve canlı yayın"; color: "#FF0000" }
                ListElement { name: "Kodi"; icon: "🎬"; desc: "Kodi medya merkezi"; color: "#17B2E7" }
                ListElement { name: "Stalker Portal"; icon: "📡"; desc: "Stalker/MAG portal"; color: "#FF9800" }
                ListElement { name: "Tarayıcı"; icon: "🌐"; desc: "Web tarayıcısı"; color: "#9C27B0" }
            }

            delegate: Rectangle {
                width: 270
                height: 150
                radius: Theme.radiusL
                color: iptvArea.containsMouse ? Qt.lighter(model.color, 1.3) : model.color

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: Theme.spacingS
                    Text { text: model.icon; font.pixelSize: 48; Layout.alignment: Qt.AlignHCenter }
                    Text { text: model.name; font.pixelSize: Theme.fontBody; font.bold: true; color: "white"; Layout.alignment: Qt.AlignHCenter }
                    Text { text: model.desc; font.pixelSize: Theme.fontSmall; color: Qt.rgba(1,1,1,0.7); Layout.alignment: Qt.AlignHCenter }
                }

                MouseArea { id: iptvArea; anchors.fill: parent; hoverEnabled: true }
            }
        }
    }
}
