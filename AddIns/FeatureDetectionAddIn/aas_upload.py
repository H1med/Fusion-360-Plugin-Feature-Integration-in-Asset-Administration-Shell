import json
import requests
import base64


def base64_encode(value):
    return base64.b64encode(value.encode()).decode()

def aas_shell_exists(server_url, aas_id):
    aas_id = base64_encode(aas_id)
    response = requests.get(f"{server_url}/{aas_id}")
    return response.status_code == 200

def submodel_exists(submodel_url, submodel_id):
    submodel_id = base64_encode(submodel_id)
    response = requests.get(f"{submodel_url}/{submodel_id}")
    return response.status_code == 200

def description_exists(concept_url, description_id):
    description_id = base64_encode(description_id)
    response = requests.get(f"{concept_url}/{description_id}")
    return response.status_code == 200

def create_aas_shell(server_url, file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    submodel_name = f"recognizedFeatures_{data['component_id']}"

    aas_shell = {
        "modelType": "AssetAdministrationShell",
        "id": f"https://example.com/ids/sm/{data['component_id']}",
        "idShort": data["component_name"],
        "assetInformation": {
            "assetKind": "NotApplicable",
            "globalAssetId": data["component_id"]
        },
        "submodels": [
            {
                "type": "ModelReference",
                "keys": [
                    {
                        "type": "Submodel",
                        "value": submodel_name
                    }
                ]
            }
        ]
    }

    if not aas_shell_exists(server_url, aas_shell["id"]):
        response = requests.post(server_url, json=aas_shell)
        print(f"AAS-Shell erstellt: {response.status_code} - {response.text}")
        return submodel_name
    else:
        print("AAS-Shell existiert bereits. Überspringe Erstellung.")
        return None


def create_concept_description(concept_url, cd_id, id_short, description, unit):
    concept_description = {
        "id": f"https://example.com/ids/cd/{cd_id}",
        "idShort": id_short,
        "modelType": "ConceptDescription",
        "description": [{"language": "de", "text": description}],
        "embeddedDataSpecifications": [
            {
                "dataSpecification": {
                    "type": "ExternalReference",
                    "keys": [{"type": "GlobalReference", "value": "https://admin-shell.io/DataSpecificationTemplates/DataSpecificationIEC61360/3/0"}]
                },
                "dataSpecificationContent": {
                    "preferredName": [{"language": "de", "text": description}],
                    "unit": unit,
                    "modelType": "DataSpecificationIec61360"
                }
            }
        ]
    }
    if not description_exists(concept_url, concept_description["id"]):
        response = requests.post(concept_url, json=concept_description)
        print(f"Concept Description {id_short} erstellt: {response.status_code} - {response.text}")
    else:
        print(f"Concept Description {id_short} existiert bereits.")

def create_main_submodel(submodel_url, submodel_name):
    submodel_id = submodel_name
    submodel = {
        "modelType": "Submodel",
        "id": submodel_id,
        "idShort": submodel_name,
        "submodelElements": [
            {
                "idShort": "Features",
                "modelType": "SubmodelElementCollection",
                "value": []
            }
        ]
    }
    if not submodel_exists(submodel_url, submodel["id"]):
        response = requests.post(submodel_url, json=submodel)
        print(f"Main Submodel erstellt: {response.status_code} - {response.text}")
    else:
        print("Submodel existiert bereits. Überspringe Erstellung.")

def add_feature_to_features(submodel_url, submodel_name, feature, index, feature_type):
    feature_collection = {
        "idShort": f"{feature_type}_{index:03d}",
        "modelType": "SubmodelElementCollection",
        "value": [
            {"idShort": "FeatureID", "modelType": "Property", "valueType": "xs:string", "value": f"{feature_type}ID_{index}"},
            {"idShort": "Name", "modelType": "Property", "valueType": "xs:string", "value": feature.get(f"{feature_type.lower()}_type", "Unknown")},
            {"idShort": "Type", "modelType": "Property", "valueType": "xs:string", "value": feature_type}
        ]
    }

    properties_collection = {
        "idShort": "Properties",
        "modelType": "SubmodelElementCollection",
        "value": []
    }

    if feature_type == "Hole":
        for param, value in feature["parameters"].items():
            if value is not None:
                properties_collection["value"].append({
                    "idShort": param,
                    "modelType": "Property",
                    "valueType": "double",
                    "value": value,
                    "semanticId": {
                        "type": "ModelReference",
                        "keys": [{"type": "ConceptDescription", "value": f"https://example.com/ids/cd/{param}"}]
                    }
                })
    elif feature_type == "Pocket":
        pocket_params = {
            "Depth": feature["depth"],
            "Closure": feature["pocket_closure"]
        }
        for param, value in pocket_params.items():
            if value is not None:
                value_type = "double" if param == "Depth" else "xs:string"
                properties_collection["value"].append({
                    "idShort": param,
                    "modelType": "Property",
                    "valueType": value_type,
                    "value": value,
                    "semanticId": {
                        "type": "ModelReference",
                        "keys": [{"type": "ConceptDescription", "value": f"https://example.com/ids/cd/{param}"}]
                    }
                })

    feature_collection["value"].append(properties_collection)

    if "coordinates" in feature or "center_coordinates" in feature:
        position_collection = {
            "idShort": "Position",
            "modelType": "SubmodelElementCollection",
            "value": []
        }

        coordinates = feature.get("coordinates", feature.get("center_coordinates", {}))
        for axis in ["x", "y", "z"]:
            if axis in coordinates:
                position_collection["value"].append({
                    "idShort": axis.upper(),
                    "modelType": "Property",
                    "valueType": "double",
                    "value": coordinates[axis]
                })

        direction_data = feature.get("direction") or feature.get("recognition_direction")
        if direction_data:
            direction_collection = {
                "idShort": "Direction",
                "modelType": "SubmodelElementCollection",
                "value": []
            }
            for axis in ["dx", "dy", "dz"]:
                if axis in direction_data:
                    direction_collection["value"].append({
                        "idShort": axis.upper().replace("d", "D"),
                        "modelType": "Property",
                        "valueType": "double",
                        "value": direction_data[axis]
                    })
            position_collection["value"].append(direction_collection)

        feature_collection["value"].append(position_collection)

    if feature_type == "Pocket" and "boundary_points" in feature:
        boundary_points_collection = {
            "idShort": "BoundaryPoints",
            "modelType": "SubmodelElementCollection",
            "value": []
        }
        for i, bp in enumerate(feature["boundary_points"]):
            bp_collection = {
                "idShort": f"BP_{i:03d}",
                "modelType": "SubmodelElementCollection",
                "value": []
            }
            for axis in ["x", "y", "z"]:
                if axis in bp:
                    bp_collection["value"].append({
                        "idShort": axis.upper(),
                        "modelType": "Property",
                        "valueType": "double",
                        "value": bp[axis]
                    })
            boundary_points_collection["value"].append(bp_collection)
        feature_collection["value"].append(boundary_points_collection)

    submodel_id_encoded = base64_encode(submodel_name)
    url = f"{submodel_url}/{submodel_id_encoded}/submodel-elements/Features"
    response = requests.post(url, json=feature_collection)
    print(f"{feature_type} {index} hinzugefügt: {response.status_code} - {response.text}")


def create_submodels_for_all_features(file_path, server_url, submodel_url, concept_url):
    submodel_name = create_aas_shell(server_url, file_path)
    if submodel_name:

        create_main_submodel(submodel_url, submodel_name)

        create_concept_description(concept_url, "DB", "Durchmesser der Bohrung", "Der Durchmesser der zylindrischen Bohrung", "mm")
        create_concept_description(concept_url, "T", "Tiefe der Bohrung", "Die Gesamttiefe der zylindrischen Bohrung", "mm")
        create_concept_description(concept_url, "L", "Länge der Bohrung", "Die Gesamtlänge der Bohrung von der Oberfläche bis zum Grund", "mm")
        create_concept_description(concept_url, "F", "Tiefer der Fase", "Die Tiefe der Fase", "mm")
        create_concept_description(concept_url, "W", "Winkel der Fase", "Der Winkel der Fase relativ zur Oberfläche", "Grad")
        create_concept_description(concept_url, "F1", "Tiefer der Fase", "Die Tiefe der ersten Fase", "mm")
        create_concept_description(concept_url, "W1", "Winkel der Fase", "Der Winkel der ersten Fase", "Grad")
        create_concept_description(concept_url, "F2", "Tiefer der Fase", "Die Tiefe der zweiten Fase", "mm")
        create_concept_description(concept_url, "W2", "Winkel der Fase", "Der Winkel der zweiten Fase", "Grad")
        create_concept_description(concept_url, "F3", "Tiefer der Fase", "Der Winkel der dritten Fase", "mm")
        create_concept_description(concept_url, "W3", "Winkel der Fase", "Der Winkel der dritten Fase", "Grad")
        create_concept_description(concept_url, "SW", "Spitzenwinkel", "Der Spitzenwinkel einer kegelförmigen Spitze einer Bohrung", "Grad")
        create_concept_description(concept_url, "DS", "Durchmesser der Schutzsenkung", "Der Durchmesser einer Schutzsenkung", "mm")
        create_concept_description(concept_url, "TS", "Tiefe der Schutzsenkung", "Die Tiefe der Schutzsenkung", "mm")
        create_concept_description(concept_url, "DF", "Durchmesser der Flachsenkung", "Der Durchmesser einer flachen Senkung", "mm")
        create_concept_description(concept_url, "TF", "Tiefe der Flachsenkung", "Die Tiefe der Flachsenkung von der Oberfläche bis zur Grundfläche", "mm")
        create_concept_description(concept_url, "DA", "Durchmesser der Aufbohrung", "Der Durchmesser einer Aufbohrung", "mm")
        create_concept_description(concept_url, "TA", "Tiefe der Aufbohrung", "Die Tiefe einer Aufbohrung", "mm")
        create_concept_description(concept_url, "Depth", "Depth", "Die Tiefe einer Tasche", "mm")

        with open(file_path, "r") as file:
            data = json.load(file)

        holes = data.get("holes", [])
        pockets = data.get("pockets", [])

        for idx, hole in enumerate(holes):
            add_feature_to_features(submodel_url, submodel_name, hole, idx, "Hole")

        for idx, pocket in enumerate(pockets):
            add_feature_to_features(submodel_url, submodel_name, pocket, idx, "Pocket")
