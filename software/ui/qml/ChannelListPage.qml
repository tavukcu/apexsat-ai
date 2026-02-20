import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

/**
 * Kanal Listesi - A-Z, tür bazlı, favori filtreleme
 */
Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        // Başlık ve filtre sekmeler
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingM

            Text {
                text: "📺 Kanallar"
                font.pixelSize: Theme.fontTitle
                color: Theme.textPrimary
            }

            Item { Layout.fillWidth: true }

            // Filtre butonları
            Row {
                spacing: Theme.spacingS

                Repeater {
                    model: ["Tümü", "TV", "HD", "Radyo", "Favoriler"]

                    delegate: Rectangle {
                        width: filterText.implicitWidth + 24
                        height: 36
                        radius: 18
                        color: filterIdx === channelFilter.currentIndex
                               ? Theme.accent : Theme.bgCard

                        property int filterIdx: index

                        Text {
                            id: filterText
                            anchors.centerIn: parent
                            text: modelData
                            font.pixelSize: Theme.fontCaption
                            color: "white"
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: channelFilter.currentIndex = index
                        }
                    }
                }
            }
        }

        QtObject {
            id: channelFilter
            property int currentIndex: 0
        }

        // Kanal Grid
        GridView {
            id: channelGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            cellWidth: 320
            cellHeight: 80
            clip: true
            focus: true

            model: ListModel {
                ListElement { num: 1; name: "TRT 1 HD"; genre: "Genel"; hd: true; fav: true; current: "Ana Haber" }
                ListElement { num: 2; name: "TRT 2"; genre: "Kültür"; hd: false; fav: false; current: "Belgesel" }
                ListElement { num: 3; name: "TRT Haber"; genre: "Haber"; hd: true; fav: true; current: "Canlı Yayın" }
                ListElement { num: 4; name: "TRT Spor"; genre: "Spor"; hd: true; fav: false; current: "Maç Özeti" }
                ListElement { num: 5; name: "TRT World"; genre: "Haber"; hd: true; fav: false; current: "Roundtable" }
                ListElement { num: 6; name: "TRT Belgesel"; genre: "Belgesel"; hd: true; fav: true; current: "Doğa" }
                ListElement { num: 7; name: "TRT Müzik"; genre: "Müzik"; hd: false; fav: false; current: "Konser" }
                ListElement { num: 8; name: "TRT Çocuk"; genre: "Çocuk"; hd: false; fav: false; current: "Çizgi Film" }
                ListElement { num: 10; name: "ATV"; genre: "Genel"; hd: true; fav: true; current: "Kuruluş Osman" }
                ListElement { num: 11; name: "A Haber"; genre: "Haber"; hd: true; fav: false; current: "Ana Haber" }
                ListElement { num: 13; name: "Show TV"; genre: "Genel"; hd: true; fav: true; current: "Çarkıfelek" }
                ListElement { num: 14; name: "Habertürk"; genre: "Haber"; hd: true; fav: false; current: "Gündem" }
                ListElement { num: 16; name: "Star TV"; genre: "Genel"; hd: true; fav: false; current: "Dizi" }
                ListElement { num: 17; name: "NTV"; genre: "Haber"; hd: true; fav: true; current: "Ekonomi" }
                ListElement { num: 18; name: "Kanal D HD"; genre: "Genel"; hd: true; fav: true; current: "Kara Sevda" }
                ListElement { num: 19; name: "CNN Türk"; genre: "Haber"; hd: true; fav: false; current: "5N1K" }
                ListElement { num: 20; name: "FOX TV"; genre: "Genel"; hd: true; fav: true; current: "Dizi" }
                ListElement { num: 21; name: "TV8"; genre: "Genel"; hd: true; fav: false; current: "Survivor" }
            }

            delegate: Rectangle {
                width: channelGrid.cellWidth - 8
                height: channelGrid.cellHeight - 8
                radius: Theme.radiusM
                color: chArea.containsMouse || GridView.isCurrentItem
                       ? Theme.bgCardHover : Theme.bgCard

                Behavior on color {
                    ColorAnimation { duration: Theme.animDurationFast }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingS
                    spacing: Theme.spacingM

                    // Kanal numarası
                    Rectangle {
                        width: 48; height: 48
                        radius: Theme.radiusS
                        color: Theme.accent

                        Text {
                            anchors.centerIn: parent
                            text: model.num
                            font.pixelSize: Theme.fontBody
                            font.bold: true
                            color: "white"
                        }
                    }

                    // Kanal bilgisi
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        RowLayout {
                            spacing: 6

                            Text {
                                text: model.name
                                font.pixelSize: Theme.fontCaption
                                font.bold: true
                                color: Theme.textPrimary
                            }

                            // HD badge
                            Rectangle {
                                visible: model.hd
                                width: 28; height: 16
                                radius: 3
                                color: Theme.success

                                Text {
                                    anchors.centerIn: parent
                                    text: "HD"
                                    font.pixelSize: 10
                                    font.bold: true
                                    color: "white"
                                }
                            }

                            // Favori yıldız
                            Text {
                                visible: model.fav
                                text: "⭐"
                                font.pixelSize: 12
                            }
                        }

                        Text {
                            text: model.current
                            font.pixelSize: Theme.fontSmall
                            color: Theme.textSecondary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }
                }

                MouseArea {
                    id: chArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        channelGrid.currentIndex = index
                        console.log("Kanal seçildi:", model.name)
                    }
                    onDoubleClicked: console.log("Kanala geçiş:", model.name)
                }

                // Focus border
                Rectangle {
                    anchors.fill: parent
                    radius: Theme.radiusM
                    color: "transparent"
                    border.color: Theme.accent
                    border.width: GridView.isCurrentItem ? 2 : 0
                }
            }
        }
    }
}
