import json
import pprint

class SceneUnderstander:
    def __init__(self):
        self.file_info = {}
        
    def load_file(self, file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)  # load the JSON file
                for vert in data["vertex-data"]: # iterate over vertices
                    self.file_info[vert['id']] = {"coords": vert['coords'], 
                                               "kind_list": vert['kind-list']} # nested dictionary
                pprint.pprint(self.file_info)
        except FileNotFoundError:
            print("Error: The file '", file_name, "' was not found.")
        except Exception as e:
            print("An error occured: ", e)

    def calculate_angle(self, vert):
        pass

    def calculate_type(self, vert):
        pass

    def analyze_vertices(self):
        for vert in self.file_info:
            self.calculate_angle(vert)
            self.calculate_type(vert)

def main():
    scene_understander = SceneUnderstander()
    scene_understander.load_file("cube.json")
    scene_understander.calculate_type()

if __name__ == "__main__":
    main()