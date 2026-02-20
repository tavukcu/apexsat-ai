import QtQuick 2.15
import QtQuick.Layouts 1.15

/**
 * EPG Grid Görünümü - Zaman eksenli program rehberi
 */
Rectangle {
    color: Theme.bgPrimary

    property real hourWidth: 300    // 1 saatlik genişlik (piksel)
    property int startHour: 18      // Görünüm başlangıç saati
    property int visibleHours: 5    // Görünen saat sayısı

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingL
        spacing: Theme.spacingM

        // Başlık
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "📋 Program Rehberi"
                font.pixelSize: Theme.fontTitle
                color: Theme.textPrimary
            }

            Item { Layout.fillWidth: true }

            Text {
                text: Qt.formatDate(new Date(), "dd MMMM yyyy, dddd")
                font.pixelSize: Theme.fontCaption
                color: Theme.textSecondary
            }
        }

        // Zaman çubuğu
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: Theme.bgSecondary
            radius: Theme.radiusS

            Row {
                anchors.fill: parent
                anchors.leftMargin: 200 // Kanal sütunu genişliği

                Repeater {
                    model: visibleHours

                    Rectangle {
                        width: hourWidth
                        height: parent.height
                        color: "transparent"
                        border.color: Theme.divider
                        border.width: 1

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 8
                            anchors.verticalCenter: parent.verticalCenter
                            text: {
                                var h = (startHour + index) % 24
                                return (h < 10 ? "0" : "") + h + ":00"
                            }
                            font.pixelSize: Theme.fontCaption
                            font.bold: true
                            color: Theme.textPrimary
                        }
                    }
                }
            }
        }

        // EPG Grid
        ListView {
            id: epgGrid
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 2
            focus: true

            model: ListModel {
                ListElement {
                    channelName: "TRT 1 HD"; channelNum: 1
                    prog1: "Ana Haber"; prog1dur: 1.0; prog1start: 0
                    prog2: "Gönül Dağı"; prog2dur: 2.0; prog2start: 1.0
                    prog3: "Spor Bülteni"; prog3dur: 0.5; prog3start: 3.0
                    prog4: "Hava Durumu"; prog4dur: 0.5; prog4start: 3.5
                }
                ListElement {
                    channelName: "ATV"; channelNum: 10
                    prog1: "Kuruluş Osman"; prog1dur: 2.5; prog1start: 0
                    prog2: "ATV Ana Haber"; prog2dur: 1.0; prog2start: 2.5
                    prog3: "Dizi Tekrar"; prog3dur: 1.5; prog3start: 3.5
                    prog4: ""; prog4dur: 0; prog4start: 0
                }
                ListElement {
                    channelName: "Kanal D HD"; channelNum: 18
                    prog1: "Kara Sevda"; prog1dur: 2.0; prog1start: 0
                    prog2: "Ana Haber"; prog2dur: 1.5; prog2start: 2.0
                    prog3: "Arka Sokaklar"; prog3dur: 1.5; prog3start: 3.5
                    prog4: ""; prog4dur: 0; prog4start: 0
                }
                ListElement {
                    channelName: "Show TV"; channelNum: 13
                    prog1: "Çarkıfelek"; prog1dur: 1.5; prog1start: 0
                    prog2: "Ana Haber"; prog2dur: 1.0; prog2start: 1.5
                    prog3: "Çukur"; prog3dur: 2.0; prog3start: 2.5
                    prog4: "Gece Haberleri"; prog4dur: 0.5; prog4start: 4.5
                }
                ListElement {
                    channelName: "FOX TV"; channelNum: 20
                    prog1: "Yasak Elma"; prog1dur: 2.0; prog1start: 0
                    prog2: "FOX Ana Haber"; prog2dur: 1.5; prog2start: 2.0
                    prog3: "Film"; prog3dur: 1.5; prog3start: 3.5
                    prog4: ""; prog4dur: 0; prog4start: 0
                }
                ListElement {
                    channelName: "NTV"; channelNum: 17
                    prog1: "Ekonomi"; prog1dur: 1.0; prog1start: 0
                    prog2: "Ana Haber"; prog2dur: 1.0; prog2start: 1.0
                    prog3: "Belgesel"; prog3dur: 1.5; prog3start: 2.0
                    prog4: "Gece Bülteni"; prog4dur: 1.5; prog4start: 3.5
                }
                ListElement {
                    channelName: "CNN Türk"; channelNum: 19
                    prog1: "5N1K"; prog1dur: 1.0; prog1start: 0
                    prog2: "Ne Oluyor?"; prog2dur: 1.0; prog2start: 1.0
                    prog3: "Haber"; prog3dur: 2.0; prog3start: 2.0
                    prog4: "Gece Görüşü"; prog4dur: 1.0; prog4start: 4.0
                }
                ListElement {
                    channelName: "TV8"; channelNum: 21
                    prog1: "Survivor"; prog1dur: 3.0; prog1start: 0
                    prog2: "MasterChef"; prog2dur: 1.5; prog2start: 3.0
                    prog3: "Film"; prog3dur: 0.5; prog3start: 4.5
                    prog4: ""; prog4dur: 0; prog4start: 0
                }
            }

            delegate: Rectangle {
                width: epgGrid.width
                height: 70
                color: "transparent"

                RowLayout {
                    anchors.fill: parent
                    spacing: 0

                    // Kanal adı (sabit sütun)
                    Rectangle {
                        Layout.preferredWidth: 200
                        Layout.fillHeight: true
                        color: ListView.isCurrentItem ? Theme.bgCardHover : Theme.bgSecondary

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            Rectangle {
                                width: 36; height: 36
                                radius: Theme.radiusS
                                color: Theme.accent

                                Text {
                                    anchors.centerIn: parent
                                    text: model.channelNum
                                    font.pixelSize: Theme.fontSmall
                                    font.bold: true
                                    color: "white"
                                }
                            }

                            Text {
                                text: model.channelName
                                font.pixelSize: Theme.fontCaption
                                color: Theme.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }

                    // Program kutuları
                    Row {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 2

                        // Program 1
                        EPGProgramBlock {
                            blockWidth: model.prog1dur * hourWidth
                            blockHeight: 68
                            programTitle: model.prog1
                            isCurrent: model.prog1start === 0
                        }

                        // Program 2
                        EPGProgramBlock {
                            blockWidth: model.prog2dur * hourWidth
                            blockHeight: 68
                            programTitle: model.prog2
                            visible: model.prog2 !== ""
                        }

                        // Program 3
                        EPGProgramBlock {
                            blockWidth: model.prog3dur * hourWidth
                            blockHeight: 68
                            programTitle: model.prog3
                            visible: model.prog3 !== ""
                        }

                        // Program 4
                        EPGProgramBlock {
                            blockWidth: model.prog4dur * hourWidth
                            blockHeight: 68
                            programTitle: model.prog4
                            visible: model.prog4 !== ""
                        }
                    }
                }
            }
        }

        // Alt bilgi
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: Theme.bgSecondary
            radius: Theme.radiusS

            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingS
                spacing: Theme.spacingL

                Text { text: "🔴 Kayda Al"; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary }
                Text { text: "⭐ Hatırlatıcı"; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary }
                Text { text: "ℹ️ Detay"; font.pixelSize: Theme.fontSmall; color: Theme.textSecondary }
                Item { Layout.fillWidth: true }
                Text { text: "◀ Geri  ▶ İleri  ▲▼ Kanal Değiştir"; font.pixelSize: Theme.fontSmall; color: Theme.textMuted }
            }
        }
    }
}
