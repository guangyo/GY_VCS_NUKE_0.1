import nuke,sys,os
def create_jpg():
    t_source_path=sys.argv[1]
    t_start_frame=sys.argv[2][6:]
    t_end_frame=sys.argv[3][4:]

    t_read_node=nuke.createNode("Read")
    t_read_node["file"].setValue(t_source_path)
    t_read_node["first"].setValue(int(t_start_frame))
    t_read_node["last"].setValue(int(t_end_frame))

    T_write_node=nuke.createNode("Write")
    t_temp_path=unicode(os.environ["TMP"]+"/"+"cgteamwork_temp/edl").replace("\\","/")
    base_t_des_path=t_temp_path+"/"+os.path.splitext(os.path.basename(t_source_path))[0]+".%04d.jpg"
    T_write_node["file"].setValue(base_t_des_path)
    try:
        nuke.execute(T_write_node,int(t_start_frame)+1,int(t_start_frame)+1) 
        nuke.execute(T_write_node,int(t_end_frame),int(t_end_frame))
    except:
        pass
if __name__=="__main__":
    create_jpg()
