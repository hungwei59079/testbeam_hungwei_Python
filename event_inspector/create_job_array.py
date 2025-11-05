filename = "eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root"
event_per_batch = 3
event_start = 0
number_of_jobs = 100

with open("hit_inspector_jobs.txt", "w") as file:
    for i in range(number_of_jobs):
        file.write(f"{filename} {event_start} {event_start + event_per_batch}\n")
        event_start += event_per_batch
