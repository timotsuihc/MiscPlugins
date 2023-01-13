import rhinoscriptsyntax as rs
import os
import scriptcontext
import time

#__commandname__ = "AutoLayerRender"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"


def check():
    if not rs.DocumentPath():
        rs.MessageBox("Save your rhino file")
        return (1)
    else:
        main()
        
def redraw ():
    if rs.MessageBox("Turn On Viewport Display? (Slower)", 4 | 32) != 6:
        redraw= rs.EnableRedraw(False)

def main():
    
    #Notice Have you lock all unused layers, including sublayers?
    go = rs.MessageBox("Before Clicking Yes: \n1)Set your render or capture settings prior to automation; \n2)Lock layers not to be Automated;\n3)Unlock layers to be Automated; \n *Mindful of your sublayers* \n *Output will be saved in same folder as Rhino file*", 4 | 32)
    LayToRen = 0
    
    if go == 6:
        #get layers
        layers = rs.LayerNames()
        pickerlayers = []
        
        #display layers
        if layers:
            displaylayer = "Layers to be automated: \n"
            for layer in layers: 
                if rs.IsLayerLocked(layer)==False:                    
                    pickerlayers.append(layer)
                    LayToRen += 1
            
            pickerlayers = [l.replace('::','>')for l in pickerlayers]
            pickedlayers = rs.MultiListBox(pickerlayers,"layers Picker","Displaying Unlocked Layers to be choosen for automation")
            
            ##display for confirmation
            for layer in pickedlayers:
                displaylayer = displaylayer + layer + '\n'                 
            go = go + rs.MessageBox(displaylayer.replace("::",">"), 4 | 32)
            
    
    if go == 12: 
    
        ##Luke's section
        layerState = [] #make empty array list
        for layer in layers: #cycle through the layers
            layerVisibility = rs.IsLayerOn(layer) #find current layer visibility
            layerState.append(layerVisibility) #add that layer visibility to empty array

    
        #get back layer name structure
        pickedlayers = [l.replace('>','::')for l in pickedlayers]
        #make directory
        directory = rs.DocumentPath() + 'AutoRender'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        if LayToRen:
        #select views                
            ViewsSelected = rs.MultiListBox(rs.NamedViews(),"Views Picker","Pick views to render")
            
            #ADD IF NO VIEWS!!!!
            
        else:
            rs.MessageBox("No layer selected(unlocked)")
        
        
        if layers and ViewsSelected:
            redraw()
            OriginalCurrent = rs.CurrentLayer()
            TempLayer = "Temprory Rendering Layer"
            rs.AddLayer(TempLayer)
            rs.CurrentLayer(TempLayer)
            
            for layer in pickedlayers:            
                
                
                #hide all unlocked layers execpt current layer to avoid error box
                if rs.IsLayerLocked(layer)==False and layer!=rs.CurrentLayer():
                    rs.LayerVisible(layer,False)            
                
                #rotate all Unlocked + Hidden layers
                if rs.LayerVisible(layer)==False and rs.IsLayerLocked(layer)==False:
                    
                    
                    #On parent
                    if rs.ParentLayer(layer):
                        parentchain = ''
                        for parent in rs.ParentLayer(layer).split('::'):
                            parentchain = parentchain + parent
                            rs.LayerVisible(parentchain,True)
                            parentchain = parentchain + "::"
                    #on self                
                    rs.LayerVisible(layer,True)               
                    
                    # Rotate All Named Views
                    for namedview in ViewsSelected:
                        
                        #rs.Redraw()
                        
                        ##############################
                        # Was escape key pressed?
                        if (scriptcontext.escape_test(False,True)):
                            print "Esc Pressed, Task Cancelled."
                            rs.CurrentLayer(OriginalCurrent)
                            rs.DeleteLayer(TempLayer)
                            return(1)
                        ################################
                        
                        rs.Command("top")                
                        rs.Command("-namedview R " + '"' + namedview + '" ' + "_enter")
                        
                        filename = layer.replace(":","_") + '_' + namedview
                        filename = ''.join( namechar for namechar in filename if namechar.isalnum() or namechar=="_" ) 
                        
                        
                        #Screen capture
                        rs.Command('_-ViewCaptureToFile ' + '"' + directory + '\\' + filename + '.jpg"' )
                        
                        """
                        #render
                        rs.Command("_-Render")
                        rs.Command("_enter")
                        rs.Command('-saverenderwindowas ' + '"' + directory + '\\' + filename + '.png"')
                        """

                    if rs.ParentLayer(layer):
                        for parent in rs.ParentLayer(layer).split('::'):
                            rs.LayerVisible(parent,False)
                        
                    rs.LayerVisible(layer,False)
                    
            rs.CurrentLayer(OriginalCurrent)
            rs.DeleteLayer(TempLayer)
            
            ##luke's section
            i = 0 #make new variable
            for layer in layers: #cycle through layers
                rs.LayerVisible(layer, layerState[i]) #revert the layer visibility
                i = i+1 #iterate through the indicies of the layerState

            
            return(0)

def RunCommand( is_interactive ):
    if rs.MessageBox("Work in progress, please do not distrubute", 4 | 32) == 6:
        scriptcontext.escape_test(False,True)
        check()


check()