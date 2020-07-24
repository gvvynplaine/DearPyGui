#### Imports for Marvel Sandbox ####
from marvel import *
import marvel_constants as mc

#### Imports for this app ####
import json
from os import path
from collections import deque
from copy import deepcopy

#### Always show logger ####
show_logger()
show_debug()
class treeItem:
    def __init__(self, name, parent, isContainer):
        self.m_name = name
        self.m_parent = parent
        self.isContainer = isContainer

class app(treeItem):
    def __init__(self, name, directory, parent):
        treeItem.__init__(self, name, parent, isContainer = False)
        self.m_directory = directory

class container(treeItem):
    def __init__(self, name, parent):
        treeItem.__init__(self, name, parent, isContainer = True)
        self.m_items = []

class layout(container):
    def __init__(self, name):
        container.__init__(self, name, parent = None)

    def getTreeItem(self, name):
        queue = deque(self.m_items)

        while queue:
            item = queue.popleft()

            if (item.m_name == name):
                return item

            elif (item.isContainer):
                queue.extendleft(reversed(item.m_items))

            else:
                pass
        return False

class layoutEditor():
    def __init__(self, layoutObject = None):
        self.layout = layoutObject
    def getLayout(self):
        return self.layout

    def setLayout(self, layoutObject):
        self.layout = layoutObject

    def createLayout(self, name):
        self.layout = layout(name)

    def addApp(self, name, directory, parent = None):
        if (parent is None or parent == self.layout.m_name):
            self.layout.m_items.append(deepcopy(app(name, directory, self.layout.m_name)))
        else:
            parentContainer = self.layout.getTreeItem(parent)
            parentContainer.m_items.append(deepcopy(app(name, directory, parentContainer.m_name)))

    def addContainer(self, name, parent = None):
        if (parent is None or parent == self.layout.m_name):
            self.layout.m_items.append(deepcopy(container(name, self.layout.m_name)))
        else:
            parentContainer = self.layout.getTreeItem(parent)
            parentContainer.m_items.append(deepcopy(container(name, parentContainer.m_name)))

    def deleteItem(self, treeItem):
        if (treeItem.m_parent == self.layout.m_name):
            self.layout.m_items.remove(treeItem)
        else:
            parentContainer = self.layout.getTreeItem(treeItem.m_parent)
            parentContainer.m_items.remove(treeItem)

    def moveItem(self, treeItem, movePos):
        print(treeItem)
        if (treeItem.m_parent == self.layout.m_name):
            maxPos = len(self.layout.m_items) - 1
            itemPos = self.layout.m_items.index(treeItem)
            if(itemPos + movePos > maxPos):
                print("greater than Max")
            elif(itemPos + movePos < 0):
                print("less than zero")
            else:
                poppedItem = self.layout.m_items.pop(itemPos)
                newPos = itemPos + movePos
                self.layout.m_items.insert(newPos, poppedItem)
        else:
            parentContainer = self.layout.getTreeItem(treeItem.m_parent)
            items = parentContainer.m_items
            maxPos = len(items) - 1
            itemPos = items.index(treeItem)
            if(itemPos + movePos < maxPos and itemPos + movePos > -1):
                poppedItem = items.pop(itemPos)
                newPos = itemPos + movePos
                items.insert(newPos, poppedItem)
            else:
                poppedItem = items.pop(itemPos)
                if(parentContainer.m_parent == self.layout.m_name):
                    poppedItem.m_parent = self.layout.m_name
                    self.layout.m_items.append(poppedItem)
                else:
                    parentofparentContainer = self.layout.getTreeItem(parentContainer.m_parent)
                    poppedItem.m_parent = parentofparentContainer.m_name
                    parentofparentContainer.m_items.append(poppedItem)

class manager():
    def __init__(self):
        self.m_layoutDirectory = "ManagerConfig.json"
        self.builder = None
        self.m_layouts = []
        self.m_defaultLayout = 0
        self.m_activeLayout = None
        self.m_endContainerFlag = 0 
        self.isEditMode = False

    def setBuilder(self, builder):
        self.builder = builder

    def loadLayout(self, dir):
        with open(dir,"r") as file:
            decodedData = json.load(file)

            #imports multiple layouts in a single json
            if isinstance(decodedData, list):
                for layoutData in decodedData:
                    layoutBuilder = layoutEditor()
                    if layoutData["__layout__"]:
                        layoutBuilder.createLayout(layoutData["name"])
                        for item in layoutData["layoutItems"]:
                            if "__container__" in item:
                                layoutBuilder.addContainer(item["name"],item["parent"])
                            elif "__app__" in item:
                                layoutBuilder.addApp(item["name"],item["directory"], item["parent"])
                        self.m_layouts.append(deepcopy(layoutBuilder.getLayout()))
                    else:
                        print("No Layout Found")

            #imports single layout in a single json
            else:
                layoutBuilder = layoutEditor()
                if decodedData["__layout__"]:
                    layoutBuilder.createLayout(decodedData["name"])
                    for item in decodedData["layoutItems"]:
                        if "__container__" in item:
                            layoutBuilder.addContainer(item["name"],item["parent"])
                        elif "__app__" in item:
                            layoutBuilder.addApp(item["name"],item["directory"], item["parent"])
                    self.m_layouts.append(deepcopy(layoutBuilder.getLayout()))
                else:
                    print("No Layout Found")

    def exportLayout(self, dir, layoutPosition = None):
        if (layoutPosition == None):
            with open(dir,"w") as file:
                json.dump(self.m_layouts, file, cls=layoutEncoder, indent=4)
        else:
            with open(dir,"w") as file:
                json.dump(self.m_layouts[layoutPosition], file, cls=layoutEncoder, indent=4)

    def setActiveLayout(self, position):
        self.m_activeLayout = self.m_layouts[position]
        self.builder.setLayout(self.m_activeLayout)

    def getAllTreeItemNames(self):
        nameList = []

        queue = deque(self.m_activeLayout.m_items)
        while queue:
            item = queue.popleft()
            if (item.isContainer):
                nameList.append(item.m_name)
                queue.extendleft(reversed(item.m_items))

            else:
                nameList.append(item.m_name)
        return deepcopy(nameList)

    def getLayoutNames(self):
        layoutNames = []
        for item in self.m_layouts:
            layoutNames.append(item.m_name)
        return deepcopy(layoutNames)

    def getLayoutItem(self, name):
        return(self.m_activeLayout.getTreeItem(name))



    #drawing part of the layout manager to be replaced with style manager
        
    def draw(self):
        #TODO: for now we will have 2 separate draws, its cleaner while building
        #TODO: window size is currenly the main window size and should be replaced with the size from the MainWindow
        if(self.isEditMode):
            add_group("App Space")
            drawWidth = get_item_width("MainWindow") - get_item_width("Properties Window") - 15
            containerLevel = 0
            appWidth = 50
            mainRowWidth = appWidth
            drawQueue = deque(self.m_activeLayout.m_items)
            while drawQueue:
                item = drawQueue.popleft()

                if (item == self.m_endContainerFlag):
                    end_window()
                    containerLevel -=1

                elif (item.isContainer):
                    print(item.m_name, mainRowWidth)
                    add_drawing(item.m_name, width = appWidth, height = appWidth)
                    add_window((item.m_name + " Popup"), movable = False, resizable = False, autosize = True, hide = True)
                    draw_circle(item.m_name, (25,25), 25, (255,255,255,255))
                    set_render_callback("onRender", handler = (item.m_name + " Popup"))
                    containerLevel += 1
                    drawQueue.appendleft(self.m_endContainerFlag)
                    drawQueue.extendleft(reversed(item.m_items))

                else:
                    print(item.m_name, mainRowWidth)
                    add_drawing(item.m_name, width = appWidth, height = appWidth)
                    draw_circle(item.m_name, (25,25), 25, (255,255,0,255))

                #determines if item is added on same line
                if(containerLevel != 0):
                        pass
                else:
                    mainRowWidth += appWidth
                if(mainRowWidth < drawWidth):
                    add_same_line()
                else:
                    mainRowWidth = appWidth + 15
            end_group()
        else:
            add_group("App Space")
            drawWidth = get_item_width("MainWindow") - 15
            containerLevel = 0
            appWidth = 50
            mainRowWidth = appWidth 
            drawQueue = deque(self.m_activeLayout.m_items)
            while drawQueue:
                item = drawQueue.popleft()

                if (item == self.m_endContainerFlag):
                    end_popup()
                    containerLevel -=1

                elif (item.isContainer):
                    print(item.m_name, mainRowWidth)
                    add_drawing(item.m_name, width = appWidth, height = appWidth)
                    add_popup(item.m_name, item.m_name + " Popup", mousebutton=mc.mvMouseButton_Left)
                    draw_circle(item.m_name, (25,25), 25, (255,255,255,255))
                    set_render_callback("onRender", handler = (item.m_name + " Popup"))
                    containerLevel += 1
                    drawQueue.appendleft(self.m_endContainerFlag)
                    drawQueue.extendleft(reversed(item.m_items))

                else:
                    print(item.m_name, mainRowWidth)
                    add_drawing(item.m_name, width = appWidth, height = appWidth)
                    draw_circle(item.m_name, (25,25), 25, (255,255,0,255))

                #determines if item is added on same line
                if(containerLevel != 0):
                        pass
                else:
                    mainRowWidth += appWidth
                if(mainRowWidth < drawWidth):
                    add_same_line()
                else:
                    mainRowWidth = appWidth + 15
            end_group()

    def undraw(self):
        if(self.isEditMode):
            drawQueue = deque(self.m_activeLayout.m_items)
            while drawQueue:
                item = drawQueue.popleft()
                if (item.isContainer):
                    delete_item(item.m_name + " Popup")
                    drawQueue.extendleft(reversed(item.m_items))
        delete_item("App Space")

    def updateDrawing(self):
        self.undraw()
        self.draw()


###########################################
#### Start Layout Manager w/ defaults #####
###########################################
theManager = manager()
layoutBuilder = layoutEditor()
theManager.setBuilder(layoutBuilder)
theManager.loadLayout(theManager.m_layoutDirectory)
theManager.setActiveLayout(theManager.m_defaultLayout)
print(layoutBuilder.layout)
print(theManager.m_activeLayout)
###########################
#### Creating Menu Bar ####
###########################

add_menu_bar("Menu Bar")
add_menu("File")
add_menu_item("Save Changes", callback = "saveLayout")
add_menu_item("Layout Options", callback = "changeLayoutWindow")
end_menu()
add_menu("Theme")
add_menu_item("Style")
add_menu("Color Scheme")
add_menu_item("Dark", callback = "ThemeCallback")
add_menu_item("Light", callback = "ThemeCallback")
add_menu_item("Classic", callback = "ThemeCallback")
add_menu_item("Dark 2", callback = "ThemeCallback")
add_menu_item("Grey", callback = "ThemeCallback")
add_menu_item("Dark Grey", callback = "ThemeCallback")
add_menu_item("Cherry", callback = "ThemeCallback")
add_menu_item("Purple", callback = "ThemeCallback")
add_menu_item("Gold", callback = "ThemeCallback")
add_menu_item("Red", callback = "ThemeCallback")
end_menu()
end_menu()
add_menu_item("Edit Mode", callback = "activateEditMode")
end_menu_bar()

############################
#### Menu Bar Callbacks ####
############################

def launchApp(sender, data):
    print(sender)
    selectedApp = theManager.getLayoutItem(sender)
    if(path.isfile(selectedApp.m_directory)):
        run_file("marvelSandbox", selectedApp.m_directory)
    else:
        log_warning(selectedApp.m_name + " does not have a valid name or directory")

def ThemeCallback(sender, data):
    set_theme(sender)

def saveLayout(sender, data):
    theManager.exportLayout("ManagerConfig.json")

def changeLayoutWindow(sender, data):
    refreshLayoutNames(sender, data)
    show_item("Change Layout Window")

def activateEditMode(sender, data):
    if(theManager.isEditMode == False):
        theManager.undraw()
        theManager.isEditMode = True
        drawPropertiesWindow()
        theManager.draw()

def deactivateEditMode(sender, data):
    delete_item("Properties Window")
    theManager.undraw()
    theManager.isEditMode = False
    theManager.draw()

###############################
#### Creating Main Widgets ####
###############################
set_main_window_size(400,500)
set_resize_callback("onResize")
set_render_callback("onRender")
theManager.draw()


def onResize(sender, data):
    add_data("Resized", True)

def onRender(sender, data):
    #redrawing if window was resized
    if(get_data("Resized")):
        theManager.updateDrawing()

    #TODO: simplify for ease
    if(theManager.isEditMode == False):
        #launching selected app
        if(is_mouse_button_clicked(mc.mvMouseButton_Left)):
            itemNames = theManager.getAllTreeItemNames()
            for name in itemNames:
                if(is_item_hovered(name)):
                    selectedItem = theManager.getLayoutItem(name)
                    add_data("selectedItemName", selectedItem.m_name)
                    print(get_data("selectedItemName"))
                    if(selectedItem.isContainer is False):
                        if(path.isfile(selectedItem.m_directory)):
                            run_file("marvelSandbox", selectedItem.m_directory)
                        else:
                            add_data("errorMessage", (selectedItem.m_name + " does not have a valid name or directory"))
                            show_item("Error Window")
    else:
        if(get_data("Resized")):

            set_window_pos("Properties Window", get_item_width("MainWindow") - get_item_width("Properties Window") ,21)
            #mainHeight = get_item_height("MainWindow")
            propertiesHeight = int(mainHeight - 21)
            set_item_height("Properties Window", propertiesHeight)
        if(is_mouse_button_clicked(mc.mvMouseButton_Left)):
            itemNames = theManager.getAllTreeItemNames()
            for name in itemNames:
                if(is_item_hovered(name)):
                    selectedItem = theManager.getLayoutItem(name)
                    add_data("selectedItemName", selectedItem.m_name)
                    if(selectedItem.isContainer):
                        show_item(selectedItem.m_name+ " Popup")
                        mousePos = get_mouse_pos(local = False)
                        print(mousePos)
                        set_window_pos(selectedItem.m_name + " Popup", mousePos[0],mousePos[1])
                        add_data("selectedItemDir","Not Avaliable")
                    else:
                        add_data("selectedItemDir", selectedItem.m_directory)
                    print(get_data("selectedItemName"))
                    break
                else:
                    add_data("selectedItemName", theManager.m_activeLayout.m_name)
                    add_data("selectedItemDir", "Not Avaliable")
    add_data("Resized", False)
            

################################
####  Main Widget Callbacks ####
################################

def addItemWindow(sender, data):
    show_item("Item Window")

def deleteItem(sender, data):
    selectedItem = theManager.getLayoutItem(get_data("selectedItemName"))
    layoutBuilder.deleteItem(selectedItem)
    theManager.updateDrawing()

def changeAppDir(sender, data):
    pass

def moveUp(sender, data):
    selectedItem = theManager.getLayoutItem(get_data("selectedItemName"))
    print(theManager.getLayoutItem(get_data("selectedItemName")))
    print(selectedItem)
    layoutBuilder.moveItem(selectedItem,-1)
    theManager.updateDrawing()

def moveDown(sender, data):
    selectedItem = theManager.getLayoutItem(get_data("selectedItemName"))
    layoutBuilder.moveItem(selectedItem,1)
    theManager.updateDrawing()

def renameItem(sender, data):
    pass


#################
#### Windows ####
#################

#properties window for edit view
def drawPropertiesWindow():
    mainWidth = get_item_width("MainWindow")
    mainHeight = get_item_height("MainWindow")
    propertiesWidth = 300
    menuHeight = 21
    propertiesHeight = int(mainHeight - menuHeight)
    print(propertiesHeight)
    propertiesXStart = int(mainWidth - propertiesWidth)
    propertiesYStart = int(menuHeight)
    add_window("Properties Window", propertiesWidth, propertiesHeight, resizable = False, movable = False, title_bar = False, start_x = propertiesXStart, start_y=propertiesYStart)
    add_label_text("Properties:","")
    add_seperator()

    add_label_text(":Name","",data_source = "selectedItemName")
    add_label_text(":Path","", data_source = "selectedItemDir")
    add_button("Change Dir", callback="changeFileSelector")
    add_button("Move Up", callback="moveUp")
    add_same_line(spacing = 5)
    add_button("Move Down", callback="moveDown")
    add_button("Add Item", callback="addItemWindow")
    add_same_line(spacing = 5)
    add_button("Delete Item", callback="deleteItem")
    add_button("Apply Changes", )
    add_button("Exit Editor", callback="deactivateEditMode")

    end_window()
    set_render_callback("onRenderProp", handler = "Properties Window")
    set_render_callback("onRender", handler = "Properties Window")

def onRenderProp(sender,data):
    #resizes and moves properties window
    if(get_data("Resized")):
        #TODO: set 21 to get_item_height("Menu Bar") 
        set_window_pos("Properties Window", (get_item_width("MainWindow") - get_item_width("Properties Window")) ,21)
        propertiesHeight = int(get_item_height("MainWindow") - 21)
        set_item_height("Properties Window", propertiesHeight)
        theManager.updateDrawing()

def changeFileSelector(sender, data):
    dir = open_file_dialog([["Python","*.py"]])
    add_data("selectedItemDir", dir)

# Item Window
add_window("Item Window", autosize = True, hide = True)
add_radio_button("Item Type", ["App","Group"], callback = "updateChoice")
add_input_text("Name", hint = "Name to be displayed")
add_button("Select App", callback="newFileSelector")
add_data("newAppDir","")
add_label_text(" :File Path", "", data_source = "newAppDir")
add_button("Apply", callback = "addItem")
end_window()
add_window("Error Window", 400, 50, hide = True)
add_data("errorMessage","")
add_label_text("Error","", data_source = "errorMessage", color = (255,255,0))
end_window()

def updateChoice(sender, data):
        if (get_value("Item Type") == 0):
            show_item("Select App")
            show_item(" :File Path")
        else:
            hide_item("Select App")
            hide_item(" :File Path")

def newFileSelector(sender, data):
    dir = open_file_dialog([["Python","*.py"]])
    add_data("newAppDir", dir)

def addItem(sender, data):
    name = get_value("Name")
    itemDoesntExist = not theManager.getLayoutItem(name)
    if (itemDoesntExist):
        if (get_value("Item Type") == 0):
            layoutBuilder.addApp(name, get_data("newAppDir"), parent = get_data("selectedItemName"))
        else:
            layoutBuilder.addContainer(name, parent = get_data("selectedItemName"))
        theManager.updateDrawing()
    else:
        add_data("errorMessage", "Item must have unique name")
        show_item("Error Window")


# Change Layout Window
add_window("Change Layout Window", autosize = True, hide = True)
layoutNames = theManager.getLayoutNames()
add_listbox("Layouts", layoutNames)
add_button("Set As Active", callback ="setLayout")
add_same_line(spacing = 5)
add_button("Create New", callback = "createLayoutWindow")
add_same_line(spacing = 5)
add_button("Import", callback = "loadLayoutStatic")
add_same_line(spacing = 5)
add_button("Export", callback = "exportLayoutStatic")
add_same_line(spacing = 5)
end_window()

def refreshLayoutNames(sender, data):
    layoutNames = theManager.getLayoutNames()
    delete_item("Layouts")
    add_listbox("Layouts", layoutNames, before="Set As Active")

def setLayout(sender, data):
    theManager.undraw()
    theManager.setActiveLayout(get_value("Layouts"))
    theManager.draw()

def createLayoutWindow(sender, data):
    show_item("Create Layout Window")

def loadLayoutStatic(sender, data):
    dir = open_file_dialog([["JSON","*.json"]])
    theManager.loadLayout(dir)
    refreshLayoutNames(sender)

def exportLayoutStatic(sender, data):
    theManager.exportLayout("ExportedLayout.json", get_value("Layouts"))

# Create Layout Window
add_window("Create Layout Window", autosize = True, hide = True)
add_input_text("Layout Name")
add_button("Finish", callback ="createLayout")
end_window()

def createLayout(sender, data):
    theManager.createLayout(get_value("Layout Name"))
    refreshLayoutNames(sender)
    hide_item("Create Layout Window")

###############################
#### JSON Encoder Subclass ####
###############################

class layoutEncoder(json.JSONEncoder):
    def default(self, layoutObject):
        if isinstance(layoutObject, layout):

            layoutJSON = { "__layout__": True, "name":layoutObject.m_name, "layoutItems":[]}

            queue = deque(layoutObject.m_items)

            while queue:
                item = queue.popleft()

                if (item.isContainer):
                    containerJSON = {"__container__": True, "name":item.m_name, "parent":item.m_parent}
                    layoutJSON["layoutItems"].append(containerJSON)
                    queue.extendleft(reversed(item.m_items))

                else:
                    appJSON = {"__app__": True, "name":item.m_name, "directory":item.m_directory, "parent":item.m_parent}
                    layoutJSON["layoutItems"].append(appJSON)
            return layoutJSON
        else:
            return super().default(layoutObject)