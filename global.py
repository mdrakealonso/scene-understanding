import json
import math

class SceneUnderstander:
    def __init__(self):
        self.file_info = {}
        
    def load_file(self, file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)  # load the JSON file
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

    def get_vector(self, vert1, vert2):
        x1, y1 = vert1
        x2, y2 = vert2
        return (x2 - x1, y2 - y1)

    def calculate_angle(self, vert): #calculate angles of vertex
        vertex = self.file_info[vert]["coords"]
        kind_list = self.file_info[vert]["kind_list"]
        neighbors = [item for item in kind_list if isinstance(item, str) and item in self.file_info]
        angles = []
        for i in range(len(neighbors)):
            next_index = (i + 1) % len(neighbors)
            first_neighbor_verts = self.file_info[neighbors[i]]["coords"]
            second_neighbor_verts = self.file_info[neighbors[next_index]]["coords"]
            vector1 = self.get_vector(vertex, first_neighbor_verts)
            vector2 = self.get_vector(vertex, second_neighbor_verts)
            v1_x, v1_y = vector1
            v2_x, v2_y = vector2
            cosine = v1_x * v2_x + v1_y * v2_y
            sine = v1_x * v2_y - v1_y * v2_x
            angle = math.degrees(math.atan2(sine, cosine))
            if angle < 0:
                angle += 360
            print("The angle from ", neighbors[i], " to ", vert, " to ", neighbors[next_index], " is ", angle)
            angles.append(angle)
        self.file_info[vert]['angles'] = angles
        return angles

    def largestAngle(self, angles): #find largest angle
        max = angles[0]
        for angle in angles:
            if angle > max:
                max = angle
        return max
    
    def smallestAngle(self, angles): #find smallest angle
        min = angles[0]
        for angle in angles:
            if angle < min:
                min = angle
        return min

    def calculate_angle_type(self, vert): #determine type of vertex based on angles
        kind_list = self.file_info[vert]["kind_list"]
        angles = self.file_info[vert]['angles']
        neighbors = []
        for i in range(len(kind_list)):
            if isinstance(kind_list[i], str):
                if kind_list[i] not in neighbors:
                    neighbors.append(kind_list[i]) # list neighboring vertices
        angle_type = ""
        if len(neighbors) == 2:
            angle_type = "L"
        elif len(neighbors) == 3:
            max_angle = self.largestAngle(angles)
            print("Max angle at vertex", vert, "is", max_angle)
            if max_angle > 180:
                angle_type = "ARROW"
            elif 170 <= max_angle <= 190:
                angle_type = "T"
            else:
                angle_type = "FORK"
        self.file_info[vert]['angle_type'] = angle_type
        print("The vertex", vert, "is of type", angle_type + ".")
        return angle_type

    def analyze_vertices(self):
        for vert in self.file_info:
            self.calculate_angle(vert)
            self.calculate_angle_type(vert)
    
    def region_linking(self,  background=None): #make links between regions based on vertex types
        links = set()
        for vert, data in self.file_info.items(): #loop through every vertex
            vert_type = data.get('angle_type') #get vertex type
            kind_list = data['kind_list'] #get kind list(regions touching that vertex)
            # numeric region IDs
            regions = [str(r) for r in kind_list if isinstance(r, int) or (isinstance(r, str) and r.isdigit())]
            #if background: #ignore background
            #    regions = [r for r in regions if r != str(background)]
            print(f"Vertex {vert}: regions={regions}, type={vert_type}")
            if len(regions) < 2:
                continue
            if vert_type == "FORK": #generate three links for each pair of regions
                for i in range(len(regions)):
                    for j in range(i + 1, len(regions)):
                        links.add(tuple(sorted((regions[i], regions[j]))))
                        print("Linked Regions:", regions[i], regions[j], "at FORK vertex", vert)
            elif vert_type == "ARROW": #generate one link between smaller angle regions
                angles = data['angles']
                if len(angles) >= 2:
                    r1, r2 = regions[0], regions[1]
                    links.add(tuple(sorted((r1, r2))))
                    print("Linked Regions:", r1, r2, "at ARROW vertex", vert)
            elif vert_type in ("L", "T"):
                continue
        if background:
            links = {l for l in links if str(background) not in l} #remove links to background
        return links
    
    def detect_background(self):
        region_counts = {}
        for data in self.file_info.values():
            for r in data['kind_list']:
                if isinstance(r, int) or (isinstance(r, str) and r.isdigit()):
                    region_counts[r] = region_counts.get(r, 0) + 1
        # background tends to appear the most times (touches many vertices)
        background = max(region_counts, key=lambda x: region_counts[x])
        print("Region Counts",region_counts)
        print("Background", background)
        return str(background)
    
    def dfs(self, region, current_nucleus, visited, graph): #recursivley find connected regions
        visited.add(region)
        current_nucleus.add(region)
        for neighbor in graph.get(region, []):
            if neighbor not in visited:
                self.dfs(neighbor, current_nucleus, visited, graph)
                
    def region_grouping(self, links): #connects regions into nuclei based on links Links {(1,2), (2,3), (4,5)} → nuclei = [['1','2','3'], ['4','5']]
        graph = {} #graph where each regions points to all linked neighbors
        for r1, r2 in links:
            graph.setdefault(r1, set()).add(r2)
            graph.setdefault(r2, set()).add(r1)
        visited = set()
        nuclei = []
        
        for region in graph: #for each region if not visited do dfs to find all connected regions
            if region not in visited:
                nucleus = set()
                self.dfs(region, nucleus, visited, graph)
                nuclei.append(sorted(nucleus))
        print("Grouped Regions into Nuclei:", nuclei)
        return nuclei #return list of nuclei (each nucleus is a list of regions)
    
    def global_grouping(self, links, background='4'): #merge nuclei if they share 2+ links
        #delete links to background
        filtered_links = {l for l in links if background not in l}
        print(":GLOBAL: Filtered links (no background):", filtered_links)

        # initialize nuclei (each region starts as its own nucleus)
        regions = set([r for link in filtered_links for r in link])
        nuclei = [{r} for r in regions]
        
        def find_nucleus(region): #find which nucleus a region belongs to
            for n in nuclei:
                if region in n:
                    return n
            return None

        # Merge if two nuclei share 2+ links
        merged = True
        while merged:
            merged = False
            link_counts = {}
            for r1, r2 in filtered_links: #count links between nuclei
                n1 = tuple(find_nucleus(r1))
                n2 = tuple(find_nucleus(r2))
                if n1 == n2:
                    continue
                pair = tuple(sorted((n1, n2)))
                link_counts[pair] = link_counts.get(pair, 0) + 1

            for (n1, n2), count in link_counts.items():
                if count >= 2:
                    nucleus1 = find_nucleus(next(iter(n1)))
                    nucleus2 = find_nucleus(next(iter(n2)))
                    if nucleus1 and nucleus2 and nucleus1 != nucleus2:
                        print(f"[GLOBAL MERGE] Joining nuclei {nucleus1} and {nucleus2}")
                        merged_nucleus = nucleus1.union(nucleus2)
                        nuclei.remove(nucleus1)
                        nuclei.remove(nucleus2)
                        nuclei.append(merged_nucleus)
                        merged = True
                        break
        return nuclei

    def single_body_gen(self, links):
        adj = {}
        for a, b in links:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
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
        changes = True
        while changes:
            changes = False
            region_to_nucleus = {}
            for i, n in enumerate(nuclei):
                for r in n:
                    region_to_nucleus[r] = i
            for i, n in enumerate(list(nuclei)):
                if len(n) == 1:
                    region = next(iter(n))
                    linked = adj.get(region, set())
                    if len(linked) == 1:
                        neighbor = next(iter(linked))
                        neighbor_idx = region_to_nucleus.get(neighbor)
                        if neighbor_idx is not None and neighbor_idx != i:
                            nuclei[neighbor_idx].update(n)
                            nuclei.remove(n)
                            print(f"Merging {n} into {nuclei[neighbor_idx]} under SINGLEBODY")
                            changes = True
                            break
        return nuclei
    
    def body_gen(self):
        background = self.detect_background()
        print(f"\nDetected background region: {background}")
        links = self.region_linking(background=background)
        nuclei = self.global_grouping(links)
        nuclei = self.single_body_gen(links)
        print("Bodies formed from all linked regions:", nuclei)
        for i, body in enumerate(nuclei, 1):
            formatted = " ".join(f":{r}" for r in sorted(body, key=int))
            print(f"(BODY {i}. IS {formatted})")
        return nuclei


def main():
    scene_understander = SceneUnderstander()
    scene_understander.load_file("cube.json")
    scene_understander.analyze_vertices()
    scene_understander.body_gen()   


if __name__ == "__main__":
    main()
