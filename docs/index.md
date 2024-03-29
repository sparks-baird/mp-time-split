# Materials Project Time Splits

```{warning}
  As of June 2023, `mp-time-split` has migrated to [**`matbench-genmetrics`**](https://github.com/sparks-baird/matbench-genmetrics) as a namespace package
```

Download Materials Project time-splits for generative modeling benchmarking via the
`mp_time_split` Python package. Download and store a snapshot dataset of experimentally
verified Materials Project entries sorted by earliest publication year of the associated
literature references. Alternatively, fetch your own dataset directly from Materials
Project using your own search criteria. The snapshot dataset, [**MPTS-52**](https://doi.org/10.6084/m9.figshare.19991516.v4),
contains only experimentally verified Materials Project entries with no more than 52
sites) and acts as an extension to the state-of-the-art materials generative model
introduced by Xie et al. via the [CDVAE](https://github.com/txie-93/cdvae) package. We recommend that in addition to the
[three CDVAE benchmark datasets](https://github.com/txie-93/cdvae/tree/main/data), you
also use the **MPTS-52** dataset and corresponding cross-validation and final test
splits for model comparison and benchmarking. **MPTS-52** can be used with the metrics
introduced in CDVAE's
[compute_metrics.py](https://github.com/txie-93/cdvae/blob/main/scripts/compute_metrics.py)
script (see [CDVAE instructions](https://github.com/txie-93/cdvae/issues/10)). Check out
our [quick start page](https://mp-time-split.readthedocs.io/en/latest/readme.html) for more details on how to use `mp_time_split`. Enjoy!

> **See also:** [`matbench-genmetrics`](https://matbench-genmetrics.readthedocs.io/), a materials benchmarking platform for
> generative models and [`xtal2png`](https://xtal2png.readthedocs.io/en/latest/), a tool converting between a crystal structure and a PNG image representation for generative modeling

<a class="github-button" href="https://github.com/sparks-baird/mp-time-split"
data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star
sparks-baird/mp-time-split on GitHub">Star</a>
<a class="github-button"
href="https://github.com/sgbaird" data-size="large" data-show-count="true"
aria-label="Follow @sgbaird on GitHub">Follow @sgbaird</a>
<a class="github-button" href="https://github.com/sparks-baird/mp-time-split/issues"
data-icon="octicon-issue-opened" data-size="large" data-show-count="true"
aria-label="Issue sparks-baird/mp-time-split on GitHub">Issue</a>
<a class="github-button" href="https://github.com/sparks-baird/mp-time-split/discussions" data-icon="octicon-comment-discussion" data-size="large" aria-label="Discuss sparks-baird/mp-time-split on GitHub">Discuss</a>
<br><br>

<!-- ## Note

> This is the main page of your project's [Sphinx] documentation. It is
> formatted in [Markdown]. Add additional pages by creating md-files in
> `docs` or rst-files (formatted in [reStructuredText]) and adding links to
> them in the `Contents` section below.
>
> Please check [Sphinx] and [MyST] for more information
> about how to document your project and how to configure your preferences. -->


## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/

<script async defer src="https://buttons.github.io/buttons.js"></script>
