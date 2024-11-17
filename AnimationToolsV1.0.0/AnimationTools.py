import maya.cmds as cmds
from PySide2.QtWidgets import QWidget, QPushButton, QSlider, QLabel,QCheckBox,QApplication,QTabWidget,QMainWindow
from PySide2.QtCore import Qt, QRect
from PySide2.QtCore import QUrl
from PySide2.QtGui import QDesktopServices,QColor
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance
from functools import partial
import json
import sys
import time

class AnimationTools(QWidget):
    def __init__(self,AT_PATH):
        super(AnimationTools, self).__init__()
        self.AT_PATH = AT_PATH
        # 获取屏幕分辨率
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_height = screen_geometry.height()

        # 基准分辨率
        base_height = 1080

        # 计算缩放比例
        self.hr = screen_height / base_height
        
        self.setGeometry(1360*self.hr,230*self.hr,250*self.hr, 240*self.hr)
        self.setWindowTitle('小叶的动画工具')
        self.setParent(wrapInstance(int(MQtUtil.mainWindow()),QWidget))
        self.setWindowFlags(Qt.Window)
        self.last_trigger_time = 0  # 上一次触发的时间
        self.last_frame = 0
        self.initUI()

    def initUI(self):
        # 创建 QTabWidget
        self.tab_widget = QTabWidget(parent=self)
        self.tab_widget.setGeometry(0, 0, 250*self.hr, 240*self.hr)
        # 创建 Tab 页面
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        # 添加 Tab 页面到 QTabWidget
        self.tab_widget.addTab(tab1, "选择/关键帧工具")
        self.tab_widget.addTab(tab2, "变换工具")
        self.tab_widget.addTab(tab3, "关于")
        #按钮
        self.b00 = QPushButton('所有控制器', parent=tab1)
        self.b00.setGeometry(QRect(self.hr*10, self.hr*10, self.hr*70, self.hr*30))
        self.b00.clicked.connect(self.all)

        self.b0001 = QPushButton('所有子控制器', parent=tab1)
        self.b0001.setGeometry(QRect(self.hr*10, self.hr*50, self.hr*70, self.hr*30))
        self.b0001.clicked.connect(self.allChildCtrl)
        
        self.b0002 = QPushButton('↑', parent=tab1)
        self.b0002.setGeometry(QRect(self.hr*85, self.hr*10, self.hr*25, self.hr*30))
        self.b0002.clicked.connect(self.selectParentCtrl)
        
        self.b0003 = QPushButton('↓', parent=tab1)
        self.b0003.setGeometry(QRect(self.hr*85, self.hr*50, self.hr*25, self.hr*30))
        self.b0003.clicked.connect(self.selectChildCtrl)
        
        self.b01 = QPushButton('轨迹线', parent=tab1)
        self.b01.setGeometry(QRect(self.hr*130, self.hr*10, self.hr*100, self.hr*30))
        self.b01.clicked.connect(self.create_motionTrail)
        
        self.b02 = QPushButton('欧拉过滤器', parent=tab1)
        self.b02.setGeometry(QRect(self.hr*130, self.hr*50, self.hr*100, self.hr*30))
        self.b02.clicked.connect(cmds.filterCurve)
        
        self.b03 = QPushButton('删小数帧', parent=tab1)
        self.b03.setGeometry(QRect(self.hr*130, self.hr*90, self.hr*100, self.hr*30))
        self.b03.clicked.connect(self.deleteDecimalFrames)
        
        self.b04 = QPushButton('记录变换', parent=tab2)
        self.b04.setGeometry(QRect(self.hr*130, self.hr*10, self.hr*60, self.hr*30))
        self.b04.clicked.connect(self.recordTransform)
        
        self.b05 = QPushButton('对齐变换', parent=tab2)
        self.b05.setGeometry(QRect(self.hr*130, self.hr*50, self.hr*60, self.hr*30))
        self.b05.clicked.connect(self.AlignTransform)
        
        self.b06 = QPushButton('旋转跟随', parent=tab2)
        self.b06.setGeometry(QRect(self.hr*10, self.hr*10, self.hr*100, self.hr*30))
        self.b06.clicked.connect(self.RF)
        
        self.b0700 = QPushButton('IKFK实时对齐', parent=tab2)
        self.b0700.setGeometry(QRect(self.hr*10, self.hr*50, self.hr*100, self.hr*30))
        self.b0700.clicked.connect(self.update_b0700)

        
        self.b0701 = QPushButton('切换', parent=tab2)
        self.b0701.setGeometry(QRect(self.hr*10, self.hr*90, self.hr*45, self.hr*30))
        self.b0701.clicked.connect(partial(self.IKFK,True))
        
        self.b08 = QPushButton('对齐', parent=tab2)
        self.b08.setGeometry(QRect(self.hr*65, self.hr*90, self.hr*45, self.hr*30))
        self.b08.clicked.connect(partial(self.IKFK,False))
        
        self.b0900 = QPushButton('重心控制', parent=tab2)
        self.b0900.setGeometry(QRect(self.hr*130, self.hr*90, self.hr*45, self.hr*30))
        self.b0900.clicked.connect(partial(self.rootCogCtrl,1))
        
        self.b0901 = QPushButton('根控制', parent=tab2)
        self.b0901.setGeometry(QRect(self.hr*185, self.hr*90, self.hr*45, self.hr*30))
        self.b0901.clicked.connect(partial(self.rootCogCtrl,0))
        
        self.b1000 = QPushButton('跨文件复制变换', parent=tab2)
        self.b1000.setGeometry(QRect(self.hr*130, self.hr*130, self.hr*100, self.hr*30))
        self.b1000.clicked.connect(self.copy_transforms)
        
        self.b1001 = QPushButton('跨文件粘贴变换', parent=tab2)
        self.b1001.setGeometry(QRect(self.hr*130, self.hr*170, self.hr*100, self.hr*30))
        self.b1001.clicked.connect(self.paste_transforms)

        self.b11 = QPushButton('对齐到边界框', parent=tab1)
        self.b11.setGeometry(QRect(self.hr * 130, self.hr * 130, self.hr * 100, self.hr * 30))
        self.b11.clicked.connect(self.match_bounding_boxes)

        self.b12 = QPushButton('对齐到顶点', parent=tab1)
        self.b12.setGeometry(QRect(self.hr * 130, self.hr * 170, self.hr * 100, self.hr * 30))
        self.b12.clicked.connect(self.match_vertex_average)

        self.b21 = QPushButton('作者主页', parent=tab3)
        self.b21.setGeometry(QRect(self.hr * 10, self.hr * 10, self.hr * 100, self.hr * 30))
        self.b21.clicked.connect(lambda:QDesktopServices.openUrl(QUrl('https://space.bilibili.com/341240492')))

        self.b22 = QPushButton('打开脚本目录', parent=tab3)
        self.b22.setGeometry(QRect(self.hr * 10, self.hr * 50, self.hr * 100, self.hr * 30))
        self.b22.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f'file:///{self.AT_PATH}')))
        #标签
        #self.ref00 = QLabel('——选择工具———', parent=self)
        #self.ref00.setGeometry(QRect(self.hr*5, self.hr*0, self.hr*120, self.hr*30))
        #self.ref01 = QLabel('——关键帧工具——', parent=self)
        #self.ref01.setGeometry(QRect(self.hr*5, self.hr*100, self.hr*120, self.hr*30))
        
        self.ql01 = QLabel('空间切换：', parent=tab2)
        self.ql01.setGeometry(QRect(self.hr*10, self.hr*150, self.hr*70, self.hr*20))

        self.ql02 = QLabel('0', parent=tab2)
        self.ql02.setGeometry(QRect(self.hr*70, self.hr*150, self.hr*70, self.hr*20))
        
        self.ref02 = QLabel('工作时间:<br>'
                            '9:30-12:00<br>'
                            '13.30-18:30<br>'
                            '20:00-23:00', parent=tab1)
        self.ref02.setGeometry(QRect(self.hr*10, self.hr*90, self.hr*120, self.hr*50))
        
        self.ref03 = QLabel('V1.0.0.20240830', parent=tab3)
        self.ref03.setGeometry(QRect(self.hr*10, self.hr*120, self.hr*300, self.hr*30))
        
        self.ref0400 = QLabel('本工具有些功能只能', parent=tab3)
        self.ref0400.setGeometry(QRect(self.hr*10, self.hr*80, self.hr*300, self.hr*30))
        
        self.ref0401 = QLabel('用于配套的绑定', parent=tab3)
        self.ref0401.setGeometry(QRect(self.hr*10, self.hr*100, self.hr*300, self.hr*30))
        
        self.ref0500 = QLabel(' | ', parent=tab2)
        self.ref0500.setGeometry(QRect(self.hr*10, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0501 = QLabel(' | ', parent=tab2)
        self.ref0501.setGeometry(QRect(self.hr*19, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0502 = QLabel(' | ', parent=tab2)
        self.ref0502.setGeometry(QRect(self.hr*28, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0503 = QLabel(' | ', parent=tab2)
        self.ref0503.setGeometry(QRect(self.hr*37, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0504 = QLabel(' | ', parent=tab2)
        self.ref0504.setGeometry(QRect(self.hr*46, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0505 = QLabel(' | ', parent=tab2)
        self.ref0505.setGeometry(QRect(self.hr*56, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0506 = QLabel(' | ', parent=tab2)
        self.ref0506.setGeometry(QRect(self.hr*65, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0507 = QLabel(' | ', parent=tab2)
        self.ref0507.setGeometry(QRect(self.hr*74, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0508 = QLabel(' | ', parent=tab2)
        self.ref0508.setGeometry(QRect(self.hr*83, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0509 = QLabel(' | ', parent=tab2)
        self.ref0509.setGeometry(QRect(self.hr*92, self.hr*130, self.hr*10, self.hr*10))
        
        self.ref0510 = QLabel(' | ', parent=tab2)
        self.ref0510.setGeometry(QRect(self.hr*101, self.hr*130, self.hr*10, self.hr*10))
        

        #滑条
        self.qs01 = QSlider(Qt.Horizontal, parent=tab2)
        self.qs01.setGeometry(QRect(self.hr*10, self.hr*120, self.hr*100, self.hr*30))
        self.qs01.setMinimum(0)
        self.qs01.setMaximum(10)
        self.qs01.valueChanged.connect(self.ql02.setNum)
        self.qs01.valueChanged.connect(self.space)
        #选框
        self.cb01 = QCheckBox('每帧',parent=tab2)
        self.cb01.setGeometry(QRect(self.hr*200, self.hr*10, self.hr*50, self.hr*30))
        self.cb01.stateChanged.connect(self.update_cb01)
        
        self.cb02 = QCheckBox('每帧',parent=tab2)
        self.cb02.setGeometry(QRect(self.hr*200, self.hr*50, self.hr*50, self.hr*30))
        self.cb02.stateChanged.connect(self.update_cb02)
    def update_cb01(self):
        self.b04.clicked.disconnect()  # 断开当前的所有连接
        if self.cb01.isChecked():
            self.b04.clicked.connect(self.recordTransform_per)  # 连接到记录变换每帧
        else:
            self.b04.clicked.connect(self.recordTransform)  # 重新连接到默认函数
    def update_cb02(self):
        self.b05.clicked.disconnect()  # 断开当前的所有连接
        if self.cb02.isChecked():
            self.b05.clicked.connect(self.AlignTransform_per)  # 连接到记录变换每帧
        else:
            self.b05.clicked.connect(self.AlignTransform)  # 重新连接到默认函数
    def update_b0700(self):
        print('update_b0700')
        darkgray = 'rgb(93, 93, 93)'
        red = 'rgb(255,0,0)'
        if self.b0700.styleSheet() == f"background-color: {red};":
            self.b0700.setStyleSheet(f"background-color: {darkgray};")  # 恢复默认颜色
            self.colse_IKFK()  # 关闭功能
        else:

            self.b0700.setStyleSheet(f"background-color: {red};")  # 改为红色
            self.open_IKFK()  # 开启功能
    '''
    所有控制器————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def all(self):
        name=cmds.ls(selection=True,showNamespace=True)
    
        if len(name)==0:
            name_space='::'
        else:
            name_space=name[1]+':'
        
            
        parent_object=[name_space+'ctrl_c_root']
        
        
        cmds.select(cmds.listRelatives(parent_object,allDescendents=True))
        selected_objects = cmds.ls(selection=True,transforms=True)
        cmds.select(selected_objects)
        
        # 获取所有名称中包含"ctrl"的对象
        ctrl_objects = cmds.ls(name_space+"ctrl*",selection=True,long=True)
        
        all_objrcts=ctrl_objects+parent_object
        
        # 取消当前的选择
        cmds.select(clear=True)
        # 选择新的对象列表
        cmds.select(all_objrcts)
    '''
    所有子控制器————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def allChildCtrl(self):
        parent_object=cmds.ls(selection=True)
        name=cmds.ls(selection=True,showNamespace=True)
        name_space=name[1]
        
        cmds.select(cmds.listRelatives(cmds.ls(selection=True),allDescendents=True)) or []
        selected_objects = cmds.ls(selection=True,transforms=True)
        cmds.select(selected_objects)
        
        # 获取所有名称中包含"ctrl"的对象
        ctrl_objects = cmds.ls(name_space+":ctrl*",selection=True,long=True)
        
        all_objrcts=ctrl_objects+parent_object
        
        # 取消当前的选择
        cmds.select(clear=True)
        # 选择新的对象列表
        cmds.select(all_objrcts)
    '''
    选择子控制器————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def selectChildCtrl(self):
        # 获取名称空间
        name = cmds.ls(selection=True)
        split_name = name[0].split(':')
        
        if len(split_name) > 1:
            ns = split_name[0] + ':'
        else:
            ns = ''
        print(ns)
        
        # 添加名称空间
        ctrl_c_root = ns + 'ctrl_c_root'
        ctrl_c_cog = ns + 'ctrl_c_cog'
        ctrl_c_spineIk = ns + 'ctrl_c_spineIk'
        ctrl_c_spineA = ns + 'ctrl_c_spineA'
        ctrl_c_spineB = ns + 'ctrl_c_spineB'
        ctrl_c_spineC = ns + 'ctrl_c_spineC'
        ctrl_c_neck = ns + 'ctrl_c_neck'
        ctrl_c_head = ns + 'ctrl_c_head'
        
        ctrl_l_shoulder = ns + 'ctrl_l_shoulder'
        ctrl_l_upperarmFk = ns + 'ctrl_l_upperarmFk'
        ctrl_l_forearmFk = ns + 'ctrl_l_forearmFk'
        ctrl_l_handFk = ns + 'ctrl_l_handFk'
        ctrl_l_armPv = ns + 'ctrl_l_armPv'
        ctrl_l_handIk = ns + 'ctrl_l_handIk'
        ctrl_l_finThumbA = ns + 'ctrl_l_finThumbA'
        ctrl_l_finThumbB = ns + 'ctrl_l_finThumbB'
        ctrl_l_finThumbC = ns + 'ctrl_l_finThumbC'
        ctrl_l_finIndexA = ns + 'ctrl_l_finIndexA'
        ctrl_l_finIndexB = ns + 'ctrl_l_finIndexB'
        ctrl_l_finIndexC = ns + 'ctrl_l_finIndexC'
        ctrl_l_finMidA = ns + 'ctrl_l_finMidA'
        ctrl_l_finMidB = ns + 'ctrl_l_finMidB'
        ctrl_l_finMidC = ns + 'ctrl_l_finMidC'
        ctrl_l_finRingA = ns + 'ctrl_l_finRingA'
        ctrl_l_finRingB = ns + 'ctrl_l_finRingB'
        ctrl_l_finRingC = ns + 'ctrl_l_finRingC'
        ctrl_l_finPinkyA = ns + 'ctrl_l_finPinkyA'
        ctrl_l_finPinkyB = ns + 'ctrl_l_finPinkyB'
        ctrl_l_finPinkyC = ns + 'ctrl_l_finPinkyC'
        
        ctrl_r_shoulder = ns + 'ctrl_r_shoulder'
        ctrl_r_upperarmFk = ns + 'ctrl_r_upperarmFk'
        ctrl_r_forearmFk = ns + 'ctrl_r_forearmFk'
        ctrl_r_handFk = ns + 'ctrl_r_handFk'
        ctrl_r_armPv = ns + 'ctrl_r_armPv'
        ctrl_r_handIk = ns + 'ctrl_r_handIk'
        ctrl_r_finThumbA = ns + 'ctrl_r_finThumbA'
        ctrl_r_finThumbB = ns + 'ctrl_r_finThumbB'
        ctrl_r_finThumbC = ns + 'ctrl_r_finThumbC'
        ctrl_r_finIndexA = ns + 'ctrl_r_finIndexA'
        ctrl_r_finIndexB = ns + 'ctrl_r_finIndexB'
        ctrl_r_finIndexC = ns + 'ctrl_r_finIndexC'
        ctrl_r_finMidA = ns + 'ctrl_r_finMidA'
        ctrl_r_finMidB = ns + 'ctrl_r_finMidB'
        ctrl_r_finMidC = ns + 'ctrl_r_finMidC'
        ctrl_r_finRingA = ns + 'ctrl_r_finRingA'
        ctrl_r_finRingB = ns + 'ctrl_r_finRingB'
        ctrl_r_finRingC = ns + 'ctrl_r_finRingC'
        ctrl_r_finPinkyA = ns + 'ctrl_r_finPinkyA'
        ctrl_r_finPinkyB = ns + 'ctrl_r_finPinkyB'
        ctrl_r_finPinkyC = ns + 'ctrl_r_finPinkyC'
        
        ctrl_l_thighFk = ns + 'ctrl_l_thighFk'
        ctrl_l_shinFk = ns + 'ctrl_l_shinFk'
        ctrl_l_footFk = ns + 'ctrl_l_footFk'
        ctrl_l_legPv = ns + 'ctrl_l_legPv'
        ctrl_l_footIk = ns + 'ctrl_l_footIk'
        ctrl_l_toe = ns + 'ctrl_l_toe'
        
        ctrl_r_thighFk = ns + 'ctrl_r_thighFk'
        ctrl_r_shinFk = ns + 'ctrl_r_shinFk'
        ctrl_r_footFk = ns + 'ctrl_r_footFk'
        ctrl_r_legPv = ns + 'ctrl_r_legPv'
        ctrl_r_footIk = ns + 'ctrl_r_footIk'
        ctrl_r_toe = ns + 'ctrl_r_toe'
        
        # 定义预设映射
        preset_map = {
            ctrl_c_root: [ctrl_c_cog],
            ctrl_c_cog: [ctrl_c_spineA,ctrl_c_spineIk],
            ctrl_c_spineA: [ctrl_c_spineB],
            ctrl_c_spineB: [ctrl_c_spineC],
            ctrl_c_spineC: [ctrl_c_neck],
            ctrl_c_spineIk: [ctrl_c_neck],
            ctrl_c_neck: [ctrl_c_head],
            
            ctrl_l_shoulder: [ctrl_l_upperarmFk,ctrl_l_armPv],
            ctrl_l_upperarmFk: [ctrl_l_forearmFk],
            ctrl_l_forearmFk: [ctrl_l_handFk],
            ctrl_l_armPv: [ctrl_l_handIk],
            ctrl_l_handFk: [ctrl_l_finThumbA, ctrl_l_finIndexA, ctrl_l_finMidA, ctrl_l_finRingA, ctrl_l_finPinkyA],
            ctrl_l_handIk: [ctrl_l_finThumbA, ctrl_l_finIndexA, ctrl_l_finMidA, ctrl_l_finRingA, ctrl_l_finPinkyA],
            ctrl_l_finThumbA: [ctrl_l_finThumbB],
            ctrl_l_finThumbB: [ctrl_l_finThumbC],
            ctrl_l_finIndexA: [ctrl_l_finIndexB],
            ctrl_l_finIndexB: [ctrl_l_finIndexC],
            ctrl_l_finMidA: [ctrl_l_finMidB],
            ctrl_l_finMidB: [ctrl_l_finMidC],
            ctrl_l_finRingA: [ctrl_l_finRingB],
            ctrl_l_finRingB: [ctrl_l_finRingC],
            ctrl_l_finPinkyA:[ctrl_l_finPinkyB],
            ctrl_l_finPinkyB:[ctrl_l_finPinkyC],
            
            ctrl_r_shoulder: [ctrl_r_upperarmFk,ctrl_r_armPv],
            ctrl_r_upperarmFk: [ctrl_r_forearmFk],
            ctrl_r_forearmFk: [ctrl_r_handFk],
            ctrl_r_armPv: [ctrl_r_handIk],
            ctrl_r_handFk: [ctrl_r_finThumbA, ctrl_r_finIndexA, ctrl_r_finMidA, ctrl_r_finRingA, ctrl_r_finPinkyA],
            ctrl_r_handIk: [ctrl_r_finThumbA, ctrl_r_finIndexA, ctrl_r_finMidA, ctrl_r_finRingA, ctrl_r_finPinkyA],
            ctrl_r_finThumbA: [ctrl_r_finThumbB],
            ctrl_r_finThumbB: [ctrl_r_finThumbC],
            ctrl_r_finIndexA: [ctrl_r_finIndexB],
            ctrl_r_finIndexB: [ctrl_r_finIndexC],
            ctrl_r_finMidA: [ctrl_r_finMidB],
            ctrl_r_finMidB: [ctrl_r_finMidC],
            ctrl_r_finRingA: [ctrl_r_finRingB],
            ctrl_r_finRingB: [ctrl_r_finRingC],
            ctrl_r_finPinkyA:[ctrl_r_finPinkyB],
            ctrl_r_finPinkyB:[ctrl_r_finPinkyC],
            
            ctrl_l_thighFk:[ctrl_l_shinFk],
            ctrl_l_shinFk:[ctrl_l_footFk],
            ctrl_l_footFk:[ctrl_l_toe],
            ctrl_l_legPv:[ctrl_l_footIk],
            ctrl_l_footIk:[ctrl_l_toe],
            
            ctrl_r_thighFk:[ctrl_r_shinFk],
            ctrl_r_shinFk:[ctrl_r_footFk],
            ctrl_r_footFk:[ctrl_r_toe],
            ctrl_r_legPv:[ctrl_r_footIk],
            ctrl_r_footIk:[ctrl_r_toe],
        }
        
        def is_visible(obj):
            # 检查对象是否可见
            if not cmds.getAttr(f"{obj}.visibility"):
                return False
            
            # 检查对象的所有父级是否可见
            parents = cmds.listRelatives(obj, allParents=True, fullPath=True) or []
            parts = parents[0].split('|')
            ps = parts[1:]
            for p in ps:
                if cmds.getAttr(p+'.visibility')==0:
                    return False
            return True
        
        def apply_preset():
            selection = cmds.ls(selection=True)
            final_selection = []
            
            for obj in selection:
                if obj in preset_map:
                    # 获取对应的预设物体
                    preset_objects = preset_map[obj]
                    for preset_obj in preset_objects:
                        if cmds.objExists(preset_obj):
                            # 只有在可见的情况下才添加到最终选择列表中
                            if is_visible(preset_obj):
                                final_selection.append(preset_obj)
                else:
                    # 如果没有找到映射，保留原始选择
                    if is_visible(obj):
                        final_selection.append(obj)
            
            if final_selection:
                # 选择所有找到的预设物体
                cmds.select(final_selection)
        apply_preset()
    '''
    选择父控制器————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def selectParentCtrl(self):
        # 获取名称空间
        name = cmds.ls(selection=True)
        split_name = name[0].split(':')
        
        if len(split_name) > 1:
            ns = split_name[0] + ':'
        else:
            ns = ''
        print(ns)
        
        # 添加名称空间
        ctrl_c_root = ns + 'ctrl_c_root'
        ctrl_c_cog = ns + 'ctrl_c_cog'
        ctrl_c_spineIk = ns + 'ctrl_c_spineIk'
        ctrl_c_spineA = ns + 'ctrl_c_spineA'
        ctrl_c_spineB = ns + 'ctrl_c_spineB'
        ctrl_c_spineC = ns + 'ctrl_c_spineC'
        ctrl_c_neck = ns + 'ctrl_c_neck'
        ctrl_c_head = ns + 'ctrl_c_head'
        
        ctrl_l_shoulder = ns + 'ctrl_l_shoulder'
        ctrl_l_upperarmFk = ns + 'ctrl_l_upperarmFk'
        ctrl_l_forearmFk = ns + 'ctrl_l_forearmFk'
        ctrl_l_handFk = ns + 'ctrl_l_handFk'
        ctrl_l_armPv = ns + 'ctrl_l_armPv'
        ctrl_l_handIk = ns + 'ctrl_l_handIk'
        ctrl_l_finThumbA = ns + 'ctrl_l_finThumbA'
        ctrl_l_finThumbB = ns + 'ctrl_l_finThumbB'
        ctrl_l_finThumbC = ns + 'ctrl_l_finThumbC'
        ctrl_l_finIndexA = ns + 'ctrl_l_finIndexA'
        ctrl_l_finIndexB = ns + 'ctrl_l_finIndexB'
        ctrl_l_finIndexC = ns + 'ctrl_l_finIndexC'
        ctrl_l_finMidA = ns + 'ctrl_l_finMidA'
        ctrl_l_finMidB = ns + 'ctrl_l_finMidB'
        ctrl_l_finMidC = ns + 'ctrl_l_finMidC'
        ctrl_l_finRingA = ns + 'ctrl_l_finRingA'
        ctrl_l_finRingB = ns + 'ctrl_l_finRingB'
        ctrl_l_finRingC = ns + 'ctrl_l_finRingC'
        ctrl_l_finPinkyA = ns + 'ctrl_l_finPinkyA'
        ctrl_l_finPinkyB = ns + 'ctrl_l_finPinkyB'
        ctrl_l_finPinkyC = ns + 'ctrl_l_finPinkyC'
        
        ctrl_r_shoulder = ns + 'ctrl_r_shoulder'
        ctrl_r_upperarmFk = ns + 'ctrl_r_upperarmFk'
        ctrl_r_forearmFk = ns + 'ctrl_r_forearmFk'
        ctrl_r_handFk = ns + 'ctrl_r_handFk'
        ctrl_r_armPv = ns + 'ctrl_r_armPv'
        ctrl_r_handIk = ns + 'ctrl_r_handIk'
        ctrl_r_finThumbA = ns + 'ctrl_r_finThumbA'
        ctrl_r_finThumbB = ns + 'ctrl_r_finThumbB'
        ctrl_r_finThumbC = ns + 'ctrl_r_finThumbC'
        ctrl_r_finIndexA = ns + 'ctrl_r_finIndexA'
        ctrl_r_finIndexB = ns + 'ctrl_r_finIndexB'
        ctrl_r_finIndexC = ns + 'ctrl_r_finIndexC'
        ctrl_r_finMidA = ns + 'ctrl_r_finMidA'
        ctrl_r_finMidB = ns + 'ctrl_r_finMidB'
        ctrl_r_finMidC = ns + 'ctrl_r_finMidC'
        ctrl_r_finRingA = ns + 'ctrl_r_finRingA'
        ctrl_r_finRingB = ns + 'ctrl_r_finRingB'
        ctrl_r_finRingC = ns + 'ctrl_r_finRingC'
        ctrl_r_finPinkyA = ns + 'ctrl_r_finPinkyA'
        ctrl_r_finPinkyB = ns + 'ctrl_r_finPinkyB'
        ctrl_r_finPinkyC = ns + 'ctrl_r_finPinkyC'
        
        ctrl_l_thighFk = ns + 'ctrl_l_thighFk'
        ctrl_l_shinFk = ns + 'ctrl_l_shinFk'
        ctrl_l_footFk = ns + 'ctrl_l_footFk'
        ctrl_l_legPv = ns + 'ctrl_l_legPv'
        ctrl_l_footIk = ns + 'ctrl_l_footIk'
        ctrl_l_toe = ns + 'ctrl_l_toe'
        
        ctrl_r_thighFk = ns + 'ctrl_r_thighFk'
        ctrl_r_shinFk = ns + 'ctrl_r_shinFk'
        ctrl_r_footFk = ns + 'ctrl_r_footFk'
        ctrl_r_legPv = ns + 'ctrl_r_legPv'
        ctrl_r_footIk = ns + 'ctrl_r_footIk'
        ctrl_r_toe = ns + 'ctrl_r_toe'
        
        # 定义预设映射
        preset_map = {
            ctrl_c_cog: [ctrl_c_root],
            ctrl_c_spineIk: [ctrl_c_cog],
            ctrl_c_spineA: [ctrl_c_cog],
            ctrl_c_spineB: [ctrl_c_spineA],
            ctrl_c_spineC: [ctrl_c_spineB],
            ctrl_c_neck: [ctrl_c_spineC,ctrl_c_spineIk],
            ctrl_c_head:[ctrl_c_neck],
            
            
            ctrl_l_shoulder:[ctrl_c_spineC,ctrl_c_spineIk],
            ctrl_l_upperarmFk: [ctrl_l_shoulder],
            ctrl_l_forearmFk: [ctrl_l_upperarmFk],
            ctrl_l_handFk: [ctrl_l_forearmFk],
            ctrl_l_handIk:[ctrl_l_armPv],
            ctrl_l_armPv:[ctrl_l_shoulder],
            ctrl_l_finThumbA:[ctrl_l_handFk,ctrl_l_handIk],
            ctrl_l_finIndexA:[ctrl_l_handFk,ctrl_l_handIk],
            ctrl_l_finMidA:[ctrl_l_handFk,ctrl_l_handIk],
            ctrl_l_finRingA:[ctrl_l_handFk,ctrl_l_handIk],
            ctrl_l_finPinkyA:[ctrl_l_handFk,ctrl_l_handIk],
            ctrl_l_finThumbB: [ctrl_l_finThumbA],
            ctrl_l_finThumbC: [ctrl_l_finThumbB],
            ctrl_l_finIndexB: [ctrl_l_finIndexA],
            ctrl_l_finIndexC: [ctrl_l_finIndexB],
            ctrl_l_finMidB: [ctrl_l_finMidA],
            ctrl_l_finMidC: [ctrl_l_finMidB],
            ctrl_l_finRingB: [ctrl_l_finRingA],
            ctrl_l_finRingC: [ctrl_l_finRingB],
            ctrl_l_finPinkyB:[ctrl_l_finPinkyA],
            ctrl_l_finPinkyC:[ctrl_l_finPinkyB],
            
            ctrl_r_shoulder:[ctrl_c_spineC,ctrl_c_spineIk],
            ctrl_r_upperarmFk: [ctrl_r_shoulder],
            ctrl_r_forearmFk: [ctrl_r_upperarmFk],
            ctrl_r_handFk: [ctrl_r_forearmFk],
            ctrl_r_handIk:[ctrl_r_armPv],
            ctrl_r_armPv:[ctrl_r_shoulder],
            ctrl_r_finThumbA:[ctrl_r_handFk,ctrl_r_handIk],
            ctrl_r_finIndexA:[ctrl_r_handFk,ctrl_r_handIk],
            ctrl_r_finMidA:[ctrl_r_handFk,ctrl_r_handIk],
            ctrl_r_finRingA:[ctrl_r_handFk,ctrl_r_handIk],
            ctrl_r_finPinkyA:[ctrl_r_handFk,ctrl_r_handIk],
            ctrl_r_finThumbB: [ctrl_r_finThumbA],
            ctrl_r_finThumbC: [ctrl_r_finThumbB],
            ctrl_r_finIndexB: [ctrl_r_finIndexA],
            ctrl_r_finIndexC: [ctrl_r_finIndexB],
            ctrl_r_finMidB: [ctrl_r_finMidA],
            ctrl_r_finMidC: [ctrl_r_finMidB],
            ctrl_r_finRingB: [ctrl_r_finRingA],
            ctrl_r_finRingC: [ctrl_r_finRingB],
            ctrl_r_finPinkyB:[ctrl_r_finPinkyA],
            ctrl_r_finPinkyC:[ctrl_r_finPinkyB],
            
            ctrl_l_thighFk:[ctrl_c_cog],
            ctrl_l_legPv:[ctrl_c_cog],
            ctrl_l_shinFk:[ctrl_l_thighFk],
            ctrl_l_footFk:[ctrl_l_shinFk],
            ctrl_l_footIk:[ctrl_l_legPv],
            ctrl_l_toe:[ctrl_l_footFk,ctrl_l_footIk],
            
            ctrl_r_thighFk:[ctrl_c_cog],
            ctrl_r_legPv:[ctrl_c_cog],
            ctrl_r_shinFk:[ctrl_r_thighFk],
            ctrl_r_footFk:[ctrl_r_shinFk],
            ctrl_r_footIk:[ctrl_r_legPv],
            ctrl_r_toe:[ctrl_r_footFk,ctrl_r_footIk],
        }
        
        def is_visible(obj):
            # 检查对象是否可见
            if not cmds.getAttr(f"{obj}.visibility"):
                return False
            
            # 检查对象的所有父级是否可见
            parents = cmds.listRelatives(obj, allParents=True, fullPath=True) or []
            parts = parents[0].split('|')
            ps = parts[1:]
            for p in ps:
                if cmds.getAttr(p+'.visibility')==0:
                    return False
            return True
        
        def apply_preset():
            selection = cmds.ls(selection=True)
            final_selection = []
            
            for obj in selection:
                if obj in preset_map:
                    # 获取对应的预设物体
                    preset_objects = preset_map[obj]
                    for preset_obj in preset_objects:
                        if cmds.objExists(preset_obj):
                            # 只有在可见的情况下才添加到最终选择列表中
                            if is_visible(preset_obj):
                                final_selection.append(preset_obj)
                else:
                    # 如果没有找到映射，保留原始选择
                    if is_visible(obj):
                        final_selection.append(obj)
            
            if final_selection:
                # 选择所有找到的预设物体
                cmds.select(final_selection)
                
        apply_preset()
    
    
    '''
    旋转跟随————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    
    def RF(self):
        # 旋转跟随功能
        selecte_objects = cmds.ls(selection=True)
        for obj in selecte_objects:
            m = cmds.xform(obj, query=True, matrix=True, worldSpace=True)
            i = cmds.getAttr(obj + '.rotateFollow')
            if i < 0.5:
                cmds.setAttr(obj + '.rotateFollow', 1)
            else:
                cmds.setAttr(obj + '.rotateFollow', 0)
            cmds.xform(obj, matrix=m, worldSpace=True)
    '''
    旋转跟随赋值————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def RF_value(self, obj, n):
        # 保存物体当前的变换矩阵
        matrix = cmds.xform(obj, query=True, matrix=True, worldSpace=True)
        
        # 更改rotateFollow属性
        cmds.setAttr(obj + '.rotateFollow', n)
        
        # 恢复物体的变换矩阵
        cmds.xform(obj, matrix=matrix, worldSpace=True)
    '''
    空间切换————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def space(self, enum):
        selecte_objects = cmds.ls(selection=True)
        for obj in selecte_objects:
            # 保存物体当前的变换矩阵
            matrix = cmds.xform(obj, query=True, matrix=True, worldSpace=True)
            
            # 更改space属性
            cmds.setAttr(obj + '.space', enum)
            
            # 恢复物体的变换矩阵
            cmds.xform(obj, matrix=matrix, worldSpace=True)
    '''
    IKFK切换————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def IKFK(self,switch=True):
        cmds.undoInfo(openChunk=True)
        #IKFK切换
        selection=cmds.ls(selection=True)
        if not selection:
            cmds.warning("没有选择对象，请选择对象后再运行脚本。")
        else:
            name=cmds.ls(selection=True,showNamespace=True)
            name_space=name[-1]+':'
            armBlend_l=name_space+'ctrl_l_armBlendIkFk'
            upperarmFk_l=name_space+'ctrl_l_upperarmFk'
            forearmFk_l=name_space+'ctrl_l_forearmFk'
            armFkPv_l=name_space+'crv_l_armFkPv'
            handFk_l=name_space+'ctrl_l_handFk'
            upperarmIk_l=name_space+'jnt_l_upperarmIk'
            forearmIk_l=name_space+'jnt_l_forearmIk'
            armPv_l=name_space+'ctrl_l_armPv'
            handIk_l=name_space+'ctrl_l_handIk'
        
            armBlend_r=name_space+'ctrl_r_armBlendIkFk'
            upperarmFk_r=name_space+'ctrl_r_upperarmFk'
            forearmFk_r=name_space+'ctrl_r_forearmFk'
            armFkPv_r=name_space+'crv_r_armFkPv'
            handFk_r=name_space+'ctrl_r_handFk'
            upperarmIk_r=name_space+'jnt_r_upperarmIk'
            forearmIk_r=name_space+'jnt_r_forearmIk'
            armPv_r=name_space+'ctrl_r_armPv'
            handIk_r=name_space+'ctrl_r_handIk'
        
            legBlend_l=name_space+'ctrl_l_legBlendIkFk'
            thighFk_l=name_space+'ctrl_l_thighFk'
            shinFk_l=name_space+'ctrl_l_shinFk'
            legFkPv_l=name_space+'crv_l_legFkPv'
            footFk_l=name_space+'ctrl_l_footFk'
            if cmds.objExists(name_space+'crv_l_footIk'):
                crv_l_footIk=name_space+'crv_l_footIk'
            else:
                crv_l_footIk=name_space+'jnt_l_footIk'
            if cmds.objExists(name_space+'crv_l_footFk'):
                crv_l_footFk=name_space+'crv_l_footFk'
            else:
                crv_l_footFk=name_space+'ctrl_l_footFk'
            thighIk_l=name_space+'jnt_l_thighIk'
            shinIk_l=name_space+'jnt_l_shinIk'
            legPv_l=name_space+'ctrl_l_legPv'
            footIk_l=name_space+'ctrl_l_footIk'
        
            legBlend_r=name_space+'ctrl_r_legBlendIkFk'
            thighFk_r=name_space+'ctrl_r_thighFk'
            shinFk_r=name_space+'ctrl_r_shinFk'
            legFkPv_r=name_space+'crv_r_legFkPv'
            footFk_r=name_space+'ctrl_r_footFk'
            if cmds.objExists(name_space+'crv_r_footIk'):
                crv_r_footIk=name_space+'crv_r_footIk'
            else:
                crv_r_footIk=name_space+'jnt_r_footIk'
            if cmds.objExists(name_space+'crv_r_footFk'):
                crv_r_footFk=name_space+'crv_r_footFk'
            else:
                crv_r_footFk=name_space+'ctrl_r_footFk'
            thighIk_r=name_space+'jnt_r_thighIk'
            shinIk_r=name_space+'jnt_r_shinIk'
            legPv_r=name_space+'ctrl_r_legPv'
            footIk_r=name_space+'ctrl_r_footIk'
            
            cog=name_space+'ctrl_c_cog'
            spineA=name_space+'ctrl_c_spineA'
            spineB=name_space+'ctrl_c_spineB'
            spineC=name_space+'ctrl_c_spineC'
            spineIk_01=name_space+'spine_01'
            spineIk_02=name_space+'spine_02'
            spineIk_03=name_space+'spine_03'
            spineIk=name_space+'ctrl_c_spineIk'
            neck=name_space+'ctrl_c_neck'
            crv_c_spineFk=name_space+'crv_c_spineFk'
            
            IKFK_dict = {
                upperarmFk_l:[armPv_l],
                forearmFk_l:[armPv_l],
                handFk_l:[handIk_l],
                armPv_l:[upperarmFk_l],
                handIk_l:[handFk_l],
                
                upperarmFk_r:[armPv_r],
                forearmFk_r:[armPv_r],
                handFk_r:[handIk_r],
                armPv_r:[upperarmFk_r],
                handIk_r:[handFk_r],
                
                thighFk_l:[legPv_l],
                shinFk_l:[legPv_l],
                footFk_l:[footIk_l],
                legPv_l:[thighFk_l],
                footIk_l:[footFk_l],
                
                thighFk_r:[legPv_r],
                shinFk_r:[legPv_r],
                footFk_r:[footIk_r],
                legPv_r:[thighFk_r],
                footIk_r:[footFk_r],
                
                spineA:[spineIk],
                spineB:[spineIk],
                spineC:[spineIk],
                spineIk:[spineC]
            }
                
                
            arm_l=[armBlend_l,upperarmFk_l,forearmFk_l,handFk_l,armPv_l,handIk_l]
        
            arm_r=[armBlend_r,upperarmFk_r,forearmFk_r,handFk_r,armPv_r,handIk_r]
        
            leg_l=[legBlend_l,thighFk_l,shinFk_l,footFk_l,legPv_l,footIk_l]
        
            leg_r=[legBlend_r,thighFk_r,shinFk_r,footFk_r,legPv_r,footIk_r]
        
            spine=[cog,spineA,spineB,spineC,spineIk_01,spineIk_02,spineIk_03,spineIk,neck]
        
        
            final_selection = []
            for obj in selection:
                if obj in arm_l:#当选中左臂时
                    if cmds.getAttr(armBlend_l+'.translateY')>=-2.35:#当IK控制左臂时
                        if switch:
                            cmds.setAttr(armBlend_l+'.translateY',-4.7)
                
                        cmds.matchTransform(upperarmFk_l,upperarmIk_l)
                        cmds.matchTransform(forearmFk_l,forearmIk_l)
                        cmds.matchTransform(handFk_l,handIk_l)
                
                    elif cmds.getAttr(armBlend_l+'.translateY')<-2.35:#当FK控制左臂时
                        if switch:
                            cmds.setAttr(armBlend_l+'.translateY',0)
                
                        cmds.matchTransform(handIk_l,handFk_l)
                        cmds.matchTransform(armPv_l,armFkPv_l)
                    
                elif obj in arm_r:#当选中右臂时
                    if cmds.getAttr(armBlend_r+'.translateY')>=-2.35:#当IK控制右臂时
                        if switch:
                            cmds.setAttr(armBlend_r+'.translateY',-4.7)
                
                        cmds.matchTransform(upperarmFk_r,upperarmIk_r)
                        cmds.matchTransform(forearmFk_r,forearmIk_r)
                        cmds.matchTransform(handFk_r,handIk_r)
                
                    elif cmds.getAttr(armBlend_r+'.translateY')<-2.35:#当FK控制右臂时
                        if switch:
                            cmds.setAttr(armBlend_r+'.translateY',0)
                
                        cmds.matchTransform(handIk_r,handFk_r)
                        cmds.matchTransform(armPv_r,armFkPv_r)
                elif obj in leg_l:#当选中左腿时
                    if cmds.getAttr(legBlend_l+'.translateY')>=-3.5:#当IK控制左腿时
                        if switch:
                            cmds.setAttr(legBlend_l+'.translateY',-7)
                
                        cmds.matchTransform(thighFk_l,thighIk_l)
                        cmds.matchTransform(shinFk_l,shinIk_l)
                        cmds.matchTransform(footFk_l,crv_l_footIk)
                
                    elif cmds.getAttr(legBlend_l+'.translateY')<-3.5:#当FK控制左腿时
                        if switch:
                            cmds.setAttr(legBlend_l+'.translateY',0)
                
                        cmds.matchTransform(footIk_l,crv_l_footFk)
                        cmds.matchTransform(legPv_l,legFkPv_l)
                
                elif obj in leg_r:#当选中右腿时
                    if cmds.getAttr(legBlend_r+'.translateY')>=-3.5:#当IK控制右腿时
                        if switch:
                            cmds.setAttr(legBlend_r+'.translateY',-7)
                
                        cmds.matchTransform(thighFk_r,thighIk_r)
                        cmds.matchTransform(shinFk_r,shinIk_r)
                        cmds.matchTransform(footFk_r,crv_r_footIk)
                
                    elif cmds.getAttr(legBlend_r+'.translateY')<-3.5:#当FK控制右腿时
                        if switch:
                            cmds.setAttr(legBlend_r+'.translateY',0)
                
                        cmds.matchTransform(footIk_r,crv_r_footFk)
                        cmds.matchTransform(legPv_r,legFkPv_r)
                    
                elif obj in spine:#当选中躯干时
                    if cmds.getAttr(cog+'.IKFK')<=0.5:#当IK控制躯干时
        
                        cmds.matchTransform(spineA,spineIk_01)
                        cmds.matchTransform(spineB,spineIk_02)
                        if cmds.objExists(spineC):
                            cmds.matchTransform(spineC,spineIk_03)
                        if switch:
                            cmds.setAttr(cog+'.IKFK',1)
                        
                    elif cmds.getAttr(cog+'.IKFK')>0.5:#当FK控制躯干时
                        
                        cmds.matchTransform(spineIk,neck,position=True)
                        if cmds.objExists(crv_c_spineFk):
                            cmds.matchTransform(spineIk,crv_c_spineFk,rotation=True)
                        else:
                            if cmds.objExists(spineC):
                                cmds.matchTransform(spineIk,spineC,rotation=True)
                            if cmds.objExists(spineB):
                                cmds.matchTransform(spineIk,spineB,rotation=True)
                        if switch:
                            cmds.setAttr(cog+'.IKFK',0)
                if switch:
                    
                    if obj in IKFK_dict:
                        switch_objects = IKFK_dict[obj]
                        
                        for switch_object in switch_objects:
                            if cmds.objExists(switch_object):
                                print(f"Switch object found: {switch_object}")
                                final_selection.append(switch_object)
            if switch:
                if final_selection:
                    # 选择所有找到的预设物体
                    cmds.select(final_selection)
                    print(f"Final selection: {final_selection}")
        cmds.undoInfo(closeChunk=True)
    '''
    实时IKFK
    '''
    def open_IKFK(self):
        cmds.scriptJob(killAll=True)
        all_objects = cmds.ls(transforms=True)
        cameras = cmds.listCameras()
        non_camera_objects = [obj for obj in all_objects if obj not in cameras]
        for obj in non_camera_objects:

            cmds.scriptJob(attributeChange=[obj + '.translate',self.job_IKFK])

            cmds.scriptJob(attributeChange=[obj + '.rotate',self.job_IKFK])

            cmds.scriptJob(attributeChange=[obj + '.scale',self.job_IKFK])


    '''
    关闭实时IKFK
    '''
    def colse_IKFK(self):
        cmds.scriptJob(killAll=True)

    '''
    job_IKFK
    '''
    def job_IKFK(self):
        cmds.undoInfo(openChunk=True)
        current_frame = cmds.currentTime(query=True)  # 获取当前帧
        current_time = time.time()#获取当前时间
        if current_time - self.last_trigger_time >= 0.1:
            self.last_trigger_time = current_time
            if not self.last_frame == current_frame:
                self.last_frame = current_frame
                return  # 如果当前帧不与上次相同，直接返回

            print('IKFK')
            selection = cmds.ls(selection=True)
            if selection:
                name = cmds.ls(selection=True, showNamespace=True)
                name_space = name[-1] + ':'
                armBlend_l = name_space + 'ctrl_l_armBlendIkFk'
                upperarmFk_l = name_space + 'ctrl_l_upperarmFk'
                forearmFk_l = name_space + 'ctrl_l_forearmFk'
                armFkPv_l = name_space + 'crv_l_armFkPv'
                handFk_l = name_space + 'ctrl_l_handFk'
                upperarmIk_l = name_space + 'jnt_l_upperarmIk'
                forearmIk_l = name_space + 'jnt_l_forearmIk'
                armPv_l = name_space + 'ctrl_l_armPv'
                handIk_l = name_space + 'ctrl_l_handIk'

                armBlend_r = name_space + 'ctrl_r_armBlendIkFk'
                upperarmFk_r = name_space + 'ctrl_r_upperarmFk'
                forearmFk_r = name_space + 'ctrl_r_forearmFk'
                armFkPv_r = name_space + 'crv_r_armFkPv'
                handFk_r = name_space + 'ctrl_r_handFk'
                upperarmIk_r = name_space + 'jnt_r_upperarmIk'
                forearmIk_r = name_space + 'jnt_r_forearmIk'
                armPv_r = name_space + 'ctrl_r_armPv'
                handIk_r = name_space + 'ctrl_r_handIk'

                legBlend_l = name_space + 'ctrl_l_legBlendIkFk'
                thighFk_l = name_space + 'ctrl_l_thighFk'
                shinFk_l = name_space + 'ctrl_l_shinFk'
                legFkPv_l = name_space + 'crv_l_legFkPv'
                footFk_l = name_space + 'ctrl_l_footFk'
                if cmds.objExists(name_space + 'crv_l_footIk'):
                    crv_l_footIk = name_space + 'crv_l_footIk'
                else:
                    crv_l_footIk = name_space + 'ctrl_l_footIk'
                if cmds.objExists(name_space + 'crv_l_footFk'):
                    crv_l_footFk = name_space + 'crv_l_footFk'
                else:
                    crv_l_footFk = name_space + 'ctrl_l_footFk'
                thighIk_l = name_space + 'jnt_l_thighIk'
                shinIk_l = name_space + 'jnt_l_shinIk'
                legPv_l = name_space + 'ctrl_l_legPv'
                footIk_l = name_space + 'ctrl_l_footIk'

                legBlend_r = name_space + 'ctrl_r_legBlendIkFk'
                thighFk_r = name_space + 'ctrl_r_thighFk'
                shinFk_r = name_space + 'ctrl_r_shinFk'
                legFkPv_r = name_space + 'crv_r_legFkPv'
                footFk_r = name_space + 'ctrl_r_footFk'
                if cmds.objExists(name_space + 'crv_r_footIk'):
                    crv_r_footIk = name_space + 'crv_r_footIk'
                else:
                    crv_r_footIk = name_space + 'ctrl_r_footIk'
                if cmds.objExists(name_space + 'crv_r_footFk'):
                    crv_r_footFk = name_space + 'crv_r_footFk'
                else:
                    crv_r_footFk = name_space + 'ctrl_r_footFk'
                thighIk_r = name_space + 'jnt_r_thighIk'
                shinIk_r = name_space + 'jnt_r_shinIk'
                legPv_r = name_space + 'ctrl_r_legPv'
                footIk_r = name_space + 'ctrl_r_footIk'

                cog = name_space + 'ctrl_c_cog'
                spineFKs = []
                for i in range(10):
                    if cmds.objExists(name_space + 'ctrl_c_spine'+chr(65+i)):
                        spineFKs.append(name_space + 'ctrl_c_spine'+chr(65+i))
                spineIKs = []
                for i in range(10):
                    if cmds.objExists(name_space + 'jnt_c_spine'+chr(65+i)):
                        spineIKs.append(name_space + 'jnt_c_spine'+chr(65+i))
                ctrl_spineIk = name_space + 'ctrl_c_spineIk'
                ctrl_spineIkSub = name_space + 'ctrl_c_spineIkSub'

                neck = name_space + 'ctrl_c_neck'
                crv_c_spineFk = name_space + 'crv_c_spineFk'

                arm_l_IK = [armPv_l, handIk_l]
                arm_l_FK = [upperarmFk_l, forearmFk_l, handFk_l]

                arm_r_IK = [armPv_r, handIk_r]
                arm_r_FK = [upperarmFk_r, forearmFk_r, handFk_r]

                leg_l_IK = [legPv_l, footIk_l]
                leg_l_FK = [thighFk_l, shinFk_l, footFk_l]

                leg_r_IK = [legPv_r, footIk_r]
                leg_r_FK = [thighFk_r, shinFk_r, footFk_r]

                ctrl_spineIKs = [ctrl_spineIk,ctrl_spineIkSub]

                for obj in selection:
                    if cmds.objExists(armBlend_l):
                        if obj in arm_l_IK:
                            cmds.matchTransform(upperarmFk_l, upperarmIk_l)
                            cmds.matchTransform(forearmFk_l, forearmIk_l)
                            cmds.matchTransform(handFk_l, handIk_l)
                        elif obj in arm_l_FK:
                            cmds.matchTransform(handIk_l, handFk_l)
                            cmds.matchTransform(armPv_l, armFkPv_l)
                        else:
                            if cmds.getAttr(armBlend_l + '.translateY') >= -2.35:  # 当IK控制左臂时
                                cmds.matchTransform(upperarmFk_l, upperarmIk_l)
                                cmds.matchTransform(forearmFk_l, forearmIk_l)
                                cmds.matchTransform(handFk_l, handIk_l)
                            elif cmds.getAttr(armBlend_l + '.translateY') < -2.35:  # 当FK控制左臂时
                                cmds.matchTransform(handIk_l, handFk_l)
                                cmds.matchTransform(armPv_l, armFkPv_l)
                    if cmds.objExists(armBlend_r):
                        if obj in arm_r_IK:
                            cmds.matchTransform(upperarmFk_r, upperarmIk_r)
                            cmds.matchTransform(forearmFk_r, forearmIk_r)
                            cmds.matchTransform(handFk_r, handIk_r)
                        elif obj in arm_r_FK:
                            cmds.matchTransform(handIk_r, handFk_r)
                            cmds.matchTransform(armPv_r, armFkPv_r)
                        else:
                            if cmds.getAttr(armBlend_r + '.translateY') >= -2.35:  # 当IK控制右臂时
                                cmds.matchTransform(upperarmFk_r, upperarmIk_r)
                                cmds.matchTransform(forearmFk_r, forearmIk_r)
                                cmds.matchTransform(handFk_r, handIk_r)
                            elif cmds.getAttr(armBlend_r + '.translateY') < -2.35:  # 当FK控制右臂时
                                cmds.matchTransform(handIk_r, handFk_r)
                                cmds.matchTransform(armPv_r, armFkPv_r)
                    if cmds.objExists(legBlend_l):
                        if obj in leg_l_IK:
                            cmds.matchTransform(thighFk_l, thighIk_l)
                            cmds.matchTransform(shinFk_l, shinIk_l)
                            cmds.matchTransform(footFk_l, crv_l_footIk)
                        elif obj in leg_l_FK:
                            cmds.matchTransform(footIk_l, crv_l_footFk)
                            cmds.matchTransform(legPv_l, legFkPv_l)
                        else:
                            if cmds.getAttr(legBlend_l + '.translateY') >= -3.5:  # 当IK控制左腿时
                                cmds.matchTransform(thighFk_l, thighIk_l)
                                cmds.matchTransform(shinFk_l, shinIk_l)
                                cmds.matchTransform(footFk_l, crv_l_footIk)
                            elif cmds.getAttr(legBlend_l + '.translateY') < -3.5:  # 当FK控制左腿时
                                cmds.matchTransform(footIk_l, crv_l_footFk)
                                cmds.matchTransform(legPv_l, legFkPv_l)
                    if cmds.objExists(legBlend_r):
                        if obj in leg_r_IK:
                            cmds.matchTransform(thighFk_r, thighIk_r)
                            cmds.matchTransform(shinFk_r, shinIk_r)
                            cmds.matchTransform(footFk_r, crv_r_footIk)
                        elif obj in leg_r_FK:
                            cmds.matchTransform(footIk_r, crv_r_footFk)
                            cmds.matchTransform(legPv_r, legFkPv_r)
                        else:
                            if cmds.getAttr(legBlend_r + '.translateY') >= -3.5:  # 当IK控制右腿时
                                cmds.matchTransform(thighFk_r, thighIk_r)
                                cmds.matchTransform(shinFk_r, shinIk_r)
                                cmds.matchTransform(footFk_r, crv_r_footIk)
                            elif cmds.getAttr(legBlend_r + '.translateY') < -3.5:  # 当FK控制右腿时
                                cmds.matchTransform(footIk_r, crv_r_footFk)
                                cmds.matchTransform(legPv_r, legFkPv_r)
                    if cmds.objExists(cog):
                        if obj in ctrl_spineIKs:
                            for i in range(len(spineIKs)):
                                cmds.matchTransform(spineFKs[i], spineIKs[i])
                        elif obj in spineFKs:
                            cmds.matchTransform(ctrl_spineIk, neck, position=True)
                            if cmds.objExists(crv_c_spineFk):
                                cmds.matchTransform(ctrl_spineIk, crv_c_spineFk, rotation=True)
                            else:
                                cmds.matchTransform(ctrl_spineIk,spineFKs[-1], rotation=True)
                        else:
                            if cmds.getAttr(cog + '.IKFK') <= 0.5:  # 当IK控制躯干时
                                for i in range(len(spineIKs)):
                                    cmds.matchTransform(spineFKs[i], spineIKs[i])
                            elif cmds.getAttr(cog + '.IKFK') > 0.5:  # 当FK控制躯干时

                                cmds.matchTransform(ctrl_spineIk, neck, position=True)
                                if cmds.objExists(crv_c_spineFk):
                                    cmds.matchTransform(ctrl_spineIk, crv_c_spineFk, rotation=True)
                                else:
                                    cmds.matchTransform(ctrl_spineIk,spineFKs[-1], rotation=True)

        cmds.undoInfo(closeChunk=True)
    '''
    按层级排列
    '''
    def hierarchy_ordered(self,objs):

        hierarchy = []#结果
        queue = []
        objs_set = set(objs)

        for obj in objs:
            long_name = cmds.ls(obj, long=True)[0]
            parents = long_name.split('|')[1:-1]
            if not any(parent in objs for parent in parents) or parents == []:  # 获取所有顶层物体
                queue.append(obj)
        while queue:
            current_obj = queue.pop(0)  # 从队列中移除最前面的关节
            if current_obj in objs_set and current_obj not in hierarchy:
                hierarchy.append(current_obj)  # 添加到层级列表中

            # 获取当前物体的子级
            children = cmds.listRelatives(current_obj, children=True) or []
            # 按照层级顺序，将子物体添加到队列
            for child in children:
                if child not in queue:
                    queue.append(child)
        return hierarchy
    '''
    记录变换————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def recordTransform(self):
        selection_objs=cmds.ls(selection=True)
        objs = self.hierarchy_ordered(selection_objs)
        for obj in objs:
            
            obj_name = cmds.ls(obj, shortNames=True)[0]
            name = obj_name.split(':')[-1]
            locator_name = 'loc_'+name
            if cmds.objExists(locator_name):
                cmds.matchTransform(locator_name,obj)
            else:
                locator = cmds.spaceLocator(name=locator_name)[0]
                cmds.setAttr(locator+'.localScaleX',20)
                cmds.setAttr(locator+'.localScaleY',20)
                cmds.setAttr(locator+'.localScaleZ',20)
                cmds.matchTransform(locator,obj)
        cmds.select(objs)
    '''
    对齐变换————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def AlignTransform(self):
        selection_objs = cmds.ls(selection=True)
        objs = self.hierarchy_ordered(selection_objs)
    
        for obj in objs:
            
            obj_name = cmds.ls(obj, shortNames=True)[0]
            name = obj_name.split(':')[-1]
    
            locator_name = 'loc_'+name
            if cmds.objExists(locator_name):
                cmds.matchTransform(obj,locator_name)
            else:
                cmds.warning('请先记录变换')
        cmds.select(objs)
    '''
    记录变换（每帧）————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def recordTransform_per(self):
        # 获取所选的对象
        selection_objs = cmds.ls(selection=True)
        objs = self.hierarchy_ordered(selection_objs)
        
        # 获取时间范围
        start_time = cmds.playbackOptions(q=True, min=True)
        end_time = cmds.playbackOptions(q=True, max=True)
        
        for frame in range(int(start_time), int(end_time) + 1):
            cmds.currentTime(frame)
            for obj in objs:
            
                obj_name = cmds.ls(obj, shortNames=True)[0]
                name = obj_name.split(':')[-1]
    
                locator_name = 'loc_' +name
            
                if not cmds.objExists(locator_name):
                    locator = cmds.spaceLocator(name=locator_name)[0]
                    cmds.setAttr(locator+'.localScaleX', 20)
                    cmds.setAttr(locator+'.localScaleY', 20)
                    cmds.setAttr(locator+'.localScaleZ', 20)
            
                cmds.matchTransform(locator_name, obj)
                cmds.setKeyframe(locator_name, at='translate')
                cmds.setKeyframe(locator_name, at='rotate')
                cmds.setKeyframe(locator_name, at='scale')
        
        # 重新选择之前选择的对象
        cmds.select(objs)
    '''
    对齐变换（每帧）————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def AlignTransform_per(self):
        # 获取所选的对象
        selection_objs = cmds.ls(selection=True)
        objs = self.hierarchy_ordered(selection_objs)
        
        # 获取时间范围
        start_time = cmds.playbackOptions(q=True, min=True)
        end_time = cmds.playbackOptions(q=True, max=True)
        
        # 检查所有物体的定位器是否存在
        missing_locators = []
        for obj in objs:
            obj_name = cmds.ls(obj, shortNames=True)[0]
            name = obj_name.split(':')[-1]
            locator_name = 'loc_' +name
            
            if not cmds.objExists(locator_name):
                missing_locators.append(locator_name)
        
        if missing_locators:
            cmds.warning(f"以下定位器不存在，请先记录变换: {', '.join(missing_locators)}")
        else:
            # 遍历时间范围内的每一帧
            for frame in range(int(start_time), int(end_time) + 1):
                cmds.currentTime(frame)
                
                # 在当前帧对齐所有选定的物体
                for obj in objs:
                    obj_name = cmds.ls(obj, shortNames=True)[0]
                    name = obj_name.split(':')[1]
                    
                    locator_name = 'loc_' +name
                    
                    cmds.matchTransform(obj, locator_name)
                    cmds.setKeyframe(locator_name, at='translate')
                    cmds.setKeyframe(locator_name, at='rotate')
                    cmds.setKeyframe(locator_name, at='scale')
            # 重新选择之前选择的对象
            print(objs)
            cmds.select(objs)
    '''
    创建轨迹线————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def create_motionTrail(self):
        cmds.undoInfo(openChunk=True)
    
        # 选择你要创建运动轨迹的物体
        selected_objects = cmds.ls(selection=True)
        cmds.select(clear=True)
        if not cmds.objExists('motionTrail'):
           cmds.createNode('transform',name='motionTrail')
        if not cmds.objExists('motionTrailLayer'):
           cmds.createDisplayLayer(name='motionTrailLayer')
           cmds.editDisplayLayerMembers('motionTrailLayer', 'motionTrail')
           cmds.setAttr('motionTrailLayer.displayType',2)
        #删除所有轨迹线
        allMotionTrails = cmds.listRelatives('motionTrail',allDescendents=True,type='transform')
        if allMotionTrails:
            cmds.delete(allMotionTrails)
        
        # 获取时间范围
        start_time = cmds.playbackOptions(q=True, min=True)
        end_time = cmds.playbackOptions(q=True, max=True)
        for obj in selected_objects:
            obj_name = cmds.ls(obj, shortNames=True)[0]
            name = obj_name.split(':')
            unNameSapce = name[-1].split('_')
            
            motion_trail_name = 'motionTrail_'+name[-1]
        
            motion_trail=cmds.snapshot(obj, motionTrail=True,startTime=start_time, endTime=end_time,name=motion_trail_name+'Handle')
            
            cmds.rename(motion_trail_name+'HandleHandle', motion_trail_name)
            # 设置轨迹属性
            cmds.setAttr(motion_trail_name+'Shape' + '.trailThickness', 1)
            cmds.setAttr(motion_trail_name+'Shape'  + '.showFrameMarkers', True)
            
            cmds.parent(motion_trail_name,'motionTrail')
        
        cmds.select(clear=True)
        cmds.select(selected_objects)
        cmds.undoInfo(closeChunk=True)
    '''
    删小数帧————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def deleteDecimalFrames(self):
        def delete_decimal_frames(selected_object):
            # 获取选择的物体的所有关键帧
            keyframes = cmds.keyframe(selected_object, query=True)
            i = 0
        
            if keyframes:
                # 遍历每个关键帧
                for frame in keyframes:
                    # 如果帧数带小数，删除该关键帧
                    if frame % 1 != 0:
                        cmds.cutKey(selected_object, time=(frame, frame), option='keys')
                        i += 1
        
            return i
        
        # 获取当前选择的物体
        selected_objects = cmds.ls(selection=True)
        
        # 记录总的删除帧数
        total_deleted_frames = 0
        
        # 遍历每个选中的物体
        for obj in selected_objects:
            total_deleted_frames += delete_decimal_frames(obj)
        
        # 显示总的删除帧数
        cmds.warning("已删除{}个重叠小数帧".format(total_deleted_frames))
    '''
    根/重心控制————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def rootCogCtrl(self,value):
        cmds.undoInfo(openChunk=True)
        name=cmds.ls(selection=True,showNamespace=True)
        ns=name[-1]+':'
        
        rotateObjs=[ns+'ctrl_r_upperarmFk',
            ns+'ctrl_l_upperarmFk',
            ns+'ctrl_l_handFk',
            ns+'ctrl_r_handFk',
            ns+'ctrl_l_footFk',
            ns+'ctrl_r_footFk',
            ns+'ctrl_c_head',
            ns+'ctrl_c_spineC',
            ns+'ctrl_c_spineB',
            ns+'ctrl_c_spineA',
            ns+'ctrl_c_tail_01',
            ns+'ctrl_c_tail_02',
            ns+'ctrl_c_tail_03',
            ns+'ctrl_c_tail_04',
            ns+'ctrl_c_tail_05',
            ns+'ctrl_c_tail_06',
            ns+'ctrl_c_tail_07',
            ns+'ctrl_c_tail_08',
            ns+'ctrl_r_thighFk',
            ns+'ctrl_l_thighFk']
        
        for rotateObj in rotateObjs:
            if cmds.objExists(rotateObj) and cmds.attributeQuery('rotateFollow', node=rotateObj, exists=True):
                self.RF_value(rotateObj,value)
            else:
                continue
        spaceObjs=[ns+'ctrl_r_handIk',
            ns+'ctrl_l_handIk',
            ns+'ctrl_r_armPv',
            ns+'ctrl_l_armPv',
            ns+'ctrl_r_footIk',
            ns+'ctrl_l_footIk',
            ns+'ctrl_r_toeIk',
            ns+'ctrl_l_toeIk',
            ns+'ctrl_r_legPv',
            ns+'ctrl_l_legPv',
            ns+'ctrl_c_spineIk']
        exist_spaceObjs = []
        for spaceObj in spaceObjs:
            if cmds.objExists(spaceObj) and cmds.attributeQuery('space', node=spaceObj, exists=True):
                exist_spaceObjs.append(spaceObj)
            else:
                continue
        cmds.select(clear=True)
        cmds.select(exist_spaceObjs)
        self.space(enum=value)
        cmds.select(name[0])
        cmds.undoInfo(closeChunk=True)
    '''
    跨文件复制粘贴变换————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
    '''
    def copy_transforms(self):
        selected_objects = cmds.ls(selection=True, type="transform")
        if not selected_objects:
            cmds.warning("选择一个变换节点")
            return

        # Get translation, rotation, and scale values
        transforms_data = {}
        for obj in selected_objects:
            translation = cmds.getAttr(obj + ".translate")[0]
            rotation = cmds.getAttr(obj + ".rotate")[0]
            scale = cmds.getAttr(obj + ".scale")[0]

            transforms_data[obj] = {"translation": translation, "rotation": rotation, "scale": scale}

        # Convert to JSON and copy to clipboard
        json_data = json.dumps(transforms_data)
        clipboard = QApplication.clipboard()
        clipboard.setText(json_data)

        cmds.warning("变换已粘贴到剪贴板")

    def paste_transforms(self):
        selected_objects = cmds.ls(selection=True, type="transform")
        if not selected_objects:
            cmds.warning("选择一个变换节点")
            return

        clipboard = QApplication.clipboard()
        json_data = clipboard.text()

        if not json_data:
            cmds.warning("剪贴板是空的")
            return

        try:
            transforms_data = json.loads(json_data)
        except ValueError:
            cmds.warning("剪贴板的数据无效")
            return

        # Get the first object from the copied data
        first_obj = list(transforms_data.keys())[0]
        translation = transforms_data[first_obj]["translation"]
        rotation = transforms_data[first_obj]["rotation"]
        scale = transforms_data[first_obj]["scale"]

        # Paste translation, rotation, and scale values to all selected objects
        for obj in selected_objects:
            cmds.setAttr(obj + ".translate", *translation)
            cmds.setAttr(obj + ".rotate", *rotation)
            cmds.setAttr(obj + ".scale", *scale)

        cmds.warning("变换已粘贴到选中物体")

    '''
    每帧对齐到边界框
    '''
    def match_bounding_boxes(self):
        # 选择网格体
        selected_objects = cmds.ls(selection=True, transforms=True)
        if not selected_objects:
            cmds.warning("请先选择一个或多个网格体")
            return
        start_time = cmds.playbackOptions(q=True, min=True)
        end_time = cmds.playbackOptions(q=True, max=True)

        for frame in range(int(start_time), int(end_time) + 1):
            cmds.currentTime(frame)
            # 初始化边界框的最小和最大值
            min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
            max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

            # 遍历每个选择的对象，获取其边界框
            for obj in selected_objects:
                bbox = cmds.xform(obj, query=True, boundingBox=True)
                min_x = min(min_x, bbox[0])
                min_y = min(min_y, bbox[1])
                min_z = min(min_z, bbox[2])
                max_x = max(max_x, bbox[3])
                max_y = max(max_y, bbox[4])
                max_z = max(max_z, bbox[5])

            # 计算整体边界框的中心点
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            locator_name='loc_camera'
            # 创建 locator
            if not cmds.objExists(locator_name):
                locator = cmds.spaceLocator()[0]
                cmds.rename(locator,locator_name)

            # 移动 locator 到边界框中心
            cmds.xform(locator_name, translation=(center_x, center_y, center_z))
            cmds.setKeyframe(locator_name, at='translate')
    '''
    每帧对齐到顶点
    '''

    def match_vertex_average(self):
        # 选择网格体
        selected_objects = cmds.ls(selection=True, transforms=True)
        if not selected_objects:
            cmds.warning("请先选择一个或多个网格体")
            return

        start_time = cmds.playbackOptions(q=True, min=True)
        end_time = cmds.playbackOptions(q=True, max=True)

        for frame in range(int(start_time), int(end_time) + 1):
            cmds.currentTime(frame)

            # 初始化顶点位置的总和
            total_x, total_y, total_z = 0, 0, 0
            total_vertices = 0

            # 遍历每个选择的对象，获取其顶点位置
            for obj in selected_objects:
                vertices = cmds.ls(f"{obj}.vtx[*]", flatten=True)
                for vertex in vertices:
                    position = cmds.xform(vertex, query=True, translation=True, worldSpace=True)
                    total_x += position[0]
                    total_y += position[1]
                    total_z += position[2]
                    total_vertices += 1

            if total_vertices > 0:
                # 计算顶点的平均位置
                avg_x = total_x / total_vertices
                avg_y = total_y / total_vertices
                avg_z = total_z / total_vertices

                locator_name = 'loc_camera'
                # 创建 locator
                if not cmds.objExists(locator_name):
                    locator = cmds.spaceLocator()[0]
                    cmds.rename(locator, locator_name)

                # 移动 locator 到顶点平均位置
                cmds.xform(locator_name, translation=(avg_x, avg_y, avg_z))
                cmds.setKeyframe(locator_name, at='translate')




    