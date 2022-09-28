# import modules
import  cadwork   
import  element_controller      as ec
import  attribute_controller    as ac
import  geometry_controller     as gc
import utility_controller       as uc

version='AddNuggetNode::v8'
# add dimensioning to this node


#where to store cube layer names
cube_attr = 25 #H_Design Description 1 
cube_dimensions = 26 #H Design Description 2

uc.print_message('[' + version + '] Select nugget node point',2,1)
p = uc.get_user_point()
if(p):
    
    #get sizes from user in cwUX
    sizesStr = uc.get_user_string('[' + version + '] Enter boundary box info: X,Y,Z,z-offset (mm):')
    sizes=sizesStr.split(',')
    if(len(sizes)==4):
        boundary_size_x = int(sizes[0])
        boundary_size_y = int(sizes[1])
        boundary_size_z = int(sizes[2])
        copy_z_offset = int(sizes[3])
            
        new_name = uc.get_user_string('Provide nugget name for display')  

        #print(p)
        n = ec.create_node(p)
        ac.set_user_attribute([n],cube_attr,'nugget node')
        ac.set_user_attribute([n],cube_dimensions,sizesStr)
        ac.set_name([n],new_name)
        uc.print_message('node created',2,1)

    else:
        uc.print_message('invalid dimension info',2,1)
else:
    uc.print_message('no point provided',2,1)

