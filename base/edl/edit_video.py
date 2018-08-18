import nuke,sys,os
def create_video():
    t_source_path=sys.argv[1]
    t_des_path=sys.argv[2]
    t_fomant=sys.argv[3]
    t_start_frame=sys.argv[4][6:]
    t_end_frame=sys.argv[5][4:]
    t_frame=sys.argv[6][4:]
    # create node
    t_read_node=nuke.createNode("Read")
    T_write_node=nuke.createNode("Write")
    # set read node
    t_read_node["file"].setValue(t_source_path)
    t_read_node["first"].setValue(int(t_start_frame))
    t_read_node["last"].setValue(int(t_end_frame))
    source_code=t_read_node.metadata()["quicktime/codec_id"]
    #-------
    if not t_fomant in [".jpg",".png",".dpx",".exr",".tiff"]:
        if not os.path.exists(os.path.dirname(t_des_path)):
            os.makedirs(os.path.dirname(t_des_path))
        T_write_node["file"].setValue(t_des_path)
        T_write_node["file_type"].setValue("mov")
        T_write_node["meta_encoder"].setValue("mov32")
        T_write_node["mov32_fps"].setValue(int(t_frame))
        T_write_node["meta_codec"].setValue(source_code)
        nuke.execute(T_write_node,int(t_start_frame),int(t_end_frame))
    else:
        if not os.path.exists(t_des_path):
            os.makedirs(t_des_path)
        t_file=t_des_path+"/"+os.path.splitext(os.path.basename(t_source_path))[0]+".%04d"+t_fomant
        T_write_node["file"].setValue(t_file)
        nuke.execute(T_write_node,int(t_start_frame),int(t_end_frame))
if __name__=="__main__":
    create_video()
