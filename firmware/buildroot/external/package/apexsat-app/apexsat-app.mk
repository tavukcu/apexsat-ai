APEXSAT_APP_VERSION = 1.0.0
APEXSAT_APP_SITE = $(BR2_EXTERNAL_APEXSAT_PATH)/../../software
APEXSAT_APP_SITE_METHOD = local
APEXSAT_APP_LICENSE = Proprietary
APEXSAT_APP_INSTALL_TARGET = YES

define APEXSAT_APP_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/apexsat
    cp -r $(@D)/dvb $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/media $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/ai $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/ui $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/iptv $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/iot $(TARGET_DIR)/opt/apexsat/
endef

$(eval $(generic-package))
