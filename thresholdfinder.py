import os
import re
import random
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import yaml
import io 

# here's something that I want to be extra careful about:
# simulation instances that, although they exist, their image does not
# I want to make absolutely sure that upon trying to load an image for an instance, if
# that image is not found, we put a -2 in that instances entry in its' combo's list
# and reevaluate the threshold window thing thingamajig you get it 

class ImageReviewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Threshold Finder")

        tk.Label(root, text="Select experiment:").grid(row=0, column=0, sticky="w", padx=5)
        self.experiment_name = tk.StringVar()
        ttk.Combobox(root, textvariable=self.experiment_name, values=["testexp1", "testexp2"], width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(root, text="Go", command=self.get_experiment).grid(row=0, column=2, padx=5, pady=5)

        # first the frame for the combo id nav stuff. 

        self.combo_main_frame = tk.Frame(root)
        
        tk.Button(self.combo_main_frame, text="⟨ Previous ID", command=self.previous_combo_id).grid(row=0, column=0, padx=10)
    
        self.crt_combo_index_label = tk.Label(self.combo_main_frame, text="Combo index: N/A")
        self.crt_combo_index_label.grid(row=0,column=1)
    
        tk.Button(self.combo_main_frame, text="Next ID ⟩", command=self.next_combo_id).grid(row=0, column=2, padx=10)
    
        self.combo_verdict_label = tk.Label(self.combo_main_frame, text="Threshold discovered: N/A")
        self.combo_verdict_label.grid(row = 1, column = 0, columnspan=3)
        self.combo_verdict_label.config(bg="gray")

        self.instance_frame = tk.Frame(root)
#        self.instance_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.image_frame = tk.Frame(self.instance_frame)  
        self.image_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.instance_index_frame = tk.Frame(self.instance_frame)
        #self.instance_index_frame.grid(row=1,column=0, columnspan=7, padx=5, pady=5)

        self.two_before_crt_instance_label = tk.Label(self.instance_index_frame, text="N/A")
        self.two_before_crt_instance_label.grid(row=0,column=0)
        
        self.one_before_crt_instance_label = tk.Label(self.instance_index_frame, text="N/A")
        self.one_before_crt_instance_label.grid(row=0,column=1)

        tk.Button(self.instance_index_frame, text="⟨ Prev", command=self.previous_instance).grid(row=0, column=2, padx=10)

        self.crt_instance_label = tk.Label(self.instance_index_frame, text="N/A")
        self.crt_instance_label.grid(row=0,column=3)

        tk.Button(self.instance_index_frame, text="Next ⟩", command=self.next_instance).grid(row=0, column=4, padx=10)

        self.one_after_crt_instance_label = tk.Label(self.instance_index_frame, text="N/A")
        self.one_after_crt_instance_label.grid(row=0,column=5)

        self.two_after_crt_instance_label = tk.Label(self.instance_index_frame, text="N/A")
        self.two_after_crt_instance_label.grid(row=0,column=6)

        self.indices_labels = [self.two_before_crt_instance_label, self.one_before_crt_instance_label, self.crt_instance_label, self.one_after_crt_instance_label, self.two_after_crt_instance_label]

        #self.instance_label = tk.Label(instance_frame, text = "Instance index: N/A")
        #self.instance_label.grid(row=1,column=0,columnspan=3,padx=5,pady=5)

        tk.Button(self.instance_frame, text="👍 Normal", command=self.like_current_instance).grid(row=2, column=0, padx=10)
        
        self.instance_verdict_label = tk.Label(self.instance_frame, text="Verdict: N/A")
        self.instance_verdict_label.grid(row=2,column=1,padx=5,pady=5)
        
        tk.Button(self.instance_frame, text ="👎 Leak", command=self.dislike_current_instance).grid(row=2,column=2,padx=10)
        
        self.hide_selected_experiment_frames()

        self.SLIDING_WINDOW_SIZE = 7
        self.MINIMUM_DISLIKES_FOR_DECIDED = 4 

        self.image_label = None         

        self.instance_data_loaded = False 

        self.exp_names_to_csv_paths = {"testexp1":"\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images-df.csv", "testexp2":"\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images-df.csv"}        
        self.df = None
        self.full_csv_path = None 
        self.img_dir_path = None 
        self.full_yaml_path = None
        self.combo_id_list = None 
        self.combo_id_to_instance_info_list = None
        self.combo_id_to_instance_state_list = None      
        self.combo_id_to_last_seen_index = None 

        self.current_combo_index = None # index for 'where we're at' in the self.combo_id_list var 
        self.current_instance_index = None # index for 'where we're at' in the instance list for the current combo id. gets calculated each time a switch to a new combo id takes place, i.e, is not stored

        self.current_instance_info_list = None
        self.current_instance_verdict_list = None 

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def browse_id_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.idfile_var.set(file)

    def hide_selected_experiment_frames(self):
        self.combo_main_frame.grid_forget()
        self.instance_frame.grid_forget()
        self.instance_index_frame.grid_forget()

    def show_selected_experiment_frames(self):
        self.combo_main_frame.grid(row=2, column=0, columnspan=10, padx=5, pady=5)
        self.instance_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self.instance_index_frame.grid(row=1,column=0, columnspan=7, padx=5, pady=5)
 
    def change_combo_id_by(self,d):
        # but first, let me update the main dict 
        # c_id = self.get_current_combid()

        # print("yeah it goes through here")
        # self.combo_id_to_instance_state_list[id] = self.current_instance_verdict_list

        n_ids = len(self.combo_id_list)
        self.current_combo_index = ( self.current_combo_index + d ) % n_ids
        self.load_current_combo_id()

    def next_combo_id(self):
        if self.instance_data_loaded:
            self.change_combo_id_by(1)

    def previous_combo_id(self):
        if self.instance_data_loaded:
            self.change_combo_id_by(-1)

    def change_instance_by(self, d):
        n_insts = len(self.current_instance_verdict_list)

        self.current_instance_index = ( self.current_instance_index + d ) % n_insts

        self.update_last_seen_instance()

        self.load_current_instance()

    def update_last_seen_instance(self):
        self.combo_id_to_last_seen_index[self.get_current_combid()] = self.current_instance_index

    def next_instance(self):
        if self.instance_data_loaded:
            self.change_instance_by(1)            

    def previous_instance(self):
        if self.instance_data_loaded:
            self.change_instance_by(-1)
        
    def get_current_combid(self):
        return self.combo_id_list[self.current_combo_index]

    def deposit_crt_comboid_state_and_info_lists_into_vars(self):
        c_id = self.get_current_combid()

        self.current_instance_info_list = self.combo_id_to_instance_info_list[c_id]
        self.current_instance_verdict_list = self.combo_id_to_instance_state_list[c_id]
    
    def update_instance_labels(self): # checked 
        idx_labels = self.indices_labels

        crt_inst_idx = self.current_instance_index
        inst_n = len(self.current_instance_verdict_list)

        for tmp_lbl_idx, inst_idx_delta in enumerate(range(-2,3)):
            tmp_inst_idx = (crt_inst_idx + inst_idx_delta) % inst_n

            idx_labels[tmp_lbl_idx].config(text=str(tmp_inst_idx))            

    def update_instance_verdict_label(self):        

        if self.current_instance_verdict_list[self.current_instance_index] == 0:
            v = "Leak"
            self.instance_verdict_label.config(bg="red")
        elif self.current_instance_verdict_list[self.current_instance_index] == 1:
            v = "Normal"
            self.instance_verdict_label.config(bg="green")
        else:
            v = "N/A"
            self.instance_verdict_label.config(bg="gray")

        self.instance_verdict_label.config(text="Verdict: " + v)

    def load_current_instance(self): # if combo id and instance id are taken care of ( and they are, see Notion table ), this is fine, too 
        
        self.update_instance_labels()

        self.update_instance_verdict_label()

        self.show_image_for_cid_and_instid(self.get_current_combid(), self.current_instance_index)

    def load_current_combo_id(self): # checked              

        if self.current_combo_index != None:
            self.crt_combo_index_label.config(text=f"Combo index: {self.current_combo_index}") # fair  

            self.deposit_crt_comboid_state_and_info_lists_into_vars() # so far so good 
            
            self.detect_crt_decision_state_and_show() # decision establishing has all been thoroughly checked ( see Notion table )

            c_id = self.get_current_combid() # this is ofc all good 

            self.current_instance_index = self.combo_id_to_last_seen_index[c_id] # this should be fine 

            self.load_current_instance() # all good 

        # here will be a bit of code that gets the current decision value and shows it in a label
        # the idea would be to stop keeping random things in the object state because I think I
        # may end up relying on these variables in the wrong way, and, having constant access to them 
        # from whichever method, I might end up introducing ways to change said variables that are logically inconsistent 

    #def img_file_name_to_img_path(self, img_name):
    #    sub_dir_name = img_name[:img_name.find('-')] 
    #    return self.img_dir_path + "\\" + sub_dir_name + "\\" + img_name 

    def show_image_for_cid_and_instid(self, c_id, inst_id): # checked 
        if self.image_label != None:         
            self.image_label.destroy()
            self.image_label = None 
        # the above, all good 

        img_name = self.combo_id_to_instance_info_list[c_id][inst_id][0]
        # all good 

        img_path = self.img_dir_path + "\\" + img_name
        # all good 

        try: # the try block is all good 
            img = Image.open(img_path)
            img.thumbnail((400, 400))
            tk_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.image_frame, image=tk_img)
            lbl.image = tk_img
            lbl.grid(row=0, column=0, padx=5, pady=5)
            self.image_label = lbl
        except Exception as e: # the exception block is all good 
            lbl = tk.Label(self.image_frame, text = "Failed to load image at path: " + img_path )
            lbl.grid(row=0,column=0,sticky="w", padx=5)  
            self.image_label = lbl # added this later, I'd ommitted it and the no. of stored labels increased by one on each method run 

    def detect_crt_decision_state_and_show(self):
        crt_dec_state = self.detect_crt_combo_id_decision_state()

        if crt_dec_state:
            self.combo_verdict_label.config(text="Threshold discovered: Yes")
            self.combo_verdict_label.config(bg="green")
        else:
            self.combo_verdict_label.config(text="Threshold discovered: No")
            self.combo_verdict_label.config(bg="gray")


    def detect_crt_combo_id_decision_state(self): # checked  
        inst_n = len(self.current_instance_verdict_list)

        current_combo_decided = False 

        for window_starting_idx in range(inst_n - self.SLIDING_WINDOW_SIZE + 1): # range is correct 
            tmp_sublist = self.current_instance_verdict_list[window_starting_idx : (window_starting_idx + self.SLIDING_WINDOW_SIZE) ] # correct sub-selection

            dislikes_count = 0 
            for inst_state in tmp_sublist:
                if inst_state == 0:
                    dislikes_count += 1

            if dislikes_count >= self.MINIMUM_DISLIKES_FOR_DECIDED:
                current_combo_decided = True 
                break  

        return current_combo_decided

    def set_current_instance_state_to_value_and_refresh_decision(self, in_val):
        self.current_instance_verdict_list[self.current_instance_index] = in_val 
        self.detect_crt_decision_state_and_show()
        self.update_instance_verdict_label()
        
    def like_current_instance(self):
        if self.instance_data_loaded:
            self.set_current_instance_state_to_value_and_refresh_decision(1)            

    def dislike_current_instance(self):
        if self.instance_data_loaded:
            self.set_current_instance_state_to_value_and_refresh_decision(0)
            
    def convert_df_to_objects(self): # assuming a certain .csv(/df respectively) structure, this is correctly implemented.
        # it's not flexible by any means, but if your csv contains combo-id, filename, stripe-thresh=cov-zero columns, this works
        # it also does not really account for whatever special/ wrong things could happen with values in these columns
        # but I'll worry about that shortly. meaning now. 

        self.combo_id_list = []
        self.combo_id_to_instance_info_list = dict()
        self.combo_id_to_instance_state_list = dict()
        self.combo_id_to_last_seen_index = dict()        

        self.df = pd.read_csv(self.full_csv_path)
        combo_id_groups = [ x for _, x in self.df.groupby(["combo-id"]) ]

        for combo_id_subdf in combo_id_groups:
            tmp_combo_id = int(combo_id_subdf.iloc[0]["combo-id"]) # ok
            
            self.combo_id_list.append(tmp_combo_id) # sure 

            sorted_subdf = combo_id_subdf.sort_values(["stripe-thresh-cov-zero"]) # great 

            tmp_sorted_instance_list = sorted_subdf[["file-name", "stripe-thresh-cov-zero"]].values.tolist() # this has been checked previously 

            self.combo_id_to_instance_info_list[tmp_combo_id] = tmp_sorted_instance_list # all good 

            self.combo_id_to_instance_state_list[tmp_combo_id] = [-1 for _ in range(len(tmp_sorted_instance_list))] # makes sense

            self.combo_id_to_last_seen_index[tmp_combo_id] = 0 # makes sense 

        self.combo_id_list.sort() # all good 

        self.instance_data_loaded = True
 
    def save_to_yaml_file(self):

        with io.open(self.full_yaml_path, "w", encoding="utf8") as outfile: # io.open with "w" overwrites/rewrites the file if it already exists. 
            try:
                save_list = [self.combo_id_list, self.combo_id_to_instance_info_list , self.combo_id_to_instance_state_list, self.combo_id_to_last_seen_index ]                                 

                yaml.safe_dump(save_list, outfile, allow_unicode=True)
            except yaml.YAMLError as exc:
                print(exc)

    def load_from_yaml_file(self):
        with open(self.full_yaml_path) as stream:
            try:
                loaded_list = yaml.safe_load(stream)

                self.combo_id_list = loaded_list[0]
                self.combo_id_to_instance_info_list = loaded_list[1]
                self.combo_id_to_instance_state_list = loaded_list[2]
                self.combo_id_to_last_seen_index = loaded_list[3]
            
                self.instance_data_loaded = True 

            except yaml.YAMLError as exc:
                print(exc)

    def get_experiment(self):
        exp_name_label_contents = self.experiment_name.get() # solid 

        if ( exp_name_label_contents != None) and (len(exp_name_label_contents) > 0): # makes sense 
            
            self.full_csv_path = self.exp_names_to_csv_paths[exp_name_label_contents] # all good 
            
            self.img_dir_path = self.full_csv_path[:self.full_csv_path.rfind('\\')] # all good 
            
            self.full_yaml_path = self.full_csv_path[:self.full_csv_path.rfind('.')] + ".yaml" # all good  

            if os.path.exists(self.full_yaml_path):
                self.load_from_yaml_file()
            else:
                self.convert_df_to_objects()
            
            self.current_combo_index = 0 # solid 

            self.show_selected_experiment_frames() # all good 

            self.load_current_combo_id() # all good, this one I know for sure I've checked well enough. 
            

        # cool, at this point either the yaml will have been loaded, or the df will have been loaded,
        # but either way we have our combos and their respective instances represented somehow 
        # and of course we have our df in self.df 

        # so I guess the next lil question is 
        # what sort of state are we going to find ourselves in when we are looking at an image 
        # well, seems we forgot to sort the GOD DAMN dataframe according to the leak values
        # so let's go back to when we were initially reading the df and do that shall we yes we FUCKING shall
        # but that actually brings about a problem that honestly I don't give much of a shit about no I actually do 
        # if we sort the instances for each combo id according to the leak metric value
        # that totally fucks up what we were trying to do with the skipped instances
        # because there's no notion of skip that makes sense anymore, at least not easily 


    def on_close(self):
        if self.full_yaml_path != None:
            self.save_to_yaml_file()
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageReviewerApp(root)
    root.mainloop()
