import math
import os
import os.path
import shutil
from subprocess import Popen, PIPE
from tkinter import *

import cv2 as cv
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

main_path = os.path.expanduser('~')

# built-in cascade:
cascade_erythrocytes = "cascade/erythrocytes_cascade.xml"
cascade_thrombocytes = "cascade/thrombocytes_cascade.xml"
cascade_monocytes = "cascade/monocytes_cascade.xml"
cascade_lymphocytes = "cascade/lymphocytes_cascade.xml"
cascade_neutrophils = "cascade/neutrophils_cascade.xml"

# standard paths:
main_path = os.path.expanduser('~')
choose_catalog = os.path.expanduser('~')

# standard file names:
standard_name_file_vec = "positive.vec"
standard_name_file_txt = "negative.txt"

# final values:
final_number_stage = 5
final_value_width = 100
final_value_height = 100
width = 24
height = 24

# other variables:
success_choose_train_cascade = 0
number_positive_images_in_file = -1
number_negative_images_in_file = 200
number_found_elements = 0
counter_positive_images = 5


class ExtendedParametersCreateSamples(QDialog):
    def __init__(self):
        super(ExtendedParametersCreateSamples, self).__init__()
        loadUi('gui/GuiExtendedParametersCreateSamples.ui', self)
        self.w11 = ChooseTrainCascade()
        self.button_train_cascade.clicked.connect(self.create_extended_samples)
        self.label_bgcolor.setToolTip("Przeźroczytość w obrazach wejściowych.")
        self.label_invert.setToolTip("Przed ekstrakcją próbki wszystkie obrazy zostaną odwrócone.")
        self.label_maxintensitydevation.setToolTip(
            "Przed ekstrakcją każdy obraz zostanie losowo rozświetlony lub przyciemniony maksymalnie do podanej "
            "wartości")
        self.label_maxxangle.setToolTip(
            "Każdy obraz zostanie obrócony o losowo wybrany kąt maksymalnie do podanej wartości.")
        self.label_maxyangle.setToolTip(
            "Każdy obraz zostanie obrócony o losowo wybrany kąt maksymalnie do podanej wartości.")
        self.label_maxzangle.setToolTip(
            "Każdy obraz zostanie obrócony o losowo wybrany kąt maksymalnie do podanej wartości.")
        self.label_showsamples.setToolTip("Wszystkie próbki zostaną pokazane")
        self.label_width.setToolTip("Wysokość w pikselach generowanych próbek")
        self.label_height.setToolTip("Szerokość w pikselach generowanych próbek")

        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)

    def help_me(self):
        self.w66.show()

    def skip_to_train_cascade(self):
        self.destroy()
        self.w11.show()

    def create_extended_samples(self):
        global bg_color, invert, max_in_density_deviation, max_x_angle, max_y_angle, max_z_angle
        global show_samples, width, height
        bg_color = self.text_bgcolor.value()
        invert = self.comboBox_invert.currentText()
        max_in_density_deviation = self.text_maxintensitydevation.value()
        max_x_angle = self.text_maxxangle.value()
        max_y_angle = self.text_maxyangle.value()
        max_z_angle = self.text_maxzangle.value()
        show_samples = self.comboBox_showsamples.currentText()
        width = self.text_width.value()
        height = self.text_height.value()

        if invert == "TRUE":
            invert = " -inv "
        else:
            invert = NONE
        if show_samples == "TRUE":
            show_samples = " -show "
        else:
            show_samples = NONE

        os.chdir(main_path)
        text_cmd = "opencv_createsamples -info positive.dat -num " + str(
            number_positive_images_in_file + 1) + " -vec positive.vec +  -bgcolor " + str(
            bg_color) + " -maxidev " + str(max_in_density_deviation) + " -maxxangle " + str(
            max_x_angle) + " -maxyangle " + str(max_y_angle) + " -maxzangle " + str(
            max_z_angle) + " -w " + str(width) + " -h " + str(height) + show_samples + invert
        print(str(text_cmd))
        os.system("start /B start cmd.exe @cmd /K" + text_cmd)

        self.skip_to_train_cascade()


class ExtendedParameters(QDialog):
    def __init__(self):
        super(ExtendedParameters, self).__init__()
        loadUi('gui/GuiExtendedParameters.ui', self)
        self.button_train_cascade.clicked.connect(self.train_extended_cascade)
        self.label_precalcValBufSize.setToolTip("Rozmiar bufora do przechowywania wstępnie obliczonych wartości cech.")
        self.label_precalcIdxBufSize.setToolTip("Rozmiar bufora buforowych wartości indeksowanych.")
        self.label_acceptanceRatioBreakValue.setToolTip(
            "Argument ten określa dokładność modelu uczenia i w którym momencie powinien się zatrzymać.")
        self.label_stageType.setToolTip("Typ etapów szkolenia klasyfikatora.")
        self.label_featureType.setToolTip("Rodzaj cech: Haara lub LBP (lokalne układy binarne).")

        self.label_boostType.setToolTip("Warianty algorytmu boostingu.")
        self.label_minHitRate.setToolTip(
            "Minimalny współczynnik trafień. Określa docelowy odsetek prawdziwych wystąpień.")
        self.label_maxFalseAlarmRate.setToolTip("Maksymalny odsetek fałszywych alarmów.")
        self.label_weightTrimRate.setToolTip("Próbki szkoleniowe do określonych iteracji algorytmu boostingu.")
        self.label_maxDepth.setToolTip("Maksymalna głębokość indywidualnych słabych klasyfikatorów.")
        self.label_maxWeakCount.setToolTip("Maksymalna liczba słabych klasyfikatorów.")
        self.label_mode.setToolTip(
            "Parametr ten znajduje zastosowanie z cechami typu Haara i określa oryginalne cechy Haara lub rozszerzone.")

        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)

    def help_me(self):
        self.w66.show()

    def train_extended_cascade(self):
        global precalcValBufSize, precalcIdxBufSize, acceptanceRatioBreakValue, minHitRate
        global maxFalseAlarmRate, weightTrimRate, maxDepth, maxWeakCount, stageType, featureType, boostType, mode
        precalcValBufSize = self.text_precalcValBufSize.value()
        precalcIdxBufSize = self.text_precalcIdxBufSize.value()
        acceptanceRatioBreakValue = self.text_acceptanceRatioBreakValue.value()
        minHitRate = self.text_minHitRate.value()
        maxFalseAlarmRate = self.text_maxFalseAlarmRate.value()
        weightTrimRate = self.text_weightTrimRate.value()
        maxDepth = self.text_maxDepth.value()
        maxWeakCount = self.text_maxWeakCount.value()
        stageType = self.comboBox_stageType.currentText()
        featureType = self.comboBox_featureType.currentText()
        boostType = self.comboBox_boostType.currentText()
        mode = self.comboBox_mode.currentText()
        if not os.path.exists(main_path + "/cascade"):
            os.makedirs(main_path + "/cascade")
        os.chdir(main_path)
        text_cmd_ex = "opencv_traincascade -data " + main_path + "/cascade" + " -vec " + standard_name_file_vec + " -bg " + standard_name_file_txt + " -numPos " + str(
            math.floor(((90 * counter_positive_images) / 100))) + " -numNeg " + str(
            number_negative_images_in_file) + " -numStages " + str(
            final_number_stage) + " -precalcValBufSize " + str(precalcValBufSize) + " -precalcIdxBufSize " + str(
            precalcIdxBufSize) + " -acceptanceRatioBreakValue " + str(
            acceptanceRatioBreakValue) + " -minHitRate " + str(
            minHitRate) + " -maxFalseAlarmRate " + str(maxFalseAlarmRate) + " -weightTrimRate " + str(
            weightTrimRate) + " -maxDepth " + str(maxDepth) + " -maxWeakCount " + str(
            maxWeakCount) + " -stageType " + stageType + " -featureType " + featureType + " -boostType " + boostType + " -mode " + mode + " -w " + str(
            width) + " -h " + str(height)
        os.system("start /B start cmd.exe @cmd /K" + text_cmd_ex)


class TrainCascade(QDialog):
    def __init__(self):
        super(TrainCascade, self).__init__()
        loadUi('gui/GuiTrainCascade.ui', self)
        self.w5 = ExtendedParameters()
        self.button_upload_vec.clicked.connect(self.choose_file_vec)
        self.button_upload_txt.clicked.connect(self.choose_file_txt)
        self.button_ok.clicked.connect(self.upload_all_date)
        self.button_extended_parameters.clicked.connect(self.open_extended_parameters)

        self.plus_stage.clicked.connect(lambda: self.change_number_stage(str("+")))
        self.minus_stage.clicked.connect(lambda: self.change_number_stage(str("-")))
        self.plus_pos.clicked.connect(lambda: self.change_number_positive_image(str("+")))
        self.minus_pos.clicked.connect(lambda: self.change_number_positive_image(str("-")))

        self.plus_stage_10.clicked.connect(lambda: self.change_number_stage_10(str("+")))
        self.minus_stage_10.clicked.connect(lambda: self.change_number_stage_10(str("-")))
        self.plus_pos_10.clicked.connect(lambda: self.change_number_positive_image_10(str("+")))
        self.minus_pos_10.clicked.connect(lambda: self.change_number_positive_image_10(str("-")))

        self.button_upload_vec.setToolTip(
            "Wskaż plik wektorowy .vec stworzony za pomocą aplikacji narzędziowej opencv_createsamples.")
        self.button_choose_createsamples_5.setToolTip(
            "Wskaż liczbę obrazów znajdujących się w wybranym poprzednio pliku wektorowym .vec")

        self.checkbox_download_count_positive.setToolTip(
            "Zaznaczając tą opcję, program sam pobierze liczbę zdjęć.")
        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)

    def help_me(self):
        self.w66.show()

    def open_extended_parameters(self):
        self.w5.show()

    def upload_all_date(self):
        if not os.path.exists(main_path + "/cascade"):
            os.makedirs(main_path + "/cascade")

        if self.checkbox_download_count_positive.isChecked():
            os.chdir(main_path)
            text_cmd = "opencv_traincascade -data " + main_path + "/cascade" + " -vec " + standard_name_file_vec + " -bg " + standard_name_file_txt + " -numPos " + str(
                math.floor(((90 * number_positive_images_in_file + 1) / 100))) + " -numNeg " + str(
                number_negative_images_in_file) + " -numStages " + str(
                final_number_stage) + " -w " + str(width) + " -h " + str(height)
            print(text_cmd)
            print(width)
            print(height)
            os.system("start /B start cmd.exe @cmd /K" + text_cmd)
        else:
            os.chdir(main_path)
            text_cmd = "opencv_traincascade -data " + main_path + "/cascade" + " -vec " + standard_name_file_vec + " -bg " + standard_name_file_txt + " -numPos " + str(
                math.floor(((90 * counter_positive_images) / 100))) + " -numNeg " + str(
                number_negative_images_in_file) + " -numStages " + str(
                final_number_stage) + " -w " + str(width) + " -h " + str(height)
            print(text_cmd)
            print(width)
            print(height)
            os.system("start /B start cmd.exe @cmd /K" + text_cmd)

    def change_number_stage(self, mark):
        stage = self.stage.text()
        stage = int(stage)
        global final_number_stage
        if mark == "+":
            final_number_stage = stage + 1
            self.stage.setText(str(final_number_stage))
        if mark == "-":
            final_number_stage = stage - 1
            if final_number_stage >= 1:
                self.stage.setText(str(final_number_stage))

    def change_number_positive_image(self, mark):
        count_pos = self.image.text()
        count_pos = int(count_pos)
        global counter_positive_images
        if mark == "+":
            counter_positive_images = count_pos + 1
            self.image.setText(str(counter_positive_images))
        if mark == "-":
            counter_positive_images = count_pos - 1
            if counter_positive_images >= 1:
                self.image.setText(str(counter_positive_images))

    def change_number_stage_10(self, mark):
        stage = self.stage.text()
        stage = int(stage)
        global final_number_stage
        if mark == "+":
            final_number_stage = stage + 10
            self.stage.setText(str(final_number_stage))
        if mark == "-":
            final_number_stage = stage - 10
            if final_number_stage >= 10:
                self.stage.setText(str(final_number_stage))

    def change_number_positive_image_10(self, mark):
        count_pos = self.image.text()
        count_pos = int(count_pos)
        global counter_positive_images
        if mark == "+":
            counter_positive_images = count_pos + 10
            self.image.setText(str(counter_positive_images))
        if mark == "-":
            counter_positive_images = count_pos - 10
            if counter_positive_images >= 10:
                self.image.setText(str(counter_positive_images))

    def choose_file_vec(self):
        filter_mask = "Python/Text files (*.vec)"
        file_vec = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        global file_vec_to_txt
        file_vec_to_txt = str(file_vec)
        file_vec_to_txt = file_vec_to_txt[:-2]
        count_text = file_vec_to_txt.rfind('/')
        file_vec_to_txt = file_vec_to_txt[2: + count_text]
        global standard_name_file_vec
        standard_name_file_vec = str(file_vec)
        count_text = standard_name_file_vec.rfind('/')
        standard_name_file_vec = standard_name_file_vec[count_text + 1:]
        standard_name_file_vec = standard_name_file_vec[:-2]
        name_vec = ".vec"
        if name_vec in str(file_vec):
            self.button_upload_txt.setEnabled(True)
            self.button_choose_createsamples_4.setEnabled(True)
            self.plus_stage_10.setEnabled(True)
            self.plus_stage.setEnabled(True)
            self.stage.setEnabled(True)
            self.minus_stage.setEnabled(True)
            self.minus_stage_10.setEnabled(True)
            if number_positive_images_in_file is not -1:
                self.checkbox_download_count_positive.setEnabled(True)
            if number_positive_images_in_file is -1:
                self.checkbox_download_count_positive.setEnabled(False)

    def choose_file_txt(self):
        filter_mask = "Python/Text files (*.txt)"
        file_txt = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        global standard_name_file_txt
        standard_name_file_txt = str(file_txt)
        copy_file_txt = standard_name_file_txt[:-2]
        copy_file_txt = copy_file_txt[2:]
        count_text = standard_name_file_txt.rfind('/')
        get_file_txt = standard_name_file_txt[2: + count_text]
        print(copy_file_txt)
        print(get_file_txt)
        print(file_vec_to_txt)
        standard_name_file_txt = standard_name_file_txt[count_text + 1:]
        standard_name_file_txt = standard_name_file_txt[:-2]

        self.button_ok.setEnabled(True)
        self.button_extended_parameters.setEnabled(True)


class NegativeSamples(QDialog):
    def __init__(self):
        super(NegativeSamples, self).__init__()
        loadUi('gui/GuiNegativeSamples.ui', self)
        self.w3 = TrainCascade()
        self.button_choose_positive_1.clicked.connect(self.load_files_negative_1)
        self.plus_width.clicked.connect(lambda: self.change_resolution_width("+"))
        self.minus_width.clicked.connect(lambda: self.change_resolution_width("-"))
        self.plus_height.clicked.connect(lambda: self.change_resolution_height("+"))
        self.minus_height.clicked.connect(lambda: self.change_resolution_height("-"))

        self.plus_width_10.clicked.connect(lambda: self.change_resolution_width_10("+"))
        self.minus_width_10.clicked.connect(lambda: self.change_resolution_width_10("-"))
        self.plus_height_10.clicked.connect(lambda: self.change_resolution_height_10("+"))
        self.minus_height_10.clicked.connect(lambda: self.change_resolution_height_10("-"))

        self.button_choose_positive_6.setToolTip(
            "Rozdzielczość wszystkich obrazów musi być taka sama. Wybierz rozdzielczość.")
        self.height.setToolTip("Wysokość obrazu.")
        self.width.setToolTip("Szerokość obrazu.")
        self.button_choose_positive_1.setToolTip(
            "Wybierz folder z obrazami negatywnymi czyli takimi na których nie znajduje się szukany obiekt.")

        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)

    def help_me(self):
        self.w66.show()

    def messagebox(self):
        QMessageBox.information(self, 'Ostrzeżenie', 'Rozdzielczość obrazu nie może być zerem ani być ujemną!')

    def load_files_negative_1(self):
        if os.path.exists(main_path + "/cascade"):
            for root, dirs, files in os.walk(main_path + "/cascade"):
                for file in files:
                    os.remove(os.path.join(root, file))
        directory = main_path + "/negative"
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))
        if not os.path.exists(directory):
            os.makedirs(directory)
        global count
        filter_mask = "Python/Text files (*.png *.jpg)"
        filenames_image = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        file_txt = open(main_path + "/negative.txt", "w+")
        for count in range(len(filenames_image)):
            src = filenames_image[count]
            print("src: " + src)
            dst = main_path + "/negative"
            print("dst: " + dst)
            val = 0
            while val <= 100:
                val += 1
                self.progressbar_negative.setValue(val)
            filenames_image[count] = QtGui.QImage(filenames_image[count]).scaled(final_value_width, final_value_height)
            filenames_image[count].save(main_path + "/negative/" + str(count) + ".png")
            if src is not dst:
                filenames_image[count] = shutil.copy(src, dst)
                os.remove(filenames_image[count])
            file_txt.write(main_path + "/negative/" + str(count) + ".png")
            file_txt.write('\n')
        file_txt.close()
        self.label_ok_negative.setPixmap(QPixmap("image/success.png"))
        count_file_images_neg = count
        print(count_file_images_neg + 1)
        self.destroy()
        self.w3.show()

    def change_resolution_width(self, mark):
        width = self.width.text()
        width = int(width)
        global final_value_width
        if mark == "+":
            final_value_width = width + 1
            self.width.setText(str(final_value_width))
        if mark == "-":
            final_value_width = width - 1
            if final_value_width >= 1:
                self.width.setText(str(final_value_width))
            else:
                self.messagebox()

    def change_resolution_height(self, mark):
        height = self.height.text()
        height = int(height)
        global final_value_height
        if mark == "+":
            final_value_height = height + 1
            self.height.setText(str(final_value_height))
        if mark == "-":
            final_value_height = height - 1
            if final_value_height >= 1:
                self.height.setText(str(final_value_height))
            else:
                self.messagebox()

    def change_resolution_width_10(self, mark):
        width = self.width.text()
        width = int(width)
        global final_value_width
        if mark == "+":
            final_value_width = width + 10
            self.width.setText(str(final_value_width))
        if mark == "-":
            final_value_width = width - 10
            if final_value_width >= 10:
                self.width.setText(str(final_value_width))
            else:
                self.messagebox()

    def change_resolution_height_10(self, mark):
        height = self.height.text()
        height = int(height)
        global final_value_height
        if mark == "+":
            final_value_height = height + 10
            self.height.setText(str(final_value_height))
        if mark == "-":
            final_value_height = height - 10
            if final_value_height >= 10:
                self.height.setText(str(final_value_height))
            else:
                self.messagebox()


class ChooseTrainCascade(QDialog):
    def __init__(self):
        super(ChooseTrainCascade, self).__init__()
        loadUi('gui/GuiChooseTrainCascade.ui', self)
        self.w34 = TrainCascade()
        self.w3 = NegativeSamples()
        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)
        self.button_only_traincascade.clicked.connect(self.choose_open_cv_train_cascade)
        self.button_only_traincascade.setToolTip(
            "Zainstaluj bibliotekę OpenCV i wskaż aplikację narzędziową opencv_traincascade.")

    def help_me(self):
        self.w66.show()

    def skip(self):
        self.destroy()
        self.w34.show()

    def messagebox(self):
        QMessageBox.information(self, 'Ostrzeżenie', 'Wskazano błędną aplikację!')

    def choose_open_cv_train_cascade(self):
        filter_mask = "Python/Text files (*.exe)"
        folder_path_train_cascade = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        global main_path
        main_path = os.path.dirname(str(folder_path_train_cascade))
        main_path = main_path[2:]
        print(str(main_path))
        train_cascade = "opencv_traincascade.exe"
        if train_cascade in str(folder_path_train_cascade):
            self.destroy()
            self.w3.show()
        else:
            self.messagebox()


class CreateSamples(QDialog):
    def __init__(self):
        super(CreateSamples, self).__init__()
        loadUi('gui/GuiCreateSamples.ui', self)
        self.w7 = ExtendedParametersCreateSamples()
        self.w4 = ChooseTrainCascade()
        self.button_choose_positive.clicked.connect(self.load_files_positive)
        self.plus_width.clicked.connect(lambda: self.change_resolution_width("+"))
        self.minus_width.clicked.connect(lambda: self.change_resolution_width("-"))
        self.plus_height.clicked.connect(lambda: self.change_resolution_height("+"))
        self.minus_height.clicked.connect(lambda: self.change_resolution_height("-"))

        self.plus_width_10.clicked.connect(lambda: self.change_resolution_width_10("+"))
        self.minus_width_10.clicked.connect(lambda: self.change_resolution_width_10("-"))
        self.plus_height_10.clicked.connect(lambda: self.change_resolution_height_10("+"))
        self.minus_height_10.clicked.connect(lambda: self.change_resolution_height_10("-"))

        self.button_ok.clicked.connect(self.create_create_samples)
        self.button_extended_parameters.clicked.connect(self.open_extend_parameters_create_samples)

        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)

    def help_me(self):
        self.w66.show()

    def open_extend_parameters_create_samples(self):
        self.destroy()
        self.w7.show()

    def back_to_select_opencv(self):
        self.destroy()
        self.w4.show()

    def create_create_samples(self):
        print(str(number_positive_images_in_file + 1))
        os.chdir(main_path)
        text_cmd = "opencv_createsamples -info positive.dat -num " + str(
            number_positive_images_in_file + 1) + " -vec positive.vec -w " + str(width) + " -h " + str(height)
        os.system("start /B start cmd.exe @cmd /K" + text_cmd)
        self.back_to_select_opencv()

    def load_files_positive(self):
        directory = main_path + "/positive"
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    os.remove(os.path.join(root, file))
        if not os.path.exists(directory):
            os.makedirs(directory)
        filter_mask = "Python/Text files (*.png *.jpg)"
        filenames_image = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        file_txt = open(main_path + "/positive.dat", "w+")
        for count in range(len(filenames_image)):
            src = filenames_image[count]
            print("src: " + src)
            dst = main_path + "/positive"
            print("dst: " + dst)
            val = 0
            while val <= 100:
                val += 1
                self.progressbar_positive.setValue(val)
            filenames_image[count] = QtGui.QImage(filenames_image[count]).scaled(final_value_width, final_value_height)

            if src is not dst:
                filenames_image[count].save(main_path + "/positive/" + str(count) + ".png")
            file_txt.write(main_path + "/positive/" + str(count) + ".png")
            file_txt.write(" 1 0 0 ")
            file_txt.write(str(final_value_width))
            file_txt.write(" ")
            file_txt.write(str(final_value_height))
            file_txt.write('\n')
        file_txt.close()
        global number_positive_images_in_file
        number_positive_images_in_file = count
        print(number_positive_images_in_file + 1)
        self.button_ok.setEnabled(True)
        self.button_extended_parameters.setEnabled(True)

    def messagebox(self):
        QMessageBox.information(self, 'Ostrzeżenie', 'Rozdzielczość obrazu nie może być zerem ani być ujemną!')

    def change_resolution_width(self, mark):
        width = self.width.text()
        width = int(width)
        global final_value_width
        if mark == "+":
            final_value_width = width + 1
            self.width.setText(str(final_value_width))
        if mark == "-":
            final_value_width = width - 1
            if final_value_width >= 1:
                self.width.setText(str(final_value_width))
            else:
                self.messagebox()

    def change_resolution_height(self, mark):
        height = self.height.text()
        height = int(height)
        global final_value_height
        if mark == "+":
            final_value_height = height + 1
            self.height.setText(str(final_value_height))
        if mark == "-":
            final_value_height = height - 1
            if final_value_height >= 1:
                self.height.setText(str(final_value_height))
            else:
                self.messagebox()

    def change_resolution_width_10(self, mark):
        width = self.width.text()
        width = int(width)
        global final_value_width
        if mark == "+":
            final_value_width = width + 10
            self.width.setText(str(final_value_width))
        if mark == "-":
            final_value_width = width - 10
            if final_value_width >= 10:
                self.width.setText(str(final_value_width))
            else:
                self.messagebox()

    def change_resolution_height_10(self, mark):
        height = self.height.text()
        height = int(height)
        global final_value_height
        if mark == "+":
            final_value_height = height + 10
            self.height.setText(str(final_value_height))
        if mark == "-":
            final_value_height = height - 10
            if final_value_height >= 10:
                self.height.setText(str(final_value_height))
            else:
                self.messagebox()


class Help(QDialog):
    def __init__(self):
        super(Help, self).__init__()
        loadUi('gui/GuiHelp.ui', self)


class SelectOpenCV(QDialog):
    def __init__(self):
        super(SelectOpenCV, self).__init__()
        loadUi('gui/GuiSelectOpenCV.ui', self)
        self.w3 = NegativeSamples()
        self.w10 = CreateSamples()
        self.w66 = Help()
        self.button_help.clicked.connect(self.help_me)
        self.button_choose_createsamples.clicked.connect(self.choose_open_cv_create_samples)
        self.button_only_traincascade.clicked.connect(self.choose_open_cv_train_cascade)
        self.button_choose_createsamples.setToolTip("Narzędzie do tworzenia pliku obrazów pozytywnych.")
        self.button_only_traincascade.setToolTip("Narzędzie do tworzenia pliku obrazów negatywnych.")

    def help_me(self):
        self.w66.show()

    def messagebox(self):
        QMessageBox.information(self, 'Ostrzeżenie', 'Wskazano błędną aplikację!')

    def choose_open_cv_create_samples(self):
        filter_mask = "Python/Text files (*.exe)"
        folder_path_create_samples = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        global main_path
        main_path = os.path.dirname(str(folder_path_create_samples))
        main_path = main_path[2:]
        print(str(main_path))
        create_samples = "opencv_createsamples.exe"
        if create_samples in str(folder_path_create_samples):
            self.destroy()
            self.w10.show()
        else:
            self.messagebox()

    def choose_open_cv_train_cascade(self):
        filter_mask = "Python/Text files (*.exe)"
        folder_path_train_cascade = QFileDialog.getOpenFileNames(None, 'Open file', './', filter_mask)[0]
        global main_path
        main_path = os.path.dirname(str(folder_path_train_cascade))
        main_path = main_path[2:]
        print(str(main_path))
        train_cascade = "opencv_traincascade.exe"
        if train_cascade in str(folder_path_train_cascade):
            self.destroy()
            self.w3.show()
        else:
            self.messagebox()


class ChangeCascade(QDialog):
    def __init__(self):
        super(ChangeCascade, self).__init__()
        loadUi('gui/GuiChangeCascade.ui', self)
        self.button_change_erythrocytes.clicked.connect(self.click_change_cascade_ery)
        self.button_change_thrombocytes.clicked.connect(self.click_change_cascade_throm)
        self.button_change_monocytes.clicked.connect(self.click_change_cascade_mono)
        self.button_change_lymphocytes.clicked.connect(self.click_change_cascade_lym)
        self.button_change_neutrophils.clicked.connect(self.click_change_cascade_neu)
        self.button_ok.clicked.connect(self.exit_change_cascade)

    def messagebox(self):
        QMessageBox.information(self, 'Informacja', 'Kaskada dodana pomyślnie.')

    def exit_change_cascade(self):
        self.destroy()

    def click_change_cascade_ery(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        cascade, _ = QFileDialog.getOpenFileName(self, "Open File", "", "XML file (*.xml)", options=options)
        global cascade_erythrocytes, cascade_thrombocytes, cascade_monocytes, cascade_lymphocytes, cascade_neutrophils

        if self.button_change_erythrocytes.clicked.connect:
            cascade_erythrocytes = cascade
            lambda: self.cv_cascade(self, name_filename, "erythrocyte", cascade_erythrocytes)
            self.messagebox()

    def click_change_cascade_throm(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        cascade, _ = QFileDialog.getOpenFileName(self, "Open File", "", "XML file (*.xml)", options=options)
        global cascade_erythrocytes, cascade_thrombocytes, cascade_monocytes, cascade_lymphocytes, cascade_neutrophils

        if self.button_change_thrombocytes.clicked.connect:
            cascade_thrombocytes = cascade
            lambda: self.cv_cascade(self, name_filename, "thrombocyte", cascade_thrombocytes)
            self.messagebox()

    def click_change_cascade_mono(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        cascade, _ = QFileDialog.getOpenFileName(self, "Open File", "", "XML file (*.xml)", options=options)
        global cascade_erythrocytes, cascade_thrombocytes, cascade_monocytes, cascade_lymphocytes, cascade_neutrophils

        if self.button_change_monocytes.clicked.connect:
            cascade_monocytes = cascade
            lambda: self.cv_cascade(self, name_filename, "monocyte", cascade_monocytes)
            self.messagebox()

    def click_change_cascade_lym(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        cascade, _ = QFileDialog.getOpenFileName(self, "Open File", "", "XML file (*.xml)", options=options)
        global cascade_erythrocytes, cascade_thrombocytes, cascade_monocytes, cascade_lymphocytes, cascade_neutrophils

        if self.button_change_lymphocytes.clicked.connect:
            cascade_lymphocytes = cascade
            lambda: self.cv_cascade(self, name_filename, "lymphocyte", cascade_lymphocytes)
            self.messagebox()

    def click_change_cascade_neu(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        cascade, _ = QFileDialog.getOpenFileName(self, "Open File", "", "XML file (*.xml)", options=options)
        global cascade_erythrocytes, cascade_thrombocytes, cascade_monocytes, cascade_lymphocytes, cascade_neutrophils

        if self.button_change_neutrophils.clicked.connect:
            cascade_neutrophils = cascade
            lambda: self.cv_cascade(self, name_filename, "neutrophil", cascade_neutrophils)

            self.messagebox()


filename = None


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.w1 = ChangeCascade()
        self.w3 = SelectOpenCV()
        loadUi('gui/GuiMakeSegmentation.ui', self)
        self.button_choose_image.clicked.connect(self.browse_folder)
        self.button_change_cascade.clicked.connect(self.open_change_cascade)
        self.button_create_own_cascade.clicked.connect(self.open_select_open_cv)
        self.button_erythrocytes.clicked.connect(self.messagebox)
        self.button_thrombocytes.clicked.connect(self.messagebox)
        self.button_monocytes.clicked.connect(self.messagebox)
        self.button_lymphocytes.clicked.connect(self.messagebox)
        self.button_neutrophils.clicked.connect(self.messagebox)
        self.button_preparation_image.clicked.connect(self.openprepareimage)

    def openprepareimage(self):
        p = Popen('python C:/Users/1/PycharmProjects/ProjektInzynierski/SnippingMenu.py', shell=True,
                  stdout=PIPE)
        out, err = p.communicate()

    def open_change_cascade(self):
        self.w1.show()

    def messagebox(self):
        if filename is None:
            QMessageBox.warning(self, 'Ostrzeżenie', 'Musisz wybrać obraz, zanim dokonasz segmentacji.')

    def browse_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        global filename
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                  "Images (*.png *.jpg)", options=options)
        if filename:
            self.load_image(filename)
            self.button_erythrocytes.clicked.connect(
                lambda: self.cv_cascade(self, name_filename, "erythrocyte", cascade_erythrocytes))
            self.button_thrombocytes.clicked.connect(
                lambda: self.cv_cascade(self, name_filename, "thrombocyte", cascade_thrombocytes))
            self.button_monocytes.clicked.connect(
                lambda: self.cv_cascade(self, name_filename, "monocyte", cascade_monocytes))
            self.button_lymphocytes.clicked.connect(
                lambda: self.cv_cascade(self, name_filename, "lymphocyte", cascade_lymphocytes))
            self.button_neutrophils.clicked.connect(
                lambda: self.cv_cascade(self, name_filename, "neutrophil", cascade_neutrophils))

            global name_filename
            name_filename = filename
            QMessageBox.information(self, 'Informacja',
                                    'Obraz załadowany pomyślnie.')
        else:
            print('Invalid Image')
        return filename

    def load_image(self, filenames):
        pimp = QPixmap(filenames)
        width = pimp.width()
        height = pimp.height()

        while height >= 800:
            height = height - 1

        while width >= 800:
            width = width - 1

        self.imageLabel.resize(width, height)
        pimp2 = QtGui.QImage(pimp).scaled(width, height, QtCore.Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(QPixmap(pimp2))
        self.imageLabel.setAlignment(QtCore.Qt.AlignHorizontal_Mask)
        return pimp2

    @staticmethod
    def cv_cascade(self, pic, text, cascade):
        blood_cascade = cv.CascadeClassifier(cascade)
        pic = str(pic)
        image = cv.imread(pic, 0)
        object_blood = blood_cascade.detectMultiScale(image, 1.3, 5)

        for (x, y, w, h) in object_blood:
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(image, text, (x + w, y + h), cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
            global number_found_elements
            number_found_elements = object_blood.shape[0]
            QPixmap(cv.imshow('img', image))
            self.complete_count(text)

        if number_found_elements == 0:
            print(number_found_elements)
            number_found_elements = 0
            self.complete_count(text)
            QPixmap(cv.imshow('img', image))

        else:
            number_found_elements = 0

    def open_select_open_cv(self):
        self.w3.show()

    def complete_count(self, text):
        if text == "erythrocyte":
            self.count_erythrocytes.setText(str(number_found_elements))
        if text == "thrombocyte":
            self.count_thrombocytes.setText(str(number_found_elements))
        if text == "monocyte":
            self.count_monocytes.setText(str(number_found_elements))
        if text == "lymphocyte":
            self.count_lymphocytes.setText(str(number_found_elements))
        if text == "neutrophil":
            self.count_neutrophils.setText(str(number_found_elements))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Segmentation')
    window.show()
    sys.exit(app.exec())
