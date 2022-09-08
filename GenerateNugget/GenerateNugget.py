# import modules
import  cadwork   
import  element_controller      as ec
import  attribute_controller    as ac
import  geometry_controller     as gc
import utility_controller       as uc
import visualization_controller as vc


version='GenerateNugget::v7R'
debug_mode=False
do_deletes=True

#TODO
#1 -refactor this POC into functions for obtaining boxes, doing copy/cut, and deletes
#2 -determined of UX inputs can have default values displayed ("just press enter")
#3 -validate z-offset of larger than z boundary (or perhaps set to z_size*3 || >5000 by default?)
#4 -convert inputs from inchaes to MM instead of requiring mm

#helper funcs
def log(do_it,astr):
    if(do_it):
        print(astr)

 
#MAIN STARTS HERE
#where to store cube layer names
cube_attr = 25 #H_Design Description 1 

#default sizes
boundary_size_x = boundary_size_y = boundary_size_z = 200
cutit_adds = 20
copy_z_offset=500

#get sizes from user in cwUX
sizes = uc.get_user_string('[' + version + '] Enter boundary sizes X,Y,Z (mm):')
sizes=sizes.split(',')
if(len(sizes)==3):
	boundary_size_x = int(sizes[0])
	boundary_size_y = int(sizes[1])
	boundary_size_z = int(sizes[2])
	
copy_z_offset = uc.get_user_double('Enter Z-axis copy offset (mm):')
if(copy_z_offset<100):
    copy_z_offset=100
log(debug_mode,'copy_z_offset=' + str(copy_z_offset))
half_x = boundary_size_x/2
log(debug_mode,'half_x=' + str(half_x))
half_y = boundary_size_y/2
log(debug_mode,'half_y=' + str(half_y))
half_z = boundary_size_z/2
log(debug_mode,'half_z=' + str(half_z))


#get address of selected node(s)
x=y=z=0
els = ec.get_user_element_ids()
for el in els:
    #use only nodes with correct cube_attr value
    if(ac.get_user_attribute(el,cube_attr)=='nugget node'):    
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
            
            if(True):
                #get size of outer box (working as of backup 4)
                p1b = p1+cadwork.point_3d(-1*cutit_adds,0,0)
                p2b = p2+cadwork.point_3d(cutit_adds,0,0)
                p3b = p3+cadwork.point_3d(cutit_adds,0,1)
                cutit_id = ec.create_rectangular_beam_points(2*cutit_adds+boundary_size_y,2*cutit_adds+boundary_size_z,p1b,p2b,p3b)
                ac.set_user_attribute([cutit_id],cube_attr,'cutit')
                ac.set_name([cutit_id],'nugget cutit')
                log(debug_mode,'cutit=' + str(cutit_id))
                vc.set_color([boundary_id,cutit_id],255)
                vc.set_material([boundary_id,cutit_id],255)
                
                #cut boundary
                the_cut_set = ec.subtract_elements([boundary_id],[cutit_id])
                if(debug_mode):
                        for c in the_cut_set:
                            log(debug_mode,'cutset=' + str(c))

            if(True):
             #check for elements inside boundary
             copy_set = []
             fullset = ec.get_all_identifiable_element_ids()
             for f in fullset:
               if(ec.check_if_elements_are_in_collision(f,boundary_id)):
                  f_added=True
                  copy_set.append(f)
                  log(debug_mode,'collision appended ' + str(f))               


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
                        log(debug_mode,'cut_set: ' + ac.get_name(cs) + '=' + str(cs))

                
                if(True):
                        #remove copy extras if not inside boundary_copy

                        #need an even bigger outside box
                        p1b = p1+cadwork.point_3d(-1*cutit_adds-5,-5,(copy_z_offset + boundary_size_z))
                        p2b = p2+cadwork.point_3d(cutit_adds+5,-5,(copy_z_offset + boundary_size_z))
                        p3b = p3+cadwork.point_3d(cutit_adds+5,-5,1+(copy_z_offset + boundary_size_z))
                        cleanup_id = ec.create_rectangular_beam_points(2*cutit_adds+boundary_size_y+20,2*cutit_adds+boundary_size_z+20,p1b,p2b,p3b)
                        ac.set_user_attribute([cleanup_id],cube_attr,'cleanup nugget')
                        ac.set_name([cleanup_id],'nugget cleanup')
                        log(debug_mode,'cleanup=' + str(cutit_id))
                        vc.set_color([cleanup_id],255)
                        vc.set_material([cleanup_id],255)

                        for e in cut_set: 
                            if(ec.check_if_elements_are_in_collision(e,cleanup_id)):
                                if(not ec.check_if_elements_are_in_collision(e,boundary_copy)):
                                    if(do_deletes and e!=boundary_copy):
                                        ec.delete_elements([e])

                        for e in copy_set2: 
                            if(ec.check_if_elements_are_in_collision(e,cleanup_id)):
                                if(not ec.check_if_elements_are_in_collision(e,boundary_copy)):
                                    if(do_deletes and e!=boundary_copy):
                                        ec.delete_elements([e])

                        #remove original boxes and copied node                
                        if(do_deletes):
                                ec.delete_elements([boundary_copy]) #commented for debug only
                                ec.delete_elements([boundary_id,cutit_id,node_copy])
                                ec.delete_elements([cleanup_id]) #commented for debug only
                        
                # label it
                ec.create_text_object(aname,
                        cadwork.point_3d(x,y,z+copy_z_offset+200+boundary_size_z),
                        cadwork.point_3d(50,0,0),
                        cadwork.point_3d(00,0,50),
                        50)
                        
                        
log(True,'script ' + version + ' done')
uc.print_message('script ' + version + ' done.',2,1)

