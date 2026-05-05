import yaml

class ThresholdExtractor:
    def __init__(self):
        
        self.combo_id_list = None
        self.combo_id_to_instance_info_list = None
        self.combo_id_to_instance_state_list = None
        self.combo_id_to_last_seen_index = None

        self.full_csv_path = "\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images\\homogeneous-eight-cell-nine-april-exported-extra-smooth-images-df.csv" # all good 
            
        self.img_dir_path = self.full_csv_path[:self.full_csv_path.rfind('\\')] # all good 
            
        self.full_yaml_path = self.full_csv_path[:self.full_csv_path.rfind('.')] + ".yaml" # all good  

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

    def print_thresholds(self):
        # 0, 3, 4, 7 
        # 2, 11, 14, 23 

        tmp_two_state_list = self.combo_id_to_instance_state_list[2]
        tmp_eleven_state_list = self.combo_id_to_instance_state_list[11]
        tmp_fourteen_state_list = self.combo_id_to_instance_state_list[14]
        tmp_twentythree_state_list = self.combo_id_to_instance_state_list[23]

        print(tmp_two_state_list)

        #print(list(self.combo_id_to_instance_info_list))
        #print(self.combo_id_to_instance_info_list[2])

if __name__ == "__main__":
    tExt = ThresholdExtractor()

    tExt.load_from_yaml_file()
    tExt.print_thresholds()

    