import maya.cmds as mc
import pymel.core as pm

class MatrixConstraints():
   
    '''
    ---------------------------------------------------------------------------
       
        Constraints two PYMEL objects using their matrices.
       
        Availiable constraints are:
           
                - parent_constraint(@)
                        @parent_object = str() name of the parent object
                        @child_object = str() name of the parent object
                        @constrain_translation = boolean, defaults to True
                        @constrain_rotation = boolean, defaults to True
                        @maintain_offset = boolean, defaults to True
                   
                - point_constraint(@)
                        @parent_object = str() name of the parent object
                        @child_object = str() name of the parent object
                       
                - orient_constraint(@)
                        @parent_object = str() name of the parent object
                        @child_object = str() name of the parent object
               
                - aim_constraint(@)
                        @parent_object = str() name of the parent object
                        @child_object = str() name of the parent object
                        @up_vector_object = str() name of the parent object

                       
        ---------------------------------------------------------------------------
       
        '''
   
    def __init__(self, parent_object, child_object):
       
        #Create pyNodes for the selected objects
        self.pm_parent_object = pm.PyNode(parent_object)
        self.pm_child_object = pm.PyNode(child_object)
       
        #Check if both objects have matrices
        if self.pm_parent_object.hasAttr('matrix') == True and self.pm_child_object.hasAttr('matrix') == True:
            print('Constraining between ' + self.pm_parent_object + ' and ' + self.pm_child_object + ' -->')
           
        else:
            raise RuntimeError('The selected objects have no matrices to constrain with.')
       
        self.pm_decompose_matrix = pm.PyNode(mc.createNode('decomposeMatrix'))
        self.pm_parent_object.wm >> self.pm_decompose_matrix.inputMatrix



# --------------------------------------------------------------------------------------------------

    # PARENT CONSTRAINT
    def parent_constraint(self,
                          constrain_translation=True,
                          constrain_rotation=True,
                          maintain_offset=True
                          ):


        # Maintain offset
        if maintain_offset == True:

            # pillamos la matriz del objeto con offset
            pm_child_offset_matrix = self.pm_child_object.getMatrix()
            self.pm_mult_matrix = pm.PyNode(mc.createNode('multMatrix'))

            # Metemos la matriz del offset en el multMatrix via setAttr para que no haya ciclos
            self.pm_mult_matrix.setAttr('matrixIn[0]', pm_child_offset_matrix)
            self.pm_parent_object.wm >> self.pm_mult_matrix.matrixIn[1]
            self.pm_mult_matrix.matrixSum >> self.pm_decompose_matrix.inputMatrix

        else:
            # Si no hay offset conectamos el parent directametnte al decompose
            self.pm_parent_object.wm >> self.pm_decompose_matrix.inputMatrix



        if constrain_translation == False and constrain_rotation == False:
            raise RuntimeError('Both translation and rotation are deactivated, there is nothing to constrain.')

        else:
            if constrain_translation:
                self.pm_decompose_matrix.outputTranslate >> self.pm_child_object.translate
            else:
                pass
               
            if constrain_rotation:
                self.pm_decompose_matrix.outputRotate >> self.pm_child_object.rotate
            else:
                pass
        print('Parent constraint!')

# --------------------------------------------------------------------------------------------------


    # ORIENT CONSTRAINT
    def orient_constraint(self):
       
        self.pm_decompose_matrix.outputRotate >> self.pm_child_object.rotate
        print('Orient Constraint!')

   
# --------------------------------------------------------------------------------------------------
   
   
    # POINT CONSTRAINT
    def point_constraint(self):
        self.pm_decompose_matrix.outputTranslate >> self.pm_child_object.translate
        print('Point Constraint!')



# --------------------------------------------------------------------------------------------------

 
    # AIM CONSTRAINT
    def aim_constraint(self, up_vector_object):
        self.pm_parent_object.wm // self.pm_decompose_matrix.inputMatrix
       
        self.pm_up_vector_object = pm.PyNode(up_vector_object)
               
        self.pm_aim_matrix_node = pm.PyNode(mc.createNode('aimMatrix'))
        
        self.pm_child_input_matrix = self.pm_child_object.getMatrix()
        self.pm_aim_matrix_node.setAttr('inputMatrix', self.pm_child_input_matrix)
       
        self.pm_parent_object.wm >> self.pm_aim_matrix_node.primary.primaryTargetMatrix
        self.pm_up_vector_object.wm >> self.pm_aim_matrix_node.secondary.secondaryTargetMatrix
        self.pm_aim_matrix_node.setAttr('secondaryMode', 1)
       
        self.pm_aim_matrix_node.outputMatrix >> self.pm_decompose_matrix.inputMatrix
       
        self.pm_decompose_matrix.outputRotate >> self.pm_child_object.rotate
       
        print('Aim Constraint!')
       

       
       

# --------------------------------------------------------------------------------------------------



#test_constraint = MatrixConstraints('PARENT','CHILD').parent_constraint(constrain_translation=True, constrain_rotation=False, maintain_offset=True)
#test_orient = MatrixConstraints('PARENT', 'CHILD').orient_constraint()
#test_point = MatrixConstraints('PARENT', 'CHILD').point_constraint()
#test_aim = MatrixConstraints('PARENT', 'CHILD').aim_constraint('UP')