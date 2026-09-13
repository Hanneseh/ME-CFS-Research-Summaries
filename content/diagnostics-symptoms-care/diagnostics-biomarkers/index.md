---
title: Diagnostics & Biomarkers
description: A living thread on diagnostic tests, biomarker panels, machine-learning classifiers, biosensors, assays, and measurement tools for ME/CFS and Long COVID.
date: 2026-08-24
last_updated: 2026-08-24
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

No single biomarker or diagnostic test for ME/CFS has reached clinical deployment, but a growing body of blood-based, genomic, metabolomic, and functional studies has moved the field from exclusion-by-symptoms toward measurable biological signatures. 3D chromosome conformation profiling, circulating cell-free RNA, extracellular vesicle microRNA signatures, metabolomic machine-learning classifiers, and autonomic measurements have each shown the ability to separate ME/CFS cohorts from healthy controls with accuracies ranging from around 77 percent to well above 90 percent in initial retrospective or pilot studies. The consistency across modalities is notable: immune dysregulation, metabolic inflexibility, and autonomic dysfunction all produce detectable signals, and multiple independent groups have converged on overlapping biological pathways.

The evidence is still early. Most studies use small, selected, or single-center cohorts, and prospective validation of exploratory biomarkers—such as candidate epigenetic panels or extracellular vesicle microRNA signatures—in real-world clinical settings remains a key barrier. Very few studies include mild or moderate patients alongside severe cases, and none of the candidate tests has been validated head-to-head against other chronic inflammatory conditions in a prospective clinical setting. Machine-learning and large language models trained on transcriptomic or metabolomic datasets show promise for feature extraction but frequently need revalidation before generalizing to complex multisystem cohorts. The practical direction is toward multi-marker panels and interpretable, low-cost methods that can scale to routine clinical use, while leaving any single universal test unproven.

## Why This Matters

ME/CFS diagnosis still rests on symptom criteria that take years to apply correctly, and misdiagnosis and diagnostic delay are common. An objective biological test would reduce that delay, allow earlier intervention, and make clinical trials more reliable by improving patient selection. The same markers that distinguish patients from controls often also stratify patients by severity or biological subtype, which points toward precision medicine approaches rather than a single average-patient treatment strategy.

Multiplexed protein biosensors, cfRNA liquid biopsy, epigenetic chromosome-conformation testing, and metabolomics-guided machine learning represent four parallel technical paths that have each produced proof-of-concept results within the past year. Functional tools—virtual reality reaction-time testing and beat-to-beat autonomic monitoring—add a layer of measurement that does not require a blood draw and can capture cognitive and autonomic dimensions that blood panels miss.

## State of Evidence

- **Established:** ME/CFS produces measurable biological differences from healthy controls across multiple modalities, including immune gene expression, plasma metabolites, autonomic parameters, and circulating nucleic acids. Machine-learning classifiers built on these signals routinely exceed 80 percent accuracy in discovery cohorts.
- **Plausible but early:** Epigenetic chromosome-conformation signatures (EpiSwitch), cfRNA liquid biopsy, extracellular vesicle microRNA and proteomic cargo profiling, SMPDL3B plasma levels, metabolomic AutoML models, LLM-guided transcriptomic feature selection, and beat-to-beat autonomic classifiers each show strong initial performance in retrospective or pilot cohorts. Objective neurophysiological measures (such as sleep EEG slow-wave microstructure disruptions, altered post-movement beta rebound, and resting alpha frequency slowing) demonstrate measurable group-level central nervous system differences. Multi-omics integration, post-exertional provocation models, and machine-learning tools may allow molecular subtyping and cognitive trajectory mapping to supplement symptom-based classification. A new cross-disease 3D-genome network analysis and a UK Biobank resting-state fMRI classifier add useful negative and hypothesis-generating evidence, but neither is a validated ME/CFS diagnostic test.
- **Not established:** Any single test validated prospectively against clinical diagnosis across mild, moderate, and severe ME/CFS. Head-to-head specificity against overlapping conditions such as multiple sclerosis, rheumatoid arthritis, and fibromyalgia. Clinically validated diagnostic biomarkers derived from exercise-challenge (PEM) provocation protocols, though pilot multi-omic and cognitive trajectory studies are underway.
- **Key limitations:** Small and often severely ill or female-only cohorts, cross-sectional designs that cannot prove causation, lack of prospective validation, and the technical gap between research-grade assays and scalable clinical tests. Several candidate markers arrive as preprints or preliminary conference abstracts lacking full diagnostic performance metrics. Furthermore, laboratory-dependent testing protocols (including in-facility polysomnography, high-density EEG, and repeated physical dynamometry) systematically exclude bedbound and very severe patients, skewing the biomarker evidence base toward ambulatory cohorts. Some metabolomic and epigenetic models rely on proprietary platforms with inherent developer conflicts of interest. The UK Biobank fatigue study used a broad self-report definition without PEM characterization and found resting-state fMRI performance near clinical-feature baselines, while the 3D-genome network extension does not report complete denominators or severe-patient representation.

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

### 2026-04-22 - Overnight polysomnography reveals sleep EEG microstructure changes in Long COVID and ME/CFS

A peer-reviewed case-control neurophysiology study in *Sleep* evaluated overnight in-facility polysomnography and sleep EEG microstructures across 19 ME/CFS patients, 28 Long COVID patients, and 28 matched healthy controls. Quantitative spectral analysis revealed elevated slow oscillation (SO) power during pre-sleep wakefulness and REM sleep in Long COVID compared to controls. During non-REM sleep stages N2 and N3, both ME/CFS and Long COVID cohorts displayed microstructural disruptions, including faster intra-spindle frequency drops and shorter frontal SO peak durations. Furthermore, the study identified altered phase-amplitude coupling with premature fast spindle coupling at the SO trough, which correlated significantly with patient-reported severity of unrefreshing sleep. These findings provide objective electrophysiological evidence that post-viral unrefreshing sleep involves disrupted thalamocortical oscillations and slow-wave coordination. However, the study is limited by modest subcohort sizes, a cross-sectional design without longitudinal tracking, and an in-laboratory overnight testing protocol that excludes bedbound or severely ill individuals while risking acute post-exertional symptom exacerbation.

Sources:

- [Sun et al. 2026, Sleep](https://doi.org/10.1093/sleep/zsag090)

### 2026-05-15 - Multi-omics review maps a molecular reclassification roadmap from genomics to AI platforms

A narrative review from Nova Southeastern University's Institute for Neuro-Immune Medicine synthesized landmark studies across genomics (DecodeME GWAS), epigenetic profiling, single-cell transcriptomics, metabolomic pathway mapping, and multi-modal AI frameworks (BioMapAI, HEAL2, Positive Unlabeled Learning) to outline how ME/CFS could shift from symptom-based diagnosis to molecularly defined subtypes. The review identified CD8+ T-cell exhaustion marked by TOX and EOMES transcription factors, compromised mitochondrial coupling efficiency, system-wide hypometabolism, and sex-specific proteomic recovery signatures as convergent downstream consequences of the disease regardless of which molecular pathway is primary in any individual patient. Circulating cell-free RNA signatures and BioMapAI are highlighted as current diagnostic and classification anchors. The review's diagnostic contribution is a framework rather than new data: the challenge it names—translating high-dimensional computational models into accessible clinical laboratory tests—remains the central unsolved problem for the field.

Sources:

- [Frank et al. 2026, International Journal of Molecular Sciences](https://doi.org/10.3390/ijms27104436)

### 2026-05-29 - Raman spectroscopy and machine learning differentiate ME/CFS from controls at rest and after standardized stress

In a study published in the *International Journal of Molecular Sciences*, Heidarifard et al. developed a label-free blood plasma screening method combining Raman spectroscopy (RS) and machine learning (ML) classification. Testing 115 ME/CFS patients (meeting CCC criteria) and 45 sedentary healthy controls at rest and 90 minutes after a non-invasive mechanical stress challenge (pulsatile arm cuff compression designed to trigger post-exertional responses), the RS-ML models differentiated patients with 79% accuracy (0.85 AUC) at rest, and 84% accuracy (0.83 AUC) post-stress. The post-stress challenge model halved the number of false positives, increasing specificity from 82% to 90%. Discriminant spectral features included altered lipid, protein, and amino acid profiles, suggesting exertion-sensitive metabolic responses. Limitations include a modest control cohort size, sex imbalance between groups, and single-point post-exertional sampling.

Sources:

- [Heidarifard et al. 2026, International Journal of Molecular Sciences](https://pubmed.ncbi.nlm.nih.gov/42278463/)

### 2026-06-11 - LLMs benchmarked for cell-free RNA diagnostic biomarker discovery

A peer-reviewed study in *Nature Communications* evaluated six large language models—including architectures from OpenAI, Anthropic, and Google—for cell-free RNA (cfRNA) diagnostic biomarker discovery across three plasma datasets, including an ME/CFS cohort paired with sedentary controls. The benchmark tested both literature-guided gene panel nomination and autonomous classifier construction. Model-nominated cfRNA panels successfully recapitulated canonical immune pathways and matched conventional differential gene expression baselines established in distinct infectious cohorts such as tuberculosis. However, end-to-end autonomous classifier performance dropped significantly for the complex ME/CFS dataset compared to more discrete inflammatory disease pairs like Kawasaki disease versus MIS-C. High prompt adherence variance across models highlighted that LLM-driven gene selection remains task-dependent and cannot yet reliably automate diagnostic classification in multisystem illnesses without human oversight. For patient care, the findings establish both the potential of AI tools for rapid transcriptomic feature extraction and their current boundaries in complex post-viral diagnostics.

Sources:

- [Li et al. 2026, Nature Communications](https://pubmed.ncbi.nlm.nih.gov/42276999/)

### 2026-06-15 - Alain Moreau presentation outlines home-based PEM provocation and cognitive trajectories

In a conference presentation at the Internationale ME/CFS-Konferenz 2026, Alain Moreau presented early pilot data detailing a deep phenotyping and post-exertional malaise (PEM) provocation protocol. The protocol utilizes a home-based inflatable cuff massage to safely and standardly trigger post-exertional responses in severely affected patients, followed by multi-omics analysis. Post-provocation, researchers identified three distinct cognitive trajectories using a 10-minute tablet-based BrainCheck test, which were indistinguishable at baseline: memory decline (Cluster A), resilience (Cluster B), and severe multi-domain decline (Cluster C). The severe decline group correlated with reduced cerebral oxygen extraction via near-infrared spectroscopy (NIRS) and a sudden drop in circulating brain-derived neurotrophic factor (BDNF). Vulnerability in Cluster C was linked to the HP2-1 haptoglobin phenotype and elevated soluble LRP1, which acts as a decoy blocking hemoglobin detoxification. While offering therapeutic leads like recombinant haptoglobin, pentoxifylline, and mitapivat, these findings represent early pilot data requiring validation in larger cohorts, and active provocation carries risk of clinical worsening.

Sources:

- [Moreau 2026, Internationale ME/CFS-Konferenz](https://youtu.be/xOMQANDBoT4)

### 2026-06-30 - Explainable ensemble learning classifies ME/CFS using plasma metabolomics and lipidomics

In a study published in the *International Journal of Molecular Sciences*, Yagin et al. evaluated three machine learning classifiers to distinguish ME/CFS patients from healthy controls based on plasma metabolomic and lipidomic profiles. Using data from 106 ME/CFS patients and 91 healthy controls across 888 features, the Explainable Boosting Machine (EBM) classifier achieved the highest performance, yielding 90.9 percent accuracy and an AUC of 0.940 under 50-repeat stratified hold-out validation. Pairwise metabolite interaction terms—specifically proline and indole-3-lactate, tyrosine and N-acetylornithine, and maleic acid and arachidic acid—provided the strongest discriminative signals, indicating that metabolite co-variation offers diagnostic value beyond individual metabolite levels. While these metabolomic alterations implicate pathways in amino acid catabolism, tryptophan-kynurenine pathway dysregulation, mitochondrial energy impairment, and lipid remodeling, the classifier requires prospective testing and calibration assessment in independent cohorts before clinical translation.

Sources:

- [Yagin et al. 2026, International Journal of Molecular Sciences](https://pmc.ncbi.nlm.nih.gov/articles/PMC13362375)

### 2026-07-10 - EpiSwitch® 3D genomic test validated in retrospective severe cohort

In a peer-reviewed retrospective case-control study published in the *Journal of Translational Medicine*, researchers validated the EpiSwitch® 3D genomic test for ME/CFS. Using whole-genome 3D DNA screening of peripheral blood mononuclear cells from 47 severe ME/CFS patients and 61 healthy controls, the study developed a 200-marker chromosome conformation model. The diagnostic panel achieved 92 percent sensitivity and 98 percent specificity in an independent retrospective validation cohort. Pathway analysis linked these conformation markers to neuroinflammatory, tumor necrosis factor alpha (TNFα), and JAK/STAT signaling, and identified a potential responder subpopulation for Rituximab and glatiramer acetate based on IL-2 pathway conformations. However, the study is limited by its retrospective design, lack of validation in mild-to-moderate cohorts, and a potential commercial conflict of interest, as multiple co-authors are employees of the test's developer, Oxford BioDynamics plc. Prospective clinical validation is still required before the assay can be deployed as a routine diagnostic tool.

Sources:

- [Hunter et al. 2025/2026, Journal of Translational Medicine](https://pubmed.ncbi.nlm.nih.gov/41057909/)

### 2026-07-10 - Exploratory proteomics identifies cellular cargo changes in plasma extracellular vesicles

In a peer-reviewed exploratory case-control study published in *Biochemistry and Biophysics Reports*, Rydland et al. analyzed plasma extracellular vesicle (EV) profiles in 49 ME/CFS patients and 50 healthy controls. The study successfully replicated findings showing significantly elevated total concentrations of plasma EVs in ME/CFS patients compared to controls. However, high-resolution quantitative proteomics of the vesicle cargo yielded less robust diagnostic markers. Out of 424 detected proteins, 11 proteins showed differential expression (including elevated liver-derived proteins and decreased erythroid and B-cell-derived proteins), but these differences did not remain statistically significant after correcting for multiple testing. While the study provides further evidence for altered systemic vesicle biology and cellular communication, the small cohort size and lack of multiple testing significance mean these specific protein cargo signatures remain unvalidated, exploratory findings requiring larger replication cohorts.

Sources:

- [Rydland et al. 2026, Biochemistry and Biophysics Reports](https://pubmed.ncbi.nlm.nih.gov/42375682/)

### 2026-07-10 - Systematic review identifies NF-κB pathway as central hub for PAIS biomarkers

In a peer-reviewed systematic literature review of 142 studies analyzing biomarkers in post-acute infection syndromes (PAIS), researchers synthesized molecular findings across Long COVID (PACS), ME/CFS, and Guillain-Barré syndrome (GBS). The review identifies widespread alterations across multiple physiological domains, including energy, lipid, and amino acid metabolism, gut microbiome dysbiosis, mitochondrial stress, and microRNA (miRNA) regulatory networks. Notably, the authors identify the NF-κB pathway as a central molecular hub that connects cellular stress, persistent immune activation, metabolic reprogramming, and systemic inflammation. The review argues that PAIS is a multisystem disorder driven by persistent dysregulated host responses rather than active viral replication, supporting a clinical shift toward mechanism-based classification. However, because the review synthesizes existing literature with high heterogeneity in patient cohorts and analytical methods, it does not present new primary patient data or validate a clinical diagnostic test.

Sources:

- [PAIS Biomarker Review 2026, Frontiers in Immunology](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2026.1741761/full)

### 2026-07-15 - Standardized repeated handgrip strength testing evaluated in young patient cohort

In a prospective observational study published in the *Journal of Translational Medicine*, Mihatsch et al. evaluated the clinical utility of a standardized two-session repeated handgrip strength (HGS) test, separated by a 60-minute break, in 147 children, adolescents, and young adults with chronic fatigue and self-reported post-exertional malaise (PEM) alongside 83 healthy controls. The test showed high feasibility with completion rates exceeding 96 percent, and patient cohorts demonstrated significantly lower handgrip strength than healthy controls, with a mean difference of -9.93 kg. HGS indices correlated modestly with physical functioning but did not correlate with PEM duration, and they failed to reliably differentiate ME/CFS patients from those with other fatiguing conditions. In a sensitivity analysis restricted to patients meeting the Canadian Consensus Criteria, the test achieved moderate diagnostic discrimination (62.8 to 70.7 percent accuracy) using absolute strength indices and recovery ratios, indicating that its utility is for tracking physical functioning and functional impairment rather than as a standalone diagnostic biomarker.

Sources:

- [Mihatsch et al. 2026, Journal of Translational Medicine](https://pubmed.ncbi.nlm.nih.gov/42458481)

### 2026-07-24 - Handgrip variability study shows coefficient of variation cannot separate ME/CFS fatigability from submaximal effort

In an observational modeling preprint on medRxiv, Steinkirchner et al. evaluated repeated handgrip strength (HGS) test variability across three multicenter cohorts comprising 211 ME/CFS patients and 170 controls. Standard repeated dynamometry protocols frequently employ the coefficient of variation (CV) as an effort-validity marker, historically misclassifying high trial-to-trial variability as poor motivation or deliberate submaximal effort. The authors demonstrate that CV distributions overlap substantially between ME/CFS patients exerting full effort and healthy controls instructed to exert only 50 percent force, showing that CV cannot reliably differentiate pathophysiological neuromuscular fatigability from voluntary submaximal force. To address this, the researchers propose a trajectory-aware sum-of-residuals metric that models fatigue decay curves to prevent false accusations of poor effort in clinical and disability assessments. As a preprint, these findings have not completed peer review, and the proposed metric remains an experimental methodological framework rather than established medicolegal practice. Additionally, the study focused solely on upper-extremity isometric dynamometry without intramuscular metabolic or electromyographic measurements, and repeated clinic testing underrepresents severe and bedbound patients while carrying risk of localized post-exertional strain.

Sources:

- [Steinkirchner et al. 2026, medRxiv](https://doi.org/10.1101/2026.07.22.26358672)

### 2026-07-27 - Circulating extracellular vesicle microRNAs differentiate ME/CFS from non-ME/CFS fatigue controls

A peer-reviewed case-control study in the *Journal of Translational Medicine* evaluated circulating extracellular vesicle (EV) microRNA profiles as potential diagnostic biomarkers for ME/CFS. Isolating plasma EVs, the researchers identified distinct EV-microRNA expression signatures that separated ME/CFS patients not only from healthy controls but also from non-ME/CFS chronic fatigue comparison groups. The specific microRNA cargo implicates systemic extracellular vesicle transport in persistent inflammatory signaling cascades and immune cell communication. Achieving high diagnostic discrimination against disease-matched fatiguing controls addresses a key historical hurdle in ME/CFS biomarker development, where non-specific fatigue controls often blur diagnostic boundaries. However, EV isolation protocols currently require specialized, resource-intensive laboratory infrastructure, and the candidate microRNA panel requires prospective validation in larger multi-center cohorts before clinical adoption. If replicated, this EV microRNA signature could support the development of a non-invasive, blood-based diagnostic assay capable of objective patient classification.

Sources:

- [Zhang et al. 2026, Journal of Translational Medicine](https://pubmed.ncbi.nlm.nih.gov/42533331/)

### 2026-08-01 - Conference abstract presents FLow-based Immune Profiling of multi-isotype antibody signatures in Long COVID and post-treatment Lyme

A conference abstract published in a *Journal of Immunology* supplement from the American Association of Immunologists meeting introduced FLow-based Immune Profiling (FLIP) for multidimensional serological profiling across post-infectious cohorts. Researchers applied the high-parameter multiplexed flow cytometry platform to evaluate pathogen-specific and surface-bound antibodies across major isotypes (IgD, IgM, IgA, IgE) and IgG subclasses (IgG1–4) in plasma from the RECOVER Long COVID cohort and the MAESTRO Post-Treatment Lyme Disease Syndrome (PTLDS) cohort. The platform identified distinct ratiometric antibody signatures that differentiated individuals experiencing persistent chronic symptoms from those who had fully recovered, revealing divergent humoral trajectories across infection-associated conditions. Because this source is a preliminary conference abstract rather than a full peer-reviewed paper, detailed analytical methodology, cohort breakdown tables, and diagnostic ROC/AUC performance metrics are omitted. The study evaluated broad Long COVID and PTLDS cohorts without a dedicated Canadian Consensus Criteria ME/CFS arm, and the findings require prospective replication before high-parameter flow-based serology can be evaluated as a diagnostic tool. While standard blood draws pose minimal physical burden for patients, the assay currently requires specialized laboratory instrumentation.

Sources:

- [Kremer et al. 2026, The Journal of Immunology](https://doi.org/10.1093/jimmun/vkag141.942)

### 2026-08-04 - Peer-reviewed publication reports haptoglobin phenotype stratification of post-exertional cognitive decline

In a peer-reviewed study in the *International Journal of Molecular Sciences*, Moezzi et al. evaluated haptoglobin (Hp) phenotypes as biological stratification markers in post-viral illness. The investigators subjected 44 Long COVID patients and 20 rapid-recovery controls to a 90-minute standardized passive pneumatic cuff provocation challenge while monitoring computerized cognitive performance, cerebral tissue oxygen extraction via near-infrared spectroscopy (NIRS), and plasma metabolomics. Patients carrying the Hp2-2 phenotype exhibited significant post-provocation cognitive decline on BrainCheck testing, reduced right-hemisphere cerebral fractional tissue oxygen extraction, and depressed plasma levels of citric acid, isethionate, and glucosamine. In contrast, cognitively resilient Hp1-1 carriers maintained cerebral oxygen extraction and metabolic stability during provocation. This Long COVID cohort therefore extends, but should not be conflated with, the earlier conference-reported ME/CFS pilot that associated Hp2-1 with a worse trajectory; the differing phenotype signals require replication and direct cohort comparison. While passive pneumatic cuff stimulation provides an exertion-testing alternative for individuals unable to perform maximal exercise tests, active provocation still carries a risk of inducing post-exertional symptom flares. Key limitations include a modest sample size, the absence of a prepandemic non-COVID ME/CFS comparison cohort, and the fact that proposed haptoglobin-modulating therapeutic concepts remain unvalidated preclinical hypotheses.

Sources:

- [Moezzi et al. 2026, International Journal of Molecular Sciences](https://doi.org/10.3390/ijms27157000)

### 2026-08-11 - EEG study identifies reduced post-movement beta rebound and resting alpha slowing in Long COVID fatigue

A peer-reviewed case-control neurophysiology study in the *Journal of Clinical Neuroscience* evaluated cortical oscillatory dynamics using 64-channel electroencephalography (EEG) in 20 Long COVID participants experiencing fatigue, brain fog, and post-exertional malaise alongside 20 matched healthy controls. Recordings obtained during resting state and sustained isometric handgrip tasks revealed a significant reduction in post-movement beta rebound (PMBR) in the primary motor and somatosensory cortex upon motor release in patients. Long COVID participants also demonstrated marked slowing of resting sensorimotor alpha center frequency (averaging ~9.6 Hz versus ~10.6 Hz in controls), with both oscillatory abnormalities correlating with self-reported fatigue severity. These electrophysiological shifts point to disrupted cortical excitatory-inhibitory balance and impaired GABAergic intracortical inhibition in post-viral neurocognitive fatigue. However, the study is limited by a small single-center sample, a cross-sectional design that cannot establish whether oscillatory changes precede or result from chronic illness, and the enrollment of a broad post-COVID cohort rather than criteria-defined ME/CFS. Furthermore, in-laboratory testing requirements and motor contraction tasks exclude severely affected or bedbound individuals while carrying potential for triggering post-exertional fatigue.

Sources:

- [Casado Sánchez et al. 2026, Journal of Clinical Neuroscience](https://doi.org/10.1016/j.jocn.2026.112230)

### 2026-08-22 - 3D-genome network analysis maps cross-disease biomarker hypotheses

This systems-biology investigation combined EpiSwitch chromosome-conformation measurements with GWAS and Orion knowledgebase analyses across ME/CFS, Long COVID, PTSD, rheumatoid arthritis, and multiple sclerosis. It reports 552 ME/CFS 3D-genomic anchors mapping to 567 genes and network-level convergence around immune, interferon, mitochondrial/metabolic, neuroendocrine, LAG3, and mTOR-related pathways, but direct gene overlap was limited and the work is retrospective and substantially in silico. Severe or bedbound representation was not reported; blood-based sampling could eventually be lower burden than exercise or imaging, but venipuncture and travel remain relevant and no home collection was established. No exertion challenge, PEM outcome, safety result, or treatment effect was studied, so proposed drug-target links are hypothesis-generating rather than clinical guidance. Cross-links include [Genetic Risk Factors](../../disease-models-mechanisms/genetic-risk-factors/), [Immune Dysregulation & Chronic Inflammation](../../disease-models-mechanisms/immune-dysregulation-inflammation/), and [Mitochondrial & Metabolic Dysfunction](../../disease-models-mechanisms/mitochondrial-metabolic-dysfunction/).

Sources:

- [Hunter et al. 2026, Journal of Translational Medicine](https://doi.org/10.1186/s12967-026-08874-9)

### 2026-08-24 - UK Biobank study finds resting-state fMRI adds little to broad fatigue classification

Pereira and colleagues evaluated preregistered machine-learning models using clinical features and 3T resting-state fMRI functional/effective connectivity in 2,247 UK Biobank participants reporting chronic fatigue or not. Clinical variables alone reached 61.2% balanced accuracy, while adding connectivity produced 60.0–63.5%; frequent insomnia was the dominant feature and reached 57.3% alone, and the planned continuous Fatigue Severity Scale analysis was abandoned because only 91 participants had sufficient data. The broad single-question fatigue phenotype did not assess PEM, autonomic or cognitive crashes, or criteria-defined ME/CFS, and the imaging protocol systematically excluded severe and bedbound patients through travel and scanner requirements; no exertion challenge or treatment was studied. The result is a useful negative test of current resting-state fMRI biomarker claims, not evidence against neurobiological illness, and it points toward disease-specific cohorts and challenge-based imaging; see [Neuroinflammation & Brain Changes](../../disease-models-mechanisms/neuroinflammation-brain-changes/) and [Clinical Characterization & Epidemiology](../clinical-characterization-epidemiology/).

Sources:

- [Pereira et al. 2026, medRxiv](https://doi.org/10.64898/2026.08.21.26360925)

## Related Threads

- [Post-Exertional Malaise & Exercise Physiology](../pem-exercise-physiology/)
- [Clinical Characterization & Epidemiology](../clinical-characterization-epidemiology/)
- [Neuroinflammation & Brain Changes](../../disease-models-mechanisms/neuroinflammation-brain-changes/)
- [Immune Dysregulation & Inflammation](../../disease-models-mechanisms/immune-dysregulation-inflammation/)
- [Mitochondrial & Metabolic Dysfunction](../../disease-models-mechanisms/mitochondrial-metabolic-dysfunction/)
- [Autoimmunity & Autoantibodies](../../disease-models-mechanisms/autoimmunity-autoantibodies/)
