import os

def basecallinganddemuxing():
    # Get user input
    print("This script speeds up the Dorado basecalling process by basecalling and demuxing")

    qscore = input("Please enter the minimum q-score:      ")
    deviceType = input("Please enter device type (0 for standard GPU and metal for Apple Silicon):     ")
    acc = input("Please enter accuracy type (hac or sup):        ")
    pod5Dir = input("Drag and drop your pod5 folder or file into terminal:     ")
    reference = input("Drag and drop your fasta reference file (if having fastq, leave this empty):       ")
    moves = input("Emit moves table? (y/n)    ")
    output = input("Output file name (include the file extension, e.g. .bam or .fastq):       ")
    map0 = input("Would you like to remove mapped reads with a score of 0? (y/n):       ")
    unmapped = input("Would you like to remove unmapped reads? (y/n):       ")

    # Emit moves command
    basecaller_command = f""
    if moves.lower() == 'y':
        basecaller_command = f"dorado basecaller --emit-moves "
    else:
        basecaller_command = f"dorado basecaller "

    basecaller_command += f"--min-qscore {qscore} --device {deviceType} /Users/akhilpeddikuppa/dorado_models/dna_r10.4.1_e8.2_400bps_{acc}@v5.0.0 {pod5Dir} "
    if(output.endswith("fastq")):
        basecaller_command += "--emit-fastq "
    if reference.lower() == "":
        basecaller_command += f"--kit-name SQK-NBD114-24 > {output}"
    else:
        basecaller_command += f"--reference {reference} --no-trim --kit-name SQK-NBD114-24 > {output}"
        
    os.system(basecaller_command)

    if(map0.lower() == "y"):
        os.system(f"samtools view -b -q 1 {output} > {output}_map0.bam")
        output = f"{output}_map0"
    
    if(unmapped.lower() == "y"):
        if(map0.lower() == "y"):
            os.system(f"samtools view -F 4 -b {output}.bam > {output}_unmapped_remove.bam")
            output = f"{output}_unmapped_remove"
        else:
            os.system(f"samtools view -F 4 -b {output}.bam > {output}_unmapped_remove.bam")
            output = f"{output}_unmapped_remove"

    
    demux_command = f""
    if(output.endswith("fastq")):
        if(map0.lower() == "y"):
            if(unmapped.lower() == "y"):
                demux_command = f"dorado demux --emit-fastq -o {output}_demuxed --no-classify  --no-trim {output}"
            else:
                demux_command = f"dorado demux --emit-fastq -o {output}_demuxed --no-classify --no-trim {output}"
        
    else:
        demux_command = f"dorado demux -o {output}_demuxed --no-classify {output}"
    os.system(demux_command)



if __name__ == "__main__":
    basecallinganddemuxing()
