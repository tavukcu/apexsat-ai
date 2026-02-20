import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * EPG Program Bloku - Tek bir program kutusu
 */
Rectangle {
    id: programBlock

    property real blockWidth: 200
    property real blockHeight: 68
    property string programTitle: ""
    property bool isCurrent: false

    width: blockWidth
    height: blockHeight
    radius: Theme.radiusS
    color: {
        if (blockArea.containsMouse || blockArea.activeFocus)
            return Theme.bgCardHover
        if (isCurrent)
            return Qt.darker(Theme.accent, 2.0)
        return Theme.bgCard
    }

    border.color: isCurrent ? Theme.accent : Theme.divider
    border.width: isCurrent ? 2 : 1
    clip: true

    Behavior on color {
        ColorAnimation { duration: Theme.animDurationFast }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 2

        Text {
            text: programTitle
            font.pixelSize: Theme.fontCaption
            font.bold: true
            color: Theme.textPrimary
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        // İlerleme çubuğu (sadece şimdiki program)
        Rectangle {
            visible: isCurrent
            Layout.fillWidth: true
            height: 3
            radius: 1.5
            color: Theme.divider

            Rectangle {
                width: parent.width * 0.45
                height: parent.height
                radius: parent.radius
                color: Theme.accent
            }
        }
    }

    MouseArea {
        id: blockArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: console.log("Program seçildi:", programTitle)
    }
}
