import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * Yan menü - Ana navigasyon (D-pad ile erişim)
 */
Rectangle {
    id: sideMenu
    color: Theme.bgSecondary
    clip: true

    property bool expanded: false
    signal menuItemSelected(string page)

    function toggle() {
        expanded = !expanded
    }

    Behavior on Layout.preferredWidth {
        NumberAnimation { duration: Theme.animDuration; easing.type: Easing.OutCubic }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: Theme.spacingL
        spacing: 4
        visible: sideMenu.expanded

        Repeater {
            model: ListModel {
                ListElement { icon: "🏠"; label: "Ana Sayfa"; page: "home" }
                ListElement { icon: "📺"; label: "Kanallar"; page: "channels" }
                ListElement { icon: "📋"; label: "Program Rehberi"; page: "epg" }
                ListElement { icon: "🔴"; label: "Kayıtlar"; page: "recordings" }
                ListElement { icon: "🌐"; label: "IPTV"; page: "iptv" }
                ListElement { icon: "📁"; label: "Medya"; page: "media" }
                ListElement { icon: "⚙️"; label: "Ayarlar"; page: "settings" }
            }

            delegate: Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 56
                Layout.leftMargin: 8
                Layout.rightMargin: 8
                radius: Theme.radiusM
                color: menuItemArea.containsMouse || menuItemArea.activeFocus
                       ? Theme.bgCardHover : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacingM
                    spacing: Theme.spacingM

                    Text {
                        text: model.icon
                        font.pixelSize: Theme.fontHeading
                    }

                    Text {
                        text: model.label
                        font.pixelSize: Theme.fontBody
                        color: Theme.textPrimary
                        Layout.fillWidth: true
                    }
                }

                MouseArea {
                    id: menuItemArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sideMenu.menuItemSelected(model.page)
                }

                Keys.onReturnPressed: sideMenu.menuItemSelected(model.page)
            }
        }

        Item { Layout.fillHeight: true }
    }
}
