def run(rdf, **kwargs):
    print("[AlignmentTest] run() called")
    print("Keys received:", list(kwargs.keys()))
    print("NominalEnergies:", kwargs.get("NominalEnergies"))
    print("areMC:", kwargs.get("areMC"))
    print("Output directory:", kwargs.get("outdir"))

    counts = rdf.Count().GetValue()
    print(f"Number of events: {counts}")
    
    return rdf
