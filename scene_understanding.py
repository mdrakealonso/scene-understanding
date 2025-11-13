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
<<<<<<< HEAD

    def largestAngle(self,angles):
        max = angles[0]
        for angle in angles:
            if angle > max:
                max = angle
        return max
    
    def smallestAngle(self,angles):
        min = angles[0]
        for angle in angles:
            if angle < min:
                min = angle
        return min

    def calculate_angle_type(self, vert):
        kind_list = self.file_info[vert]["kind_list"]
        angles = self.file_info[vert]['angles']
=======

    def calculate_angle_type(self, vert):
        kind_list = self.file_info[vert]["kind_list"]
        angles = self.calculate_angle(vert)
>>>>>>> ae24f214f93bea78cb3dde6fb7e25bd56674c57b
        angle_type = ""
        neighbors = []
        for i in range(len(kind_list)):
            if isinstance(kind_list[i], str):
                if kind_list[i] not in neighbors:
                    neighbors.append(kind_list[i]) # list neighboring vertices
        if len(neighbors) == 2:
            angle_type = "L"
        elif len(neighbors) == 3:
<<<<<<< HEAD
            max_angle = self.largestAngle(angles)
            if abs(max_angle) < 190 and abs(max_angle) > 170:
                angle_type = "T"
            elif max_angle > 180:
                angle_type = "ARROW"
            else:
                angle_type = "FORK"
        self.file_info[vert]['angle_type'] = angle_type
        print("The verex", vert, "is of type", angle_type + ".")
        return angle_type
=======
            if any(175 < angle < 185 for angle in angles):
                angle_type = "T"
            elif any(angle > 180 for angle in angles):
                angle_type = "arrow"
            else:
                angle_type = 'fork'
        print("The angle", vert, "is of type", angle_type + ".")
>>>>>>> ae24f214f93bea78cb3dde6fb7e25bd56674c57b

    def analyze_vertices(self):
        for vert in self.file_info:
            self.calculate_angle_type(vert)
    
    def region_linking(self):
        links = set()
        for vert,data in self.file_info.items():
            vert_type = data.get('angle_type')
            kind_list = data['kind_list']
            regions = [str(r) for r in kind_list if isinstance(r, (str, int))]
            if len(regions) < 2:
                continue
            if vert_type == "FORK":
                for i in range(len(regions)):
                    for j in range(i+1,len(regions)):
                        links.add(tuple(sorted((regions[i],regions[j]))))
                        #three links should be generated between each pair of regions
                        print("Linked Regions:", regions[i], regions[j], "at FORK vertex", vert)
            elif vert_type == "ARROW":
                #one link between two regions of smaller angle
                angles = data['angles']
                min = angles.index(self.smallestAngle(angles))
                r1 = regions[min]
                r2 = regions[(min+1)%len(regions)]
                links.add((r1,r2))
                print("Linked Regions:", r1, r2, "at ARROW vertex", vert)
            elif vert_type == "L" or vert_type == "T":
                continue
        return links
    
    def dfs(self, region, current_nucleus, visited, graph):
        visited.add(region)
        current_nucleus.add(region)
        for neighbor in graph.get(region, []):
            if neighbor not in visited:
                self.dfs(neighbor, current_nucleus, visited, graph)
                
    def region_grouping(self,links):
        graph = {}
        for r1, r2 in links:
            if r1 not in graph:
                graph[r1] = set()
            if r2 not in graph:
                graph[r2] = set()
            graph[r1].add(r2)
            graph[r2].add(r1)
        visited = set()
        nuclei = []
        
        for region in graph:
            if region not in visited:
                nucleus = []
                self.dfs(region, nucleus, visited, graph)
                nuclei.append(sorted(nucleus))
        print("Grouped Regions into Nuclei:", nuclei)
        return nuclei
    def single_body_gen(self,links):
        adj = {}
        for a,b in links:
            if a not in adj:
                adj[a] = set()
            if b not in adj:
                adj[b] = set()
            adj[a].add(b)
            adj[b].add(a)
        visited = set()
        nuclei = []
        
        def dfs(node, current_nucleus):
            visited.add(node)
            current_nucleus.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, current_nucleus)
        for region in adj.keys():
            if region not in visited:
                nucleus = set()
                dfs(region, nucleus)
                nuclei.append(sorted(nucleus))
        return nuclei
    def body_gen(self):
        links = self.region_linking()
        nuclei = self.single_body_gen(links)
        print("Bodies formed from all linked regions:", nuclei)
        for i, body in enumerate(nuclei):
            print("Body", i+1, ":", body)
        return nuclei  

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
<<<<<<< HEAD
    scene_understander.calculate_angle("A")
    scene_understander.calculate_angle_type("A")
    links = scene_understander.region_linking()
    nuclei = scene_understander.region_grouping(links)
=======
    scene_understander.analyze_vertices()
>>>>>>> ae24f214f93bea78cb3dde6fb7e25bd56674c57b

if __name__ == "__main__":
    main()