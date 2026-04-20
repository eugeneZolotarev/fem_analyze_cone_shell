# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1150, 895)
        MainWindow.setStyleSheet(u"\n"
"/* --- \u041e\u0431\u0449\u0438\u0439 \u0444\u043e\u043d --- */\n"
"QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: \"Segoe UI\"; font-size: 10pt; }\n"
"QGroupBox { border: 1px solid #555555; border-radius: 6px; margin-top: 1.2em; padding-top: 10px; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; color: #4da6ff; font-weight: bold; }\n"
"QSpinBox, QLineEdit { background-color: #3c3f41; border: 1px solid #555555; border-radius: 4px; padding: 4px; color: #ffffff; }\n"
"QSpinBox:focus, QLineEdit:focus { border: 1px solid #4da6ff; }\n"
"QPushButton { background-color: #45494a; border: 1px solid #555555; border-radius: 4px; padding: 8px 15px; color: #e0e0e0; }\n"
"QPushButton#btn_run { background-color: #2b7041; border: 1px solid #3d9e5a; color: white; font-weight: bold; }\n"
"QPushButton#btn_run:hover { background-color: #358c51; }\n"
"QPushButton#btn_stop { background-color: #8c3d3d; border: 1px solid #a64d4d; color: white;}\n"
"QTableWidget"
                        " { background-color: #1e1e1e; alternate-background-color: #2a2d2e; gridline-color: #3c3f41; border: 1px solid #555555; }\n"
"QHeaderView::section { background-color: #3c3f41; color: white; padding: 5px; font-weight: bold; border: 1px solid #555555; }\n"
"QTextEdit#log_output { background-color: #121212; color: #a9b7c6; font-family: \"Consolas\", monospace; border: 1px solid #555555; }\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_main = QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.horizontalLayout_top = QHBoxLayout()
        self.horizontalLayout_top.setObjectName(u"horizontalLayout_top")
        self.verticalLayout_left = QVBoxLayout()
        self.verticalLayout_left.setObjectName(u"verticalLayout_left")
        self.group_geometry = QGroupBox(self.centralwidget)
        self.group_geometry.setObjectName(u"group_geometry")
        self.gridLayout = QGridLayout(self.group_geometry)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lbl_geom_dl = QLabel(self.group_geometry)
        self.lbl_geom_dl.setObjectName(u"lbl_geom_dl")

        self.gridLayout.addWidget(self.lbl_geom_dl, 0, 2, 1, 1)

        self.lbl_geom_ds = QLabel(self.group_geometry)
        self.lbl_geom_ds.setObjectName(u"lbl_geom_ds")

        self.gridLayout.addWidget(self.lbl_geom_ds, 1, 0, 1, 1)

        self.lbl_geom_h = QLabel(self.group_geometry)
        self.lbl_geom_h.setObjectName(u"lbl_geom_h")

        self.gridLayout.addWidget(self.lbl_geom_h, 0, 0, 1, 1)

        self.sb_d_small = QLineEdit(self.group_geometry)
        self.sb_d_small.setObjectName(u"sb_d_small")

        self.gridLayout.addWidget(self.sb_d_small, 1, 1, 1, 1)

        self.sb_height = QLineEdit(self.group_geometry)
        self.sb_height.setObjectName(u"sb_height")

        self.gridLayout.addWidget(self.sb_height, 0, 1, 1, 1)

        self.sb_d_large = QLineEdit(self.group_geometry)
        self.sb_d_large.setObjectName(u"sb_d_large")

        self.gridLayout.addWidget(self.sb_d_large, 0, 3, 1, 1)


        self.verticalLayout_left.addWidget(self.group_geometry)

        self.group_material = QGroupBox(self.centralwidget)
        self.group_material.setObjectName(u"group_material")
        self.gridLayout_2 = QGridLayout(self.group_material)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lbl_mat_name = QLabel(self.group_material)
        self.lbl_mat_name.setObjectName(u"lbl_mat_name")

        self.gridLayout_2.addWidget(self.lbl_mat_name, 0, 0, 1, 1)

        self.txt_mat_name = QLineEdit(self.group_material)
        self.txt_mat_name.setObjectName(u"txt_mat_name")

        self.gridLayout_2.addWidget(self.txt_mat_name, 0, 1, 1, 1)

        self.sb_mat_e = QLineEdit(self.group_material)
        self.sb_mat_e.setObjectName(u"sb_mat_e")

        self.gridLayout_2.addWidget(self.sb_mat_e, 1, 1, 1, 1)

        self.lbl_mat_nu = QLabel(self.group_material)
        self.lbl_mat_nu.setObjectName(u"lbl_mat_nu")

        self.gridLayout_2.addWidget(self.lbl_mat_nu, 0, 2, 1, 1)

        self.lbl_mat_e = QLabel(self.group_material)
        self.lbl_mat_e.setObjectName(u"lbl_mat_e")

        self.gridLayout_2.addWidget(self.lbl_mat_e, 1, 0, 1, 1)

        self.sb_mat_nu = QLineEdit(self.group_material)
        self.sb_mat_nu.setObjectName(u"sb_mat_nu")

        self.gridLayout_2.addWidget(self.sb_mat_nu, 0, 3, 1, 1)

        self.lbl_mat_density = QLabel(self.group_material)
        self.lbl_mat_density.setObjectName(u"lbl_mat_density")

        self.gridLayout_2.addWidget(self.lbl_mat_density, 1, 2, 1, 1)

        self.sb_mat_density = QLineEdit(self.group_material)
        self.sb_mat_density.setObjectName(u"sb_mat_density")

        self.gridLayout_2.addWidget(self.sb_mat_density, 1, 3, 1, 1)


        self.verticalLayout_left.addWidget(self.group_material)

        self.group_loads = QGroupBox(self.centralwidget)
        self.group_loads.setObjectName(u"group_loads")
        self.form_loads = QFormLayout(self.group_loads)
        self.form_loads.setObjectName(u"form_loads")
        self.lbl_load_force = QLabel(self.group_loads)
        self.lbl_load_force.setObjectName(u"lbl_load_force")

        self.form_loads.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_load_force)

        self.sb_load = QLineEdit(self.group_loads)
        self.sb_load.setObjectName(u"sb_load")

        self.form_loads.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sb_load)


        self.verticalLayout_left.addWidget(self.group_loads)

        self.horizontalLayout_ranges = QHBoxLayout()
        self.horizontalLayout_ranges.setObjectName(u"horizontalLayout_ranges")
        self.group_skin = QGroupBox(self.centralwidget)
        self.group_skin.setObjectName(u"group_skin")
        self.gridLayout_3 = QGridLayout(self.group_skin)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.sb_thick_max = QLineEdit(self.group_skin)
        self.sb_thick_max.setObjectName(u"sb_thick_max")

        self.gridLayout_3.addWidget(self.sb_thick_max, 1, 1, 1, 1)

        self.sb_thick_min = QLineEdit(self.group_skin)
        self.sb_thick_min.setObjectName(u"sb_thick_min")

        self.gridLayout_3.addWidget(self.sb_thick_min, 0, 1, 1, 1)

        self.lbl_skin_max = QLabel(self.group_skin)
        self.lbl_skin_max.setObjectName(u"lbl_skin_max")

        self.gridLayout_3.addWidget(self.lbl_skin_max, 1, 0, 1, 1)

        self.lbl_skin_min = QLabel(self.group_skin)
        self.lbl_skin_min.setObjectName(u"lbl_skin_min")

        self.gridLayout_3.addWidget(self.lbl_skin_min, 0, 0, 1, 1)

        self.lbl_skin_step = QLabel(self.group_skin)
        self.lbl_skin_step.setObjectName(u"lbl_skin_step")

        self.gridLayout_3.addWidget(self.lbl_skin_step, 0, 2, 1, 1)

        self.sb_thick_step = QLineEdit(self.group_skin)
        self.sb_thick_step.setObjectName(u"sb_thick_step")

        self.gridLayout_3.addWidget(self.sb_thick_step, 0, 3, 1, 1)


        self.horizontalLayout_ranges.addWidget(self.group_skin)

        self.group_stringers = QGroupBox(self.centralwidget)
        self.group_stringers.setObjectName(u"group_stringers")
        self.gridLayout_4 = QGridLayout(self.group_stringers)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.lbl_str_min = QLabel(self.group_stringers)
        self.lbl_str_min.setObjectName(u"lbl_str_min")

        self.gridLayout_4.addWidget(self.lbl_str_min, 0, 0, 1, 1)

        self.sb_str_max = QSpinBox(self.group_stringers)
        self.sb_str_max.setObjectName(u"sb_str_max")
        self.sb_str_max.setMaximum(500)
        self.sb_str_max.setValue(80)

        self.gridLayout_4.addWidget(self.sb_str_max, 1, 1, 1, 1)

        self.lbl_str_max = QLabel(self.group_stringers)
        self.lbl_str_max.setObjectName(u"lbl_str_max")

        self.gridLayout_4.addWidget(self.lbl_str_max, 1, 0, 1, 1)

        self.sb_str_min = QSpinBox(self.group_stringers)
        self.sb_str_min.setObjectName(u"sb_str_min")
        self.sb_str_min.setMaximum(500)
        self.sb_str_min.setValue(40)

        self.gridLayout_4.addWidget(self.sb_str_min, 0, 1, 1, 1)

        self.lbl_str_eb = QLabel(self.group_stringers)
        self.lbl_str_eb.setObjectName(u"lbl_str_eb")

        self.gridLayout_4.addWidget(self.lbl_str_eb, 0, 2, 1, 1)

        self.sb_elements_between = QSpinBox(self.group_stringers)
        self.sb_elements_between.setObjectName(u"sb_elements_between")
        self.sb_elements_between.setValue(2)

        self.gridLayout_4.addWidget(self.sb_elements_between, 0, 3, 1, 1)

        self.lbl_str_along = QLabel(self.group_stringers)
        self.lbl_str_along.setObjectName(u"lbl_str_along")

        self.gridLayout_4.addWidget(self.lbl_str_along, 1, 2, 1, 1)

        self.sb_str_along = QSpinBox(self.group_stringers)
        self.sb_str_along.setObjectName(u"sb_str_along")

        self.gridLayout_4.addWidget(self.sb_str_along, 1, 3, 1, 1)


        self.horizontalLayout_ranges.addWidget(self.group_stringers)

        self.horizontalLayout_ranges.setStretch(0, 1)
        self.horizontalLayout_ranges.setStretch(1, 1)

        self.verticalLayout_left.addLayout(self.horizontalLayout_ranges)

        self.group_assortment = QGroupBox(self.centralwidget)
        self.group_assortment.setObjectName(u"group_assortment")
        self.vboxLayout = QVBoxLayout(self.group_assortment)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.table_profiles = QTableWidget(self.group_assortment)
        self.table_profiles.setObjectName(u"table_profiles")

        self.vboxLayout.addWidget(self.table_profiles)


        self.verticalLayout_left.addWidget(self.group_assortment)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.hboxLayout.addItem(self.horizontalSpacer)

        self.btn_run = QPushButton(self.centralwidget)
        self.btn_run.setObjectName(u"btn_run")

        self.hboxLayout.addWidget(self.btn_run)

        self.btn_stop = QPushButton(self.centralwidget)
        self.btn_stop.setObjectName(u"btn_stop")

        self.hboxLayout.addWidget(self.btn_stop)


        self.verticalLayout_left.addLayout(self.hboxLayout)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")

        self.verticalLayout_left.addWidget(self.progressBar)


        self.horizontalLayout_top.addLayout(self.verticalLayout_left)

        self.layout_plot = QVBoxLayout()
        self.layout_plot.setObjectName(u"layout_plot")

        self.horizontalLayout_top.addLayout(self.layout_plot)

        self.horizontalLayout_top.setStretch(0, 1)
        self.horizontalLayout_top.setStretch(1, 2)

        self.verticalLayout_main.addLayout(self.horizontalLayout_top)

        self.log_output = QTextEdit(self.centralwidget)
        self.log_output.setObjectName(u"log_output")

        self.verticalLayout_main.addWidget(self.log_output)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"RocketShell Optimizer", None))
        self.group_geometry.setTitle(QCoreApplication.translate("MainWindow", u"\u0413\u0435\u043e\u043c\u0435\u0442\u0440\u0438\u044f \u043a\u043e\u043d\u0443\u0441\u0430 (\u043c\u043c)", None))
        self.lbl_geom_dl.setText(QCoreApplication.translate("MainWindow", u"\u0411\u043e\u043b\u044c\u0448\u0438\u0439 \u0434\u0438\u0430\u043c. (D):", None))
        self.lbl_geom_ds.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043b\u044b\u0439 \u0434\u0438\u0430\u043c. (d):", None))
        self.lbl_geom_h.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0441\u043e\u0442\u0430 (H):", None))
        self.sb_d_small.setText(QCoreApplication.translate("MainWindow", u"1400.0", None))
        self.sb_height.setText(QCoreApplication.translate("MainWindow", u"1036.0", None))
        self.sb_d_large.setText(QCoreApplication.translate("MainWindow", u"1600.0", None))
        self.group_material.setTitle(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b", None))
        self.lbl_mat_name.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435:", None))
        self.txt_mat_name.setText(QCoreApplication.translate("MainWindow", u"Steel", None))
        self.sb_mat_e.setText(QCoreApplication.translate("MainWindow", u"210000.0", None))
        self.lbl_mat_nu.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u044d\u0444. \u041f\u0443\u0430\u0441\u0441\u043e\u043d\u0430:", None))
        self.lbl_mat_e.setText(QCoreApplication.translate("MainWindow", u"E (\u041c\u041f\u0430):", None))
        self.sb_mat_nu.setText(QCoreApplication.translate("MainWindow", u"0.3", None))
        self.lbl_mat_density.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043b\u043e\u0442\u043d\u043e\u0441\u0442\u044c:", None))
        self.group_loads.setTitle(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0433\u0440\u0443\u0437\u043a\u0438", None))
        self.lbl_load_force.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0441\u0435\u0432\u0430\u044f \u0441\u0438\u043b\u0430 (\u041d):", None))
        self.sb_load.setText(QCoreApplication.translate("MainWindow", u"-1000.0", None))
        self.group_skin.setTitle(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u0448\u0438\u0432\u043a\u0430 (t, \u043c\u043c)", None))
        self.sb_thick_max.setText(QCoreApplication.translate("MainWindow", u"2.0", None))
        self.sb_thick_min.setText(QCoreApplication.translate("MainWindow", u"0.5", None))
        self.lbl_skin_max.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441:", None))
        self.lbl_skin_min.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d:", None))
        self.lbl_skin_step.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0430\u0433:", None))
        self.sb_thick_step.setText(QCoreApplication.translate("MainWindow", u"0.5", None))
        self.group_stringers.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0440\u0438\u043d\u0433\u0435\u0440\u044b (\u0428\u0442)", None))
        self.lbl_str_min.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d:", None))
        self.lbl_str_max.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441:", None))
        self.lbl_str_eb.setText(QCoreApplication.translate("MainWindow", u"\u041a\u042d \u043c\u0435\u0436\u0434\u0443:", None))
        self.lbl_str_along.setText(QCoreApplication.translate("MainWindow", u"\u041a\u042d \u0432\u0434\u043e\u043b\u044c:", None))
        self.group_assortment.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0440\u0442\u0430\u043c\u0435\u043d\u0442 \u043f\u0440\u043e\u0444\u0438\u043b\u0435\u0439", None))
        self.btn_run.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043e\u043f\u0442\u0438\u043c\u0438\u0437\u0430\u0446\u0438\u044e", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u043e\u043f", None))
        self.log_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041b\u043e\u0433 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u0430...", None))
    # retranslateUi

