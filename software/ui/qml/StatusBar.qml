import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * Üst durum çubuğu - Saat, sinyal, kayıt durumu, ağ
 */
Rectangle {
    id: statusBar
    color: Qt.rgba(0, 0, 0, 0.85)

    property bool isRecording: false

    function toggleRecording() {
        isRecording = !isRecording
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingL
        anchors.rightMargin: Theme.spacingL
        spacing: Theme.spacingM

        // APEXSAT Logo
        Text {
            text: "APEXSAT AI"
            font.pixelSize: Theme.fontBody
            font.bold: true
            color: Theme.accent
        }

        // Kanal bilgisi
        Text {
            id: channelInfo
            text: "TRT 1 HD"
            font.pixelSize: Theme.fontCaption
            color: Theme.textSecondary
        }

        Item { Layout.fillWidth: true }

        // Kayıt göstergesi
        Row {
            spacing: 6
            visible: statusBar.isRecording

            Rectangle {
                width: 10; height: 10
                radius: 5
                color: Theme.error

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.3; duration: 500 }
                    NumberAnimation { to: 1.0; duration: 500 }
                }
            }

            Text {
                text: "REC"
                font.pixelSize: Theme.fontSmall
                font.bold: true
                color: Theme.error
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        // Sinyal gücü
        Row {
            spacing: 3
            Repeater {
                model: 5
                Rectangle {
                    width: 4
                    height: 8 + index * 4
                    radius: 1
                    color: index < 4 ? Theme.success : Theme.textMuted
                    anchors.bottom: parent.bottom
                }
            }
        }

        // WiFi ikonu
        Text {
            text: "WiFi"
            font.pixelSize: Theme.fontSmall
            color: Theme.success
        }

        // Saat
        Text {
            id: clockText
            font.pixelSize: Theme.fontBody
            font.bold: true
            color: Theme.textPrimary

            Timer {
                interval: 1000
                running: true
                repeat: true
                triggeredOnStart: true
                onTriggered: {
                    var now = new Date()
                    clockText.text = Qt.formatTime(now, "HH:mm")
                }
            }
        }
    }
}
