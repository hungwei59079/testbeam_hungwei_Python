from pathlib import Path

CONDOR_DIR = Path(__file__).resolve().parents[1]
OUT_PATH = CONDOR_DIR / "input"/ "hit_inspector_jobs.txt"

filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/v5/NANO_999.root"
event_per_batch = 3
event_start = 0
number_of_jobs = 100

with open(OUT_PATH, "w") as file:
    for i in range(number_of_jobs):
        file.write(f"{filename} {event_start} {event_start + event_per_batch}\n")
        event_start += event_per_batch
