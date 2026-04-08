# Eco points system based on waste category

ECO_POINTS_TABLE = {
    "organic": 18,
    "paper": 12,
    "glass": 25,
    "plastic": 20,
    "metal": 30,
    "mixed": 15
}


def calculate_points(waste_type):

    points = ECO_POINTS_TABLE.get(waste_type, 0)

    return points