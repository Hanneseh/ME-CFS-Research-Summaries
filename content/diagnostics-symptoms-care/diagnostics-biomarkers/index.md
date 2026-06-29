---
title: Diagnostics & Biomarkers
description: A living thread on diagnostic tests, biomarker panels, machine-learning classifiers, biosensors, assays, and measurement tools for ME/CFS and Long COVID.
date: 2026-05-29
last_updated: 2026-05-29
thread_status: active
evidence_level: early clinical validation
primary_topics:
  - Diagnostic Biomarkers
  - Machine Learning Classifiers
  - Blood-Based Tests
  - Omics Profiling
  - Biosensors
  - Patient Stratification
cssclasses: [thread-page]
---

## Current Takeaway

No single biomarker or diagnostic test for ME/CFS has reached clinical deployment, but a growing body of blood-based, genomic, metabolomic, and functional studies has moved the field from exclusion-by-symptoms toward measurable biological signatures. Epigenetic profiling, circulating cell-free RNA, extracellular vesicle cargo, metabolomic machine-learning classifiers, and autonomic measurements have each shown the ability to separate ME/CFS cohorts from healthy controls with accuracies ranging from around 77 percent to well above 90 percent in initial studies. The consistency across modalities is notable: immune dysregulation, metabolic inflexibility, and autonomic dysfunction all produce detectable signals, and multiple independent groups have converged on overlapping biological pathways.

The evidence is still early. Most studies use small, selected, or single-center cohorts, very few include mild or moderate patients alongside severe cases, and none of the candidate tests has been validated head-to-head against other chronic inflammatory conditions in a prospective clinical setting. Machine-learning models trained on one dataset frequently need revalidation before they generalize. The practical direction is toward multi-marker panels and interpretable, low-cost methods that can scale to routine clinical use, while leaving any single universal test unproven.

## Why This Matters

ME/CFS diagnosis still rests on symptom criteria that take years to apply correctly, and misdiagnosis and diagnostic delay are common. An objective biological test would reduce that delay, allow earlier intervention, and make clinical trials more reliable by improving patient selection. The same markers that distinguish patients from controls often also stratify patients by severity or biological subtype, which points toward precision medicine approaches rather than a single average-patient treatment strategy.

Multiplexed protein biosensors, cfRNA liquid biopsy, epigenetic chromosome-conformation testing, and metabolomics-guided machine learning represent four parallel technical paths that have each produced proof-of-concept results within the past year. Functional tools—virtual reality reaction-time testing and beat-to-beat autonomic monitoring—add a layer of measurement that does not require a blood draw and can capture cognitive and autonomic dimensions that blood panels miss.

## State of Evidence

- **Established:** ME/CFS produces measurable biological differences from healthy controls across multiple modalities, including immune gene expression, plasma metabolites, autonomic parameters, and circulating nucleic acids. Machine-learning classifiers built on these signals routinely exceed 80 percent accuracy in discovery cohorts.
- **Plausible but early:** Epigenetic chromosome-conformation signatures (EpiSwitch), cfRNA liquid biopsy, extracellular vesicle miRNA panels, SMPDL3B plasma levels, metabolomic AutoML models, and beat-to-beat autonomic classifiers each show strong initial performance. Multi-omics integration and large-language-model-adjacent tools may allow molecular subtyping to replace symptom-only classification.
- **Not established:** Any single test validated prospectively against clinical diagnosis across mild, moderate, and severe ME/CFS. Head-to-head specificity against overlapping conditions such as multiple sclerosis, rheumatoid arthritis, and fibromyalgia. Diagnostic biomarkers derived from exercise-challenge (PEM) conditions rather than resting samples.
- **Key limitations:** Small and often severely ill or female-only cohorts, cross-sectional designs that cannot prove causation, limited external replication, and the technical gap between research-grade assays and scalable clinical tests. Some metabolomic and epigenetic models rely on proprietary or not-yet-commercial platforms.

## Timeline

### 2025-07-07 - SMPDL3B identified as a severity-tracking biomarker in two cohorts

A case-control study at CHU Sainte-Justine compared 249 Canadian and 141 Norwegian ME/CFS patients against healthy controls and found that soluble SMPDL3B in plasma was significantly elevated and correlated with symptom severity, while the membrane-bound form on monocytes was reduced by increased PI-PLC cleavage activity. The protein normally dampens TLR4-driven inflammatory signaling, so its loss from the cell surface provides a mechanistic link between the observed immune dysregulation and chronic inflammation. In laboratory experiments, vildagliptin and saxagliptin both restored membrane-bound SMPDL3B by inhibiting PI-PLC, offering a potential therapeutic direction. The study is cross-sectional and cannot prove causation, and the cohorts were predominantly female, limiting sex-specific analysis.

Sources:

- [Rostami-Afshari et al. 2025, Journal of Translational Medicine](https://doi.org/10.1186/s12967-025-06829-0)

### 2025-07-28 - Review maps CIRS biomarker pathway as a differential-diagnosis model for ME/CFS

This literature review traced the chronological development of diagnostic tools for Chronic Inflammatory Response Syndrome, a biotoxin-triggered illness that shares overlapping symptoms with ME/CFS. The review's diagnostic relevance for ME/CFS is in the contrast it draws: CIRS has a structured, reproducible biomarker panel including MSH, MMP-9, TGF-β1, NeuroQuant brain-volume MRI, and the GENIE transcriptomic test, each of which normalizes with targeted therapy, whereas ME/CFS lacks equivalent validated markers. The author argues that a fraction of patients carrying an ME/CFS label may have unrecognized, treatable CIRS, which demands differential testing. The review is single-author, single-institution, and advocacy-adjacent rather than a systematic meta-analysis, so its quantitative claims about the size of the misdiagnosed population are unsupported.

Sources:

- [Dooley 2025, International Journal of Molecular Sciences](https://doi.org/10.3390/ijms26157284)

### 2025-08-11 - cfRNA liquid biopsy separates ME/CFS from healthy controls at AUC 0.81

A Cornell University case-control study sequenced circulating cell-free RNA from the plasma of 93 ME/CFS patients and 75 sedentary healthy controls. A 21-gene cfRNA signature trained on a GLMNET Lasso model achieved 77 percent accuracy and an AUC of 0.81 on held-out test samples, with deconvolution analysis pointing to elevated contributions from plasmacytoid dendritic cells, monocytes, and T cells alongside reduced platelet-derived cfRNA. Pathway analysis flagged T-cell exhaustion and chronic inflammatory signaling as the dominant biological themes. Diagnostic performance varied between individuals in a way that correlated with platelet cfRNA abundance, suggesting true platelet biology is contributing to the signal rather than only noise. All samples were resting-state; the study did not capture cfRNA dynamics during PEM, and the cohort was too small to assess disease subgroups.

Sources:

- [Gardella et al. 2025, PNAS](https://doi.org/10.1073/pnas.2507345122)

### 2025-09-29 - Editorial frames shared oxidative-stress pathomechanisms as prerequisite for ME/CFS diagnostics

This editorial in Neuroprotection, introducing a thematic journal issue, grouped ME/CFS and Long COVID alongside major depressive disorder and other CNS disorders as models of oxidative-stress-driven neuroinflammation. The diagnostic implication is that shared vicious-circle inflammatory biology between these conditions makes differential biomarker development harder: single inflammatory markers are unlikely to be disease-specific without mechanistic context. The authors note that precision medicine requiring individual inflammatory profiling is a necessary precondition before targeted diagnostics can work. As an editorial and literature synthesis rather than original data, the paper contributes framing rather than new biomarker evidence.

Sources:

- [Walczak et al. 2024/2025, Neuroprotection](https://doi.org/10.1002/nep3.70017)

### 2025-10-08 - EpiSwitch® chromosome-conformation test reaches 96% accuracy for severe ME/CFS

A retrospective case-control study from Oxford BioDynamics and the University of East Anglia analyzed whole blood from 47 severely ill, housebound ME/CFS patients and 61 healthy controls using a genome-wide microarray screening nearly one million chromosome conformations. A machine-learning model selected 200 markers that formed the EpiSwitch CFS test, which in an independent validation cohort achieved 92 percent sensitivity, 98 percent specificity, and 96 percent overall accuracy. Pathway analysis of the markers revealed dysregulation of IL-2, TNFα, and JAK/STAT signaling and allowed patients to cluster into distinct biological subgroups, which points toward precision immunotherapy matching. The test has not yet been validated against other chronic inflammatory diseases such as MS or rheumatoid arthritis, and the cohort was limited to severe cases, leaving mild and moderate ME/CFS applicability unknown.

Sources:

- [Hunter et al. 2025, Journal of Translational Medicine](https://doi.org/10.1186/s12967-025-07203-w)

### 2025-10-30 - AutoML metabolomics model achieves 87% diagnostic accuracy using explainable AI

This study from Inonu University and partner institutions benchmarked three Automated Machine Learning frameworks—TPOT, Auto-Sklearn, and H2O AutoML—against a metabolomic and lipidomic dataset of 888 features from 106 ME/CFS patients and 91 matched controls. TPOT outperformed the others with 87.3 percent accuracy and a 0.853 AUC. SHAP attribution analysis identified elevated succinic acid and pyruvic acid as the strongest disease signals, implicating a bottleneck at the glycolysis-to-TCA-cycle transition, alongside decreased leucine and prostaglandin D₂. The paper's use of explainable AI translates model predictions into biochemical pathways accessible to clinicians rather than leaving them as opaque scores. Sample size is modest, data are cross-sectional, and the dataset was publicly available rather than a prospective clinical collection.

Sources:

- [Yagin et al. 2025, Diagnostics](https://doi.org/10.3390/diagnostics15212755)

### 2025-12-17 - Metabolomics ML model differentiates Long COVID from ME/CFS and four other conditions

Researchers at UC San Diego trained a multi-layer perceptron on molecular descriptors of dysregulated plasma metabolites from PASC patients and used it to separate PASC from healthy controls and five phenotypically similar conditions: ME/CFS, Lyme disease, POTS, IBS, and fibromyalgia. The model achieved high predictive accuracy for PASC versus healthy controls and successfully discriminated PASC from ME/CFS, Lyme, POTS, and IBS, but found the metabolic profiles of PASC and fibromyalgia indistinguishable, suggesting shared molecular pathology. The use of molecular descriptors rather than fixed metabolite lists provides flexibility for adapting the framework to new biomarker discoveries. The study did not report sample sizes in the available summary, and the indistinguishability from fibromyalgia is a practical diagnostic limitation.

Sources:

- [Cai et al. 2025, Metabolites](https://doi.org/10.3390/metabo15120801)

### 2025-12-22 - Symptom questionnaire topic modeling stratifies Long COVID into ten endotypes and three severity groups

A preprint from the J. Craig Venter Institute and collaborating centers applied Poisson Factor Analysis to de-identified questionnaire data from 1,661 Long COVID participants across four independent cohorts. Unsupervised clustering identified ten global endotypes and three severity levels—mild, moderate, and severe—that were consistent across sites. A severe, female-predominant cluster characterized by neurological, hormonal, and temperature-regulation symptoms emerged as the most distinctively impaired group. Severity scores correlated with SARS-CoV-2-specific plasmablast antibodies (MENSA assay), validating that patient-reported severity reflects active immune biology rather than only subjective experience. Patients with non-mild acute illness had a 2.6-fold higher risk of developing moderate or severe Long COVID. The clustering approach relies on symptom co-occurrence rather than biomarkers and has not yet been linked to treatment-predictive biological markers.

Sources:

- [Peng et al. 2025, medRxiv](https://doi.org/10.1101/2025.11.16.25340350)

### 2025-12-23 - Beat-to-beat autonomic classifier reaches 89% accuracy without a blood test

A prospective case-control study from Nicolaus Copernicus University and the University of Oxford enrolled 112 ME/CFS patients and 61 healthy controls and recorded high-frequency beat-to-beat heart rate, blood pressure, and stroke volume using a Task Force Monitor. A sequential machine-learning pipeline combining a Transformer model with XGBoost classified participants at 89 percent subject-level accuracy. ME/CFS patients showed reduced cardiac vagal tone, higher sympathetic vascular tone, and lower stroke volume compared to controls, confirming autonomic dysfunction as a measurable core feature. The approach is non-invasive and does not require specialized laboratory infrastructure, which matters for clinical scalability. Validation in larger and more diverse cohorts is still needed before this could become a standardized diagnostic.

Sources:

- [Kujawski et al. 2025, Journal of Translational Medicine](https://doi.org/10.1186/s12967-025-07433-y)

### 2026-01-09 - Autoantibody profiling separates Long COVID, PASC-ME/CFS, and post-vaccination syndrome

A cross-sectional study from Columbia University Irving Medical Center compared 71 PASC patients meeting ME/CFS criteria, 82 non-ME/CFS PASC patients, and 28 post-acute COVID-19 vaccination syndrome patients on symptom burden, functional impairment, and immunologic markers. The ME/CFS phenotype showed the highest multi-system symptom burden, and the post-vaccination group showed comparable functional impairment to the ME/CFS group, despite different symptom profiles that included higher rates of peripheral neuropathy, tinnitus, and rash. Immunologically, the post-vaccination group had markedly higher rates of anticardiolipin IgM (43%) and anti-U1-RNP (21%) positivity, distinguishing it from both PASC groups. High rates of HSP-70 autoantibodies and cytokine elevations appeared across all three groups. The single-center, cross-sectional design and small post-vaccination subgroup (n=28) limit generalizability, and the autoantibody findings require prospective replication.

Sources:

- [Purpura et al. 2026, Clinical Infectious Diseases](https://doi.org/10.1093/cid/ciaf624)

### 2026-02-26 - ICD-10 record analysis identifies pre-diagnostic patterns in 6,077 young ME/CFS patients

A large-scale case-control study using German statutory health insurance data matched 6,077 ME/CFS patients aged 6–27 with 30,385 healthy controls and compared diagnosis codes in the year before the ME/CFS diagnosis was assigned. Forty-four diagnosis classes were significantly overrepresented in the ME/CFS group, with post-COVID-19 condition showing the strongest association; fibromyalgia and mild cognitive impairment also carried high predictive value. The finding that many preceding diagnoses may be early ME/CFS symptoms rather than comorbidities has practical implications for earlier clinical recognition without requiring novel biomarker tests. The study is limited by reliance on billing codes, which may contain errors or reflect clinical uncertainty rather than true pathological differences.

Sources:

- [Wirth et al. 2026, Scientific Reports](https://doi.org/10.1038/s41598-026-40848-1)

### 2026-02-28 - Extracellular vesicle miRNA and protein signatures distinguish post-COVID ME/CFS

A Charité Berlin case-control study isolated small extracellular vesicles from the plasma of female ME/CFS patients and healthy controls using size-exclusion chromatography, then characterized cargo by proteomic mass spectrometry and small RNA sequencing. Two proteins—hemoglobin subunit alpha and insulin-like growth factor-binding protein acid labile subunit—were altered in ME/CFS, and the miRNA hsa-let-7b-5p was significantly downregulated specifically in patients with post-COVID-19 ME/CFS, with lower levels correlating with more severe fatigue, pain, and immune activation. Surface markers on the vesicles themselves were unchanged, meaning the disease signal is carried inside the vesicle rather than on its exterior, which affects assay design choices. The study was restricted to female participants and used a small sample, limiting replication and generalizability to male patients.

Sources:

- [Seifert et al. 2026, International Journal of Molecular Sciences](https://doi.org/10.3390/ijms27052314)

### 2026-03-01 - UK Biobank pipeline model reaches 93.9% accuracy using ten routine blood biomarkers

A Fudan University team analyzed data from 1,137 ME/CFS cases and 66,838 controls in the UK Biobank, testing 11 machine-learning algorithms with various imputation and feature-selection strategies before identifying a pipeline that achieved 93.9 percent accuracy and an AUC of 0.979. The ten selected biomarkers—anchored by urea, total protein, glucose, total bilirubin, leucine, and vitamin D—are available from routine clinical blood panels, which sharply lowers the bar for clinical translation. Mendelian randomization analysis suggested causal relationships for several of the markers with ME/CFS outcomes, and elevated glucose and leucine were associated with greater symptom severity. Controls with overlapping conditions were included, improving clinical specificity. Prospective validation in an independent clinical population has not yet been reported.

Sources:

- [Li et al. 2026, Computational Biology and Chemistry](https://doi.org/10.1016/j.compbiolchem.2026.108995)

### 2026-03-28 - Muscle secretome and redox markers proposed as non-invasive diagnostic targets

This narrative review from the University G. d'Annunzio of Chieti-Pescara synthesized three decades of literature on skeletal muscle involvement in ME/CFS, identifying mitochondrial oxidative distress, redox imbalance, and impaired calcium handling in muscle cells as primary rather than secondary defects. The diagnostic implication is that the muscle secretome and specific redox biomarkers measurable non-invasively could serve as objective indicators of disease severity. The review explicitly frames these as primary physiological defects rather than consequences of deconditioning, which matters for how diagnostic thresholds would be interpreted clinically. No prospective biomarker validation study is reported; the muscle secretome proposal remains a conceptual target requiring dedicated assay development.

Sources:

- [Fanò-Illic et al. 2026, Diagnostics](https://doi.org/10.3390/diagnostics16071019)

### 2026-04-01 - Multiplexed silicon-photonic biosensors show two-orders-of-magnitude sensitivity gain over current standards

A University of Michigan review assessed the state of multiplexed protein biosensing platforms for complex infection-associated conditions including ME/CFS and Long COVID, comparing silicon photonic microring resonators and Liquid-phase Interference Tomography against the current gold standard of Luminex multiplexing. Newer designs reduced incubation times from several hours to 15 minutes, required substantially smaller sample volumes, and achieved two-orders-of-magnitude sensitivity improvements. The review emphasizes that ME/CFS and Long COVID require simultaneous detection of multiple immune and metabolic markers rather than single biomarkers, and that scalable automated systems are now reaching a maturity level where clinical deployment is realistic. The primary remaining barriers are analytical robustness across diverse patient populations and regulatory approval for multi-target diagnostic panels.

Sources:

- [Vajrala et al. 2026, TrAC Trends in Analytical Chemistry](https://doi.org/10.1016/j.trac.2026.118123)

### 2026-04-09 - 3D virtual reality reaction-time test quantifies cognitive fatigue objectively

A study from Universitätsklinikum Erlangen had 60 ME/CFS patients and 60 healthy controls complete a 3D stereoptic VR task across three rounds and measured reaction times and within-session improvement. Patients showed consistently slower reaction times than controls at all difficulty levels and, unlike controls, did not improve significantly across rounds, which researchers interpreted as the measurable footprint of mental fatigability rather than fixed slowed processing. Notably, objective VR performance did not correlate with patients' own self-assessment scores, suggesting that subjective questionnaires under-capture cognitive slowing. Age was not perfectly matched between groups and required statistical correction. The tool is still in a proof-of-concept phase and has not been paired with biological markers in the same subjects to confirm convergent validity.

Sources:

- [Ladek et al. 2026, Biomedicines](https://doi.org/10.3390/biomedicines14040855)

### 2026-05-15 - Multi-omics review maps a molecular reclassification roadmap from genomics to AI platforms

A narrative review from Nova Southeastern University's Institute for Neuro-Immune Medicine synthesized landmark studies across genomics (DecodeME GWAS), epigenetic profiling, single-cell transcriptomics, metabolomic pathway mapping, and multi-modal AI frameworks (BioMapAI, HEAL2, Positive Unlabeled Learning) to outline how ME/CFS could shift from symptom-based diagnosis to molecularly defined subtypes. The review identified CD8+ T-cell exhaustion marked by TOX and EOMES transcription factors, compromised mitochondrial coupling efficiency, system-wide hypometabolism, and sex-specific proteomic recovery signatures as convergent downstream consequences of the disease regardless of which molecular pathway is primary in any individual patient. Circulating cell-free RNA signatures and BioMapAI are highlighted as current diagnostic and classification anchors. The review's diagnostic contribution is a framework rather than new data: the challenge it names—translating high-dimensional computational models into accessible clinical laboratory tests—remains the central unsolved problem for the field.

Sources:

- [Frank et al. 2026, International Journal of Molecular Sciences](https://doi.org/10.3390/ijms27104436)

### 2026-05-29 - Raman spectroscopy and machine learning differentiate ME/CFS from controls at rest and after standardized stress

In a study published in the *International Journal of Molecular Sciences*, Heidarifard et al. developed a label-free blood plasma screening method combining Raman spectroscopy (RS) and machine learning (ML) classification. Testing 115 ME/CFS patients (meeting CCC criteria) and 45 sedentary healthy controls at rest and 90 minutes after a non-invasive mechanical stress challenge (pulsatile arm cuff compression designed to trigger post-exertional responses), the RS-ML models differentiated patients with 79% accuracy (0.85 AUC) at rest, and 84% accuracy (0.83 AUC) post-stress. The post-stress challenge model halved the number of false positives, increasing specificity from 82% to 90%. Discriminant spectral features included altered lipid, protein, and amino acid profiles, suggesting exertion-sensitive metabolic responses. Limitations include a modest control cohort size, sex imbalance between groups, and single-point post-exertional sampling.

Sources:

- [Heidarifard et al. 2026, International Journal of Molecular Sciences](https://pubmed.ncbi.nlm.nih.gov/42278463/)

### 2026-06 - Study finds elevated plasma EV concentrations but protein cargo changes lack statistical correction significance

In an exploratory case-control study published in *Biochemistry and Biophysics Reports*, Rydland et al. analyzed plasma extracellular vesicle (EV) profiles in 49 ME/CFS patients and 50 healthy controls. While they successfully replicated findings of significantly higher concentrations of EVs in ME/CFS patients compared to healthy controls, their proteomic analysis yielded less robust results. Of 424 proteins analyzed, 11 showed differing levels—including elevated liver-derived proteins and decreased erythroid and B-cell-derived proteins—but these differences did not survive correction for multiple testing or correlate with illness severity. The study was underpowered due to the relatively small sample size, and functional replication is needed.

Sources:

- [Rydland et al. 2026, Biochemistry and Biophysics Reports](https://www.sciencedirect.com/science/article/pii/S2405580826002396)

## Related Threads

- [Post-Exertional Malaise & Exercise Physiology](../pem-exercise-physiology/)
- [Clinical Characterization & Epidemiology](../clinical-characterization-epidemiology/)
- [Immune Dysregulation & Inflammation](../../disease-models-mechanisms/immune-dysregulation-inflammation/)
- [Mitochondrial & Metabolic Dysfunction](../../disease-models-mechanisms/mitochondrial-metabolic-dysfunction/)
- [Autoimmunity & Autoantibodies](../../disease-models-mechanisms/autoimmunity-autoantibodies/)
