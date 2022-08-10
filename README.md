# playcanvas2obj

A quick and dirty script that attempts to convert a [PlayCanvas][] JSON model
into a (partial) [Wavefront OBJ][obj] file. See [example_input.json][input] for
an example of the expected input format.

## Current status

This script only knows how to extract the vertices from the input file and
print those vertices in OBJ format.  More complete translation is not yet a
goal.

## Usage

Download the [playcanvas2obj.py script][download] and run it using Python 3,
passing in a URL or local file path pointing to a valid PlayCanvas JSON model.

```bash
# URL as input
python3 playcanvas2obj.py https://raw.githubusercontent.com/mccutchen/playcanvas2obj/main/example_input.json

# Local file as input
python3 playcanvas2obj.py example_input.json
```

By default, output is written to stdout and can be redirected to a file as necessary:

```bash
python3 playcanvas2obj.py example_input.json > example_output.obj
```

Specify the `-o`/`--output` argument to write output to a file instead:

```bash
python3 playcanvas2obj.py example_input.json -o example_output.obj
```

## Output format

The output will be a list of vertexes in [OBJ format][obj]:

```bash
$ python3 playcanvas2obj.py example_input.json | head -10
v -49.528900  201.930000  196.712000
v -44.706600  201.800000  196.670000
v -45.864800  202.291000  196.826000
v -49.021700  202.299000  196.830000
v -49.616000  199.781000  196.027000
v -42.772400  199.255000  195.859000
v -49.397200  199.193000  195.839000
v -47.617700  181.155000  185.601000
v -47.162200  181.472000  185.847000
v -50.034100  181.486000  185.862000
```


[PlayCanvas]: https://playcanvas.com/
[obj]: https://en.wikipedia.org/wiki/Wavefront_.obj_file
[input]: ./example_input.json
[download]: https://raw.githubusercontent.com/mccutchen/playcanvas2obj/main/playcanvas2obj.py
