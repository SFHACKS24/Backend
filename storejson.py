import json
compatibilitiesStruct={
    0:{
        1:{"qnsRanking":[],"compatibilityScore":0},
        2:{"qnsRanking":[],"compatibilityScore":0},
        3:{"qnsRanking":[],"compatibilityScore":0},
        4:{"qnsRanking":[],"compatibilityScore":0},
    },
    1:{
        0:{"qnsRanking":[],"compatibilityScore":0},
        2:{"qnsRanking":[],"compatibilityScore":0},
        3:{"qnsRanking":[],"compatibilityScore":0},
        4:{"qnsRanking":[],"compatibilityScore":0},
    },
    2:{
        0:{"qnsRanking":[],"compatibilityScore":0},
        1:{"qnsRanking":[],"compatibilityScore":0},
        3:{"qnsRanking":[],"compatibilityScore":0},
        4:{"qnsRanking":[],"compatibilityScore":0},
    },
    3:{
        0:{"qnsRanking":[],"compatibilityScore":0},
        1:{"qnsRanking":[],"compatibilityScore":0},
        2:{"qnsRanking":[],"compatibilityScore":0},
        4:{"qnsRanking":[],"compatibilityScore":0},
    },
    4:{
        0:{"qnsRanking":[],"compatibilityScore":0},
        1:{"qnsRanking":[],"compatibilityScore":0},
        2:{"qnsRanking":[],"compatibilityScore":0},
        3:{"qnsRanking":[],"compatibilityScore":0},
    }
}

#file_path = 'compatibility.json'

# Open the file for writing
with open(file_path, 'w') as file:
    # Use json.dump to write the dictionary to the file
    json.dump(compatibilitiesStruct, file, indent=4)

print(f"Dictionary saved to {file_path}")