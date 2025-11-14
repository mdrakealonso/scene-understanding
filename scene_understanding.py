import json
import math
from prettytable import PrettyTable

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
        self.file_info[vert]['angle_measures'] = angles
        return angles
    
    def largestAngle(self, angles):
        max = angles[0]
        for angle in angles:
            if angle > max:
                max = angle
        return max
    
    def smallestAngle(self, angles):
        min = angles[0]
        for angle in angles:
            if angle < min:
                min = angle
        return min

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
            elif any(angle > 185 for angle in angles):
                angle_type = "ARROW"
            else:
                angle_type = 'FORK'
        print("The angle", vert, "is of type", angle_type + ".")
        self.file_info[vert]['angle_type'] = angle_type

    def analyze_vertices(self):
        for vert in self.file_info:
            self.calculate_angle_type(vert)

    def link_regions(self):
        links = set()

        for v in self.file_info:
            self.file_info[v]['links'] = set()

        for angle in self.file_info:
            angle_type = self.file_info[angle]['angle_type']
            kind_list = self.file_info[angle]['kind_list']
            regions = [region for region in kind_list if isinstance(region, int)]
            print("regions:", regions)
            if angle_type.lower() == "L" or angle_type.lower() == "T":
                continue
            elif angle_type.lower() == "fork":
                for i in range(len(regions)):
                    for j in range(i+1, len(regions)):
                        link = tuple(sorted((regions[i], regions[j])))
                        links.add(link)
                        self.file_info[angle]['links'].add(link)
                        print(f"FORK at {angle}: LINK {sorted((regions[i], regions[j]))}")
            elif angle_type.lower() == "arrow":
                angles = self.file_info[angle]['angle_measures']
                region_pairs = []
                for i in range(len(regions)):
                    next = (i + 1) % len(regions)
                    region_pairs.append((regions[i], regions[next]))
                
                min_index = angles.index(min(angles))
                smallest_pair = region_pairs[min_index]

                link = tuple(sorted(smallest_pair))
                links.add(link)
                self.file_info[angle]['links'].add(link)
                print(f"ARROW at {angle}: LINK {sorted((regions[0], regions[1]))}")
        print(links)
        return links
      
    def region_linking(self, background=None):
        links = set()

        for v in self.file_info:
            self.file_info[v]['links'] = set()

        for vert,data in self.file_info.items():
            angle_type = self.file_info[vert]['angle_type']
            kind_list = data['kind_list']
            regions = [str(r) for r in kind_list if isinstance(r, (int))]
            if angle_type.lower() == "fork":
                for i in range(len(regions)):
                    for j in range(i + 1, len(regions)):
                        link = tuple(sorted((regions[i], regions[j])))
                        links.add(link)
                        self.file_info[vert]['links'].add(link)
                        print(f"[LINK] FORK at {vert}: link {sorted((regions[i], regions[j]))}")
            elif angle_type.lower() == "arrow":
                #one link between two regions of smaller angle
                angles = data['angle_measures']
                if len(angles) >= 2:
                    link = tuple(sorted((regions[0], regions[1])))
                    links.add(link)
                    self.file_info[vert]['links'].add(link)
                    print(f"[LINK] ARROW at {vert}: link {sorted((regions[0], regions[1]))}")
            elif angle_type.lower() == "l" or angle_type.lower() == "t":
                continue
        return links

    def detect_background(self, file_name):
        with open(file_name, "r") as f:
            data = json.load(f)
            if "background" in data:
                background = str(data["background"])
                print(f"[INFO] Using background from file: {background}")
                return background
    
    def dfs(self, region, current_nucleus, visited, graph): #recursivley find connected regions
        visited.add(region)
        current_nucleus.add(region)
        for neighbor in graph.get(region, []):
            if neighbor not in visited:
                self.dfs(neighbor, current_nucleus, visited, graph)
    
    def global_grouping(self, links, background=None): #connects regions into nuclei based on links Links {(1,2), (2,3), (4,5)} → nuclei = [['1','2','3'], ['4','5']]
        # Remove links to background
        if background:
            filtered_links = {l for l in links if background not in l}
        else:
            filtered_links = links
        print(":GLOBAL: Filtered links (no background):", filtered_links)
        graph = {} #graph where each regions points to all linked neighbors
        for r1, r2 in filtered_links:
            graph.setdefault(r1, set()).add(r2)
            graph.setdefault(r2, set()).add(r1)
        #find connected components (each is a nucleus)
        visited = set()
        nuclei = []
        def dfs(region, nucleus):
            visited.add(region)
            nucleus.add(region)
            for neighbor in graph.get(region, []):
                if neighbor not in visited:
                    dfs(neighbor, nucleus)
        for region in graph: #for each region if not visited do dfs to find all connected regions
            if region not in visited:
                nucleus = set()
                dfs(region, nucleus)
                nuclei.append(nucleus)
                print(f"[GLOBAL MERGE] Formed nucleus {nucleus}")

        return nuclei #return list of nuclei (each nucleus is a list of regions)

    def single_body_gen(self, links, nuclei):
        adj = {}
        for a, b in links:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)

        #map each region to its nucleus index
        def region_to_nucleus_map(nuclei):
            mapping = {}
            for i, n in enumerate(nuclei):
                for r in n:
                    mapping[r] = i
            return mapping
        changed = True
        while changed:
            changed = False
            region_to_nucleus = region_to_nucleus_map(nuclei)

            for i, n in enumerate(list(nuclei)):
                # only single-region nuclei are eligible
                if len(n) != 1:
                    continue
                region = next(iter(n))
                linked = adj.get(region, set())
                if len(linked) == 1:  # only one link
                    neighbor = next(iter(linked))
                    neighbor_idx = region_to_nucleus.get(neighbor)
                    if neighbor_idx is not None and neighbor_idx != i:
                        # merge single region nucleus into neighbor nucleus
                        print(f"[SINGLEBODY MERGE] Joining {n} with {nuclei[neighbor_idx]}")
                        nuclei[neighbor_idx].update(n)
                        nuclei.remove(n)
                        changed = True
                        break
        return nuclei

    
    def body_gen(self, file_name):
        background = self.detect_background(file_name)
        print(f"\nDetected background region: {background}")
        links = self.region_linking(background=background)
        nuclei = self.global_grouping(links, background)
        nuclei = self.single_body_gen(links, nuclei)

        print("Bodies formed from all linked regions:", nuclei)
        for i, body in enumerate(nuclei, 1):
            formatted = " ".join(f":{r}" for r in sorted(body, key=int))
            print(f"(BODY {i}. IS {formatted})")
        return nuclei

    def print_table(self):
        table = PrettyTable()
        table.field_names = ["Vertex ID", "Vertex Type", "Links Generated"]
        for item in self.file_info:
            angle_type = self.file_info[item].get("angle_type", "")
            generated_links = self.file_info[item].get('links', "")
            if not generated_links:
                generated_links = ""
            table.add_rows([[item, angle_type, generated_links]])
        print(table)

def main():
    scene_understander = SceneUnderstander()
    scene_understander.load_file("cube.json")
    scene_understander.analyze_vertices()
    links = scene_understander.link_regions()
    scene_understander.link_regions()
    scene_understander.print_table()

    nuclei = scene_understander.body_gen("cube.json")  
    scene_understander.single_body_gen(links, nuclei)

if __name__ == "__main__":
    main()
