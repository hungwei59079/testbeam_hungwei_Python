
with open("passed_event_indices.txt","r") as file:
    lines = file.readlines()
    event_indices = [int(entry.strip()) for entry in lines]

filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/v4/NANO_999.root"

with open("hit_inspector_jobs.txt","w") as out_file:
    for index in event_indices:
        out_file.write(f"{filename} {index} {index+1}\n")
