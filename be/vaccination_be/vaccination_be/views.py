# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import math
import itertools
import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx
import geneticalgorithm as ga
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import gc
import logging
import os 
import random 

# Configure logging
logging.basicConfig(level=logging.INFO)



# BarangayList Class
class BarangayList:
    def __init__(self, locations, populations, infected, vaccinated=None):
        self.locations = locations
        self.populations = populations
        self.infected = infected
        if vaccinated is None:
            self.vaccinated = [False for _ in populations]
        else:
            self.vaccinated = vaccinated

        total_population = sum(populations)
        total_infected = sum(infected)
        self.weights = [
            (populations[i] / total_population) + (infected[i] / total_infected) # Weights ng simple optimization
            for i in range(len(populations))
        ]
        self.count = len(populations)

    def __str__(self):
        return (
            f"Count: {self.count}\n"
            f"Location: {self.locations}\n"
            f"Population: {self.populations}\n"
            f"Infected: {self.infected}\n"
            f"Weights: {self.weights}\n"
            f"Vaccinated: {self.vaccinated}"
        )

# Distance Functions
def euclidean(a, b, G):
    return ox.distance.great_circle_vec(a[0], a[1], b[0], b[1], earth_radius=6371009)

def road(a, b, G):
    try:
        origin_node = ox.distance.nearest_nodes(G, X=a[1], Y=a[0])
        destination_node = ox.distance.nearest_nodes(G, X=b[1], Y=b[0])
        return nx.shortest_path_length(G, origin_node, destination_node, weight='length')
    except nx.exception.NetworkXNoPath:
        return math.inf

def time(a, b, G):
    try:
        G1 = ox.add_edge_speeds(G.copy())
        G1 = ox.add_edge_travel_times(G1)
        origin_node = ox.distance.nearest_nodes(G1, X=a[1], Y=a[0])
        destination_node = ox.distance.nearest_nodes(G1, X=b[1], Y=b[0])
        return nx.shortest_path_length(G1, origin_node, destination_node, weight='travel_time')
    except nx.exception.NetworkXNoPath:
        return math.inf

# Optimization Functions
def simple_optimization(L, sites, barangays, distance=road, method='numerical', G=None):
    if G is None:
        return None

    distance_list = [
        [
            barangays.weights[j] * distance(barangays.locations[j], sites[i], G)
            for j in range(barangays.count)
        ]
        for i in range(len(sites))
    ]

    if method == 'numerical':
        v_combinations = list(itertools.combinations(range(len(sites)), L))
        best_sum = math.inf
        best = None
        for combo in v_combinations:
            d_sum = sum(
                min([distance_list[x][j] for x in combo]) for j in range(barangays.count)
            )
            if d_sum < best_sum:
                best = combo
                best_sum = d_sum
        return best
    elif method == 'genetic':
        varbound = np.array([[0, len(sites) - 1]] * L)

        def f(n):
            n = n.astype(np.int64).tolist()
            d_sum = sum(
                min([distance_list[x][j] for x in n]) for j in range(barangays.count)
            )
            return d_sum

        algorithm_param = {
            'max_num_iteration': 300 * L,
            'population_size': 20 * (L ** 2),
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'crossover_probability': 0.5,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': 50,
        }
        model = ga.geneticalgorithm(
            function=f,
            dimension=L,
            variable_type='int',
            variable_boundaries=varbound,
            algorithm_parameters=algorithm_param,
            convergence_curve=False,
        )
        model.run()
        return sorted(model.output_dict['variable'].astype(np.int64).tolist())
    else:
        return None

def bi_objective_optimization(L, radius, sites, barangays, distance, method='numerical', G=None):
    if G is None:
        return None

    if method == 'numerical':
        distance_list = [
            [
                (barangays.infected[j] / sum(barangays.infected))
                * distance(barangays.locations[j], sites[i], G)
                for j in range(barangays.count)
            ]
            for i in range(len(sites))
        ]
        pop_distance_list = [
            [
                distance(barangays.locations[j], sites[i], G)
                for j in range(barangays.count)
            ]
            for i in range(len(sites))
        ]
        v_combinations = sorted(
            list(itertools.combinations(range(len(sites)), L)),
            key=lambda s: sum(sum(distance_list[i]) for i in s),
        )
        best_sum = math.inf
        best = []
        for combo in v_combinations:
            d_sum = -sum(
                sum(
                    [
                        barangays.populations[j]
                        for k in combo
                        if pop_distance_list[k][j] <= radius
                    ]
                )
                for j in range(barangays.count)
            )
            if d_sum < best_sum:
                best.append(combo)
                best_sum = d_sum
        return best
    elif method == 'genetic':
        # Genetic algorithm implementation can be added here
        return None
    else:
        return None

def dynamic_optimization(L, sites, barangays, distance, method='numerical', G=None):
    if G is None:
        return None

    distance_list = [
        [
            barangays.weights[j] * distance(barangays.locations[j], sites[i], G)
            for j in range(barangays.count)
        ]
        for i in range(len(sites))
    ]

    if method == 'numerical':
        v_combinations = list(itertools.combinations(range(len(sites)), L))
        best_sum = math.inf
        best = None
        for combo in v_combinations:
            d_sum = sum(
                min(
                    [distance_list[x][j] for x in combo if not barangays.vaccinated[j]],
                    default=0,
                )
                for j in range(barangays.count)
            )
            if d_sum < best_sum:
                best = combo
                best_sum = d_sum
        return best
    elif method == 'genetic':
        varbound = np.array([[0, len(sites) - 1]] * L)

        def f(n):
            n = n.astype(np.int64).tolist()
            d_sum = sum(
                min(
                    [distance_list[x][j] for x in n if not barangays.vaccinated[j]],
                    default=0,
                )
                for j in range(barangays.count)
            )
            return d_sum

        algorithm_param = {
            'max_num_iteration': 300 * L,
            'population_size': 20 * (L ** 2),
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'crossover_probability': 0.5,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': 50,
        }
        model = ga.geneticalgorithm(
            function=f,
            dimension=L,
            variable_type='int',
            variable_boundaries=varbound,
            algorithm_parameters=algorithm_param,
            convergence_curve=False,
        )
        model.run()
        return sorted(model.output_dict['variable'].astype(np.int64).tolist())
    else:
        return None

# Helper function to load graph based on address
def load_graph(address):
    try:
        G = ox.graph_from_place(address, network_type='drive')
        return G
    except Exception as e:
        return None

class TransformXLSX(APIView):
    parser_classes = [MultiPartParser]  # Enable handling of multipart/form-data

    def post(self, request):
        # Check if file is present
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the tmp directory exists (Windows compatibility fix)
        tmp_dir = os.path.join(default_storage.location, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        # Save the uploaded file temporarily
        file_path = default_storage.save(os.path.join('tmp', file.name), ContentFile(file.read()))
        tmp_file = default_storage.path(file_path)

        try:
            # Read the XLSX file using pandas
            xls = pd.ExcelFile(tmp_file)

            # Check for required sheets
            required_sheets = ['Barangays', 'Sites']
            for sheet in required_sheets:
                if sheet not in xls.sheet_names:
                    return Response(
                        {'error': f'Missing required sheet: {sheet}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Parse Barangays Sheet
            barangays_df = pd.read_excel(xls, 'Barangays')
            required_barangay_columns = ['infected', 'population', 'latitude', 'longitude', 'Barangay_name']
            if not all(col in barangays_df.columns for col in required_barangay_columns):
                return Response(
                    {'error': f'Barangays sheet must contain columns: {required_barangay_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Parse Sites Sheet
            sites_df = pd.read_excel(xls, 'Sites')
            required_site_columns = ['latitude', 'longitude', 'Name']
            if not all(col in sites_df.columns for col in required_site_columns):
                return Response(
                    {'error': f'Sites sheet must contain columns: {required_site_columns}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Construct JSON
            json_data = {
                "sites": {
                    "locations": sites_df[['latitude', 'longitude']].values.tolist(),
                    "names": sites_df['Name'].fillna('').tolist()
                },
                "barangays": {
                    "locations": barangays_df[['latitude', 'longitude']].values.tolist(),
                    "names": barangays_df['Barangay_name'].fillna('').tolist(),
                    "populations": barangays_df['population'].fillna(0).astype(int).tolist(),
                    "infected": barangays_df['infected'].fillna(0).astype(int).tolist()
                }
            }
            return Response({'data': json_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error processing the file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # Ensure the file is deleted
            # if default_storage.exists(file_path):
            #     os.remove(os.path.join(tmp_dir,file.name))
            # gc.collect()  # Force garbage collection
            pass



# Helper function for graph coloring on selected sites
def compute_adjacency(selected_sites, threshold):
    """
    Build an adjacency list: two sites are adjacent if the great-circle distance
    between them is less than the threshold.
    """
    n = len(selected_sites)
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            d = ox.distance.great_circle(
                selected_sites[i]['coordinates'][0],
                selected_sites[i]['coordinates'][1],
                selected_sites[j]['coordinates'][0],
                selected_sites[j]['coordinates'][1],
                earth_radius=6371009
            )
            if d < threshold:
                adj[i].add(j)
                adj[j].add(i)
    return adj

def count_conflicts(selected_sites, adj):
    """
    Count the total number of conflicting edges (i.e., adjacent sites with the same color)
    and return the set of nodes involved in conflicts.
    """
    conflicts = 0
    conflict_nodes = set()
    for i in range(len(selected_sites)):
        for j in adj[i]:
            if selected_sites[i]['color'] == selected_sites[j]['color']:
                conflicts += 1
                conflict_nodes.add(i)
                conflict_nodes.add(j)
    # Each conflict is counted twice (once for each node) so divide by 2.
    return conflicts // 2, conflict_nodes

def iterative_conflict_resolution(selected_sites, threshold, available_colors=None, max_iterations=1000):
    """
    Assign colors to selected_sites using an iterative conflict resolution algorithm.
    
    Parameters:
      selected_sites: list of dicts; each dict must have a 'coordinates' key.
      threshold: distance threshold (in meters) to consider two sites as adjacent.
      available_colors: list of color names (default provided if None).
      max_iterations: maximum iterations for the local search.
      
    The algorithm randomly assigns colors, then iteratively resolves conflicts by reassigning
    a color that minimizes conflicts with adjacent nodes.
    """
    if available_colors is None:
        available_colors = ["red", "blue", "green", "orange", "purple", "yellow", "cyan", "brown"]
    
    n = len(selected_sites)
    # Build adjacency list based on the threshold
    adj = compute_adjacency(selected_sites, threshold)
    
    # Initial random color assignment
    for i in range(n):
        selected_sites[i]['color'] = random.choice(available_colors)
    
    conflicts, conflict_nodes = count_conflicts(selected_sites, adj)
    iteration = 0
    # Iteratively resolve conflicts until there are none or max_iterations is reached
    while conflicts > 0 and iteration < max_iterations:
        iteration += 1
        # Process each node involved in a conflict
        for node in list(conflict_nodes):
            current_color = selected_sites[node]['color']
            # Count conflicts for the current color
            current_conflicts = sum(1 for neighbor in adj[node] if selected_sites[neighbor]['color'] == current_color)
            
            best_color = current_color
            best_conflicts = current_conflicts
            # Try each available color to see if it reduces conflicts
            for color in available_colors:
                if color == current_color:
                    continue
                conflict_count = sum(1 for neighbor in adj[node] if selected_sites[neighbor]['color'] == color)
                if conflict_count < best_conflicts:
                    best_conflicts = conflict_count
                    best_color = color
            selected_sites[node]['color'] = best_color
        conflicts, conflict_nodes = count_conflicts(selected_sites, adj)
    
    print("Final conflicts:", conflicts, "after iterations:", iteration)
    return selected_sites



# Revised SimpleOptimization API View
class SimpleOptimization(APIView):
    def post(self, request):
        data = request.data
        L = data.get('L')
        method = data.get('method')
        sites_data = data.get('sites')
        barangays_data = data.get('barangays')
        address = barangays_data.get('Municipality')[0]
        # Validate required parameters
        if not all([address, L, method, sites_data, barangays_data]):
            return Response(
                {'error': 'Missing required parameters: address, L, method, sites, barangays.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract site data
        sites = sites_data.get('locations')
        site_names = sites_data.get('names', [])
        if len(site_names) != len(sites):
            site_names = [''] * len(sites)

        # Extract barangay data
        barangay_locations = barangays_data.get('locations')
        barangay_populations = barangays_data.get('populations')
        barangay_infected = barangays_data.get('infected')
        barangay_names = barangays_data.get('names', [])
        if len(barangay_names) != len(barangay_locations):
            barangay_names = [''] * len(barangay_locations)

        # Log details
        logging.info(f'Address: {address}')
        logging.info(f'L: {L}')
        logging.info(f'Method: {method}')
        logging.info(f'Sites data: {sites_data}')
        logging.info(f'Barangays data: {barangays_data}')

        # Create BarangayList object
        barangays = BarangayList(
            locations=barangay_locations,
            populations=barangay_populations,
            infected=barangay_infected
        )

        # Load graph based on address
        G = load_graph(address)
        if G is None:
            return Response(
                {'error': f'Unable to load graph for address: {address}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Run optimization
        result_indices = simple_optimization(L, sites, barangays, distance=road, method=method, G=G)
        if result_indices is None:
            return Response(
                {'error': 'Optimization failed due to invalid parameters or data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build selected_sites list without color first
        selected_sites = []
        for site_index in result_indices:
            selected_sites.append({
                'index': site_index,
                'name': site_names[site_index],
                'coordinates': sites[site_index]
            })
        
        # Run graph coloring to assign marker colors based on proximity
        selected_sites = iterative_conflict_resolution(selected_sites, threshold=5000)

        # Calculate the closest optimal vaccination center for each barangay
        barangay_assignments = []
        for j, b_loc in enumerate(barangay_locations):
            best_distance = math.inf
            best_center = None
            for site in selected_sites:
                d = road(b_loc, site['coordinates'], G)
                if d < best_distance:
                    best_distance = d
                    best_center = site
            barangay_assignments.append({
                'barangay_index': j,
                'barangay_name': barangay_names[j],
                'closest_center': best_center,  # includes index, name, coordinates, color
                'distance': best_distance
            })

        logging.info(f'Selected sites: {selected_sites}')
        logging.info(f'Barangay assignments: {barangay_assignments}')

        return Response({
            'result_indices': result_indices,
            'selected_sites': selected_sites,
            'barangay_assignments': barangay_assignments
        })
    
    
class BiObjectiveOptimization(APIView):
    def post(self, request):
        data = request.data
        address = data.get('address')
        L = data.get('L')
        radius = data.get('radius')
        method = data.get('method')
        sites_data = data.get('sites')
        barangays_data = data.get('barangays')

        # Validate required parameters
        if not all([address, L, radius, method, sites_data, barangays_data]):
            return Response(
                {'error': 'Missing required parameters: address, L, radius, method, sites, barangays.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Load graph based on address
        G = load_graph(address)
        if G is None:
            return Response(
                {'error': f'Unable to load graph for address: {address}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract site data
        sites = sites_data.get('locations')
        site_names = sites_data.get('names', [])

        # Ensure the names list is the same length as locations
        if len(site_names) != len(sites):
            site_names = [''] * len(sites)

        # Extract barangay data
        barangay_locations = barangays_data.get('locations')
        barangay_populations = barangays_data.get('populations')
        barangay_infected = barangays_data.get('infected')
        barangay_names = barangays_data.get('names', [])

        # Validate barangay data
        if not all([barangay_locations, barangay_populations, barangay_infected]):
            return Response(
                {'error': 'Incomplete barangays data: locations, populations, and infected counts are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(barangay_names) != len(barangay_locations):
            barangay_names = [''] * len(barangay_locations)

        # Create BarangayList object
        barangays = BarangayList(
            locations=barangay_locations,
            populations=barangay_populations,
            infected=barangay_infected
        )

        # Run optimization
        result_indices_list = bi_objective_optimization(L, radius, sites, barangays, distance=road, method=method, G=G)

        if result_indices_list is None:
            return Response(
                {'error': 'Optimization failed due to invalid parameters or data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Map result indices to site names
        selected_sites_list = []
        for indices in result_indices_list:
            selected_sites = [{
                'index': i,
                'name': site_names[i],
                'coordinates': sites[i]
            } for i in indices]
            selected_sites_list.append(selected_sites)

        return Response({'result_indices': result_indices_list, 'selected_sites_list': selected_sites_list})


class DynamicOptimization(APIView):
    def post(self, request):
        data = request.data
        address = data.get('address')
        L = data.get('L')
        method = data.get('method')
        sites_data = data.get('sites')
        barangays_data = data.get('barangays')

        # Validate required parameters
        if not all([address, L, method, sites_data, barangays_data]):
            return Response(
                {'error': 'Missing required parameters: address, L, method, sites, barangays.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Load graph based on address
        G = load_graph(address)
        if G is None:
            return Response(
                {'error': f'Unable to load graph for address: {address}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract site data
        sites = sites_data.get('locations')
        site_names = sites_data.get('names', [])

        # Ensure the names list is the same length as locations
        if len(site_names) != len(sites):
            site_names = [''] * len(sites)

        # Extract barangay data
        barangay_locations = barangays_data.get('locations')
        barangay_populations = barangays_data.get('populations')
        barangay_infected = barangays_data.get('infected')
        barangay_vaccinated = barangays_data.get('vaccinated', [False] * len(barangay_locations))
        barangay_names = barangays_data.get('names', [])

        # Validate barangay data
        if not all([barangay_locations, barangay_populations, barangay_infected]):
            return Response(
                {'error': 'Incomplete barangays data: locations, populations, and infected counts are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(barangay_names) != len(barangay_locations):
            barangay_names = [''] * len(barangay_locations)
        if len(barangay_vaccinated) != len(barangay_locations):
            barangay_vaccinated = [False] * len(barangay_locations)

        # Create BarangayList object
        barangays = BarangayList(
            locations=barangay_locations,
            populations=barangay_populations,
            infected=barangay_infected,
            vaccinated=barangay_vaccinated
        )

        # Run optimization
        result_indices = dynamic_optimization(L, sites, barangays, distance=road, method=method, G=G)

        if result_indices is None:
            return Response(
                {'error': 'Optimization failed due to invalid parameters or data.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Map result indices to site names
        selected_sites = [{
            'index': i,
            'name': site_names[i],
            'coordinates': sites[i]
        } for i in result_indices]

        return Response({'result_indices': result_indices, 'selected_sites': selected_sites})
