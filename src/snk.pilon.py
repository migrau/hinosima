#########################################################################################################
# snk.pilon.py                                                                                       	#
#                                                                                                       #
## Script to polish a PacBio assembly using PILON and illumina raw reads. 	                            #
# 1. BWA alignment.                                                            							#
# 2. Samtools conversion                                                                      			#
# 3. pilon run                                                                          				#
#                                                                                                       #
## Requirements:                                                                                        #
# - pacbio assembly (from canu, falcon, etc)                                                            #
# - Illumina (paired) reads, fastq format                                                               #
#                                                                                                       #
## Example run:                                                                                         #        
# one node, cpus=24  [1 run with 24threads]                                                             #
# (dry run) $ snakemake --snakefile snk.pilon.py -j 1 --config rawRead1=reads1.fq rawRead2=reads2.fq 	# 
# 																	assembly=assembly.fasta -np			#
#                                                                                                       #
#########################################################################################################

# Globals ---------------------------------------------------------------------

#PATH of pilon
PILONloc="/apps/pilon-1.20/pilon-1.20.jar"

# Illumina raw reads fastq
R1 = config["rawRead1"]
R2 = config["rawRead2"]
# assemnbly folder path 
ASBLY = config["assembly"]

threads="24"

# Rules -----------------------------------------------------------------------

rule all:
  input:
    'pilon.fasta'

rule BWAindex:
	input:
		assembly=ASBLY
	output:
		ASBLY+".amb"
	shell:"""
		bwa index {input}
	"""

rule BWA:
  input:
    r1=R1,
    r2=R2,
    assembly=ASBLY,
    index=ASBLY+".amb"
  output:
    'bwa_alignment.sam'
  params: 
    th=threads
  shell:"""
  	bwa mem -t {params.th} {input.assembly} {input.r1} {input.r2} > {output}
  """

rule samToBam:
  input:
    'bwa_alignment.sam'
  output:
    'bwa_alignment.bam'
  params: 
    th=threads
  shell:"""
  	samtools view --threads {params.th} -o {output} {input}
  """

rule samSORT:
  input:
  	'bwa_alignment.bam'
  output:
    'bwa_alignment.sort.bam'
  params: 
    th=threads
  shell:"""
    samtools sort --threads {params.th} {input} -o {output}
  """
rule samINDEX:
  input:
  	'bwa_alignment.sort.bam'
  output:
    'bwa_alignment.sort.bam.bai'
  shell:"""
    samtools index {input}
  """

rule pilon:
  input:
    alignment='bwa_alignment.sort.bam',
    assembly=ASBLY,
    index='bwa_alignment.sort.bam.bai'
  output:
    'pilon.fasta'
  params:
  	pilonPATH=PILONloc,
  	th=threads,
  	prefix='pilon'
  shell:"""
    module load java-jdk/1.8.0_20
    java -Xms110g -jar {params.pilonPATH} --genome {input.assembly} --frags {input.alignment} --output {params.prefix} --threads {params.th} --verbose
  """