from PyQt6.QtWidgets import *
from gui import *
import csv
from typing import Dict, TypedDict, Optional

class GradeInfo(TypedDict, total = False):
    Score: int
    Grade: str

class Logic(QMainWindow, Ui_MainWindow):
    """Main Window

    Initializes the gradebook dictionary and button functionality on the GUI"""
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.gradebook = {
        }

        self.pushButton_add.clicked.connect(self.add)
        self.pushButton_edit.clicked.connect(self.edit)
        self.pushButton_delete.clicked.connect(self.delete)
        self.pushButton_save.clicked.connect(self.save)
        self.pushButton_load.clicked.connect(self.load)
        self.listWidget_grades.itemClicked.connect(self.prefill_inputs)

    def prefill_inputs(self, item: QListWidgetItem) -> None:
        """This displays the selected line's name and score in their respective input lines"""
        line = item.text()
        name, score, *_ = line.split(" : ")
        self.lineEdit_name.setText(name)
        self.lineEdit_score.setText(score)

    def grade_curve(self) -> None:
        """Checks for existence of a gradebook dictionary then assigns curved grades based on the highest score in the gradebook dictionary"""
        if not self.gradebook:
            return

        high_score: int = max(int(info["Score"]) for info in self.gradebook.values())

        for name, info in self.gradebook.items():
            score: int = info["Score"]
            if score >= (high_score - 10):
                letter = "A"
            elif score >= (high_score - 20):
                letter = "B"
            elif score >= (high_score - 30):
                letter = "C"
            elif score >= (high_score - 40):
                letter = "D"
            else:
                letter = "F"

            info["Grade"] = letter

    def update_list(self) -> None:
        """Updates the gradebook dictionary with grades and then sorts entries by name"""
        self.listWidget_grades.clear()
        for name, info in self.gradebook.items():
            score: int = info["Score"]
            grade: str = info.get("Grade", "")
            text = f"{name} : {score}"
            if grade:
                text += f" : {grade}"
            self.listWidget_grades.addItem(text)
            self.listWidget_grades.sortItems()

    def add(self) -> None:
        """Add a student and score to the gradebook dictionary"""
        name: str = self.lineEdit_name.text().strip()
        score: str = self.lineEdit_score.text().strip()

        if not name or not score:
            QMessageBox.warning(self, "Error", "Please enter your name and your score")
            return

        try:
            score: int = int(score)
        except ValueError:
            QMessageBox.warning(self, "Error", "Score must be a number")
            return

        if int(score) > 100:
            QMessageBox.warning(self, "Error", "Score must be less than or equal to 100")
            return

        self.gradebook[name] = {"Score": int(score)}
        self.listWidget_grades.addItem(f"{name} : {score}")
        self.grade_curve()
        self.update_list()
        self.lineEdit_name.clear()
        self.lineEdit_score.clear()

    def edit(self) -> None:
        """Edits the gradebook name and score using the selected line in the list widget"""
        item_to_edit: Optional[QListWidgetItem] = self.listWidget_grades.currentItem()

        if item_to_edit is None:
            QMessageBox.warning(self, "Error", "Please select a line to edit")
            return

        line: str = item_to_edit.text()
        old_name: str = line.split(" : ")[0]

        new_name: str = self.lineEdit_name.text().strip()
        new_score: str = self.lineEdit_score.text().strip()

        if not new_name or not new_score:
            QMessageBox.warning(self, "Error", "Please enter your name and your score")
            return

        try:
            new_score: int = int(new_score)
        except ValueError:
            QMessageBox.warning(self, "Error", "Score must be a number")
            return

        if new_score > 100:
            QMessageBox.warning(self, "Error", "Score cannot exceed 100")
            return

        if old_name != new_name:
            if old_name in self.gradebook:
                del self.gradebook[old_name]

        self.gradebook[new_name] = {"Score" : int(new_score)}
        item_to_edit.setText(f"{new_name} : {new_score}")
        self.grade_curve()
        self.update_list()
        self.lineEdit_name.clear()
        self.lineEdit_score.clear()

    def delete(self) -> None:
        """Deletes the selected line in the list widget from the gradebook dictionary"""
        item_to_delete = self.listWidget_grades.currentItem()

        if item_to_delete is None:
            QMessageBox.warning(self, "Error", "Please select a line to delete")
            return

        line = item_to_delete.text()
        name = line.split(" : ")[0]

        if name in self.gradebook:
            del self.gradebook[name]

        row = self.listWidget_grades.row(item_to_delete)
        self.listWidget_grades.takeItem(row)
        self.grade_curve()
        self.update_list()

    def load(self) -> None:
        """Loads a CSV file and updates the gradebook dictionary and list widget with the contents"""
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", ".", "CSV (*.csv)")

        if not filename:
            return

        try:
            self.gradebook.clear()
            self.listWidget_grades.clear()

            with open(filename, "r", newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row.get("Name")
                    score = row.get("Score")
                    grade = row.get("Grade", "")
                    if name and score:
                        self.gradebook[name] = {"Score" : int(score), "Grade" : grade}
                        text = f"{name} : {score}"
                        if grade:
                            text += f" : {grade}"
                        self.listWidget_grades.addItem(text)
            QMessageBox.information(self, "Success!", "Gradebook has been loaded!")

        except Exception as e:
            QMessageBox.critical(self, "Error!", f"Failed to load file due to {str(e)}")

    def save(self) -> None:
        """Saves current gradebook dictionary information to a CSV file in the current directory"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "./", "*.csv")

        if not filename:
            return

        try:

            self.grade_curve()

            with open(filename, "w", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Name", "Score", "Grade"])

                for name, info in self.gradebook.items():
                    score = info["Score"]
                    grade = info.get("Grade", "")
                    writer.writerow([name, score, grade])

            QMessageBox.information(self, "Success!", "Gradebook has been saved!")

        except Exception as e:
            QMessageBox.warning(self, "Error!", f"Failed to save gradebook due to {str(e)}")