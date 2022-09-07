# import modules
import  cadwork   
import  element_controller      as ec
import  attribute_controller    as ac
import  geometry_controller     as gc
import utility_controller       as uc

version='AddNuggetNode::v1'

#where to store cube layer names
cube_attr = 25 #H_Design Description 1 

uc.print_message('[' + version + '] Select nugget node point',2,1)
p = uc.get_user_point()
if(p):
    print(p)
    n = ec.create_node(p)
    ac.set_user_attribute([n],cube_attr,'nugget node')
    new_name = uc.get_user_string('Provide nugget name for display')
    ac.set_name([n],new_name)
    uc.print_message('node created',2,1)
else:
    uc.print_message('no point provided',2,1)

