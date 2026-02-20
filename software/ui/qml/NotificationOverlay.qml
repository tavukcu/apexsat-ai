import QtQuick 2.15
import QtQuick.Layouts 1.15

Item {
    id: notifOverlay
    width: 350
    height: notifColumn.height

    function show(title, message, type) {
        notifModel.append({title: title, message: message, ntype: type || "info"})
    }

    ColumnLayout {
        id: notifColumn
        width: parent.width
        spacing: 8

        Repeater {
            model: ListModel { id: notifModel }

            delegate: Rectangle {
                Layout.fillWidth: true
                height: 60
                radius: Theme.radiusM
                color: Qt.rgba(0.1, 0.1, 0.2, 0.95)
                border.color: model.ntype === "error" ? Theme.error : Theme.accent
                border.width: 1
                opacity: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 10

                    Text {
                        text: model.ntype === "error" ? "❌" : model.ntype === "success" ? "✅" : "ℹ️"
                        font.pixelSize: 20
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text { text: model.title; font.pixelSize: Theme.fontCaption; font.bold: true; color: Theme.textPrimary }
                        Text { text: model.message; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary; elide: Text.ElideRight; Layout.fillWidth: true }
                    }
                }

                // Otomatik kapanma
                Timer {
                    interval: 4000
                    running: true
                    onTriggered: {
                        fadeOut.start()
                    }
                }

                NumberAnimation on opacity {
                    id: fadeOut
                    running: false
                    to: 0
                    duration: 500
                    onFinished: notifModel.remove(index)
                }
            }
        }
    }
}
