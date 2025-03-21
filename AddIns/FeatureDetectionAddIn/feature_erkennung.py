import adsk.core, adsk.fusion, adsk.cam, traceback, json, os
import math
from .Bohrungen import *
from .aas_upload import *
_app = adsk.core.Application.get()
_ui = _app.userInterface

def filter_zero_and_null(data):
    """Rekursiv durchläuft das Dictionary oder die Liste und entfernt Werte, die 0.0 oder None sind,
    außer in 'coordinates' und 'direction'."""
    if isinstance(data, dict):
        filtered = {}
        for k, v in data.items():
            if k in ["coordinates", "direction"]:
                filtered[k] = v
            else:
                value = filter_zero_and_null(v)
                if value not in [0.0, None, {}, []]:
                    filtered[k] = value
        return filtered
    elif isinstance(data, list):
        return [filter_zero_and_null(v) for v in data if v not in [0.0, None]]
    else:
        return data


 #* ---------------------------- Hole recognition ----------------------------------- *#

def is_valid(recognized_hole, hole_pattern):
    i = j = 0
    n, m = len(recognized_hole), len(hole_pattern)

    while i < n and j < m:
        current_dynamic = hole_pattern[j]
        optional = None in current_dynamic
        allowed = [v for v in current_dynamic if v is not None]

        if recognized_hole[i] in allowed:
            i += 1
            j += 1
        elif optional:
            j += 1
        else:
            return False

    while j < m:
        if None not in hole_pattern[j]:
            return False
        j += 1

    return i == n

def get_hole_direction(hole):
    try:
        direction = hole.axis
        return {
            "dx": round(direction.x, 3),
            "dy": round(direction.y, 3),
            "dz": round(direction.z, 3)
        }
    except:
        _ui.messageBox("Fehler beim Abrufen der Richtung der Bohrung.")
        return {"dx": 0.0, "dy": 0.0, "dz": 1.0}

def get_mapping(recognized_hole, hole_pattern):
    mapping = []
    i = j = 0
    n, m = len(recognized_hole), len(hole_pattern)

    while i < n and j < m:
        current_dynamic = hole_pattern[j]
        optional = None in current_dynamic
        allowed = [v for v in current_dynamic if v is not None]

        if recognized_hole[i] in allowed:
            mapping.append(i)
            i += 1
            j += 1
        elif optional:
            mapping.append(None)
            j += 1
        else:
            return None

    while j < m:
        if None not in hole_pattern[j]:
            return None
        mapping.append(None)
        j += 1

    return mapping if i == n else None


def recognize_holes(hole, design):
    segments = []
    angle_dict = {}

    for i in range(hole.segmentCount):
        segment = hole.segment(i)
        segment_type = ""
        is_through = hole.isThrough

        if segment.holeSegmentType == adsk.cam.HoleSegmentType.HoleSegmentTypeCylinder:
            segment_type = "Cylinder"
        elif segment.holeSegmentType == adsk.cam.HoleSegmentType.HoleSegmentTypeCone:
            segment_type = "Cone"
            angle = round(segment.halfAngle * (180 / math.pi), 2)
        elif segment.holeSegmentType == adsk.cam.HoleSegmentType.HoleSegmentTypeFlat:
            segment_type = "Flat"

        if segment_type == "Cone":
            if not "W1" in angle_dict:
                angle_dict["W1"] = angle
            elif not "W2" in angle_dict:
                angle_dict["W2"] = angle
            elif not "W3" in angle_dict:
                angle_dict["W3"] = angle

        segments.append({
            "type": segment_type,
            "height": round(segment.height * 10, 3),
            "diameter": round(segment.topDiameter * 10, 3)
        })

    classified_hole = classify_hole(segments, angle_dict, is_through)
    coordinates = hole.top.asArray()
    direction = get_hole_direction(hole)

    return {
        "hole_type": classified_hole.hole_type,
        "parameters": classified_hole.get_parameter(),
        "coordinates": {
            "x": round(coordinates[0] * 10, 3),
            "y": round(coordinates[1] * 10, 3),
            "z": round(coordinates[2] * 10, 3)
        },
        "direction": direction
    }


def classify_hole(segments: list[dict], angles: dict, is_through: bool) -> BaseHole:
    segment_types = [segment["type"] for segment in segments]

    hole_configs = [
        {
            "hole_class": Grundbohrung,
            "pattern": Grundbohrung.segmente,
            "conditions": lambda: not is_through,
            "param_logic": lambda mapping, segs: {
                "DB": segs[mapping[1]]["diameter"],
                "T": sum(s["height"] for s in segs),
                "F": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W": angles.get("W1"),
                "SW": angles.get("W2")
            }
        },
        {
            "hole_class": EbeneGrundbohrung,
            "pattern": EbeneGrundbohrung.segmente,
            "conditions": lambda: not is_through,
            "param_logic": lambda mapping, segs: {
                "DB": segs[mapping[1]]["diameter"],
                "T": sum(s["height"] for s in segs),
                "F": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W": angles.get("W1"),
            }
        },
        {
            "hole_class": Durchgangsbohrung,
            "pattern": Durchgangsbohrung.segmente,
            "conditions": lambda: is_through,
            "param_logic": lambda mapping, segs: {
                "DB": segs[mapping[1]]["diameter"],
                "L": sum(s["height"] for s in segs),
                "F1": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W1": angles.get("W1"),
                "F2": segs[mapping[2]]["height"] if mapping[2] is not None else 0.0,
                "W2": angles.get("W2"),
            }
        },
        {
            "hole_class": DurchgangsbohrungMitSchutzsenkung,
            "pattern": DurchgangsbohrungMitSchutzsenkung.segmente,
            "conditions": lambda: is_through,
            "param_logic": lambda mapping, segs: {
                "DS": segs[mapping[0]]["diameter"],
                "TS": segs[mapping[0]]["height"],
                "DB": segs[mapping[2]]["diameter"],
                "L": sum(s["height"] for s in segs),
                "F1": segs[mapping[1]]["height"] if mapping[1] is not None else 0.0,
                "W1": angles.get("W1"),
                "F2": segs[mapping[3]]["height"] if mapping[3] is not None else 0.0,
                "W2": angles.get("W2"),
            }
        },
        {
            "hole_class": DurchgangsbohrungMit2Fasen,
            "pattern": DurchgangsbohrungMit2Fasen.segmente,
            "conditions": lambda: is_through,
            "param_logic": lambda mapping, segs: {
                "DB": segs[mapping[2]]["diameter"],
                "L": sum(s["height"] for s in segs),
                "F1": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W1": angles.get("W1"),
                "F2": segs[mapping[1]]["height"] if mapping[1] is not None else 0.0,
                "W2": angles.get("W2"),
                "F3": segs[mapping[3]]["height"] if mapping[3] is not None else 0.0,
                "W3": angles.get("W3"),
            }
        },
        {
            "hole_class": DurchgangsbohrungMitFlachsenkung,
            "pattern": DurchgangsbohrungMitFlachsenkung.segmente,
            "conditions": lambda: is_through,
            "param_logic": lambda mapping, segs: {
                "DF": segs[mapping[1]]["diameter"],
                "DB": segs[mapping[4]]["diameter"],
                "TF": sum(s["height"] for s in segs[:2]),
                "L": sum(s["height"] for s in segs),
                "F1": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W1": angles.get("W1"),
                "F2": segs[mapping[3]]["height"] if mapping[3] is not None else 0.0,
                "W2": angles.get("W2"),
                "F3": segs[mapping[5]]["height"] if mapping[5] is not None else 0.0,
            }
        },
        {
            "hole_class": DurchgangsbohrungMitAufbohrung,
            "pattern": DurchgangsbohrungMitAufbohrung.segmente,
            "conditions": lambda: is_through,
            "param_logic": lambda mapping, segs: {
                "DA": segs[mapping[1]]["diameter"],
                "DB": segs[mapping[3]]["diameter"],
                "TA": sum(s["height"] for s in segs[:2]),
                "L": sum(s["height"] for s in segs),
                "F1": segs[mapping[0]]["height"] if mapping[0] is not None else 0.0,
                "W1": angles.get("W1"),
                "F2": segs[mapping[3]]["height"] if mapping[3] is not None else 0.0,
                "W2": angles.get("W2"),
                "F3": segs[mapping[4]]["height"] if mapping[4] is not None else 0.0,
                "W3": angles.get("W3"),
            }
        },
    ]

    for config in hole_configs:
        if (is_valid(segment_types, config["pattern"]) and config.get("conditions", lambda: True)()):  # <-- Bedingung prüfen
            _app.log(f"segment_types: {segment_types}")
            mapping = get_mapping(segment_types, config["pattern"])
            _app.log(f"Mapping: {mapping}")

            if mapping:
                params = config["param_logic"](mapping, segments)
                return config["hole_class"](**params)

    return BaseHole("Unclassified", segment_types)



#* ---------------------------- Hole recognition ----------------------------------- *#
#? ---------------------------- POCKET recognition ----------------------------------- ?#
def get_all_pockets(body):
    directions = [
        adsk.core.Vector3D.create(0, 0, -1),
        adsk.core.Vector3D.create(0, 0, 1),
        adsk.core.Vector3D.create(1, 0, 0),
        adsk.core.Vector3D.create(-1, 0, 0),
        adsk.core.Vector3D.create(0, 1, 0),
        adsk.core.Vector3D.create(0, -1, 0)
    ]

    pockets_with_dir = []

    for direction in directions:
        try:
            pockets = adsk.cam.RecognizedPocket.recognizePockets(body, direction)

            for pocket in pockets:
                pockets_with_dir.append({'pocket': pocket, 'direction': direction})

        except:
            _ui.messageBox(f"Fehler bei der Suche nach Taschen in Richtung {direction.asArray()}.")

    unique_pockets = remove_duplicate_pockets(pockets_with_dir)
    return unique_pockets


def remove_duplicate_pockets(pockets_with_dir):
    unique = []
    seen = set()

    for item in pockets_with_dir:
        pocket = item['pocket']
        direction = item['direction']
        pocket_center = calculate_pocket_center(pocket)

        if pocket_center is None:
            continue

        pocket_key = (
            round(abs(pocket_center.x), 3),
            round(abs(pocket_center.y), 3),
            round(pocket_center.z, 3),
        )

        if pocket_key not in seen:
            seen.add(pocket_key)
            unique.append(item)

    return unique


def calculate_pocket_center(pocket):
    boundary_points = get_boundary_points(pocket)
    if not boundary_points:
        return None

    center_x = sum(pt.x for pt in boundary_points) / len(boundary_points)
    center_y = sum(pt.y for pt in boundary_points) / len(boundary_points)


    if pocket.isThrough:
        center_z = -pocket.depth / 2
    else:
        bottom_face_z = min(pt.z for pt in boundary_points)
        center_z = bottom_face_z + (pocket.depth / 2)

    return adsk.core.Point3D.create(center_x, center_y, center_z)

def get_boundary_points(pocket: adsk.cam.RecognizedPocket) -> list:
    points = []
    for boundary in pocket.boundaries:
        for curve in boundary:
            if isinstance(curve, adsk.core.Line3D):
                points.append(curve.startPoint)
                points.append(curve.endPoint)
            elif isinstance(curve, adsk.core.Arc3D):
                points.append(curve.startPoint)
                points.append(curve.endPoint)
    readable_points = [
        f"({point.x}, {point.y}, {point.z})"
        for point in points
    ]
    return points

def is_circular_pocket(pocket: adsk.cam.RecognizedPocket) -> bool:
    for boundary in pocket.boundaries:
        for curve in boundary:
            if not isinstance(curve, adsk.core.Circle3D):
                return False
    return True

def process_pocket_data(pocket, design, direction):
    pocket_type = "Through Pocket" if pocket.isThrough else "Blind Pocket"
    pocket_closure = "Closed Pocket" if pocket.isClosed else "Open Pocket"
    pocket_center = calculate_pocket_center(pocket)
    boundary_points = get_boundary_points(pocket)

    raw_boundary_points = [{
        "x": round(pt.x * 10, 3),
        "y": round(pt.y * 10, 3),
        "z": round(pt.z * 10, 3)
    } for pt in boundary_points] if boundary_points else []

    unique_boundary_points = []
    seen = set()
    for pt in raw_boundary_points:
        key = (pt["x"], pt["y"], pt["z"])
        if key not in seen:
            seen.add(key)
            unique_boundary_points.append(pt)

    return {
        "pocket_type": pocket_type,
        "pocket_closure": pocket_closure,
        "depth": round(pocket.depth * 10, 3),
        "center_coordinates": {
            "x": round(pocket_center.x * 10, 3) if pocket_center else 0.0,
            "y": round(pocket_center.y * 10, 3) if pocket_center else 0.0,
            "z": round(pocket_center.z * 10, 3) if pocket_center else 0.0
        },
        "recognition_direction": {
            "dx": round(direction.x, 3),
            "dy": round(direction.y, 3),
            "dz": round(direction.z, 3)
        },
        "boundary_points": unique_boundary_points
    }




#? ---------------------------- Hole recognition ----------------------------------- ?#

""" ---------------------------- Main ----------------------------------- """

def run(user_input):
    try:
        doc = _app.activeDocument
        des = doc.products.itemByProductType('DesignProductType')
        body = des.rootComponent.bRepBodies[0]

        component_name = des.rootComponent.name
        component_id = doc.name.split('.')[0]

        feature_data = {
            "component_id": component_id,
            "component_name": component_name,
            "holes": [],
            "pockets": []
        }

        recognizedHolesInput = adsk.cam.RecognizedHolesInput.create()
        holeGroups = adsk.cam.RecognizedHoleGroup.recognizeHoleGroupsWithInput([body], recognizedHolesInput)
        for holeGroup in holeGroups:
            for hole in holeGroup:
                hole_data = recognize_holes(hole, des)
                feature_data["holes"].append(hole_data)

        pockets_with_dir = get_all_pockets(body)
        for item in pockets_with_dir:
            pocket = item['pocket']
            direction = item['direction']

            if not pocket.isClosed:
                continue

            if is_circular_pocket(pocket):
                continue

            pocket_data = process_pocket_data(pocket, des, direction)
            feature_data["pockets"].append(pocket_data)


        filtered_feature_data = filter_zero_and_null(feature_data)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "Feature_daten.json")

        if not output_path.lower().endswith('.json'):
            output_path += '/Feature_daten.json'

        directory = os.path.dirname(output_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(output_path):
            with open(output_path, 'w') as f:
                json.dump({}, f)

        with open(output_path, 'w') as json_file:
            json.dump(filtered_feature_data, json_file, indent=4)

        create_submodels_for_all_features(
            output_path,
            user_input["serverUrl"],
            user_input["submodelUrl"],
            user_input["conceptUrl"]
        )

        _ui.messageBox(f"Daten gespeichert und gesendet: {output_path}")

    except Exception as e:
        _ui.messageBox(f"Kritischer Fehler: {str(e)}\n{traceback.format_exc()}")
