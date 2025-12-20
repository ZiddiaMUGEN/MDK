## this is a utility for viewing animations built via MDK (code-based animations).
import os
import sys
import math
import importlib.util
from pathlib import Path

from mdk.types.context import CompilerContext
from mdk.resources.animation import Animation, Sequence, SequenceModifier, Frame

from mdk.utils.sff import SFF

from PyQt6.QtCore import Qt, QFileSystemWatcher
from PyQt6.QtGui import QImage, QPixmap, QTransform
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
    QComboBox,
    QLabel,
    QTabWidget,
    QTextEdit,
    QPushButton,
    QSlider
)

class MainWindow(QMainWindow):
    def __init__(self, input_file: str, sff: SFF):
        super().__init__()
        self._loaded = False
        self.sff = sff

        directory = os.path.dirname(os.path.abspath(input_file))
        ## this is hacky, but i guess most venv will follow this name?
        watches = [str(file) for file in Path(directory).rglob("*.py") if file.is_file() and "venv" not in str(file.parent)]
        print(f"Watching files for modifications: {watches}")
        self.watcher = QFileSystemWatcher(watches)
        self.watcher.fileChanged.connect(self.onModuleUpdated)

        self.path = input_file
        self.packages = [k for k in sys.modules]
        self.module = isolate(self.path)
        self.components = recurse_animations(self.module, [])

        self.setWindowTitle("MDK Animation Viewer")
        self.resize(1200, 800)

        center = QWidget()
        self.setCentralWidget(center)

        self.gridLayout = QGridLayout()
        center.setLayout(self.gridLayout)

        ## upper left: display image
        image = QImage(400, 400, QImage.Format.Format_RGBA8888)
        image.fill(Qt.GlobalColor.black)

        pixmap = QPixmap.fromImage(image)

        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(pixmap)

        self.gridLayout.addWidget(self.imageLabel, 0, 0, 5, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        ## upper right: select component
        self.componentSwitch = QComboBox()
        self.componentSwitch.addItems([c['name'] for c in self.components])
        self.componentSwitch.currentIndexChanged.connect(self.onAnimSelected)
        self.gridLayout.addWidget(self.componentSwitch, 0, 1)

        ## middle right: toggles and reload
        reload = QPushButton()
        reload.clicked.connect(self.onModuleUpdated)
        reload.setText("Reload")
        self.gridLayout.addWidget(reload, 1, 1)

        ## middle right: frame select
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.onFrameSelected)
        self.gridLayout.addWidget(self.slider, 2, 1)

        ## middle right: frame number, total frames, animation length
        self.animtext = QLabel()
        self.animtext.setText("Loading...")
        self.gridLayout.addWidget(self.animtext, 3, 1)

        ## lower right: infobox
        self.infobox = QTabWidget()
        self.pythonContent = QTextEdit()
        self.pythonContent.setReadOnly(True)
        self.cnsContent = QTextEdit()
        self.cnsContent.setReadOnly(True)
        self.infobox.addTab(self.pythonContent, "Python (Decompiled)")
        self.infobox.addTab(self.cnsContent, "AIR (Output)")
        self.gridLayout.addWidget(self.infobox, 4, 1)

        ## trigger onAnimSelected once to preload python/CNS/sprites
        self.onAnimSelected()

        self._loaded = True

    def onAnimSelected(self):
        ## disconnect the slider events first!
        self.slider.valueChanged.disconnect(self.onFrameSelected)

        ## note the weird try/excepts here are to preserve id of None
        ## (since `Animation.compile()` assigns IDs to animations in the context)
        component = self.components[self.componentSwitch.currentIndex()]['name']
        script: Animation = self.components[self.componentSwitch.currentIndex()]['obj']

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

        self.frames: list[Frame] = script.sequence._frames if isinstance(script, Animation) else script._frames

        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.frames) - 1)
        self.slider.setValue(0)

        self.onFrameSelected()

        self.slider.valueChanged.connect(self.onFrameSelected)

    def onFrameSelected(self):
        frame = self.slider.value()
        sum_len = sum([x._length for x in self.frames])
        sum_now = sum([x._length for x in self.frames[:frame]])
        self.reload_sprite(frame, 0)
        self.animtext.setText(f"Frame {frame + 1} / {len(self.frames)}: tick {sum_now} / {sum_len}, length {self.frames[frame]._length}")
    
    def reload_sprite(self, index: int, palette: int):
        sprite = self.sff.find_sprite(self.frames[index]._group, self.frames[index]._index)
        if sprite != None:
            temp_paletted = sprite.palette(self.sff.palettes[palette])
            scale_ratio =  self.frames[index]._scale[0] / self.frames[index]._scale[1]
            if scale_ratio > 0:
                scale_width = 400
                scale_height = math.ceil(400 / scale_ratio)
            else:
                scale_width = math.ceil(400 / scale_ratio)
                scale_height = 400
            image = QImage(temp_paletted, sprite.width, sprite.height, QImage.Format.Format_RGBA8888).scaled(scale_width, scale_height)
            if self.frames[index]._rotate != 0:
                transform = QTransform()
                transform.rotate(self.frames[index]._rotate * -1)
                image = image.transformed(transform).scaled(scale_width, scale_height)
            pixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(pixmap)
        else:
            image = QImage(400, 400, QImage.Format.Format_RGBA8888)
            image.fill(Qt.GlobalColor.black)
            pixmap = QPixmap.fromImage(image)
            self.imageLabel.setPixmap(pixmap)

    def onModuleUpdated(self):
        selection = self.components[self.componentSwitch.currentIndex()]

        ## discard the loaded module and reload from scratch.
        try:
            ## remove the old context, since it will contain a full list of animations from prior loads.
            del CompilerContext._instance
            self.module = isolate(self.path)
            reloads: list[str] = []
            for k in sys.modules:
                if k not in self.packages:
                    print(f"Hot reload dynamic module {k}")
                    reloads.append(k)
            for k in reloads:
                importlib.reload(sys.modules[k])
            self.components = recurse_animations(self.module, [])

            self.componentSwitch.currentIndexChanged.disconnect()
            self.componentSwitch.clear()
            self.componentSwitch.addItems([c['name'] for c in self.components])
            self.componentSwitch.currentIndexChanged.connect(self.onAnimSelected)
            idx = next((index for index, d in enumerate(self.components) if d["name"] == selection['name']), None)
            if idx != None:
                self.componentSwitch.setCurrentIndex(idx)
            else:
                self.componentSwitch.setCurrentIndex(0)
            self.reload_sprite(0, 0)
        except Exception as exc:
            self.cnsContent.setText(f"Failed to load module!\n{exc}")
            self.pythonContent.setText(f"Failed to load module!\n{exc}")

def isolate(path):
    if not os.path.dirname(os.path.abspath(path)) in sys.path:
        sys.path.append(os.path.dirname(os.path.abspath(path)))
    # isolated namespace
    spec = importlib.util.spec_from_file_location("isolate", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {path}")
    
    # import module in namespace
    module = importlib.util.module_from_spec(spec)
    
    # execute
    spec.loader.exec_module(module)
    
    return module

def recurse_animations(module, visited: list[str] = []):
    components = []
    for key in module.__dict__:
        if isinstance(module.__dict__[key], Animation) or isinstance(module.__dict__[key], Sequence) or isinstance(module.__dict__[key], SequenceModifier):
            if not any([x for x in components if x['name'] == key]):
                components.append({ "name": key, "obj": module.__dict__[key] })
        elif type(module.__dict__[key]).__name__ == "module" and key not in visited:
            visited.append(key)
            for c in recurse_animations(module.__dict__[key], visited):
                if not any([x for x in components if x['name'] == c['name']]):
                    components.append(c)

    return components

def launch():
    if len(sys.argv) < 3:
        raise Exception("Usage: mdkair <build script> <sff file>")
    input_file = sys.argv[1]
    sff_file = sys.argv[2]

    ## the window falls in this context manager because `sff_file` needs to stay open.
    with open(sff_file, mode='rb') as f:
        sff = SFF.load(f)

        app = QApplication(sys.argv)
        window = MainWindow(input_file, sff)
        window.show()
        app.exec()

if __name__ == "__main__":
    launch()