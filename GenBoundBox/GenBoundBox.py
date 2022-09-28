# import modules
import  cadwork   
import  element_controller      as ec
import  attribute_controller    as ac
import  geometry_controller     as gc
import utility_controller       as uc
import visualization_controller as vc


version='GenBoundBox::v8'
debug_mode=True
do_deletes=True

#CHANGES
#a - v8 moves dimensioning to addnuggetnode

#helper funcs
def log(do_it,astr):
    if(do_it):
        print(astr)

 
#MAIN STARTS HERE
#where to store cube layer names
cube_attr = 25 #H_Design Description 1 
cube_dimensions = 26

#default sizes
boundary_size_x = boundary_size_y = boundary_size_z = 200
cutit_adds = 20
copy_z_offset=500

#get address of selected node(s)
els = ec.get_user_element_ids()
log(debug_mode,els)

for el in els:
    x=y=z=0
    log(debug_mode,'processing elementid: ' + str(el))
    #use only nodes with correct cube_attr value
    if(ac.get_user_attribute(el,cube_attr)=='nugget node'):    
        #read node dimensions
        #sizes = uc.get_user_string('[' + version + '] Enter boundary sizes X,Y,Z (mm):')
        sizesStr = ac.get_user_attribute(el,cube_dimensions)
        
        sizes=sizesStr.split(',')
        if(len(sizes)==4):
            boundary_size_x = int(sizes[0])
            boundary_size_y = int(sizes[1])
            boundary_size_z = int(sizes[2])
            copy_z_offset = int(sizes[3])
            
        if(copy_z_offset<100):
            copy_z_offset=100
        log(debug_mode,'copy_z_offset=' + str(copy_z_offset))
        half_x = boundary_size_x/2
        log(debug_mode,'half_x=' + str(half_x))
        half_y = boundary_size_y/2
        log(debug_mode,'half_y=' + str(half_y))
        half_z = boundary_size_z/2
        log(debug_mode,'half_z=' + str(half_z))


        aname=ac.get_name(el)
        log(debug_mode,aname)
        log(debug_mode,'user_' + str(cube_attr) + '=' + ac.get_user_attribute(el,cube_attr))
        verts = gc.get_element_vertices(el)
        for v in verts:
            x=v.x # + uc.get_global_x_offset()
            y=v.y #+ uc.get_global_y_offset()
            z=v.z #+ uc.get_global_z_offset()
            log(debug_mode,'Node ' + str(el) + ': x=' + str(v.x) + ', y=' + str(v.y) + ', z=' + str(v.z))
    
                    

            #get size of inner box in mm (working as of backup 3)
            p1 = cadwork.point_3d(x-half_x,y,z) # origin
            p2 = cadwork.point_3d(x+half_x,y,z) # x offset, keep y+z same as origin
            p3 = cadwork.point_3d(x-half_x,y,z+1) # z offset, keep x offset and y origin
            boundary_id = ec.create_rectangular_beam_points(boundary_size_y,boundary_size_z,p1,p2,p3)
            ac.set_user_attribute([boundary_id],cube_attr,'boundary')
            ac.set_name([boundary_id],'nugget boundary')
            log(debug_mode,'boundary=' + str(boundary_id)+ 'P1.(x,y,z)=' + str(p1.x) + ',' + str(p1.y) + ',' + str(p1.z))
            log(debug_mode,'boundary=' + str(boundary_id)+ 'P2.(x,y,z)=' + str(p2.x) + ',' + str(p2.y) + ',' + str(p2.z))
            log(debug_mode,'boundary=' + str(boundary_id)+ 'P3.(x,y,z)=' + str(p3.x) + ',' + str(p3.y) + ',' + str(p3.z))
            
                        
                        
log(True,'script ' + version + ' done')
uc.print_message('script ' + version + ' done.',2,1)

