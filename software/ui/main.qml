import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

/**
 * APEXSAT AI - Ana Uygulama Penceresi
 * 10-foot UI (TV uzaktan kumanda ile navigasyon)
 * Karanlık tema, büyük fontlar, D-pad navigasyonu
 */
ApplicationWindow {
    id: root
    visible: true
    width: 1920
    height: 1080
    title: "APEXSAT AI"
    color: Theme.bgPrimary

    // Tam ekran (TV modu)
    visibility: Window.FullScreen

    // ─── Global Tema ──────────────────────────────────────────────
    QtObject {
        id: Theme

        // Renkler - Karanlık Tema (OLED-friendly)
        readonly property color bgPrimary: "#0D0D0D"
        readonly property color bgSecondary: "#1A1A2E"
        readonly property color bgCard: "#16213E"
        readonly property color bgCardHover: "#1A2744"
        readonly property color accent: "#E94560"
        readonly property color accentLight: "#FF6B81"
        readonly property color textPrimary: "#FFFFFF"
        readonly property color textSecondary: "#B0B0B0"
        readonly property color textMuted: "#666666"
        readonly property color success: "#00C851"
        readonly property color warning: "#FFBB33"
        readonly property color error: "#FF4444"
        readonly property color divider: "#2A2A3E"

        // Fontlar (10-foot UI - büyük)
        readonly property int fontTitle: 42
        readonly property int fontHeading: 32
        readonly property int fontBody: 24
        readonly property int fontCaption: 18
        readonly property int fontSmall: 14

        // Animasyon
        readonly property int animDuration: 250
        readonly property int animDurationFast: 150

        // Aralıklar
        readonly property int spacingXL: 40
        readonly property int spacingL: 24
        readonly property int spacingM: 16
        readonly property int spacingS: 8
        readonly property int radiusL: 16
        readonly property int radiusM: 10
        readonly property int radiusS: 6
    }

    // ─── Keyboard / D-pad Navigasyonu ─────────────────────────────
    focus: true

    Keys.onPressed: function(event) {
        switch (event.key) {
            case Qt.Key_Back:
            case Qt.Key_Escape:
                if (contentStack.depth > 1) {
                    contentStack.pop()
                    event.accepted = true
                }
                break
            case Qt.Key_Menu:
                sideMenu.toggle()
                event.accepted = true
                break
            case Qt.Key_F1: // EPG kısa yolu
                contentStack.push(epgPage)
                event.accepted = true
                break
            case Qt.Key_R: // Kayıt kısa yolu
                statusBar.toggleRecording()
                event.accepted = true
                break
        }
    }

    // ─── Ana Layout ───────────────────────────────────────────────
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Üst Durum Çubuğu
        StatusBar {
            id: statusBar
            Layout.fillWidth: true
            Layout.preferredHeight: 56
        }

        // Ana İçerik Alanı
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Yan Menü (Focus ile açılır)
            SideMenu {
                id: sideMenu
                Layout.preferredWidth: sideMenu.expanded ? 280 : 0
                Layout.fillHeight: true

                onMenuItemSelected: function(page) {
                    switch (page) {
                        case "home": contentStack.replace(homePage); break
                        case "channels": contentStack.replace(channelListPage); break
                        case "epg": contentStack.replace(epgPage); break
                        case "recordings": contentStack.replace(recordingsPage); break
                        case "iptv": contentStack.replace(iptvPage); break
                        case "settings": contentStack.replace(settingsPage); break
                        case "media": contentStack.replace(mediaBrowserPage); break
                    }
                }
            }

            // İçerik Stack
            StackView {
                id: contentStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                initialItem: homePage

                pushEnter: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 0; to: 1
                        duration: Theme.animDuration
                    }
                    PropertyAnimation {
                        property: "x"
                        from: 100; to: 0
                        duration: Theme.animDuration
                        easing.type: Easing.OutCubic
                    }
                }

                pushExit: Transition {
                    PropertyAnimation {
                        property: "opacity"
                        from: 1; to: 0
                        duration: Theme.animDurationFast
                    }
                }
            }
        }

        // Alt Bilgi Çubuğu
        InfoBar {
            id: infoBar
            Layout.fillWidth: true
            Layout.preferredHeight: 48
        }
    }

    // ─── Sayfalar ─────────────────────────────────────────────────

    Component { id: homePage; HomePage {} }
    Component { id: channelListPage; ChannelListPage {} }
    Component { id: epgPage; EPGPage {} }
    Component { id: recordingsPage; RecordingsPage {} }
    Component { id: iptvPage; IPTVPage {} }
    Component { id: settingsPage; SettingsPage {} }
    Component { id: mediaBrowserPage; MediaBrowserPage {} }

    // ─── Bildirim Overlay ─────────────────────────────────────────
    NotificationOverlay {
        id: notificationOverlay
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.topMargin: 70
        anchors.rightMargin: 20
    }

    // ─── Ses Asistanı Overlay ─────────────────────────────────────
    VoiceAssistantOverlay {
        id: voiceOverlay
        anchors.centerIn: parent
    }
}
