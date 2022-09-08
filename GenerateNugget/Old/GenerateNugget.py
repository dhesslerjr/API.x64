# import modules
import  cadwork   
import  element_controller      as ec
import  attribute_controller    as ac
import  geometry_controller     as gc
import utility_controller       as uc
import visualization_controller as vc


version='GenerateNugget::v7m'
debug_mode=True
do_deletes=True


#where to store cube layer names
cube_attr = 25 #H_Design Description 1 
boundary_size_x = boundary_size_y = boundary_size_z = 200
cutit_adds = 20
copy_z_offset=500

sizes = uc.get_user_string('[' + version + '] Enter boundary sizes X,Y,Z (mm):')
sizes=sizes.split(',')
if(len(sizes)==3):
	boundary_size_x = int(sizes[0])
	boundary_size_y = int(sizes[1])
	boundary_size_z = int(sizes[2])

	
copy_z_offset = uc.get_user_double('Enter Z-axis copy offset (mm):')
if(copy_z_offset<100):
    copy_z_offset=100

x=y=z=0
#get address of selected node(s)
els = ec.get_user_element_ids()
for el in els:
    #use only nodes with correct cube_attr value
    if(ac.get_user_attribute(el,cube_attr)=='nugget node'):    
        print(ac.get_name(el))
        if(debug_mode):
                print('user_' + str(cube_attr) + '=' + ac.get_user_attribute(el,cube_attr))
        verts = gc.get_element_vertices(el)
        for v in verts:
            x=v.x + uc.get_global_x_offset();
            y=v.y + uc.get_global_y_offset();
            z=v.z + uc.get_global_z_offset();
            if(debug_mode):
                    print('Node ' + str(el) + ': x=' + str(v.x) + ', y=' + str(v.y) + ', z=' + str(v.z))
    
            half_x = boundary_size_x/2
            half_y = boundary_size_y/2
            half_z = boundary_size_z/2

            #get size of inner box in mm (working as of backup 3)
            p1 = cadwork.point_3d(x-half_x,y,z-half_z) # origin
            p2 = cadwork.point_3d(x+half_x,y,z+half_z*2) # x offset, keep y+z same as origin
            p3 = cadwork.point_3d(x+half_x,y,z+half_z*2) # z offset, keep x offset and y origin
            boundary_id = ec.create_square_beam_points(2*half_y,p1,p2,p3)
            ac.set_user_attribute([boundary_id],cube_attr,'boundary')
            ac.set_name([boundary_id],'nugget boundary')
            if(debug_mode):
                    print('boundary=' + str(boundary_id)+ ' x,y,z=' + str(p1.x) + ',' + str(p1.y) + ',' + str(p1.z))
            
            
            #get size of outer box (working as of backup 4)
            p1b = p1+cadwork.point_3d(-1*cutit_adds,0,0)
            p2b = p2+cadwork.point_3d(cutit_adds,0,0)
            p3b = p3+cadwork.point_3d(cutit_adds,0,cutit_adds*2+boundary_size_z*2)
            cutit_id = ec.create_square_beam_points(2*cutit_adds+boundary_size_y,p1b,p2b,p3b)
            ac.set_user_attribute([cutit_id],cube_attr,'cutit')
            ac.set_name([cutit_id],'nugget cutit')
            if(debug_mode):
                    print('cutit=' + str(cutit_id))
            vc.set_color([boundary_id,cutit_id],255)
            vc.set_material([boundary_id,cutit_id],255)
            
            #cut boundary
            the_cut_set = ec.subtract_elements([boundary_id],[cutit_id])
            if(debug_mode):
                    for c in the_cut_set:
                        print('cutset=' + str(c))

            if(True):
             #check for elements inside boundary
             copy_set = []
             fullset = ec.get_all_identifiable_element_ids()
             for f in fullset:
               verts = gc.get_element_vertices(f)
               f_added=False
               for v in verts:      
                    if(ec.check_if_point_is_in_element(v,boundary_id)):
                            if(not f_added):
                              f_added=True
                              copy_set.append(f)
                              if(debug_mode):
                                print('collision appended ' + str(f))
                    #else:
                            #if(debug_mode):
                                    #print('no contact ' +str(f))


            boundary_copy=None
            cutit_copy=None
            node_cop=None
            if(len(copy_set)):
                copy_set.append(boundary_id)
                copy_set.append(cutit_id)
                pc = cadwork.point_3d(0,0,copy_z_offset + boundary_size_z)
                copy_set2 = ec.copy_elements(copy_set,pc)
                for c in copy_set2:
                        new_name=ac.get_user_attribute(c,cube_attr) + ' copy'
                        ac.set_user_attribute([c],cube_attr,new_name)
                        if(new_name=='nugget node copy'):
                                node_copy=c
                        if(new_name=='boundary copy'):
                                boundary_copy=c
                        if(new_name=='cutit copy'):
                                cutit_copy=c

                #do the cut
                cut_set = ec.subtract_elements([cutit_copy],copy_set2)
                for cs in cut_set:
                        new_name=ac.get_user_attribute(cs,cube_attr) + ' cut_set' #for debugging only
                        ac.set_user_attribute([cs],cube_attr,new_name)                        
                        if(debug_mode):
                                print('cut_set: ' + ac.get_name(cs) + '=' + str(cs))
                # label it
                ec.create_text_object(ac.get_name(node_copy),
                        cadwork.point_3d(x,y,z+copy_z_offset+1.5*boundary_size_z),
                        cadwork.point_3d(50,0,0),
                        cadwork.point_3d(00,0,50),
                        75)
                if(do_deletes):
                        #remove copy extras if not inside boundary_copy

                        #need an even bigger outside box
                        p1b = p1+cadwork.point_3d(-1*cutit_adds-5,-5,(copy_z_offset + boundary_size_z))
                        p2b = p2+cadwork.point_3d(cutit_adds+5,-5,(copy_z_offset + boundary_size_z))
                        p3b = p3+cadwork.point_3d(cutit_adds+5,-5,cutit_adds*2+boundary_size_z+10+(copy_z_offset + boundary_size_z*2))
                        cleanup_id = ec.create_square_beam_points(2*cutit_adds+boundary_size_y+20,p1b,p2b,p3b)
                        ac.set_user_attribute([cleanup_id],cube_attr,'cleanup nugget')
                        ac.set_name([cleanup_id],'nugget cleanup')
                        if(debug_mode):
                                print('cleanup=' + str(cutit_id))
                        vc.set_color([cleanup_id],255)
                        vc.set_material([cleanup_id],255)

                        for e in cut_set: 
                            if(ec.check_if_elements_are_in_collision(e,cleanup_id)):
                                if(not ec.check_if_elements_are_in_collision(e,boundary_copy)):
                                    if(e!=boundary_copy):
                                        ec.delete_elements([e])

                        for e in copy_set2: 
                            if(ec.check_if_elements_are_in_collision(e,cleanup_id)):
                                if(not ec.check_if_elements_are_in_collision(e,boundary_copy)):
                                    if(e!=boundary_copy):
                                        ec.delete_elements([e])

                        #remove original boxes and copied node
                        #ec.delete_elements([boundary_copy]) #commented for debug only
                        ec.delete_elements([boundary_id,cutit_id,node_copy,cleanup_id])
                        
                        
print('script ' + version + ' done')
uc.print_message('script ' + version + ' done.',2,1)

