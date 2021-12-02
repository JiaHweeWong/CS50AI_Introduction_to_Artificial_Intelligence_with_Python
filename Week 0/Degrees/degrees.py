import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # TODO

    # Start with QueueFrontier that contains the initial node
    
    # Create the initial node
    initial_node_movies_id = people[source]['movies']
    initial_node = Node(source,None,initial_node_movies_id,None)

    # Initialize the QueueFrontier
    queue = QueueFrontier()

    # Queue the initial node
    queue.add(initial_node)

    # Start with an empty explored list
    explored = [] # For nodes
    explored_ids = set() # For person_id, for computation efficiency

    # Repeat
    while queue.empty() == False:
        # If QueueFrontier is empty, then return no solution
        # Remove the node from frontier
        curr_node = queue.remove()
        curr_state = curr_node.state # Current state
        # print("curr_state:", curr_state)

        # If node is the target, return the solution (need to find a way to track the paths)
        if curr_state == target:
            path_completed = False # Flag
            solution = [] # (common_movie_id, next_person_id)
            sol_node = curr_node # current solution node
            while path_completed == False:
                # Common movie_id with parent node
                curr_common_movie_id = sol_node.parent_common_movie_id
                # person_id of current solution node
                curr_person = sol_node.state
                sol_pair = (curr_common_movie_id, curr_person) # create tuple
                # print("sol_pair:", sol_pair)
                solution.append(sol_pair) # append tuple to solution list
                sol_node = sol_node.parent # let the next sol_node be the parent node
                if sol_node == initial_node: # if the next sol_node is the initial node
                    path_completed = True # path is completed
            solution.reverse() # reverse the list to get the correct order
            # print("solution:", solution)
            # print(solution)
            return solution # Needs editing

        # Add node to the explored list
        explored.append(curr_node)
        # Add person_id to explored_ids set
        explored_ids.add(curr_state)

        # Obtain the movie_id associated with the node
        node_movie_id_set = curr_node.action # Obtain all the movies_id the person starred in
        person_movie_pairs = [] # Initialize a list to store (person_id, common_movie_id) 
        for movie_id in node_movie_id_set:
            stars = list(movies[movie_id]['stars']) # person_id of all the stars in each movies_id
            for star in stars:
                if star not in explored_ids: # if peron_id/node has not been explored
                    pair = (star, movie_id)
                    person_movie_pairs.append(pair) # append the person_id for creation of new nodes
        
        # Create the new nodes and queue them
        for pair in person_movie_pairs:
            person_id = pair[0]
            common_movie_id = pair[1]
            node_movie_id = people[person_id]['movies'] # person_id's movie_id
            new_node = Node(person_id, curr_node,node_movie_id,common_movie_id) # Create new node
            queue.add(new_node) # Queue the new node


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
