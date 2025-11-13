import json
import math
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
        except FileNotFoundError:
            print("Error: The file '", file_name, "' was not found.")
        except Exception as e:
            print("An error occured: ", e)

    def get_vector(self, vert1, vert2):
        vert1_x = vert1[0]
        vert1_y = vert1[1]
        vert2_x = vert2[0]
        vert2_y = vert2[1]
        vector = (vert2_x - vert1_x, vert2_y - vert1_y) # the vector from vert1 to vert2
        return vector
    
    def normalize_angle(self, angle_deg):
        return angle_deg % 360

    def calculate_angle(self, vert):
        vertex = self.file_info[vert]["coords"] # coordinates of central vertex
        kind_list = self.file_info[vert]["kind_list"]

        neighbors = []
        for i in range(len(kind_list)):
            if isinstance(kind_list[i], str) and kind_list[i] not in neighbors:
                neighbors.append(kind_list[i]) # list neighboring vertices

        angles = []
        for i in range(len(neighbors)): # loop through each neighbor
            next_index = (i + 1) % len(neighbors)
            first_neighbor_verts = self.file_info[neighbors[i]]["coords"] 
            second_neighbor_verts = self.file_info[neighbors[next_index]]["coords"] 
            vector1 = self.get_vector(vertex, first_neighbor_verts) # vecor from central vertex to first neighbor
            vector2 = self.get_vector(vertex, second_neighbor_verts) # vecor from central vertex to second neighbor
            v1_x, v1_y = vector1 # seperate vector x and y
            v2_x, v2_y = vector2
            cosine = v1_x * v2_x + v1_y * v2_y
            sine = v1_x * v2_y - v1_y * v2_x
            angle = math.degrees(math.atan2(sine, cosine)) # angle from vector1 to vector2 in degrees
            angle = self.normalize_angle(angle)
            angles.append(angle)
            print("The angle from ", neighbors[i], " to ", vert, " to ", neighbors[next_index], " is ", angle)
        self.file_info[vert]['angles'] = angles
        return angles

    def calculate_angle_type(self, vert):
        kind_list = self.file_info[vert]["kind_list"]
        angles = self.calculate_angle(vert)
        angle_type = ""

        neighbors = []
        for i in range(len(kind_list)):
            if isinstance(kind_list[i], str):
                if kind_list[i] not in neighbors:
                    neighbors.append(kind_list[i]) # list neighboring vertices
        if len(neighbors) == 2:
            angle_type = 'L'
        elif len(neighbors) == 3:
            if any(175 < angle < 185 for angle in angles):
                angle_type = "T"
            elif any(angle > 180 for angle in angles):
                angle_type = "arrow"
            else:
                angle_type = 'fork'
        print("The angle", vert, "is of type", angle_type + ".")

    def analyze_vertices(self):
        for vert in self.file_info:
            self.calculate_angle_type(vert)

    def join_global(self):
        pass
        #delete background links
        #create initial nuclei (containing region + links)
        #merge nuclei with links between them
        #repeat until can't merge anymore
    
    def join_singlebody(self):
        pass
        # find any nucleus containing a single region which has a single link 
        #                           to another nucleus and no other links
        # once found, join the two nuclei
        # whenever a join occurs, print a logging message to indicate 
        #        that two nuclei were merged and which regions were involved
        # let the nuclei grow and merge under these rules until 
        #                           no new nuclei can be formed

def main():
    scene_understander = SceneUnderstander()
    scene_understander.load_file("cube.json")
    scene_understander.analyze_vertices()

if __name__ == "__main__":
    main()
