#Run root -l -b -q '../hexaplot_helper.C("test_values.txt", "test.png", true)' to generate test.png

with open("test_values.py","w") as file:
    for i in range(222):
        file.write(f"{i}\n")
