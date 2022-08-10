import argparse
import contextlib
import json
import re
import sys
import urllib.error
import urllib.request


def main(input_data, output_file):
    vertices = extract_vertices(input_data)
    write_obj_vertices(vertices, output_file)


def write_obj_vertices(vertices, output_file):
    """
    Write a series of vertex coordinates in OBJ format to the given destination
    file.
    """
    for coords in vertices:
        formatted_coords = " ".join(f"{n: f}" for n in coords)
        try:
            print(f"v {formatted_coords}", file=output_file)
        except BrokenPipeError:
            sys.stdout = None # https://stackoverflow.com/a/69833114/151221


def extract_vertices(input_data):
    """
    Yield a sequence of (x, y, z) coordinates for each vertex in the input
    data.
    """
    vertices = input_data["model"]["vertices"]
    for vertex in vertices:
        position = vertex["position"]
        for batch in gen_batches(position["data"], position["components"]):
            yield batch


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
