import math
from copy import deepcopy

# Helper function for Euclidean distance
def euclidean_distance(loc1, loc2):
    return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

# CSP Solver for VRPTW
class CSP_VRPTW:
    def __init__(self, customers, vehicle_capacity, num_vehicles):
        self.customers = customers # List of customer data
        self.vehicle_capacity = vehicle_capacity # Capacity of each vehicle
        self.num_vehicles = num_vehicles # Number of available vehicles
        self.num_customers = len(customers) # Total number of customers
        self.depot = 0  # Assuming the first customer is the depot

        # Variables (excluding the depot)
        self.variables = list(range(1, self.num_customers))  # Exclude the depot

        # Domains for variables: available vehicles
        self.domains = {v: list(range(self.num_vehicles)) for v in self.variables}

        # Precompute the distance matrix between all locations
        self.distance_matrix = self._create_distance_matrix()

        # Assignment state
        self.assignments = {}
        self.routes = {v: [] for v in range(self.num_vehicles)}

    # Create the distance matrix for all locations
    def _create_distance_matrix(self):
        locations = [(c["x"], c["y"]) for c in self.customers]
        size = len(locations)
        dist_matrix = [[0] * size for _ in range(size)]
        for i in range(size):
            for j in range(size):
                dist_matrix[i][j] = euclidean_distance(locations[i], locations[j])
        return dist_matrix

    # Check if a variable assignment is consistent with constraints
    def is_consistent(self, variable, value, route):
        # Ensure the customer is not already assigned to another route
        if variable in [cust for r in self.routes.values() for cust in r]:
            return False  # Prevent repeating customers

        # Check if adding this customer exceeds the vehicle's capacity
        total_demand = sum(self.customers[c]["demand"] for c in route) + self.customers[variable]["demand"]
        if total_demand > self.vehicle_capacity:
            return False

        # Validate that time windows are respected
        return self._validate_time_windows(route + [variable])

    # Validate time windows for a given route
    def _validate_time_windows(self, route):
        time = 0 # Start time
        for i, cust in enumerate(route):
            travel_time = self.distance_matrix[route[i - 1]][cust] if i > 0 else self.distance_matrix[self.depot][cust]
            time += travel_time

            # Ensure arrival is within the ready_time and due_time
            time = max(time, self.customers[cust]["ready_time"])
            if time > self.customers[cust]["due_time"]:
                return False  # Cannot start service beyond due_time

            # Add service time
            time += self.customers[cust]["service_time"]

        return True

    # Perform a backtracking search to find a solution
    def backtracking_search(self):
        return self._backtrack()

    # Forward checking to reduce domains of unassigned variables
    def _forward_checking(self, variable, value):
        original_domains = deepcopy(self.domains)
        for neighbor in self.variables:
            if neighbor not in self.assignments:
                self.domains[neighbor] = [
                    v for v in self.domains[neighbor]
                    if self.is_consistent(neighbor, v, deepcopy(self.routes[v]))
                ]
                if not self.domains[neighbor]:
                    self.domains = original_domains # Restore domains if inconsistent
                    return False
        return True

    # Ensure arc consistency for the CSP
    def _arc_consistency(self):
        queue = [(var, neighbor) for var in self.variables for neighbor in self.variables if var != neighbor]
        while queue:
            x, y = queue.pop(0)
            if self._revise(x, y):
                if not self.domains[x]:
                    return False # Domain of a variable is empty
                for z in self.variables:
                    if z != x and z != y:
                        queue.append((z, x))
        return True

    # Revise the domain of a variable to ensure consistency with another variable
    def _revise(self, x, y):
        revised = False
        for value in self.domains[x][:]:
            if not any(self.is_consistent(x, value, deepcopy(self.routes[value])) for value in self.domains[y]):
                self.domains[x].remove(value)
                revised = True
        return revised

    # Backtracking algorithm for the CSP
    def _backtrack(self):
        if len(self.assignments) == len(self.variables):
            return self.routes

        variable = self._select_unassigned_variable()
        for value in sorted(self.domains[variable], key=lambda v: self._least_constraining_value(variable, v)):
            if self.is_consistent(variable, value, deepcopy(self.routes[value])):
                self.assignments[variable] = value
                self.routes[value].append(variable)

                # Save current routes to restore later if needed
                previous_routes = deepcopy(self.routes)
                if self._forward_checking(variable, value):
                    result = self._backtrack()
                    if result is not None:
                        return result

                # Undo the assignment and restore routes
                self.assignments.pop(variable)
                self.routes = previous_routes

        return None

    # Select the next variable to assign based on the MRV heuristic
    def _select_unassigned_variable(self):
        unassigned = [v for v in self.variables if v not in self.assignments]
        return min(unassigned, key=lambda var: len(self.domains[var]))

    # Least constraining value heuristic to prioritize values with minimal impact
    def _least_constraining_value(self, variable, value):
        count = 0
        for neighbor in self.variables:
            if neighbor not in self.assignments and value in self.domains[neighbor]:
                count += 1
        return count

    # Solve the VRPTW problem using backtracking and arc consistency
    def solve(self):
        # Prioritize minimizing the number of vehicles by initially limiting the domain to fewer vehicles.
        for vehicle_limit in range(1, self.num_vehicles + 1):
            print(f"Trying with {vehicle_limit} vehicles...")
            self.domains = {v: list(range(vehicle_limit)) for v in self.variables}
            self.routes = {v: [] for v in range(vehicle_limit)}
            self.assignments = {}

            if self._arc_consistency(): # Enforce arc consistency before backtracking
                solution = self.backtracking_search()
                if solution:
                    print("Solution found!")
                    return solution

        print("No solution found.")
        return None

    # Calculate the total distance for all routes
    def calculate_total_distance(self):
        total_distance = 0
        for vehicle, route in self.routes.items():
            if not route:
                continue
            dist = self.distance_matrix[self.depot][route[0]] # From depot to first customer
            for i in range(len(route) - 1):
                dist += self.distance_matrix[route[i]][route[i + 1]]
            dist += self.distance_matrix[route[-1]][self.depot] # Back to depot
            total_distance += dist
        return total_distance

    # Format the solution into a human-readable format
    def format_solution(self):
        formatted_routes = []
        for vehicle, route in self.routes.items():
            if route:
                formatted_routes.append(f"Route {vehicle + 1} : 0 {' '.join(map(str, route))} 0")
        total_distance = self.calculate_total_distance()
        return '\n'.join(formatted_routes), len(formatted_routes), total_distance

# File Parsing
def parse_solomon_file(file_path, max_customers=None):
    # Parse a single Solomon dataset file and optionally limit to the first `max_customers`
    with open(file_path, "r") as file:
        lines = file.readlines()

    vehicle_info = {}
    customers = []
    lines = [line.strip() for line in lines if line.strip()]

    for i, line in enumerate(lines):
        if line.startswith("VEHICLE NUMBER"):
            vehicle_info["number"] = int(line.split()[-1])
        elif line.startswith("CAPACITY"):
            vehicle_info["capacity"] = int(line.split()[-1])
        elif line.startswith("CUST NO."):
            for customer_line in lines[i + 1:]:
                data = customer_line.split()
                if len(data) >= 7:
                    customers.append({
                        "id": int(data[0]),
                        "x": float(data[1]),
                        "y": float(data[2]),
                        "demand": int(data[3]),
                        "ready_time": int(data[4]),
                        "due_time": int(data[5]),
                        "service_time": int(data[6]),
                    })
            break

    if max_customers:
        customers = customers[:max_customers]

    return vehicle_info, customers

# Process Multiple Files
def process_solomon_folder(folder_path, max_customers=None, output_file="results.csv"):
    import os
    import csv

    results = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            try:
                vehicle_info, customers = parse_solomon_file(file_path, max_customers=max_customers)

                csp = CSP_VRPTW(customers, vehicle_info["capacity"], vehicle_info["number"])
                print(f"Processing file: {file_name}")
                solution = csp.solve()

                if solution:
                    routes, num_vehicles, total_distance = csp.format_solution()
                    results.append({
                        "File": file_name,
                        "Vehicles Used": num_vehicles,
                        "Total Distance": total_distance,
                        "Routes": routes
                    })
                else:
                    results.append({
                        "File": file_name,
                        "Vehicles Used": "No Solution",
                        "Total Distance": "No Solution",
                        "Routes": "No Solution"
                    })
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
                results.append({
                    "File": file_name,
                    "Vehicles Used": "Error",
                    "Total Distance": "Error",
                    "Routes": str(e)
                })

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["File", "Vehicles Used", "Total Distance", "Routes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {output_file}.")

# Main Execution
def main():
    folder_path = "solomon-100"
    output_file = "results.csv"
    process_solomon_folder(folder_path, max_customers=100, output_file=output_file)

if __name__ == "__main__":
    main()
