import json
import shutil
from pathlib import Path

DATA_FILE = Path("data/seed_data.json")
BACKUP_FILE = Path("data/seed_data-before-duration.json")

# Create a fresh backup from the current file
shutil.copy2(DATA_FILE, BACKUP_FILE)

with DATA_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)


def set_duration(node, duration):
    if isinstance(node, dict):
        node["duration"] = duration


def set_path_duration(stream, path_id, duration):
    path = stream.get("paths", {}).get(path_id)

    if not path:
        missing.append(f"{path_id}")
        return

    children = path.get("children")

    if children:
        for child in children.values():
            set_duration(child, duration)
            updated.append(path_id)
    else:
        set_duration(path, duration)
        updated.append(path_id)


# ---------------------------------------------------------
# DURATION DATA
# ---------------------------------------------------------

DURATIONS = {

    "mpc": {
        "engineering": {
            "cse": "4 years",
            "aids": "4 years",
            "aiml": "4 years",
            "it": "4 years",
            "cybersecurity": "4 years",
            "datascience": "4 years",
            "ece": "4 years",
            "eee": "4 years",
            "mechanical": "4 years",
            "civil": "4 years",
            "chemical": "4 years",
            "aeronautical": "4 years",
            "aerospace": "4 years",
            "automobile": "4 years",
            "mechatronics": "4 years",
            "robotics": "4 years",
            "biotech": "4 years",
            "biomedical": "4 years",
            "agricultural": "4 years",
            "mining": "4 years",
            "petroleum": "4 years",
            "foodtech": "4 years",
            "textile": "4 years",
            "metallurgical": "4 years",
            "marine": "4 years"
        },

        "degree": {
            "bsc_cs": "3 years",
            "bsc_physics": "3 years",
            "bsc_maths": "3 years",
            "bsc_stats": "3 years",
            "bsc_datascience": "3 years",
            "bca": "3 years",
            "bba": "3 years"
        },

        "architecture": "5 years",
        "nda": "Varies",
        "commercialpilot": "Varies",
        "merchantnavy": "Varies",

        "space": {
            "aerospace": "4 years",
            "isro": "Varies",
            "remotesensing": "3 years",
            "astronaut": "Varies"
        }
    },


    "bipc": {
        "medical": {
            "mbbs": "5.5 years",
            "bds": "5 years",
            "bams": "5.5 years",
            "bhms": "5.5 years",
            "bums": "5.5 years"
        },

        "pharmacynursing": {
            "bpharm": "4 years",
            "pharmd": "6 years",
            "bscnursing": "4 years",
            "gnm": "3 years"
        },

        "agriculture": {
            "bscagri": "4 years",
            "horticulture": "4 years",
            "forestry": "4 years",
            "fisheries": "4 years",
            "dairytech": "4 years"
        },

        "alliedhealth": {
            "bpt": "4.5 years",
            "bmlt": "3 years",
            "radiology": "3 years",
            "ottech": "3 years",
            "optometry": "4 years",
            "dialysis": "3 years",
            "cardiaccare": "3 years",
            "respiratory": "4 years",
            "emt": "3 years"
        },

        "science": {
            "biotechsci": "3 years",
            "microbiology": "3 years",
            "biochemistry": "3 years",
            "genetics": "3 years",
            "zoology": "3 years",
            "botany": "3 years",
            "nutrition": "3 years"
        },

        "veterinary": "5.5 years"
    },


    "mec": {
        "commerce": {
            "bcomgeneral": "3 years",
            "bcomcomputers": "3 years",
            "bcomhonours": "3 years",
            "bcomaccfin": "3 years",
            "bcombankins": "3 years"
        },

        "management": {
            "bba": "3 years",
            "bbm": "3 years"
        },

        "professional": {
            "ca": "Varies",
            "cma": "Varies",
            "cs": "Varies"
        },

        "economics": {
            "baeconomics": "3 years",
            "bsceconomics": "3 years"
        },

        "banking": "Not applicable",
        "finance": "Varies",
        "investment": "Varies",
        "actuarial": "Varies"
    },


    "cec": {
        "bcom": "3 years",
        "bba": "3 years",
        "bbm": "3 years",

        "ba": {
            "bapolisci": "3 years",
            "baeconomics": "3 years",
            "bapublicadmin": "3 years"
        },

        "llb": "3 or 5 years",
        "journalism": "3 years",
        "hotelmanagement": "3 years",
        "traveltourism": "3 years",
        "eventmanagement": "3 years",
        "business": "Varies",
        "realestate": "Varies"
    },


    "hec": {
        "humanities": {
            "bahistory": "3 years",
            "baeconomics": "3 years",
            "bapolisci": "3 years",
            "bapublicadmin": "3 years",
            "basociology": "3 years",
            "bapsychology": "3 years"
        },

        "bsw": "3 years",
        "llb": "3 or 5 years",
        "journalism": "3 years",
        "librarysci": "3 years",
        "teaching": "Varies",
        "civilservices": "Varies",
        "politics": "Varies",
        "professor": "Varies",
        "allindiaservices": "Varies",
        "judiciary": "Varies"
    },


    "polytechnic": {
        "dme": "3 years",
        "dce": "3 years",
        "deee": "3 years",
        "dece": "3 years",
        "dcse": "3 years",
        "automobile": "3 years",
        "daiml": "3 years",
        "daids": "3 years",
        "dit": "3 years",
        "dcybersecurity": "3 years",
        "dchemical": "3 years",
        "dmining": "3 years",
        "dmetallurgical": "3 years",
        "dagricultural": "3 years",
        "dtextile": "3 years",
        "dprinting": "3 years",
        "darchitecture": "3 years"
    },


    "iti": {
        "electrician": "2 years",
        "fitter": "2 years",
        "welder": "1 year",
        "turner": "2 years",
        "machinist": "2 years",
        "mechanicdiesel": "1 year",
        "mechanicmv": "2 years",
        "copa": "1 year",
        "stenographer": "1 year",
        "plumber": "1 year",
        "refrigerationac": "2 years",
        "wireman": "2 years",
        "electronicsmechanic": "2 years",
        "surveyor": "2 years",
        "draughtsman": "2 years",
        "driver": "Varies"
    },
"vocational": {
    "agriculturevoc": "Varies",
    "healthcarevoc": "Varies",
    "tourismvoc": "Varies",
    "retailvoc": "Varies",
    "computerappsvoc": "Varies",
    "multimediavoc": "Varies",
    "farmervoc": "Varies",
    "ruralhealthworker": "Varies",
    "chef": "Varies",
    "security": "Varies",
    "filmmusic": "Varies",
    "fashiondesign": "Varies",
    "hairstyling": "Varies"
},

"skilldev": {
    "programmingsd": "Varies",
    "graphicdesignsd": "Varies",
    "digitalmarketingsd": "Varies",
    "videoeditingsd": "Varies",
    "webdevsd": "Varies",
    "aidataanalyticssd": "Varies"
},

"defence": {
    "sainikschool": "Varies",
    "ndaprep": "Varies",
    "defenceplanning": "Varies"
},

"govtjobs": {
    "railways": "Not applicable",
    "ssc": "Not applicable",
    "police": "Not applicable",
    "govbanking": "Not applicable",
    "stategovt": "Not applicable",
    "postal": "Not applicable"
}


    }


# ---------------------------------------------------------
# APPLY DURATIONS
# ---------------------------------------------------------

updated = []
missing = []


for stream_id, stream_mapping in DURATIONS.items():

    stream = data.get(stream_id)

    if not stream:
        missing.append(f"STREAM: {stream_id}")
        continue

    paths = stream.get("paths", {})

    for path_id, mapping in stream_mapping.items():

        path = paths.get(path_id)

        if not path:
            missing.append(f"{stream_id}/{path_id}")
            continue


        # Apply same duration to all courses inside a path
        if isinstance(mapping, str):

            children = path.get("children")

            if children:
                for child_id, child in children.items():
                    set_duration(child, mapping)
                    updated.append(
                        f"{stream_id}/{path_id}/{child_id}"
                    )
            else:
                set_duration(path, mapping)
                updated.append(
                    f"{stream_id}/{path_id}"
                )

            continue


        # Apply individual durations to children
        if isinstance(mapping, dict):

            children = path.get("children", {})

            for course_id, duration in mapping.items():

                course = children.get(course_id)

                if not course:
                    missing.append(
                        f"{stream_id}/{path_id}/{course_id}"
                    )
                    continue

                set_duration(course, duration)

                updated.append(
                    f"{stream_id}/{path_id}/{course_id}"
                )


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

with DATA_FILE.open("w", encoding="utf-8") as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("========================================")
print("DURATION UPDATE SUCCESSFUL")
print("========================================")
print(f"Courses/paths updated : {len(updated)}")
print(f"Items not found       : {len(missing)}")
print(f"Backup                : {BACKUP_FILE}")
print("========================================")

if missing:
    print()
    print("NOT FOUND:")
    for item in missing:
        print(" -", item)