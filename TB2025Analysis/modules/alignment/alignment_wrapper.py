import os

from .selection import selection


def run(rdf, **kwargs):
    outdir = kwargs.get("outdir")
    outdir = os.path.normpath(outdir)
    outdir = os.path.abspath(outdir)

    print(outdir)

    # counts = rdf.Count().GetValue()
    # print(f"Number of events: {counts}")
    # os.chdir(os.path.dirname(__file__))

    selection(rdf, outdir)

    return rdf
