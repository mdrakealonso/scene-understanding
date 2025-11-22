import json
import math

class SceneUnderstander:
    def __init__(self):
        self.vertices = {}
        self.file_info = {}
        self.background = None
        self.all_links = []
        self.nuclei = []
        
    def load_file(self, file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)  # load the JSON file
                self.background = data.get("background")
                for vert in data["vertex-data"]:  # iterate over vertices
                    self.file_info[vert['id']] = {
                        "coords": vert['coords'], 
                        "kind_list": vert['kind-list']
                    }
            print(f"Loaded {len(self.file_info)} vertices from {file_name}")
        except FileNotFoundError:
            print("Error: The file '", file_name, "' was not found.")
        except Exception as e:
            print("An error occurred: ", e)

    class Vertex:
        def __init__(self, vertex_id, coords, kind_list):
            self.id = vertex_id
            self.coords = coords  # (x, y)
            self.kind_list = kind_list
            self.vertex_type = None
            self.angles = []  # store calculated angles
            self.neigboring_vertices = []  # connected vertices
        
        def get_vector(self, v_coords,needs_flip):
            x = v_coords[0] - self.coords[0]
            y = (v_coords[1] - self.coords[1])
            if(needs_flip):
                y = -(v_coords[1] - self.coords[1])
            return x,y
        
        def calculate_angle(self, v1_coords, v2_coords,needs_flip): #calculate angles of vertex
            dx1,dy1 = self.get_vector(v1_coords,needs_flip) #calculate vectors
            dx2,dy2 = self.get_vector(v2_coords,needs_flip)
            angle1 = math.atan2(dy1, dx1) #calculate angles
            angle2 = math.atan2(dy2, dx2)
            angle_diff = angle2 - angle1 #calculate counterclockwise angle from angle1 to angle2
            if angle_diff < 0:
                angle_diff += 2 * math.pi
            angle_degrees = math.degrees(angle_diff) #convert to degrees
            return angle_degrees
            
        def calculate_vertex_type(self, vertices_dict, needs_flip): #determine type of vertex based on angles
            neighbors = []
            for i in range(len(self.kind_list)):
                if isinstance(self.kind_list[i], str):
                    neighbors.append(self.kind_list[i]) # list neighboring vertices
            if neighbors[0] == neighbors[-1]:
                neighbors = neighbors[:-1]
            neighbor_count = len(neighbors)
            print("-----CLASSIFYING VERTEX TYPE of Vertex" ,self.id,"-----")
            if neighbor_count == 2: ##if only 2 edges
                self.vertex_type = "L"
                v1 = neighbors[0]
                v2 = neighbors[1]
                v1_coords = vertices_dict[v1].coords
                v2_coords = vertices_dict[v2].coords
                angle = self.calculate_angle(v1_coords, v2_coords,needs_flip)
                self.angles = [angle]
                print(f"  Angle from {v1} to {v2}: {angle:.2f}")
                print(f"  Vertex Type: L (two lines)")
                return
            elif neighbor_count == 3:
                angles = []
                for i in range(3):
                    v1 = neighbors[i]
                    v2 = neighbors[(i + 1) % 3]
                    v1_coords = vertices_dict[v1].coords
                    v2_coords = vertices_dict[v2].coords
                    angle = self.calculate_angle(v1_coords, v2_coords, needs_flip) 
                    angles.append(angle)
                    print(f"  Angle from {v1} to {v2}: {angle:.2f}")
                self.angles = angles
                if any(abs(a - 180) < 5 for a in angles):
                    self.vertex_type = "T"
                elif any(a > 180 for a in angles):
                    self.vertex_type = "ARROW"
                else:
                    self.vertex_type = "FORK"
            print("The vertex", self.id, "is of type", self.vertex_type)
            return

        def region_linking(self,  background): #make links between regions based on vertex types
            links = []
            regions_all = [r for r in self.kind_list if isinstance(r, int) or (isinstance(r, str) and r.isdigit())]
            regions_no_background = [r for r in regions_all if r != background]
            vert_type = self.vertex_type
            print(f"Vertex {self.id}: regions_all={regions_all}, type={vert_type}")
            if vert_type in ("L", "T") or len(regions_no_background) < 2:
                return links
            if vert_type == "FORK": #generate three links for each pair of regions
                for i in range(len(regions_no_background)):
                    for j in range(i + 1, len(regions_no_background)):
                        link = tuple(sorted([regions_no_background[i], regions_no_background[j]]))
                        links.append(link) 
                        print(f"[LINK] FORK at {self.id}: {link}")
            elif vert_type == "ARROW": #generate one link between smaller angle regions
                if len(self.angles) >= 3 and len(regions_no_background) >= 2:
                    max_angle = self.angles.index(max(self.angles)) #get index of max value
                    if len(regions_no_background) == 2: #if there is only have 2 non-background regions, link them
                        r1, r2 = regions_no_background[0], regions_no_background[1]
                    elif len(regions_no_background) >= 3: #remove the largest angle, and link the 2 smallest ones
                        region_indices = [0, 1, 2] 
                        region_indices.remove(max_angle)
                        r1, r2 = regions_no_background[region_indices[0]], regions_no_background[region_indices[1]]
                    else:
                        return links
                    link = tuple(sorted([r1, r2]))
                    links.append(link)
                    print(f"[LINK] ARROW at {self.id}: {link}")
            return links
        
    def create_vertices(self):
        for vid, info in self.file_info.items():
            self.vertices[vid] = self.Vertex(vid, tuple(info["coords"]), info["kind_list"])
    
    def analyze_vertices(self,needs_flip):
        for v in self.vertices.values(): #calculate vertex types
            v.calculate_vertex_type(self.vertices, needs_flip)
        self.all_links = []
        print("\n" + "="*50)
        print("REGION LINKING")
        print("="*50)
        for v in self.vertices.values(): #region linking
            self.all_links.extend(v.region_linking(self.background))
        print(f"All links (with duplicates): {self.all_links}")

    class Nucleus:
        def __init__(self, regions):
            self.regions = set(regions) #regions is a set
            self.links = set()

        def __repr__(self):
            return f"Nucleus(regions={sorted(self.regions)}, links={sorted(self.links)})"

    def global_grouping(self): #connects regions into nuclei based on links Links {(1,2), (2,3), (4,5)} → nuclei = [['1','2','3'], ['4','5']]
        print("\n" + "="*50)
        print("GLOBAL GROUPING")
        print("="*50)

        correct_links = [link for link in self.all_links if self.background not in link] #remove background links
        region_ids = set(r for link in correct_links for r in link)
        self.nuclei = [self.Nucleus([r]) for r in region_ids]#initial nuclei
        for n in self.nuclei: #give nucleus its initial links
            n.links = set([link for link in correct_links if link[0] in n.regions or link[1] in n.regions])

        merged = True
        while merged: # Merge until stable
            merged = False
            for i in range(len(self.nuclei)): #try each pair of nuclei
                for j in range(i + 1, len(self.nuclei)):
                    n1, n2 = self.nuclei[i], self.nuclei[j]
                    #count links between n1 and n2
                    connecting_links = [link for link in correct_links if (link[0] in n1.regions and link[1] in n2.regions) or (link[1] in n1.regions and link[0] in n2.regions)]
                    if len(connecting_links) >= 2:  #make new nucleus
                        new_regions = n1.regions.union(n2.regions)
                        new_n = self.Nucleus(new_regions)
                        new_n.links = n1.links.union(n2.links) #new nucleus gets all links from both
                        print(f"[GLOBAL MERGE] Merging nuclei {sorted(n1.regions)} + {sorted(n2.regions)} -> {sorted(new_regions)}")
                        self.nuclei.pop(j)# delete old nuclei, add merged
                        self.nuclei.pop(i)
                        self.nuclei.append(new_n)
                        merged = True
                        break
                if merged:
                    break
        return self.nuclei

    def singlebody(self):
        merged = True
        while merged:
            merged = False
            for n in self.nuclei[:]:
                if len(n.regions) == 1: #nucleus composed of a single region
                    single_region = next(iter(n.regions)) 
                    connected_links = [link for link in n.links if single_region in link] #gets all links from this single region
                    if len(connected_links) == 1: #if only one link ->merge
                        other = connected_links[0][0] if connected_links[0][1] == single_region else connected_links[0][1]
                        # Find the nucleus containing other_region
                        target = next((nu for nu in self.nuclei if other in nu.regions), None)
                        if target: # merge single region into target
                            print(f"[SINGLEBODY MERGE] {n.regions} merged into {target.regions} via {connected_links[0]}")
                            target.regions.update(n.regions)
                            target.links.update(n.links)  # inherit all links from the single-region nucleus
                            self.nuclei.remove(n) #delete merged nucleus
                            merged = True
                            break 
        return self.nuclei

    def print_bodies(self):
        print("\n" + "="*50)
        print("FINAL BODIES")
        print("="*50)
        for idx, n in enumerate(self.nuclei, 1):
            print(f"Body {idx}: Regions = {sorted(n.regions)}")
    
    def analyze_scene(self, needs_flip):
        self.create_vertices()
        self.analyze_vertices(needs_flip)
        self.global_grouping()
        self.singlebody()
        self.print_bodies()

def main():
    print("\n" + "="*50)
    print("CUBE")
    print("="*50)
    scene_understander = SceneUnderstander()
    scene_understander.load_file("cube.json")
    scene_understander.analyze_scene(False)
    
    print("\n" + "="*50)
    print("ONE")
    print("="*50)
    scene_understander = SceneUnderstander()
    scene_understander.load_file("one.json")
    scene_understander.analyze_scene(True)

if __name__ == "__main__":
    main()
