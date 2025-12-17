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

    rdf_sel = selection(rdf, outdir)

    """
    rdf_sel, idxs = selection(rdf, outdir, return_index = True)
    with open("passed_event_indices.txt","w") as file:
        for idx in idxs:
            file.write(f"{idx}\n") 
    """
    return rdf
