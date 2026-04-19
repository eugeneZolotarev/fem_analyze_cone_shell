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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1150, 750)
        MainWindow.setMinimumSize(QSize(1150, 750))
        MainWindow.setStyleSheet(u"/* =========================================\n"
"   \u041e\u0411\u0429\u0418\u0419 \u0424\u041e\u041d \u0418 \u0428\u0420\u0418\u0424\u0422\u042b\n"
"   ========================================= */\n"
"QWidget {\n"
"    background-color: #2b2b2b;\n"
"    color: #e0e0e0;\n"
"    font-family: \"Segoe UI\", \"Helvetica Neue\", Arial, sans-serif;\n"
"    font-size: 10pt;\n"
"}\n"
"\n"
"/* =========================================\n"
"   \u0413\u0420\u0423\u041f\u041f\u042b \u041f\u0410\u0420\u0410\u041c\u0415\u0422\u0420\u041e\u0412 (QGroupBox)\n"
"   ========================================= */\n"
"QGroupBox {\n"
"    border: 1px solid #555555;\n"
"    border-radius: 6px;\n"
"    margin-top: 1.2em; /* \u041e\u0442\u0441\u0442\u0443\u043f \u0441\u0432\u0435\u0440\u0445\u0443, \u0447\u0442\u043e\u0431\u044b \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a \u043d\u0435 \u043d\u0430\u0435\u0437\u0436\u0430\u043b \u043d\u0430 \u0440\u0430\u043c\u043a\u0443 */\n"
"    padding-top: 10px;\n"
"}\n"
"\n"
"QGroupBox::"
                        "title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top left;\n"
"    padding: 0 8px;\n"
"    color: #4da6ff; /* \u0418\u043d\u0436\u0435\u043d\u0435\u0440\u043d\u044b\u0439 \u0441\u0438\u043d\u0438\u0439 \u0430\u043a\u0446\u0435\u043d\u0442 */\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* =========================================\n"
"   \u041f\u041e\u041b\u042f \u0412\u0412\u041e\u0414\u0410 (SpinBoxes)\n"
"   ========================================= */\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color: #3c3f41;\n"
"    border: 1px solid #555555;\n"
"    border-radius: 4px;\n"
"    padding: 4px;\n"
"    color: #ffffff;\n"
"    min-width: 60px;\n"
"}\n"
"\n"
"QSpinBox:focus, QDoubleSpinBox:focus {\n"
"    border: 1px solid #4da6ff; /* \u0421\u0438\u043d\u044f\u044f \u043f\u043e\u0434\u0441\u0432\u0435\u0442\u043a\u0430 \u043f\u0440\u0438 \u0432\u0432\u043e\u0434\u0435 \u0441 \u043a\u043b\u0430\u0432\u0438\u0430\u0442\u0443\u0440\u044b */\n"
"    background-color: #45494a;\n"
"}\n"
"\n"
""
                        "/* \u0421\u0442\u0438\u043b\u0438\u0437\u0430\u0446\u0438\u044f \u0441\u0442\u0440\u0435\u043b\u043e\u0447\u0435\u043a \u0432\u0432\u0435\u0440\u0445/\u0432\u043d\u0438\u0437 */\n"
"QSpinBox::up-button, QDoubleSpinBox::up-button,\n"
"QSpinBox::down-button, QDoubleSpinBox::down-button {\n"
"    background-color: #45494a;\n"
"    border-left: 1px solid #555555;\n"
"    width: 20px;\n"
"}\n"
"\n"
"QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,\n"
"QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {\n"
"    background-color: #54585a;\n"
"}\n"
"\n"
"/* =========================================\n"
"   \u0422\u0410\u0411\u041b\u0418\u0426\u0410 \u0421\u041e\u0420\u0422\u0410\u041c\u0415\u041d\u0422\u0410 (QTableWidget)\n"
"   ========================================= */\n"
"QTableWidget {\n"
"    background-color: #1e1e1e;\n"
"    alternate-background-color: #2a2d2e; /* \u0426\u0432\u0435\u0442 \u0434\u043b\u044f \"\u0437\u0435\u0431\u0440\u044b\" (\u0447\u0435\u0442\u043d\u044b\u0435 \u0441"
                        "\u0442\u0440\u043e\u043a\u0438) */\n"
"    color: #e0e0e0;\n"
"    gridline-color: #3c3f41;\n"
"    border: 1px solid #555555;\n"
"    border-radius: 4px;\n"
"    outline: none; /* \u0423\u0431\u0438\u0440\u0430\u0435\u0442 \u043f\u0443\u043d\u043a\u0442\u0438\u0440\u043d\u0443\u044e \u0440\u0430\u043c\u043a\u0443 \u0444\u043e\u043a\u0443\u0441\u0430 */\n"
"}\n"
"\n"
"QTableWidget::item {\n"
"    padding: 4px;\n"
"}\n"
"\n"
"QTableWidget::item:hover {\n"
"    background-color: #353839; /* \u041b\u0435\u0433\u043a\u0430\u044f \u043f\u043e\u0434\u0441\u0432\u0435\u0442\u043a\u0430 \u043f\u0440\u0438 \u043d\u0430\u0432\u0435\u0434\u0435\u043d\u0438\u0438 */\n"
"}\n"
"\n"
"QTableWidget::item:selected {\n"
"    background-color: #007ACC; /* \u0413\u043b\u0443\u0431\u043e\u043a\u0438\u0439 \u0441\u0438\u043d\u0438\u0439 \u043f\u0440\u0438 \u0432\u044b\u0431\u043e\u0440\u0435 \u043f\u0440\u043e\u0444\u0438\u043b\u044f */\n"
"    color: white;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* \u0417\u0430\u0433\u043e\u043b"
                        "\u043e\u0432\u043a\u0438 \u0441\u0442\u043e\u043b\u0431\u0446\u043e\u0432 \u0442\u0430\u0431\u043b\u0438\u0446\u044b */\n"
"QHeaderView::section {\n"
"    background-color: #3c3f41;\n"
"    color: #ffffff;\n"
"    padding: 6px;\n"
"    border: 1px solid #555555;\n"
"    border-top: none;\n"
"    border-left: none;\n"
"    font-weight: bold;\n"
"    font-size: 9pt;\n"
"}\n"
"\n"
"QHeaderView::section:hover {\n"
"    background-color: #54585a;\n"
"}\n"
"\n"
"/* \u041a\u0432\u0430\u0434\u0440\u0430\u0442\u0438\u043a \u0432 \u043b\u0435\u0432\u043e\u043c \u0432\u0435\u0440\u0445\u043d\u0435\u043c \u0443\u0433\u043b\u0443 \u0442\u0430\u0431\u043b\u0438\u0446\u044b */\n"
"QTableCornerButton::section {\n"
"    background-color: #3c3f41;\n"
"    border: 1px solid #555555;\n"
"}\n"
"\n"
"/* =========================================\n"
"   \u041a\u041d\u041e\u041f\u041a\u0418 (QPushButton)\n"
"   ========================================= */\n"
"QPushButton {\n"
"    background-color: #45494a;\n"
"    border: 1px solid #"
                        "555555;\n"
"    border-radius: 4px;\n"
"    padding: 8px 15px;\n"
"    color: #e0e0e0;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #54585a;\n"
"    border: 1px solid #777777;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #3c3f41;\n"
"}\n"
"\n"
"/* \u0421\u043f\u0435\u0446. \u0441\u0442\u0438\u043b\u044c \u0434\u043b\u044f \u043a\u043d\u043e\u043f\u043a\u0438 \"\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c\" */\n"
"QPushButton#btn_run {\n"
"    background-color: #2b7041; /* \u0421\u043f\u043e\u043a\u043e\u0439\u043d\u044b\u0439 \u0437\u0435\u043b\u0435\u043d\u044b\u0439 */\n"
"    border: 1px solid #3d9e5a;\n"
"    color: white;\n"
"    font-size: 11pt;\n"
"}\n"
"\n"
"QPushButton#btn_run:hover {\n"
"    background-color: #358c51;\n"
"}\n"
"\n"
"QPushButton#btn_run:pressed {\n"
"    background-color: #1f5230;\n"
"}\n"
"\n"
"/* \u0421\u043f\u0435\u0446. \u0441\u0442\u0438\u043b\u044c \u0434\u043b\u044f \u043a\u043d\u043e\u043f\u043a\u0438 \"\u0421\u0442\u043e\u043f\" */\n"
""
                        "QPushButton#btn_stop {\n"
"    background-color: #8c3d3d; /* \u0421\u043f\u043e\u043a\u043e\u0439\u043d\u044b\u0439 \u043a\u0440\u0430\u0441\u043d\u044b\u0439 */\n"
"    border: 1px solid #a64d4d;\n"
"    color: white;\n"
"}\n"
"\n"
"QPushButton#btn_stop:hover {\n"
"    background-color: #a64d4d;\n"
"}\n"
"\n"
"QPushButton#btn_stop:pressed {\n"
"    background-color: #5c2828;\n"
"}\n"
"\n"
"/* =========================================\n"
"   \u0428\u041a\u0410\u041b\u0410 \u041f\u0420\u041e\u0413\u0420\u0415\u0421\u0421\u0410 (QProgressBar)\n"
"   ========================================= */\n"
"QProgressBar {\n"
"    border: 1px solid #555555;\n"
"    border-radius: 4px;\n"
"    text-align: center;\n"
"    background-color: #1e1e1e;\n"
"    color: white;\n"
"    font-weight: bold;\n"
"    min-height: 20px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #007ACC, stop:1 #4da6ff);\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"/* ============"
                        "=============================\n"
"   \u0422\u0415\u0420\u041c\u0418\u041d\u0410\u041b \u041b\u041e\u0413\u041e\u0412 (QTextEdit)\n"
"   ========================================= */\n"
"QTextEdit#log_output {\n"
"    background-color: #121212; /* \u0427\u0435\u0440\u043d\u044b\u0439 \u0444\u043e\u043d \u043a\u0430\u043a \u0432 \u043d\u0430\u0441\u0442\u043e\u044f\u0449\u0435\u043c \u0442\u0435\u0440\u043c\u0438\u043d\u0430\u043b\u0435 */\n"
"    color: #a9b7c6; /* \u0426\u0432\u0435\u0442 \u0442\u0435\u043a\u0441\u0442\u0430 \u043a\u0430\u043a \u0432 IDE */\n"
"    font-family: \"Consolas\", \"Courier New\", monospace; /* \u0421\u0442\u0440\u043e\u0433\u043e \u043c\u043e\u043d\u043e\u0448\u0438\u0440\u0438\u043d\u043d\u044b\u0439 \u0448\u0440\u0438\u0444\u0442 */\n"
"    font-size: 10pt;\n"
"    border: 1px solid #555555;\n"
"    border-radius: 4px;\n"
"    padding: 8px;\n"
"}")
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
        self.gridLayout_geom = QGridLayout(self.group_geometry)
        self.gridLayout_geom.setObjectName(u"gridLayout_geom")
        self.label_height = QLabel(self.group_geometry)
        self.label_height.setObjectName(u"label_height")

        self.gridLayout_geom.addWidget(self.label_height, 0, 0, 1, 1)

        self.sb_height = QDoubleSpinBox(self.group_geometry)
        self.sb_height.setObjectName(u"sb_height")
        self.sb_height.setMaximum(10000.000000000000000)
        self.sb_height.setValue(1036.000000000000000)

        self.gridLayout_geom.addWidget(self.sb_height, 0, 1, 1, 1)

        self.label_d_small = QLabel(self.group_geometry)
        self.label_d_small.setObjectName(u"label_d_small")

        self.gridLayout_geom.addWidget(self.label_d_small, 1, 0, 1, 1)

        self.sb_d_small = QDoubleSpinBox(self.group_geometry)
        self.sb_d_small.setObjectName(u"sb_d_small")
        self.sb_d_small.setMaximum(5000.000000000000000)
        self.sb_d_small.setValue(1400.000000000000000)

        self.gridLayout_geom.addWidget(self.sb_d_small, 1, 1, 1, 1)

        self.label_d_large = QLabel(self.group_geometry)
        self.label_d_large.setObjectName(u"label_d_large")

        self.gridLayout_geom.addWidget(self.label_d_large, 2, 0, 1, 1)

        self.sb_d_large = QDoubleSpinBox(self.group_geometry)
        self.sb_d_large.setObjectName(u"sb_d_large")
        self.sb_d_large.setMaximum(5000.000000000000000)
        self.sb_d_large.setValue(1600.000000000000000)

        self.gridLayout_geom.addWidget(self.sb_d_large, 2, 1, 1, 1)


        self.verticalLayout_left.addWidget(self.group_geometry)

        self.horizontalLayout_ranges = QHBoxLayout()
        self.horizontalLayout_ranges.setObjectName(u"horizontalLayout_ranges")
        self.group_skin = QGroupBox(self.centralwidget)
        self.group_skin.setObjectName(u"group_skin")
        self.form_skin = QFormLayout(self.group_skin)
        self.form_skin.setObjectName(u"form_skin")
        self.label_t_min = QLabel(self.group_skin)
        self.label_t_min.setObjectName(u"label_t_min")

        self.form_skin.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_t_min)

        self.sb_thick_min = QDoubleSpinBox(self.group_skin)
        self.sb_thick_min.setObjectName(u"sb_thick_min")
        self.sb_thick_min.setValue(0.500000000000000)

        self.form_skin.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sb_thick_min)

        self.label_t_max = QLabel(self.group_skin)
        self.label_t_max.setObjectName(u"label_t_max")

        self.form_skin.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_t_max)

        self.sb_thick_max = QDoubleSpinBox(self.group_skin)
        self.sb_thick_max.setObjectName(u"sb_thick_max")
        self.sb_thick_max.setValue(2.000000000000000)

        self.form_skin.setWidget(1, QFormLayout.ItemRole.FieldRole, self.sb_thick_max)

        self.label_t_step = QLabel(self.group_skin)
        self.label_t_step.setObjectName(u"label_t_step")

        self.form_skin.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_t_step)

        self.sb_thick_step = QDoubleSpinBox(self.group_skin)
        self.sb_thick_step.setObjectName(u"sb_thick_step")
        self.sb_thick_step.setValue(0.100000000000000)

        self.form_skin.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sb_thick_step)


        self.horizontalLayout_ranges.addWidget(self.group_skin)

        self.group_stringers = QGroupBox(self.centralwidget)
        self.group_stringers.setObjectName(u"group_stringers")
        self.form_stringers = QFormLayout(self.group_stringers)
        self.form_stringers.setObjectName(u"form_stringers")
        self.label_str_min = QLabel(self.group_stringers)
        self.label_str_min.setObjectName(u"label_str_min")

        self.form_stringers.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_str_min)

        self.sb_str_min = QSpinBox(self.group_stringers)
        self.sb_str_min.setObjectName(u"sb_str_min")
        self.sb_str_min.setMaximum(500)
        self.sb_str_min.setValue(40)

        self.form_stringers.setWidget(0, QFormLayout.ItemRole.FieldRole, self.sb_str_min)

        self.label_str_max = QLabel(self.group_stringers)
        self.label_str_max.setObjectName(u"label_str_max")

        self.form_stringers.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_str_max)

        self.sb_str_max = QSpinBox(self.group_stringers)
        self.sb_str_max.setObjectName(u"sb_str_max")
        self.sb_str_max.setMaximum(500)
        self.sb_str_max.setValue(120)

        self.form_stringers.setWidget(1, QFormLayout.ItemRole.FieldRole, self.sb_str_max)

        self.label_str_step = QLabel(self.group_stringers)
        self.label_str_step.setObjectName(u"label_str_step")

        self.form_stringers.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_str_step)

        self.sb_str_step = QSpinBox(self.group_stringers)
        self.sb_str_step.setObjectName(u"sb_str_step")
        self.sb_str_step.setValue(10)

        self.form_stringers.setWidget(2, QFormLayout.ItemRole.FieldRole, self.sb_str_step)


        self.horizontalLayout_ranges.addWidget(self.group_stringers)


        self.verticalLayout_left.addLayout(self.horizontalLayout_ranges)

        self.group_assortment = QGroupBox(self.centralwidget)
        self.group_assortment.setObjectName(u"group_assortment")
        self.verticalLayout_list = QVBoxLayout(self.group_assortment)
        self.verticalLayout_list.setObjectName(u"verticalLayout_list")
        self.table_profiles = QTableWidget(self.group_assortment)
        if (self.table_profiles.columnCount() < 8):
            self.table_profiles.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.table_profiles.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.table_profiles.setObjectName(u"table_profiles")

        self.verticalLayout_list.addWidget(self.table_profiles)


        self.verticalLayout_left.addWidget(self.group_assortment)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer)

        self.btn_run = QPushButton(self.centralwidget)
        self.btn_run.setObjectName(u"btn_run")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_run.sizePolicy().hasHeightForWidth())
        self.btn_run.setSizePolicy(sizePolicy)
        self.btn_run.setMinimumSize(QSize(0, 0))
        self.btn_run.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_buttons.addWidget(self.btn_run)

        self.btn_stop = QPushButton(self.centralwidget)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_buttons.addWidget(self.btn_stop)


        self.verticalLayout_left.addLayout(self.horizontalLayout_buttons)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout_left.addWidget(self.progressBar)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_left.addItem(self.verticalSpacer)


        self.horizontalLayout_top.addLayout(self.verticalLayout_left)

        self.layout_plot = QVBoxLayout()
        self.layout_plot.setObjectName(u"layout_plot")

        self.horizontalLayout_top.addLayout(self.layout_plot)

        self.horizontalLayout_top.setStretch(0, 1)
        self.horizontalLayout_top.setStretch(1, 1)

        self.verticalLayout_main.addLayout(self.horizontalLayout_top)

        self.log_output = QTextEdit(self.centralwidget)
        self.log_output.setObjectName(u"log_output")
        self.log_output.setMaximumSize(QSize(16777215, 150))
        self.log_output.setReadOnly(True)

        self.verticalLayout_main.addWidget(self.log_output)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"RocketShell Optimizer - \u0420\u0430\u0441\u0447\u0435\u0442 \u043a\u043e\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u043e\u0442\u0441\u0435\u043a\u043e\u0432", None))
        self.group_geometry.setTitle(QCoreApplication.translate("MainWindow", u"\u0413\u0435\u043e\u043c\u0435\u0442\u0440\u0438\u044f \u0443\u0441\u0435\u0447\u0435\u043d\u043d\u043e\u0433\u043e \u043a\u043e\u043d\u0443\u0441\u0430 (\u043c\u043c)", None))
        self.label_height.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0441\u043e\u0442\u0430 (H):", None))
        self.label_d_small.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043b\u044b\u0439 \u0434\u0438\u0430\u043c. (d):", None))
        self.label_d_large.setText(QCoreApplication.translate("MainWindow", u"\u0411\u043e\u043b\u044c\u0448\u0438\u0439 \u0434\u0438\u0430\u043c. (D):", None))
        self.group_skin.setTitle(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u0448\u0438\u0432\u043a\u0430 (t, \u043c\u043c)", None))
        self.label_t_min.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d:", None))
        self.label_t_max.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441:", None))
        self.label_t_step.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0430\u0433:", None))
        self.group_stringers.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0440\u0438\u043d\u0433\u0435\u0440\u044b (\u0428\u0442)", None))
        self.label_str_min.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0438\u043d:", None))
        self.label_str_max.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u043a\u0441:", None))
        self.label_str_step.setText(QCoreApplication.translate("MainWindow", u"\u0428\u0430\u0433:", None))
        self.group_assortment.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0440\u0442\u0430\u043c\u0435\u043d\u0442 \u043f\u0440\u043e\u0444\u0438\u043b\u0435\u0439", None))
        ___qtablewidgetitem = self.table_profiles.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u2116", None));
        ___qtablewidgetitem1 = self.table_profiles.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"H, \u043c\u043c", None));
        ___qtablewidgetitem2 = self.table_profiles.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"B, \u043c\u043c", None));
        ___qtablewidgetitem3 = self.table_profiles.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"S, \u043c\u043c", None));
        ___qtablewidgetitem4 = self.table_profiles.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"S1, \u043c\u043c", None));
        ___qtablewidgetitem5 = self.table_profiles.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"S2, \u043c\u043c", None));
        ___qtablewidgetitem6 = self.table_profiles.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"S \u0441\u0435\u0447\u0435\u043d\u0438\u044f, \u043c\u043c^2", None));
        ___qtablewidgetitem7 = self.table_profiles.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"\u041c\u0430\u0441\u0441\u0430 1 \u043c, \u043a\u0433", None));
        self.btn_run.setStyleSheet(QCoreApplication.translate("MainWindow", u"font-weight: bold; height: 40px;", None))
        self.btn_run.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u043e\u043f\u0442\u0438\u043c\u0438\u0437\u0430\u0446\u0438\u044e", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0442\u043e\u043f", None))
        self.log_output.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041b\u043e\u0433 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u0430 \u0440\u0430\u0441\u0447\u0435\u0442\u043d\u043e\u0433\u043e \u044f\u0434\u0440\u0430 Nastran...", None))
    # retranslateUi

