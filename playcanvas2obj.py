import argparse
import contextlib
import json
import re
import sys
import urllib.error
import urllib.request


def main(input_data, output_file):
    vertices = extract_coords(input_data, "position")
    normals = extract_coords(input_data, "normal")
    faces = extract_faces(input_data, vertices)

    try:
        write_obj_coords("v", vertices, output_file)
        write_obj_coords("vn", normals, output_file)
        write_obj_faces(faces, output_file)
    except BrokenPipeError:
        sys.stdout = None # https://stackoverflow.com/a/69833114/151221


def write_obj_coords(prefix, coords, output_file):
    """
    Write a series of coordinates in OBJ format to the given destination file.
    """
    labels = {"v": "vertices", "vn": "vertex normals"}
    assert prefix in labels, f"unknown OBJ prefix: {prefix}"

    for coord in coords:
        formatted_coords = " ".join(f"{n: f}" for n in coord)
        print(f"{prefix} {formatted_coords}", file=output_file)
    print(f"# {len(coords)} {labels[prefix]}\n", file=output_file)


def write_obj_faces(vertex_indices, output_file):
    """
    Write a series of OBJ faces to the given destination file.
    """
    for i, indices in enumerate(vertex_indices):
        formatted_faces = " ".join(f"{n}//{i+1}" for n in indices)
        print(f"f {formatted_faces}", file=output_file)
    print(f"# {len(vertex_indices)} faces\n", file=output_file)


def extract_coords(input_data, key):
    """
    Returns a list of (x, y, z) coordinates for the given key in the input
    data.
    """
    assert len(input_data["model"]["vertices"]) == 1
    source = input_data["model"]["vertices"][0][key]
    assert source["components"] == 3

    results = []
    for coord in gen_batches(source["data"], source["components"]):
        results.append(coord)
    return results


def extract_faces(input_data, vertices):
    """
    Returns a list of 3-tuple indexes into the vertex list for the input data.
    """
    assert len(input_data["model"]["meshes"]) == 1
    mesh = input_data["model"]["meshes"][0]
    assert mesh["vertices"] == 0
    assert mesh["type"] == "triangles"
    assert mesh["base"] == 0

    vertex_count = len(vertices)
    results = []
    for indices in gen_batches(mesh["indices"], 3):
        assert all(i < vertex_count for i in indices), f"face index in {indices} out of bounds"
        # obj indexes are 1-based, playcanvas indexes are 0-based
        results.append(tuple(i + 1 for i in indices))
    return results



def gen_batches(xs, size):
    """
    Given a sequence xs and a batch size, yield batches from the sequence as
    lists of length size, where the last batch might be smaller than the rest.
    """
    assert size > 0
    acc = []
    for i, x in enumerate(xs):
        if i and i % size == 0:
            yield acc
            acc = []
        acc.append(x)
    if acc:
        assert len(acc) == size, f"sequence not evenly divisible by batch size {size}"
        yield acc


def load_input(url_or_path):
    """
    Load a JSON model from the given input URL or path.
    """
    opener = open
    if re.match(r"^https?://", url_or_path):
        opener = urllib.request.urlopen
    try:
        with opener(url_or_path) as f:
            return json.loads(f.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"failed to load URL {url_or_path}: {e}")
    except FileNotFoundError:
        raise RuntimeError(f"file not found: {url_or_path}")
    except json.decoder.JSONDecodeError as e:
        raise RuntimeError(f"invalid JSON in {url_or_path}: {e}")


@contextlib.contextmanager
def open_output(path):
    """
    Returns an output file pointer ready for writing, properly handling stdout
    vs files on disk.
    """
    if not path or path == "-":
        yield sys.stdout
    else:
        with open(path, "w") as f:
            yield f

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert playcanvas.com JSON format into OBJ format')
    parser.add_argument('input', metavar='INPUT', help='Input file URL (or local file path)')
    parser.add_argument('-o', '--output', dest='output_path', default="-", help="Output file path (defaults to STDOUT)")
    args = parser.parse_args()
    try:
        input_data = load_input(args.input)
        with open_output(args.output_path) as output_file:
            main(input_data, output_file)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
