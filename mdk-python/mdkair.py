## this is a utility for viewing animations built via MDK (code-based animations).
import os
import sys
import importlib.util

from mdk.types.context import CompilerContext
from mdk.resources.animation import Animation, Sequence, SequenceModifier

from PyQt6.QtCore import Qt, QFileSystemWatcher
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
    QComboBox,
    QLabel,
    QTabWidget,
    QTextEdit,
    QPushButton
)

class MainWindow(QMainWindow):
    def __init__(self, input_file):
        super().__init__()
        self._loaded = False

        self.watcher = QFileSystemWatcher([os.path.abspath(input_file)])
        self.watcher.fileChanged.connect(self.onModuleUpdated)

        self.path = input_file
        self.module = isolate(self.path)
        self.components = []
        for key in self.module.__dict__:
            if isinstance(self.module.__dict__[key], Animation) or isinstance(self.module.__dict__[key], Sequence) or isinstance(self.module.__dict__[key], SequenceModifier):
                self.components.append(key)

        self.setWindowTitle("MDK Animation Viewer")
        self.resize(800, 600)

        center = QWidget()
        self.setCentralWidget(center)

        self.gridLayout = QGridLayout()
        center.setLayout(self.gridLayout)

        ## upper left: display image
        self.image = QImage(400, 600, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.black)

        self.pixmap = QPixmap.fromImage(self.image)

        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(self.pixmap)

        self.gridLayout.addWidget(self.imageLabel, 0, 0, 3, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        ## upper right: select component
        self.componentSwitch = QComboBox()
        self.componentSwitch.addItems(self.components)
        self.componentSwitch.currentIndexChanged.connect(self.onAnimSelected)
        self.gridLayout.addWidget(self.componentSwitch, 0, 1)

        ## middle right: toggles and reload
        reload = QPushButton()
        reload.clicked.connect(self.onModuleUpdated)
        reload.setText("Reload")
        self.gridLayout.addWidget(reload, 1, 1)

        ## lower right: infobox
        self.infobox = QTabWidget()
        self.pythonContent = QTextEdit()
        self.pythonContent.setReadOnly(True)
        self.cnsContent = QTextEdit()
        self.cnsContent.setReadOnly(True)
        self.infobox.addTab(self.pythonContent, "Python (Decompiled)")
        self.infobox.addTab(self.cnsContent, "AIR (Output)")
        self.gridLayout.addWidget(self.infobox, 2, 1)

        ## trigger onAnimSelected once to preload python/CNS/sprites
        self.onAnimSelected()

        self._loaded = True

    def onAnimSelected(self):
        ## note the weird try/excepts here are to preserve id of None
        ## (since `Animation.compile()` assigns IDs to animations in the context)
        component = self.components[self.componentSwitch.currentIndex()]
        script = self.module.__dict__[component]

        content = script.python(component)
        self.pythonContent.setText(content)

        try:
            original_id = script._id
        except:
            pass

        content = script.compile()
        if content.startswith("[Begin Action"):
            content = "\n".join(content.split("\n")[1:])
        self.cnsContent.setText(content)

        try:
            script._id = original_id # type: ignore
        except:
            pass

    def onModuleUpdated(self):
        selection = self.components[self.componentSwitch.currentIndex()]

        ## discard the loaded module and reload from scratch.
        try:
            ## remove the old context, since it will contain a full list of animations from prior loads.
            del CompilerContext._instance
            self.module = isolate(self.path)
            self.components = []
            for key in self.module.__dict__:
                if isinstance(self.module.__dict__[key], Animation) or isinstance(self.module.__dict__[key], Sequence) or isinstance(self.module.__dict__[key], SequenceModifier):
                    self.components.append(key)
        except Exception as exc:
            self.cnsContent.setText(f"Failed to load module!\n{exc}")
            self.pythonContent.setText(f"Failed to load module!\n{exc}")

        self.componentSwitch.clear()
        self.componentSwitch.addItems(self.components)
        if selection in self.components:
            self.componentSwitch.setCurrentIndex(self.components.index(selection))
        else:
            self.componentSwitch.setCurrentIndex(0)


def isolate(path):
    # isolated namespace
    spec = importlib.util.spec_from_file_location("isolate", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {path}")
    
    # import module in namespace
    module = importlib.util.module_from_spec(spec)
    
    # execute
    spec.loader.exec_module(module)
    
    return module

def launch():
    if len(sys.argv) < 2:
        raise Exception("Usage: mdkair <animation script>")
    input_file = sys.argv[1]

    app = QApplication(sys.argv)
    window = MainWindow(input_file)
    window.show()
    app.exec()

if __name__ == "__main__":
    launch()