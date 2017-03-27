# hinosima
High-Noise Single-Molecule sequence Assembly pipeline

## Description 

Set of different tools to perfom an assembly using High-Noise Single-Molecule sequences (from PacBio or Nanopore).

## Contents

* _src/snk_canupipe.py_ . Run correction of pacbio reads and performs a canu assembly.
* _src/snk.quiver2.3.py_ . Polish canu assembly using Quiver 2.3.
* _src/snk.quiver3.0.py_ . Polish canu assembly using Quiver 3.0.
* _src/snk.pilon.py_ . Polish canu assembly using Pilon 1.20.

### snk_canupipe

First, it uses [colormap](https://github.com/cchauve/CoLoRMap) or [proovread](https://github.com/BioInf-Wuerzburg/proovread) to run a correction of pacbio reads (long reads) using illumina reads (short reads). Since it takes long time (colormap runs bwa two times during the process, proovread is faster but takes time anyway), the script splits the pacbio reads (by default in 999 sub-files), it runs the correction in parallel and finally it merges the results.

Second, [canu](https://github.com/marbl/canu) performs the assembly.

_Considerations_

- Replace the _numJobs_-_threadsCorrection_ (colormap) and _genomeSize_ (canu) as needed.
- Script optimized to run on a slurm cluster.
- python/3.5.0 required to run the snakemake script.

_Usage_

```{bash}
(dry run) $ snakemake -j 60 --snakefile snk_canupipe.py --cluster "sbatch --partition=compute --cpus-per-task=12 --time=14-0 --job-name=snkmk --mem=20GB" --config pfasta=pacbio.fasta ifasta=illumina.fastq fix=colormap -np
```

To use proovread instead:
```{bash}
(dry run) $ snakemake -j 60 --snakefile snk_canupipe.py --cluster "sbatch --partition=compute --cpus-per-task=12 --time=14-0 --job-name=snkmk --mem=20GB" --config pfasta=pacbio.fasta ifasta=illumina.fastq fix=proovread -np
```

_Possible improvements_

- ~~~Add polishing step, after the canu assembly, using pacbio reads (quiver) or illumina reads (pilon)~~~ done.

### snk_quiver2.3

Once the assembly is obtained (from canu or falcon for example), the result can be polished using the PacBio reads and [Quiver](https://github.com/PacificBiosciences/GenomicConsensus). The _snk.quiver2.3.py_ script uses SMRTANALYSIS V2.3. The steps are:

 1. Create fofn files from the input bax.h5.
 2. Run pbalign on each fofn file.
 3. Merge all the cmp.h5 files ([pbh5tools](https://github.com/PacificBiosciences/pbh5tools/blob/master/doc/index.rst)).
 4. Sort the cmp.h5 single file.
 5. Run quiver.

_Installation notes_

Download and install [SMRT ANAlYSIS V2.3](http://www.pacb.com/support/software-downloads/).
Before run the script, the SMRTANALYSIS installation path variable _SMRTloc_ has to be edited.

_Requirements_

 - Raw reads in bax.h5 format
 - Assembly in fasta format.

_Usage_

In case we run the script in a single node, the available threads will be limited by the available cpus on the node:
```{bash}
(dry run) $ snakemake --snakefile snk_quiver2.3.py -j 1 --config rdir=raw_bax.h5_folder/ assembly=canu.fasta -np
 ```
It can be run also in multi-node mode (for example, 80 jobs at once, each one with 24 threads):
```{bash}
(dry run) $ snakemake -j 80 --snakefile snk_quiver2.3.py --cluster-config cluster.json --cluster "sbatch --partition=compute --cpus-per-task=1 --time=14-0 --job-name=snkmk --mem=10GB" --config rdir=raw_bax.h5_folder/ assembly=canu.fasta -np
```
_Considerations_

Last step (the quiver run itself) has high memory demand. It took ~7 days for a ~450Mbps genome using, at least, 1T of memory.

Snakemake cluster config file is attached.

Script based in the [PacificBiosciences tutorial](https://github.com/PacificBiosciences/pbalign/wiki/Tutorial:-How-to-divide-and-conquer-large-RSII-dataset-using-pbalign-and-blasr-in-SMRTAnalysis-2.3-(and-previous-version))

Useful links [1](https://github.com/PacificBiosciences/GenomicConsensus/blob/master/doc/HowTo.rst) [2](https://github.com/PacificBiosciences/GenomicConsensus/blob/master/doc/HowTo.rst) [3](https://github.com/PacificBiosciences/FALCON/issues/304) [4](https://github.com/PacificBiosciences/pbalign/issues/16) [5](https://github.com/PacificBiosciences/pbalign/issues/67) [6](https://github.com/PacificBiosciences/FALCON_unzip/issues/12)

### snk_quiver3.0

There are important differences using the SMRTANALYSIS V3.0, since quiver started to work with bam files instead h5 format. In this case, the steps are:

 1. Convert bax.h5 files to bam
 2. Run pbalign with each bam file.
 3. Merge all the pbalign bam files output in a single bam file ([bamtools](https://github.com/PacificBiosciences/PacBioFileFormats/wiki/BAM-recipes)). 
 4. (sort/index bam and index fasta)
 5. run Quiver.

_Run notes_

Download and install [pitchfork](https://github.com/PacificBiosciences/pitchfork/)
Before run the script, the SMRTANALYSIS installation path variable _SMRTloc_ has to be edited.

_Requirements_

 - Raw reads in bax.h5 format
 - Canu/falcon assembly in fasta format.
 
_Usage_

In case we run the script in a single node, the available threads will be limited by the available cpus on the node:
```{bash}
(dry run) $ snakemake --snakefile snk_quiver3.0.py -j 1 --config rdir=raw_bax.h5_folder/ assembly=canu.fasta -np
 ```
It can be run also in multi-node mode (for example, 80 jobs at once, each one with 24 threads):
```{bash}
(dry run) $ snakemake -j 80 --snakefile snk_quiver3.0.py --cluster-config cluster.json --cluster "sbatch --partition=compute --cpus-per-task=1 --time=14-0 --job-name=snkmk --mem=10GB" --config rdir=raw_bax.h5_folder/ assembly=canu.fasta -np
```
_Considerations_

To convert the h5 files to BAM, it uses the [recommended parammeters](https://github.com/PacificBiosciences/blasr/wiki/bax2bam-wiki:-installation,-basic-usage-and-FAQ) propagating additional pulse features (QVs).

Last step (the quiver run itself) has high memory demand. It took ~7 days for a ~450Mbps genome using, at least, 1T of memory.

Snakemake cluster config file is attached.

### snk.pilon

To perform a polishing using Illumina reads instead PacBio reads we can use [PILON](https://github.com/broadinstitute/pilon/wiki).

 1. BWA alignments using the pacbio assembly and the raw illumina reads.
 2. Samtools conversion.
 3. Pilon.
 
_Requeriments_

 - PacBio assembly (canu, falcon...)
 - Illumina (paired) raw reads.

_Run notes_

Edit _PILONloc_ with the pilon location.
Pilon tested using java-jdk/1.8.0_20.
Run on a node with 24 threads available.

_Usage_

```{bash}
(dry run) $ snakemake --snakefile snk.pilon.py -j 1 --config rawRead1=reads1.fq rawRead2=reads2.fq assembly=assembly.fasta -np
```

### Coming soon

 - colormap pre-correction (using illumina reads).
 - ~~pilon polishing (using illumina reads)~~.
 - Generate a falcon assembly and merge it with the canu one.
 - Generate quiver report.
 


