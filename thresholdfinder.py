import os
import re
import random
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import yaml

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
        ttk.Combobox(root, textvariable=self.experiment_name, values=["testexp1", "testexp2"], width=60).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(root, text="Go", command=self.get_experiment).grid(row=0, column=2, padx=5, pady=5)

        # I've got an idea for how to incorporate the 
        # current combo id label more fluidly from a visual standpoint.
        
        # self.crt_combo_index_label = tk.Label(root, text="Combo index: N/A")
        # self.crt_combo_index_label.grid(row=1, column=0, sticky="w", padx=5)

        # first the frame for the combo id nav stuff. 

        combo_main_frame = tk.Frame(root)
        combo_main_frame.grid(row=2, column=0, columnspan=10, padx=5, pady=5)

        tk.Button(combo_main_frame, text="⟨ Previous ID", command=self.previous_combo_id).grid(row=0, column=0, padx=10)
    
        self.crt_combo_index_label = tk.Label(combo_main_frame, text="Combo index: N/A")
        self.crt_combo_index_label.grid(row=0,column=1)
    
        tk.Button(combo_main_frame, text="Next ID ⟩", command=self.next_combo_id).grid(row=0, column=2, padx=10)
    
        self.combo_verdict_label = tk.Label(combo_main_frame, text="Threshold discovered: N/A")
        self.combo_verdict_label.grid(row = 1, column = 0, columnspan=3)
        self.combo_verdict_label.config(bg="gray")

        instance_frame = tk.Frame(root)
        instance_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.image_frame = tk.Frame(instance_frame)  
        self.image_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.instance_label = tk.Label(instance_frame, text = "Instance index: N/A")
        self.instance_label.grid(row=1,column=0,columnspan=3,padx=5,pady=5)

        tk.Button(instance_frame, text="👍 Like", command=self.like_current_instance).grid(row=2, column=0, padx=10)
        
        self.instance_verdict = tk.Label(instance_frame, text="Verdict: N/A")
        self.instance_verdict.grid(row=2,column=1,padx=5,pady=5)
        
        tk.Button(instance_frame, text ="👎 Dislike", command=self.dislike_current_instance).grid(row=2,column=2,padx=10)
        
        tk.Button(instance_frame, text="⟨ Previous instance", command=self.previous_instance).grid(row=3, column=0, padx=10)
        tk.Button(instance_frame, text="Next instance ⟩", command=self.next_instance).grid(row=3, column=2, padx=10)
    
        tk.Button(root, text = "Save", command=self.save).grid(row=4, column=0, padx=10)
        tk.Button(root, text="Load", command=self.load).grid(row=4,column=1,padx=0)

        # # -------- UI: Image folder input --------
        # tk.Label(root, text="Image Folder:").grid(row=0, column=0, sticky="w", padx=5)
        # self.path_var = tk.StringVar()
        # tk.Entry(root, textvariable=self.path_var, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # tk.Button(root, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # # -------- UI: ID text file input --------
        # tk.Label(root, text="ID List File:").grid(row=1, column=0, sticky="w", padx=5)
        # self.idfile_var = tk.StringVar()
        # tk.Entry(root, textvariable=self.idfile_var, width=60).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        # tk.Button(root, text="Browse", command=self.browse_id_file).grid(row=1, column=2, padx=5, pady=5)

        # # -------- Load button --------
        # tk.Button(root, text="Load Images", command=self.load_images).grid(row=2, column=0, columnspan=3, pady=10)

        # # -------- Labels --------
        # self.current_id_label = tk.Label(root, text="Current ID: N/A", font=("Arial", 12, "bold"))
        # self.current_id_label.grid(row=3, column=0, columnspan=3, pady=(0, 10))

        # self.verdict_label = tk.Label(root, text="Verdict: N/A", font=("Arial", 10))
        # self.verdict_label.grid(row=4, column=0, columnspan=3)

        # # -------- Navigation + like/dislike --------
        # nav_frame = tk.Frame(root)
        # nav_frame.grid(row=5, column=0, columnspan=3, pady=10)

        # tk.Button(nav_frame, text="⟨ Previous ID", command=self.previous_id).grid(row=0, column=0, padx=10)
        # tk.Button(nav_frame, text="👍 Like", command=lambda: self.set_verdict(1)).grid(row=0, column=1, padx=10)
        # tk.Button(nav_frame, text="👎 Dislike", command=lambda: self.set_verdict(0)).grid(row=0, column=2, padx=10)
        # tk.Button(nav_frame, text="Next ID ⟩", command=self.next_id).grid(row=0, column=3, padx=10)

        # # -------- Image display area --------
        # self.image_frame = tk.Frame(root)
        # self.image_frame.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.SLIDING_WINDOW_SIZE = 7
        self.MINIMUM_DISLIKES_FOR_DECIDED = 4 

        # deposit_crt_comboid_state_and_info_lists_intO_vars

        self.exp_names_to_csv_paths = {"testexp1":"\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images.csv", "testexp2":"\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images.csv"}        
        self.df = None
        self.full_csv_path = None 
        self.img_dir_path = None 
        self.full_yaml_path = None
        self.max_instance_count = None
        self.combo_id_list = None 
        self.combo_id_to_instance_info_list = None
        self.combo_id_to_instance_state_list = None          

        self.current_combo_index = None # index for 'where we're at' in the self.combo_id_list var 
        self.current_instance_index = None # index for 'where we're at' in the instance list for the current combo id. gets calculated each time a switch to a new combo id takes place, i.e, is not stored
        # self.current_combo_decided # boolean that specifies whether the criterion has been met for the current combo id having been decided upon. also gets calculated anew each time a combo id is loaded 
        # upon further reflection perhaps this shouldn't be an object variable 

        self.current_instance_info_list = None
        self.current_instance_verdict_list = None 

        # Internal state
        self.folder_path = None
        self.identifier_dict = {}
        self.verdict_list = []
        self.image_label = None 
        self.target_ids = []
        self.current_index = None
        self.verdict_file = ""
        self.max_identifier_found = 0


    # ------------------- UI -------------------
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def browse_id_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.idfile_var.set(file)

    # ------------------- Core logic -------------------

    def change_combo_id_by(self,d):
        n_ids = len(self.combo_id_list)
        self.current_combo_index = ( self.current_combo_index + d ) % n_ids
        self.load_current_combo_id()

    def next_combo_id(self):
        self.change_combo_id_by(1)

    def previous_combo_id(self):
        self.change_combo_id_by(-1)

    def change_instance_by(self, d):
        n_insts = len(self.current_instance_verdict_list)

        self.current_instance_index = ( self.current_instance_index + d ) % n_insts

        self.show_image_for_cid_and_instid(self.get_current_combid(), self.current_instance_index)

    def next_instance(self):
        self.change_instance_by(1)

    def previous_instance(self):
        self.change_instance_by(-1)
        
    def get_current_combid(self):
        return self.combo_id_list[self.current_combo_index]

    def deposit_crt_comboid_state_and_info_lists_into_vars(self):
        c_id = self.get_current_combid()

        self.current_instance_info_list = self.combo_id_to_instance_info_list[c_id]
        self.current_instance_verdict_list = self.combo_id_to_instance_state_list[c_id]
    
    def find_undecided_instance_index_in_current_state_list(self, st_idx):          
        inst_n = len(self.current_instance_verdict_list)

        try: 
            und_idx = next( idx for idx in range(st_idx, inst_n) if self.current_instance_verdict_list[idx] == -1 )
        except:
            und_idx = inst_n - 1

        return und_idx

    def load_current_combo_id(self):
                
        if self.current_combo_index != None:
            self.crt_combo_index_label.config(text=f"Combo index: {self.current_combo_index}")

        self.deposit_crt_comboid_state_and_info_lists_into_vars()

        c_id = self.get_current_combid()
                    
        self.current_instance_index = self.find_undecided_instance_index_in_current_state_list(0)

        self.show_image_for_cid_and_instid(c_id, self.current_instance_index)



        # here will be a bit of code that gets the current decision value and shows it in a label
        # the idea would be to stop keeping random things in the object state because I think I
        # may end up relying on these variables in the wrong way, and, having constant access to them 
        # from whichever method, I might end up introducing ways to change said variables that are logically inconsistent 

    def img_file_name_to_img_path(self, img_name):

        sub_dir_name = img_name[:img_name.find('-')] 

        return self.img_dir_path + "\\" + sub_dir_name + "\\" + img_name 

    def show_image_for_cid_and_instid(self, c_id, inst_id):  
        if self.image_label != None:         
            self.image_label.destroy()
            self.image_label = None 
        
        img_name = self.combo_id_to_instance_info_list[c_id][inst_id][0]
        img_path = self.img_file_name_to_img_path(img_name)

        try:
            img = Image.open(img_path)
            img.thumbnail((400, 400))
            tk_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.image_frame, image=tk_img)
            lbl.image = tk_img
            lbl.grid(row=0, column=0, padx=5, pady=5)
            self.image_label = lbl
        except Exception as e:
            lbl = tk.Label(self.image_frame, text = "Failed to load image at path: " + img_path )
            lbl.grid(row=0,column=0,sticky="w", padx=5)                    

    # propune-ti, dar nu forta <3 

    # doing the right thing at the right time gives you the right to live <3 

    def detect_crt_combo_id_decision_state(self):    
        inst_n = len(self.current_instance_verdict_list)

        current_combo_decided = False 

        for window_starting_idx in range(inst_n - self.SLIDING_WINDOW_SIZE + 1):
            tmp_sublist = self.current_instance_verdict_list[window_starting_idx : (window_starting_idx + self.SLIDING_WINDOW_SIZE) ]

            dislikes_count = 0 
            for inst_state in tmp_sublist:
                if inst_state == 0:
                    dislikes_count += 1

            if dislikes_count >= self.MINIMUM_DISLIKES_FOR_DECIDED:
                current_combo_decided = True 
                break  

        return current_combo_decided


    def set_current_instance_state_to_value(self, in_val):
        self.current_instance_verdict_list[self.current_instance_index] = in_val 

    def like_current_instance(self):
        self.set_current_instance_state_to_value(1)


        # but we both know that liking is not the only thing that needs to happen
        # we need to be reevaluating the state list, also 
        # and honestly idgaf whether or not it's computationally efficient


    def dislike_current_instance(self):
        self.set_current_instance_state_to_value(0)
    
    def convert_df_to_objects(self):
        self.df = pd.read_csv(self.full_csv_path)

        self.max_instance_count = 0 
        self.combo_id_list = []

        combo_id_groups = [ x for _, x in self.df.groupby(["combo-id"]) ]
        for combo_id_subdf in combo_id_groups:
            tmp_combo_id = int(combo_id_subdf.iloc[0]["combo-id"])
            self.combo_id_list.append(tmp_combo_id)

            tmp_count = len(combo_id_subdf)
            if tmp_count > self.max_instance_count:
                self.max_instance_count = tmp_count

        self.combo_id_list.sort()
        
        self.combo_id_to_instance_info_list = dict()
        self.combo_id_to_instance_state_list = dict()
        
        for combo_id_subdf in combo_id_groups:
            tmp_combo_id = int(combo_id_subdf.iloc[0]["combo-id"])
            
            sorted_subdf = combo_id_subdf.sort_values(["stripe-thresh-cov-zero"])

            tmp_sorted_instance_list = sorted_subdf[["file-name", "stripe-thresh-cov-zero"]].values.tolist()

            self.combo_id_to_instance_info_list[tmp_combo_id] = tmp_sorted_instance_list

            self.combo_id_to_instance_state_list[tmp_combo_id] = [-1 for _ in range(len(self.combo_id_to_instance_info_list[tmp_combo_id]))] 



        # ok, the first thing I'm interested in: list of combo-ids,
        # and then a dict linking each combo id to a list of digits representing the state of each instance
        # -2 = skipped, -1 undecided, 0 disliked, 1 liked
        # and yeah I'd rather have -2 as skipped, allowing me to have all instance state lists the same ( maximal ) length
 
        # but that does mean that I basically have to do a semi-redundant groupby combo-id followed by a count
        # just to get, before I even start on the dict, what the maximum number of instances for any one 
        # combo-id 

    def save(self):
        with open(self.full_yaml_path) as stream:
            try:
                yaml.safe_dump(save_list,stream)

                save_list = [self.max_instance_count, self.combo_id_list, self.combo_id_to_instance_info_list , self.combo_id_to_instance_state_list ]                                 
            except yaml.YAMLError as exc:
                print(exc)


    def convert_yaml_to_objects(self):
        with open(self.full_yaml_path) as stream:
            try:
                save_list = [self.max_instance_count, self.combo_id_list, self.combo_id_to_instance_info_list , self.combo_id_to_instance_state_list ] 
                yaml.safe_dump(save_list,stream)                
            except yaml.YAMLError as exc:
                print(exc)

    def get_experiment(self):
        self.full_csv_path = self.exp_names_to_csv_paths[self.experiment_name.get()]
        
        self.img_dir_path = self.full_csv_path[:self.full_csv_path.rfind('\\')]
        
        self.full_yaml_path = self.full_csv_path[:self.full_csv_path.rfind('.')] + ".yaml" 

        #if os.path.exists(self.full_yaml_path):
        #    self.convert_yaml_to_objects()
        #else:
        
        self.convert_df_to_objects()
        
        self.current_combo_index = 0

        self.load_current_combo_id()

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

        

    def load_images(self):
        self.folder_path = self.path_var.get().strip()
        idfile_path = self.idfile_var.get().strip()

        if not os.path.isdir(self.folder_path):
            messagebox.showerror("Error", "Invalid image directory.")
            return
        if not os.path.isfile(idfile_path):
            messagebox.showerror("Error", "Invalid ID list file.")
            return

        # Read target IDs from text file
        try:
            with open(idfile_path, "r") as f:
                self.target_ids = [int(line.strip()) for line in f if line.strip().isdigit()]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read ID list file:\n{e}")
            return

        if not self.target_ids:
            messagebox.showerror("Error", "No valid IDs found in the text file.")
            return

        # Collect all valid PNGs
        pattern = re.compile(r"^(\d+)-\d+\.png$")
        self.identifier_dict.clear()
        all_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(".png")]
        identifiers_found = set()

        for filename in all_files:
            match = pattern.match(filename)
            if match:
                identifier = int(match.group(1))
                identifiers_found.add(identifier)
                self.identifier_dict.setdefault(identifier, []).append(os.path.join(self.folder_path, filename))

        if not identifiers_found:
            messagebox.showerror("Error", "No valid filenames found in folder.")
            return

        self.max_identifier_found = max(identifiers_found)
        self.verdict_list = [-2] * (self.max_identifier_found + 1)
        for i in self.target_ids:
            if i in identifiers_found:
                self.verdict_list[i] = -1  # unreviewed

        self.set_verdicts_file_path()

        self.load_verdicts()

        first_valid_index = next((idx for idx, i in enumerate(self.target_ids) if i in identifiers_found), None)
        if first_valid_index is not None:
            self.current_index = first_valid_index
            self.display_current_id()
        else:
            messagebox.showinfo("Info", "None of the target IDs were found in the folder.")

    # ------------------- Display -------------------
    def display_current_id(self):
        if self.current_index is None:
            return
        current_id = self.target_ids[self.current_index]
        self.current_id_label.config(text=f"Current ID: {current_id}")
        verdict = self.verdict_list[current_id]
        verdict_text = {1: "Liked 👍", 0: "Disliked 👎", -1: "Not reviewed", -2: "Missing"}[verdict]
        self.verdict_label.config(text=f"Verdict: {verdict_text}")
        self.display_images(current_id)

    def display_images(self, identifier):
        for label in self.image_labels:
            label.destroy()
        self.image_labels.clear()

        image_paths = self.identifier_dict.get(identifier, [])
        if not image_paths:
            messagebox.showinfo("Info", f"No images found for identifier {identifier}")
            return

        sample_paths = random.sample(image_paths, min(10, len(image_paths)))
        for idx, img_path in enumerate(sample_paths):
            try:
                img = Image.open(img_path)
                img.thumbnail((150, 150))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(self.image_frame, image=tk_img)
                lbl.image = tk_img
                lbl.grid(row=idx // 5, column=idx % 5, padx=5, pady=5)
                self.image_labels.append(lbl)
            except Exception as e:
                print(f"Failed to load {img_path}: {e}")

    # ------------------- Verdict handling -------------------

    def set_verdicts_file_path(self):
        if self.folder_path != None and len(self.folder_path) > 0: 
            verdictFileSuffix = ( self.folder_path[self.folder_path.rfind('/') + 1:])
            self.verdict_file = verdictFileSuffix + "-verdicts.txt"

    def set_verdict(self, value):
        if self.current_index is None:
            return
        current_id = self.target_ids[self.current_index]
        self.verdict_list[current_id] = value
        self.save_verdicts()
        self.display_current_id()

    def load_verdicts(self):
        """Load the verdict file, whose name is generated based on the image folder name (only verdicts, one per line)."""
            
        if not os.path.exists(self.verdict_file):
            return
        try:
            with open(self.verdict_file, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
            for i, val in enumerate(lines):
                if val in {"-2", "-1", "0", "1"} and i < len(self.verdict_list):
                    self.verdict_list[i] = int(val)
        except Exception as e:
            print(f"Failed to load verdicts: {e}")


    # "am prea multa treaba sa ma gandesc la asta - dar n-am zis cu vreo urma de resentiment"

    def save_verdicts(self):
        """Auto-save verdicts as plain values, one per line."""
        
        try:
            with open(self.verdict_file, "w") as f:
                for val in self.verdict_list:
                    f.write(f"{val}\n")
        except Exception as e:
            print(f"Failed to save verdicts: {e}")

    # ------------------- Navigation -------------------
    def next_id(self):
        if self.current_index is None or not self.target_ids:
            return
        if self.current_index < len(self.target_ids) - 1:
            self.current_index += 1
            self.display_current_id()
        else:
            messagebox.showinfo("End", "You’ve reached the last ID.")

    def previous_id(self):
        if self.current_index is None or not self.target_ids:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_id()
        else:
            messagebox.showinfo("Start", "You’re already at the first ID.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageReviewerApp(root)
    root.mainloop()
