# signalfloweeg

*signalfloweeg* is a Python package for EEG signal processing and analysis. It provides a comprehensive set of tools and functions to preprocess, analyze, and visualize EEG data using MNE, a popular open-source library for processing electrophysiological data.

Features
* Preprocessing: Filtering, resampling, artifact rejection, ICA, rereferencing, epoching.
* Feature Extraction: Time-domain, frequency-domain, time-frequency, connectivity, and nonlinear features.
* Decomposition: PCA, ICA, CSP.
* Source Estimation: Beamforming, dipole fitting, MNE.
* Connectivity: Functional connectivity, effective connectivity, graph theory.
* Machine Learning: Supervised learning, unsupervised learning, deep learning, transfer learning.
* Statistical Analysis: Descriptive statistics, statistical inference, multiple comparisons correction.
* Visualization: Raw data plots, time-series plots, topographic maps, source space plots, interactive visualizations.
* Reporting: Report generation, event logging, and notifications.
* Validation: Input validation for MNE object types (Raw, Epochs, Evoked).
* Jupyter Notebook Integration: Interactive widgets, inline visualization, markdown explanations, example datasets, error handling, progress tracking, and interactive debugging.


## Contributing

[Insert contribution guidelines here]

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Preproccessing functions to make first 
import set

FILTERS: 
notch (57-63hz) - DONE, Gavin
lowpass of 100 hz  - DONE, Gavin
highpass of 0.5 hz  - DONE, Gavin

resample (to 500 for human data, to 625 for mouse) - DONE, Gavin
reject bad segments (aka visual continuous artifact rejection) - Working, Gavin
ICA (decompose by ICA, aka independent component analysis) - Done, Nate
reject independent components (aka visual component rejection) - Working, Nate - Need input on manual removal
<!-- Reject bad channels --> - Part of segment rejection - Done 
channel interpolation 
average re-reference
epoching! (1 sec trials)
export set
SET to Excel 
Calc power (and other analyses)



