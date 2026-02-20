import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        Text {
            text: "🔴 Kayıtlar"
            font.pixelSize: Theme.fontTitle
            color: Theme.textPrimary
        }

        ListView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 8
            clip: true

            model: ListModel {
                ListElement { title: "Kuruluş Osman - Bölüm 145"; channel: "ATV"; date: "19.02.2026"; duration: "120 dk"; size: "4.2 GB" }
                ListElement { title: "Ana Haber Bülteni"; channel: "TRT 1"; date: "19.02.2026"; duration: "60 dk"; size: "2.1 GB" }
                ListElement { title: "Survivor"; channel: "TV8"; date: "18.02.2026"; duration: "180 dk"; size: "6.3 GB" }
                ListElement { title: "Belgesel: Mavi Gezegen"; channel: "TRT Belgesel"; date: "17.02.2026"; duration: "90 dk"; size: "3.1 GB" }
            }

            delegate: Rectangle {
                width: parent ? parent.width : 0
                height: 80
                radius: Theme.radiusM
                color: recArea.containsMouse ? Theme.bgCardHover : Theme.bgCard

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingM
                    spacing: Theme.spacingM

                    Rectangle {
                        width: 56; height: 56; radius: Theme.radiusS
                        color: Theme.accent
                        Text { anchors.centerIn: parent; text: "▶"; font.pixelSize: 24; color: "white" }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        Text { text: model.title; font.pixelSize: Theme.fontBody; font.bold: true; color: Theme.textPrimary }
                        Text { text: model.channel + " • " + model.date + " • " + model.duration; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary }
                    }

                    Text { text: model.size; font.pixelSize: Theme.fontCaption; color: Theme.textMuted }
                }

                MouseArea { id: recArea; anchors.fill: parent; hoverEnabled: true }
            }
        }
    }
}
