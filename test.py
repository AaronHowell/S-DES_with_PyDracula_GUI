from PyQt5.QtWidgets import QApplication, QComboBox, QWidget

def handle_combobox_change(index):
    print(f"Selected index: {index}")

app = QApplication([])

window = QWidget()
combo_box = QComboBox(window)

# 添加选项到组合框
combo_box.addItem("Option 1")
combo_box.addItem("Option 2")
combo_box.addItem("Option 3")

# 连接信号和槽
combo_box.currentIndexChanged.connect(handle_combobox_change)

window.show()
app.exec_()
