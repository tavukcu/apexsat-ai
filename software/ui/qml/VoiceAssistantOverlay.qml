import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * Sesli Asistan Overlay - Mikrofon butonu basıldığında açılır
 */
Rectangle {
    id: voiceOverlay
    width: 500
    height: 300
    radius: Theme.radiusL
    color: Qt.rgba(0.05, 0.05, 0.15, 0.95)
    border.color: Theme.accent
    border.width: 2
    visible: false
    opacity: 0

    function show() {
        visible = true
        showAnim.start()
        statusText.text = "Dinliyorum..."
        waveAnim.running = true
    }

    function hide() {
        hideAnim.start()
    }

    function showResult(text, response) {
        statusText.text = response
        waveAnim.running = false
        hideTimer.start()
    }

    NumberAnimation on opacity { id: showAnim; to: 1; duration: 200; running: false }
    NumberAnimation on opacity { id: hideAnim; to: 0; duration: 200; running: false; onFinished: voiceOverlay.visible = false }
    Timer { id: hideTimer; interval: 3000; onTriggered: hide() }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: Theme.spacingL

        // APEX Voice başlığı
        Text {
            text: "🎙️ APEX Voice"
            font.pixelSize: Theme.fontHeading
            font.bold: true
            color: Theme.accent
            Layout.alignment: Qt.AlignHCenter
        }

        // Ses dalgası animasyonu
        Row {
            Layout.alignment: Qt.AlignHCenter
            spacing: 4

            Repeater {
                model: 12

                Rectangle {
                    width: 6
                    height: 20
                    radius: 3
                    color: Theme.accent
                    anchors.verticalCenter: parent.verticalCenter

                    SequentialAnimation on height {
                        id: waveAnim
                        running: false
                        loops: Animation.Infinite
                        NumberAnimation {
                            to: 10 + Math.random() * 50
                            duration: 200 + Math.random() * 300
                        }
                        NumberAnimation {
                            to: 10 + Math.random() * 20
                            duration: 200 + Math.random() * 300
                        }
                    }
                }
            }
        }

        // Durum metni
        Text {
            id: statusText
            text: "Dinliyorum..."
            font.pixelSize: Theme.fontBody
            color: Theme.textPrimary
            Layout.alignment: Qt.AlignHCenter
        }

        // İpucu
        Text {
            text: "\"APEX, TRT 1'e geç\" gibi komutlar verebilirsiniz"
            font.pixelSize: Theme.fontSmall
            color: Theme.textMuted
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
