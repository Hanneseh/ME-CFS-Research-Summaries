---

title: "Leveraging Explainable Automated Machine Learning (AutoML) and Metabolomics for Robust Diagnosis and Pathophysiological Insights in Myalgic Encephalomyelitis/Chronic Fatigue Syndrome (ME/CFS)"
tags:
- ➕ 2025-12-25
- 🧪 Biomarker
created: '2025-10-30'
published: '2025-10-30'

---


<details>
<summary>Yagin et al. (2025)</summary>

- **Authors:** Fatma Hilal Yagin, Cemil Colak, Fahaid Al-Hashem, Sarah A. Alzakari, Amel Ali Alhussan, Mohammadreza Aghaei.
- **Institutes:** Malatya Turgut Ozal University; Lakehead University; Inonu University; King Khalid University; Princess Nourah bint Abdulrahman University; Norwegian University of Science and Technology (NTNU).
- **Publisher:** Diagnostics
- **Link:** [DOI](https://doi.org/10.3390/diagnostics15212755)

</details>


## Summary

This research demonstrates that advanced artificial intelligence can accurately identify ME/CFS patients using blood metabolic profiles, achieving a diagnostic accuracy of over 87%. By decoding the AI's decision-making process, the study provides biochemical evidence supporting patient experiences of energy deficits, pointing specifically to blocks in the cellular energy cycles (mitochondria) and muscle metabolism. This supports the validity of ME/CFS as a physiological condition with measurable biological abnormalities. While not yet a commercially available test, this approach highlights specific targets—such as the glycolysis-TCA transition and specific lipids—that could form the basis for future clinical diagnostics and targeted treatments.

## What was researched?

This study investigated the use of advanced Automated Machine Learning (AutoML) to detect ME/CFS by analyzing plasma metabolomic and lipidomic profiles. The researchers aimed to identify a high-performance predictive model and use Explainable Artificial Intelligence (XAI) to interpret the biological meaning behind the model's decisions. Specifically, they benchmarked three AutoML frameworks—TPOT, Auto-Sklearn, and H2O AutoML—to see which could most accurately distinguish patients from healthy controls.

## Why was it researched?

ME/CFS is a complex disease that currently lacks objective diagnostic biomarkers, leading to delayed diagnoses and inadequate management. While metabolomics offers a window into the cellular activity of the disease, the data is high-dimensional and difficult to analyze using traditional statistical methods. The authors utilized AutoML to automate the complex process of model selection and optimization, hoping to discover robust diagnostic patterns and biological insights that might be missed by human experts or standard techniques.

## How was it researched?

The study utilized a publicly available dataset containing 888 metabolic features (metabolites and lipids) from 106 ME/CFS patients and 91 matched healthy controls. The researchers cleaned the data and imputed missing values using a method called MICE. They then trained three different AutoML frameworks under identical time constraints to classify the participants. The models were validated using a rigorous process called Repeated Random Sub-sampling (repeated 100 times) to ensure the results were reliable. Finally, they used SHAP (SHapley Additive Explanations) analysis to visualize which specific metabolites were most important for the model's predictions.

## What has been found?

The TPOT framework significantly outperformed the other models, achieving a high diagnostic accuracy of 87.3%, with a sensitivity of 85.8% and specificity of 89.0%. Through SHAP analysis, the optimal model identified a distinct metabolic signature for ME/CFS. Key findings included elevated levels of succinic acid and pyruvic acid, suggesting disruptions in mitochondrial energy metabolism (specifically the TCA cycle and glycolysis transition). The model also identified decreased levels of leucine (linked to muscle fatigue) and prostaglandin $D_{2}$ (an inflammatory mediator), as well as alterations in gut-brain axis markers like glycocholic acid.

## Discussion

The authors highlight that their TPOT-derived model provides both a robust diagnostic tool and biologically interpretable insights. The identification of elevated pyruvate and succinate supports the "mitochondrial bottleneck" hypothesis and metabolic inflexibility often reported in ME/CFS literature. They note that the decrease in prostaglandin $D_{2}$ was unexpected and may suggest a compensatory shift in chronic inflammation pathways rather than simple immune activation. Limitations of the study include the relatively small sample size, the cross-sectional nature of the data (which prevents proving cause-and-effect), and the lack of real-time symptom tracking during blood collection.

## Conclusion & Future Work

The study concludes that combining AutoML with explainable AI is a powerful approach for distilling complex metabolic data into accurate diagnostics for ME/CFS. The results reinforce the involvement of mitochondrial dysfunction, lipid metabolism issues, and gut-brain axis dysregulation in the disease's pathophysiology. Future research should focus on larger independent cohorts, integration with other "omics" data (like proteomics), and longitudinal studies that track metabolite levels alongside symptom fluctuations.
