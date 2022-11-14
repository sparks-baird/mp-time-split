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
bibliography: mp-time-split.bib

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


<!-- The latest advances in machine learning are often in natural language processing such as with long
short-term memory networks (LSTMs) and Transformers, or image processing such as with
generative adversarial networks (GANs), variational autoencoders (VAEs), and guided
diffusion models. `xtal2png` encodes and decodes crystal structures via PNG
images (see e.g. \autoref{fig:64-bit}) by writing and reading the necessary information
for crystal reconstruction (unit cell, atomic elements, atomic coordinates) as a square
matrix of numbers. This is akin to making/reading a QR code for crystal
structures, where the `xtal2png` representation is an invertible representation. The
ability to feed these images directly into image-based pipelines allows you, as a
materials informatics practitioner, to get streamlined results for new state-of-the-art
image-based machine learning models applied to crystal structures.

![A real size $64\times64$ pixel `xtal2png` representation of a crystal structure.\label{fig:64-bit}](figures/Zn8B8Pb4O24,volume=623,uid=bc2d.png) -->

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

<!-- Using a state-of-the-art method in a separate domain with a custom data representation
is often an expensive and drawn-out process. For example, [@vaswaniAttentionAllYou2017]
introduced the revolutionary natural language processing Transformer architecture in
June 2017, yet the application of Transformers to the adjacent domain of materials
informatics (chemical-formula-based predictions) was not publicly realized until late
2019 [@goodallPredictingMaterialsProperties2019], approximately two-and-a-half years
later, with peer-reviewed publications dating to late 2020
[@goodallPredictingMaterialsProperties2020]. Interestingly, a nearly identical
implementation was being developed concurrently in a different research group with
slightly later public release [@wangCompositionallyrestrictedAttentionbasedNetwork2020]
and publication [@wangCompositionallyRestrictedAttentionbased2021] dates. Another
example of a state-of-the-art algorithm domain transfer is refactoring image-processing
models for crystal structure applications, which was first introduced in a preprint
[@kipfSemisupervisedClassificationGraph2016] and published with application for
materials' property prediction in a peer-reviewed journal over a year later
[@xieCrystalGraphConvolutional2018]. Similarly, VAEs were introduced in 2013
[@kingmaAutoEncodingVariationalBayes2014a] and implemented for molecules in 2016
[@gomez-bombarelliAutomaticChemicalDesign2016], and denoising diffusion probabilistic
models (DDPMs) were introduced in 2015 [@sohl-dicksteinDeepUnsupervisedLearning2015] and
implemented for crystal structures in 2021 [@xieCrystalDiffusionVariational2021]. Here,
we focus on state-of-the-art domain transfer (especially of generative models) from
image processing to crystal structure to enable materials science practitioners to
leverage the most advanced image processing models for materials' property prediction
and inverse design. -->

<!-- `xtal2png` is a Python package that allows you to convert between a crystal structure
and a PNG image for direct use with image-based machine learning models. Let's take
[Google's image-to-image diffusion model,
Palette](https://iterative-refinement.github.io/palette/)
[@sahariaPaletteImagetoImageDiffusion2022a], which supports unconditional image
generation, conditional inpainting, and conditional image restoration, which are modeling tasks
that can be used in crystal generation, structure prediction, and structure
relaxation, respectively. Rather than dig into the code and spending hours, days, or
weeks modifying, debugging, and playing GitHub phone tag with the developers before you
can (maybe) get preliminary results, `xtal2png` lets you get comparable results using the default parameters, assuming the instructions can be run without
error. While there are other invertible representations for crystal structures
[@xieCrystalDiffusionVariational2022;@renInvertibleCrystallographicRepresentation2022a]
as well as cross-domain conversions such as converting between molecules and strings
[@weiningerSMILESChemicalLanguage1988;@selfies], to our knowledge, this is the first
package that enables conversion between a crystal structure and an image file format.

![(a) upscaled example image and (b) legend of the `xtal2png` encoding.\label{fig:example-and-legend}](figures/example-and-legend.png)

`xtal2png` was designed to be easy to use by both
"[Pythonistas](https://en.wiktionary.org/wiki/Pythonista)" and entry-level coders alike.
`xtal2png` provides a straightforward Python application programming interface (API) and
command-line interface (CLI). `xtal2png` relies on `pymatgen.core.structure.Structure`
[@ongPythonMaterialsGenomics2013] objects for representing crystal structures and also
supports reading crystallographic information files (CIFs) from directories. `xtal2png`
encodes crystallographic information related to the unit cell, crystallographic
symmetry, and atomic elements and coordinates which are each scaled individually
according to the information type. An upscaled version of the PNG image and a legend of
the representation are given in \autoref{fig:example-and-legend}. Due to the encoding of
numerical values as PNG images (allowable values are integers between 0 and
255), a round-off error is present during a single round of encoding and decoding.
An example comparing an original vs. decoded structure is given in
\autoref{fig:original-decoded}.

There are some limitations and design considerations for `xtal2png` that are described
in `xtal2png`'s [documentation](https://xtal2png.readthedocs.io/en/latest/index.html) in
the Overview section.
At this time, it is unclear to what extent deviation from the aforementioned design
choices will affect performance. We intend to use hyperparameter optimization to
determine an optimal configuration for crystal structure generation tasks using the
`xtal2png` representation.

![(a) Original and (b) `xtal2png` decoded visualizations of
[`mp-560471`](https://materialsproject.org/materials/mp-560471/) / Zn$_2$B$_2$PbO$_6$. Images were generated using [ase visualizations](https://wiki.fysik.dtu.dk/ase/ase/visualize/visualize.html). \label{fig:original-decoded}](figures/original-decoded.png){ width=50% }

The significance of the representation lies in being able to directly use the PNG
representation with image-based models which often do not directly support custom
dataset types. We expect the use of `xtal2png` as a screening tool for such models to
save significant user time of code refactoring and adaptation during the process of
obtaining preliminary results on a newly released model. After obtaining preliminary
results, you get to decide whether it's worth it to you to take on the
higher-cost/higher-expertise task of modifying the codebase and using a more customized
approach. Or you can stick with the results of xtal2png. It's up to you!

We plan to apply `xtal2png` to a probabilistic diffusion generative model as a
proof of concept and present our findings in the near future. -->

<!-- ![Caption for example figure.\label{fig:example}](figure.png) -->

<!-- # Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text. -->

<!--
# Citations
Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)" -->

<!-- # Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% } -->

# Acknowledgements

S.G.B. and T.D.S. acknowledge support by the National Science Foundation, USA under
Grant No. DMR-1651668.

# References
