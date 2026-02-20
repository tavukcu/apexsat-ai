import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * Ana Sayfa - Canlı TV + Öneri Karusel + Hızlı Erişim
 */
Rectangle {
    color: Theme.bgPrimary

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingL

        // ─── Canlı TV Alanı ──────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: parent.height * 0.45
            radius: Theme.radiusL
            color: "#000000"
            border.color: Theme.divider
            border.width: 1

            // Video placeholder (gerçek cihazda VideoOutput olacak)
            Text {
                anchors.centerIn: parent
                text: "📺 Canlı TV\nTRT 1 HD"
                font.pixelSize: Theme.fontHeading
                color: Theme.textSecondary
                horizontalAlignment: Text.AlignHCenter
            }

            // Şimdiki/sonraki program bilgisi
            Rectangle {
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: 80
                radius: Theme.radiusL
                color: Qt.rgba(0, 0, 0, 0.8)

                // Alt köşelerde radius, üst köşelerde düz
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: parent.radius
                    color: parent.color
                }

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingM
                    spacing: 4

                    RowLayout {
                        spacing: Theme.spacingS

                        Rectangle {
                            width: 8; height: 8; radius: 4
                            color: Theme.success
                        }

                        Text {
                            text: "Şimdi: Ana Haber Bülteni"
                            font.pixelSize: Theme.fontCaption
                            font.bold: true
                            color: Theme.textPrimary
                        }

                        // İlerleme çubuğu
                        Rectangle {
                            Layout.fillWidth: true
                            height: 4
                            radius: 2
                            color: Theme.divider

                            Rectangle {
                                width: parent.width * 0.65
                                height: parent.height
                                radius: parent.radius
                                color: Theme.accent
                            }
                        }

                        Text {
                            text: "65%"
                            font.pixelSize: Theme.fontSmall
                            color: Theme.textMuted
                        }
                    }

                    Text {
                        text: "Sonraki: Gönül Dağı (21:00)"
                        font.pixelSize: Theme.fontSmall
                        color: Theme.textSecondary
                    }
                }
            }
        }

        // ─── AI Öneri Karusel ────────────────────────────────────
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingS

            Text {
                text: "🤖 Sizin İçin Öneriler"
                font.pixelSize: Theme.fontHeading
                color: Theme.textPrimary
            }

            ListView {
                id: recommendationList
                Layout.fillWidth: true
                Layout.preferredHeight: 200
                orientation: ListView.Horizontal
                spacing: Theme.spacingM
                clip: true

                model: ListModel {
                    ListElement { title: "Kuruluş Osman"; channel: "ATV"; time: "20:00"; genre: "Dizi"; rating: "8.2" }
                    ListElement { title: "Barbaroslar"; channel: "TRT 1"; time: "20:00"; genre: "Dizi"; rating: "7.8" }
                    ListElement { title: "UEFA Şampiyonlar Ligi"; channel: "TV8"; time: "21:45"; genre: "Spor"; rating: "9.0" }
                    ListElement { title: "Mavi Gezegen"; channel: "TRT Belgesel"; time: "22:00"; genre: "Belgesel"; rating: "9.2" }
                    ListElement { title: "Yeşilçam Klasikleri"; channel: "TRT 2"; time: "23:00"; genre: "Film"; rating: "8.5" }
                    ListElement { title: "Haber Analizi"; channel: "NTV"; time: "21:00"; genre: "Haber"; rating: "7.5" }
                }

                delegate: Rectangle {
                    width: 260
                    height: 190
                    radius: Theme.radiusM
                    color: cardArea.containsMouse || cardArea.activeFocus
                           ? Theme.bgCardHover : Theme.bgCard

                    Behavior on color {
                        ColorAnimation { duration: Theme.animDurationFast }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingM
                        spacing: Theme.spacingS

                        // Tür etiketi
                        Rectangle {
                            width: genreText.implicitWidth + 16
                            height: 24
                            radius: 12
                            color: Theme.accent

                            Text {
                                id: genreText
                                anchors.centerIn: parent
                                text: model.genre
                                font.pixelSize: Theme.fontSmall
                                color: "white"
                            }
                        }

                        Text {
                            text: model.title
                            font.pixelSize: Theme.fontBody
                            font.bold: true
                            color: Theme.textPrimary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        Text {
                            text: model.channel + " • " + model.time
                            font.pixelSize: Theme.fontCaption
                            color: Theme.textSecondary
                        }

                        Item { Layout.fillHeight: true }

                        RowLayout {
                            Text {
                                text: "⭐ " + model.rating
                                font.pixelSize: Theme.fontCaption
                                color: Theme.warning
                            }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: "▶ İzle"
                                font.pixelSize: Theme.fontCaption
                                font.bold: true
                                color: Theme.accent
                            }
                        }
                    }

                    MouseArea {
                        id: cardArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: console.log("Seçildi:", model.title)
                    }

                    // Focus border
                    Rectangle {
                        anchors.fill: parent
                        radius: Theme.radiusM
                        color: "transparent"
                        border.color: Theme.accent
                        border.width: cardArea.activeFocus ? 3 : 0
                    }
                }
            }
        }

        // ─── Hızlı Erişim Butonları ─────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            spacing: Theme.spacingM

            Repeater {
                model: ListModel {
                    ListElement { icon: "📺"; label: "Canlı TV"; action: "channels" }
                    ListElement { icon: "📋"; label: "Program Rehberi"; action: "epg" }
                    ListElement { icon: "🌐"; label: "IPTV"; action: "iptv" }
                    ListElement { icon: "▶️"; label: "YouTube"; action: "youtube" }
                    ListElement { icon: "🎬"; label: "Medya"; action: "media" }
                    ListElement { icon: "🎙️"; label: "Sesli Komut"; action: "voice" }
                }

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: Theme.radiusM
                    color: quickBtnArea.containsMouse || quickBtnArea.activeFocus
                           ? Theme.bgCardHover : Theme.bgCard

                    Behavior on color {
                        ColorAnimation { duration: Theme.animDurationFast }
                    }

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: Theme.spacingS

                        Text {
                            text: model.icon
                            font.pixelSize: 36
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: model.label
                            font.pixelSize: Theme.fontCaption
                            color: Theme.textPrimary
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }

                    MouseArea {
                        id: quickBtnArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: console.log("Hızlı erişim:", model.action)
                    }
                }
            }
        }
    }
}
