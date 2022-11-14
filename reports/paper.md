---
title: 'mp-time-split: A Python package for creating time-based splits of Materials Project crystal structures for generative modeling benchmarking'
tags:
  - Python
  - materials informatics
  - crystal structure
  - generative modeling
  - TimeSeriesSplit
authors:
  - name: Sterling G. Baird
    orcid: 0000-0002-4491-6876
    equal-contrib: false
    corresponding: true
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: Joseph Montoya
    orcid: 0000-0001-5760-2860
    affiliation: "2"
  - name: Taylor D. Sparks
    orcid: 0000-0001-8020-7711
    equal-contrib: false
    affiliation: "1" # (Multiple affiliations must be quoted)
affiliations:
 - name: Materials Science & Engineering, University of Utah, USA
   index: 1
 - name: Toyota Research Institute, Los Altos, CA, USA
   index: 2
date: 14 November 2022
bibliography: paper.bib

# # Optional fields if submitting to a AAS journal too, see this blog post:
# # https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

The progress of a machine learning field is both tracked and propelled through the
development of robust benchmarks. In the field of materials informatics, benchmarks
often consist of standard metrics such as mean absolute error (MAE) and root mean
squared error (RMSE) using traditional train-test splits. In the case of materials
discovery, one domain-specific metric involves the ability to successfully predict
known materials which have been held out. For experimental materials discovery, a robust
measure of performance is whether or not we can predict materials of the future based
only on training data from the past. In
other words: "how well can we predict what will be discovered in the future?" In the
Materials Project database [@jain_commentary_2013], there are
records of when experimentally validated compounds were first reported in the
literature. As a robust validation setup, we formalize the time-series splits of
Materials Project crystal structures for use in generative modeling benchmarking via the
`mp-time-split` Python package (see \autoref{fig:summary}). The Python package provides convenience functions for
downloading and processing snapshots of experimentally verified Materials Project
entries and creating  random time-series splits of the data.

![Summary visualization of splitting Materials Project entries into train and test
splits using grouping by first report of experimental verification in the
literature.\label{fig:summary}](figures/time-split-abstract.png)

<!--- Mention similar options in molecular discovery benchmarking, e.g. guacamol which I believe has something similar in terms of rediscovery, though maybe not time-based. Mention legacy materials informatics (CrabNet, CGCNN, etc.) and the shift towards inverse design via generative modeling (CDVAE, FTCP, PGCGM, CubicGAN, etc.). --->


# Statement of need

Time-based splits have been used in the past for validating materials informatics
models. For example, Jain et al. [@tshitoyanUnsupervisedWordEmbeddings2019] "tested whether [the] model -- if trained at various
points in the past -- would have correctly predicted thermoelectric materials reported
later in the literature." Likewise, Montoya et al. [@palizhati_agents_2022] "seeded [multi-fidelity agents with
the] first 500 experimentally discovered compositions (based on ICSD58 timeline of their
first publication) and their corresponding DFT data." Hummelshøj et al.
[@aykol_network_2019] describe the
difficulties associated with predicting future trends of materials discovery in the
time-evolution of a materials stability network. We note that each of these examples
used bespoke splitting of the data. Recently, Hu et al. [@zhao_physics_2022] used a rediscovery metric to
evaluate the results of their generative model for crystal structure, though this was
not using a time-based split. The need to generate millions of structures to replicate
small portions of the heldout dataset highlights the difficulty of the task. When used
with other benchmarking metrics, time-based rediscovery can provide the rigor required
to effectively evaluate the performance of generative materials discovery models.
`mp-time-split` acts as a convenient, standardized backend for rediscovery benchmarking
metrics as well as other applications such as the ones listed previously.

In particular, the `mp-time-split` package provides the following features:
- downloading and storing snapshots of Materials Project crystal structures via pymatgen [REF]
  (experimentally verified, theoretical, or both)
- modification of search criteria to fetch custom datasets
- utilities for post-processing the Materials Project entries
- convenient access to a snapshot dataset
- predefined scikit-learn TimeSeriesSplit cross-validation splits [REF]

We believe `mp-time-split` provides the convenience and standardization required of
rigorous benchmarking of generative materials discovery models. `mp-time-split` serves
as the basis for a set of benchmarking metrics hosted in the [`matbench-genmetrics`](https://github.com/sparks-baird/matbench-genmetrics) suite
which has recently been applied to `xtal2png` [@baird_xtal2png_2022], a generative model for crystal structure.

# Acknowledgements

S.G.B. and T.D.S. acknowledge support by the National Science Foundation, USA under
Grant No. DMR-1651668.

# References
