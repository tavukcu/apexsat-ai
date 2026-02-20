import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        Text {
            text: "📁 Medya Tarayıcı"
            font.pixelSize: Theme.fontTitle
            color: Theme.textPrimary
        }

        // Kaynak seçim
        Row {
            spacing: Theme.spacingM

            Repeater {
                model: ["USB Disk", "microSD", "Ağ (SMB)", "NFS"]
                delegate: Rectangle {
                    width: 160; height: 48; radius: Theme.radiusM
                    color: index === 0 ? Theme.accent : Theme.bgCard
                    Text { anchors.centerIn: parent; text: modelData; font.pixelSize: Theme.fontCaption; color: "white" }
                }
            }
        }

        // Dosya listesi
        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 4
            clip: true

            model: ListModel {
                ListElement { name: "Filmler"; ftype: "folder"; size: "" }
                ListElement { name: "Diziler"; ftype: "folder"; size: "" }
                ListElement { name: "Müzik"; ftype: "folder"; size: "" }
                ListElement { name: "Kayıtlar"; ftype: "folder"; size: "" }
                ListElement { name: "tatil_video.mp4"; ftype: "video"; size: "2.3 GB" }
                ListElement { name: "aile_foto.jpg"; ftype: "image"; size: "4.5 MB" }
            }

            delegate: Rectangle {
                width: parent ? parent.width : 0
                height: 56
                radius: Theme.radiusS
                color: fileArea.containsMouse ? Theme.bgCardHover : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingS
                    spacing: Theme.spacingM

                    Text {
                        text: model.ftype === "folder" ? "📁" : model.ftype === "video" ? "🎬" : "🖼️"
                        font.pixelSize: 24
                    }
                    Text { text: model.name; font.pixelSize: Theme.fontBody; color: Theme.textPrimary; Layout.fillWidth: true }
                    Text { text: model.size; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
                }

                MouseArea { id: fileArea; anchors.fill: parent; hoverEnabled: true }
            }
        }
    }
}
