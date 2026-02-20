import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: Qt.rgba(0, 0, 0, 0.7)

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.spacingL
        anchors.rightMargin: Theme.spacingL
        spacing: Theme.spacingL

        Text { text: "🔴 REC"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
        Text { text: "🟢 OK"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
        Text { text: "🔵 EPG"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
        Text { text: "🟡 Favori"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }

        Item { Layout.fillWidth: true }

        Text { text: "MENU: Menü  |  BACK: Geri  |  MIC: Sesli Komut"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
    }
}
