import subprocess
import streamlit as st

def run_command(command):
    # Create a placeholder for the output
    output_area = st.empty()
    output_text = ""
    
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr and stdout
        text=True,
        bufsize=1
    )
    
    # Process stdout in real-time
    for line in iter(process.stdout.readline, ''):
        output_text += line
        # Update the display with accumulated output
        output_area.text_area("Output:", output_text, height=400)
    
    process.stdout.close()
    return_code = process.wait()
    
    if return_code != 0:
        st.error(f"Command failed with return code {return_code}")
    
    return return_code



def basecallinganddemuxing():
    st.title("Dorado Basecalling and Demuxing Assistant")
    
    st.write("This script speeds up the Dorado basecalling process by basecalling and demuxing")

    # Get user inputs using Streamlit widgets
    qscore = st.text_input("Enter the minimum q-score")
    deviceType = st.selectbox("Select device type", ["0", "metal"], help="0 for standard GPU, metal for Apple Silicon")
    acc = st.selectbox("Select accuracy type", ["hac", "sup"])
    pod5Dir = st.text_input("Enter path to your pod5 folder or file")
    reference = st.text_input("Enter path to your fasta reference file (optional)")
    moves = st.radio("Emit moves table?", ["Yes", "No"])
    output = st.text_input("Output file name (include extension .bam or .fastq)")
    if(output.endswith('.fastq') != True):
        map0 = st.radio("Remove mapped reads with score of 0?", ["Yes", "No"])
        unmapped = st.radio("Remove unmapped reads?", ["Yes", "No"])

    if st.button("Run Basecalling"):
        with st.spinner("Processing basecalling..."):
            # Emit moves command
            basecaller_command = ""
            if moves.lower() == 'Yes':
                basecaller_command = "dorado basecaller --emit-moves "
            else:
                basecaller_command = "dorado basecaller "

            basecaller_command += f"--min-qscore {qscore} --device {deviceType} /Users/akhilpeddikuppa/dorado_models/dna_r10.4.1_e8.2_400bps_{acc}@v5.0.0 {pod5Dir} "
            if(output.endswith("fastq")):
                basecaller_command += "--emit-fastq "
            if reference == "":
                basecaller_command += f"--kit-name SQK-NBD114-24 > {output}"
            else:
                basecaller_command += f"--reference {reference} --no-trim --kit-name SQK-NBD114-24 > {output}"
            
            st.subheader("Basecalling Command")
            st.code(basecaller_command, language="bash")
            
            with st.expander("Basecalling Output", expanded=True):
                return_code = run_command(basecaller_command)
                if return_code == 0:
                    st.success("Basecalling completed successfully!")
                else:
                    st.error("Basecalling failed!")
                    return

            if(map0.lower() == "Yes" and output.endswith('.fastq') != True):
                st.subheader("Processing mapped reads")
                map0_command = f"samtools view -b -q 1 {output} > {output}_map0.bam"
                st.code(map0_command, language="bash")
                with st.expander("Mapping Output", expanded=True):
                    run_command(map0_command)
                output = f"{output}_map0"
            
            if(unmapped.lower() == "Yes" and output.endswith('.fastq') != True):
                st.subheader("Processing unmapped reads")
                if(map0.lower() == "Yes"):
                    unmapped_command = f"samtools view -F 4 -b {output}.bam > {output}_unmapped_remove.bam"
                else:
                    unmapped_command = f"samtools view -F 4 -b {output}.bam > {output}_unmapped_remove.bam"
                st.code(unmapped_command, language="bash")
                with st.expander("Unmapped Reads Output", expanded=True):
                    run_command(unmapped_command)
                output = f"{output}_unmapped_remove"

            
            
            st.subheader("Demultiplexing")
            demux_command = ""
            if(output.endswith("fastq")):
                if(map0.lower() == "Yes"):
                    if(unmapped.lower() == "Yes"):
                        demux_command = f"dorado demux --emit-fastq -o {output}_demuxed --no-classify --no-trim {output}"
                    else:
                        demux_command = f"dorado demux --emit-fastq -o {output}_demuxed --no-classify --no-trim {output}"
                else:
                    demux_command = f"dorado demux --emit-fastq -o {output}_demuxed --no-classify --no-trim {output}"
            else:
                demux_command = f"dorado demux -o {output}_demuxed --no-classify {output}"
            
            st.code(demux_command, language="bash")
            with st.expander("Demultiplexing Output", expanded=True):
                return_code = run_command(demux_command)
                if return_code == 0:
                    st.success("Demultiplexing completed successfully!")
                else:
                    st.error("Demultiplexing failed!")

        st.success("All processing completed!")

if __name__ == "__main__":
    basecallinganddemuxing()
