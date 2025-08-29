CLUSTERS = {
    "Theory": {
        "Maths-related": ["MC", "ODE&VC"],
        "Physics-related": ["AP", "BEE", "EDC"],
        "Programming-related": ["PPS", "P_PROG"],
        "Chemistry-related": ["EC"],
        "Language/Communication": ["ESE"],
        "Engineering Graphics": ["CAEG"],
    },
    "Lab": {
        "Physics/Chemistry Labs": ["AP_LAB", "EC_LAB", "BEEE LAB"],
        "Programming/CS Labs": ["ECS_LAB", "PPS LAB", "PP/LAC_LAB"],
        "Maths Labs": ["LAC/PP_LAB"],
        "Language Labs": ["ELCS_LAB"],
        "Workshop": ["EWS_LAB"],
    }
}

# Build subject to cluster type and name mappings
SUBJECT_TO_CLUSTER_TYPE = {}
SUBJECT_TO_CLUSTER_NAME = {
    "BASIC ELECTRICAL AND ELECTRONICS ENGINEERING LABORATORY": "Electrical Labs",
    "BEE": "Electrical",
    "CAEG": "Engineering Graphics",
    "EC": "Chemistry",
    "EDC": "Electronics",
    "ENGINEERING CHEMISTRY LABORATORY": "Chemistry Labs",
    "MATRICES AND CALCULUS": "Mathematics",
    "NAN": "Unknown",
    "PPS": "Programming",
    "PROGRAMMING FOR PROBLEM SOLVING LABORATORY": "Programming Labs",
    "BASIC ELECTRICAL AND ELECTRONICS ENGINEERING LABOR": "Electrical Labs",
    # Add any other short forms you find!
}

SUBJECT_TO_CLUSTER_NAME.update({
    "PROGRAMMING FOR PROBLEM SOLVING": "Programming-related",
    "BASIC ELECTRICAL ENGINEERING": "Physics-related",
    "ENGINEERING CHEMISTRY": "Chemistry-related",
    "ELECTRONIC DEVICES AND CIRCUITS": "Physics-related",
    "COMPUTER AIDED ENGINEERING GRAPHICS": "Engineering Graphics",
    "NAN": "Unknown"
})

SUBJECT_TO_CLUSTER_TYPE.update({
    "PROGRAMMING FOR PROBLEM SOLVING": "Theory",
    "BASIC ELECTRICAL ENGINEERING": "Theory",
    "ENGINEERING CHEMISTRY": "Theory",
    "ELECTRONIC DEVICES AND CIRCUITS": "Theory",
    "COMPUTER AIDED ENGINEERING GRAPHICS": "Theory",
    "NAN": "Unknown"
})

for cluster_type, clusters in CLUSTERS.items():
    for cluster_name, subjects in clusters.items():
        for subj in subjects:
            SUBJECT_TO_CLUSTER_TYPE[subj] = cluster_type
            SUBJECT_TO_CLUSTER_NAME[subj] = cluster_name 