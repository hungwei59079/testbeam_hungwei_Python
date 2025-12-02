import os


def run(rdf, **kwargs):
    NominalEnergies = kwargs.get("NominalEnergies")
    areMC = kwargs.get("areMC")
    outdir = kwargs.get("outdir")
    outdir = os.path.normpath(outdir)
    outdir = os.path.abspath(outdir)

    print(outdir)

    counts = rdf.Count().GetValue()
    print(f"Number of events: {counts}")

    return rdf
