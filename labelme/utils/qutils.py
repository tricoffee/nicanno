from qtpy import QtCore
import os 
import cv2
from .image import img_data_to_pil
from ..label_file import LabelFile,LabelFileError
from ..widgets.brightness_contrast_dialog import BrightnessContrastDialog
from qtpy import QtGui
import PIL 


def mqplot(qmw,fnm):
    filename = qmw.filename
    if filename in qmw.imageList and (
        qmw.fileListWidget.currentRow() != qmw.imageList.index(filename)
    ):
        qmw.fileListWidget.setCurrentRow(qmw.imageList.index(filename))
        qmw.fileListWidget.repaint()
        return

    qmw.resetState()
    qmw.canvas.setEnabled(False)
    if filename is None:
        filename = qmw.settings.value("filename", "")
    filename = str(filename)
    if not QtCore.QFile.exists(filename):
        qmw.errorMessage(
            qmw.tr("Error opening file"),
            qmw.tr("No such file: <b>%s</b>") % filename,
        )
        return False
    # assumes same name, but json extension
    qmw.status(qmw.tr("Loading %s...") % os.path.basename(str(filename)))
    label_file = os.path.splitext(filename)[0] + ".json"
    if qmw.output_dir:
        label_file_without_path = os.path.basename(label_file)
        label_file = os.path.join(qmw.output_dir, label_file_without_path)
    if QtCore.QFile.exists(label_file) and LabelFile.is_label_file(
        label_file
    ):
        try:
            qmw.labelFile = LabelFile(label_file)
        except LabelFileError as e:
            qmw.errorMessage(
                qmw.tr("Error opening file"),
                qmw.tr(
                    "<p><b>%s</b></p>"
                    "<p>Make sure <i>%s</i> is a valid label file."
                )
                % (e, label_file),
            )
            qmw.status(qmw.tr("Error reading %s") % label_file)
            return False
        #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # qmw.imageData = qmw.labelFile.imageData
        # qmw.imagePath = os.path.join(
        #    os.path.dirname(label_file),
        #   qmw.labelFile.imagePath,
        # )
        # qmw.imageData = LabelFile.load_image_file(filename)
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        qmw.imageData = cv2.imread(filename)
        if qmw.imageData:
            qmw.imagePath = filename
        qmw.otherData = qmw.labelFile.otherData
    else:
        #qmw.imageData = LabelFile.load_image_file(filename)
        #qmw.imageData = cv2.imread(filename).tobytes()
        qmw.imageData = cv2.imread(filename)



        # if qmw.imageData:
        #     qmw.imagePath = filename
        qmw.imagePath = filename
        qmw.labelFile = None
    #image = QtGui.QImage.fromData(qmw.imageData)
    #https://blog.csdn.net/weixin_45875105/article/details/109580568
    # cv 图片转换成 qt图片
    image = QtGui.QImage(qmw.imageData.data, # 数据源
                            qmw.imageData.shape[1],  # 宽度
                            qmw.imageData.shape[0],	# 高度
                            qmw.imageData.shape[1] * 1, # 行字节数
                            QtGui.QImage.Format_Grayscale8)

    if image.isNull():
        formats = [
            "*.{}".format(fmt.data().decode())
            for fmt in QtGui.QImageReader.supportedImageFormats()
        ]
        qmw.errorMessage(
            qmw.tr("Error opening file"),
            qmw.tr(
                "<p>Make sure <i>{0}</i> is a valid image file.<br/>"
                "Supported image formats: {1}</p>"
            ).format(filename, ",".join(formats)),
        )
        qmw.status(qmw.tr("Error reading %s") % filename)
        return False
    qmw.image = image
    qmw.filename = filename
    if qmw._config["keep_prev"]:
        prev_shapes = qmw.canvas.shapes
    qmw.canvas.loadPixmap(QtGui.QPixmap.fromImage(image))
    flags = {k: False for k in qmw._config["flags"] or []}
    if qmw.labelFile:
        qmw.loadLabels(qmw.labelFile.shapes)
        if qmw.labelFile.flags is not None:
            flags.update(qmw.labelFile.flags)
    qmw.loadFlags(flags)
    if qmw._config["keep_prev"] and qmw.noShapes():
        qmw.loadShapes(prev_shapes, replace=False)
        qmw.setDirty()
    else:
        qmw.setClean()
    qmw.canvas.setEnabled(True)
    # set zoom values
    is_initial_load = not qmw.zoom_values
    if qmw.filename in qmw.zoom_values:
        qmw.zoomMode = qmw.zoom_values[qmw.filename][0]
        qmw.setZoom(qmw.zoom_values[qmw.filename][1])
    elif is_initial_load or not qmw._config["keep_prev_scale"]:
        qmw.adjustScale(initial=True)
    # set scroll values
    for orientation in qmw.scroll_values:
        if qmw.filename in qmw.scroll_values[orientation]:
            qmw.setScroll(
                orientation, qmw.scroll_values[orientation][qmw.filename]
            )
    # set brightness constrast values
    dialog = BrightnessContrastDialog(
        #img_data_to_pil(qmw.imageData),
        #PIL.Image.fromarray(qmw.imageData),
        qmw.imageData,
        qmw.onNewBrightnessContrast,
        parent=qmw,
    )
    brightness, contrast = qmw.brightnessContrast_values.get(
        qmw.filename, (None, None)
    )
    if qmw._config["keep_prev_brightness"] and qmw.recentFiles:
        brightness, _ = qmw.brightnessContrast_values.get(
            qmw.recentFiles[0], (None, None)
        )
    if qmw._config["keep_prev_contrast"] and qmw.recentFiles:
        _, contrast = qmw.brightnessContrast_values.get(
            qmw.recentFiles[0], (None, None)
        )
    if brightness is not None:
        dialog.slider_brightness.setValue(brightness)
    if contrast is not None:
        dialog.slider_contrast.setValue(contrast)
    qmw.brightnessContrast_values[qmw.filename] = (brightness, contrast)
    if brightness is not None or contrast is not None:
        dialog.onNewValue(None)
    qmw.paintCanvas()
    qmw.addRecentFile(qmw.filename)
    qmw.toggleActions(True)
    qmw.canvas.setFocus()
    qmw.status(qmw.tr("Loaded %s") % os.path.basename(str(filename)))
    return True


class PlotThread(QtCore.QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串

    #trigger = QtCore.Signal(str)
    #trigger = QtCore.Signal([list,int])
    trigger = QtCore.Signal([object,str])
    
    qmw = None 
    filename  = None

    def __int__(self):
        # 初始化函数
        super(PlotThread, self).__init__()

    def run(self):
        #重写线程执行的run函数
        #触发自定义信号
        # 通过自定义信号把待显示的字符串传递给槽函数

        # for i in range(20):
        #     time.sleep(1)
        #     # 通过自定义信号把待显示的字符串传递给槽函数
        #     self.trigger.emit(str(i))

        #self.trigger.emit(self.filename)
        self.trigger.emit(self.qmw,self.filename)
