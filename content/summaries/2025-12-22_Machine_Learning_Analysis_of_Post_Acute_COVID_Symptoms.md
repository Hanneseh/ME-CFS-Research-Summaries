---
title: "Machine Learning Analysis of Post-Acute COVID Symptoms Identifies Distinct Clusters, Severity Groups, and Trajectories"
tags:
  - ➕ 2025-12-25
  - 🧪 Biomarker
  - ⭐ Landmark
created: '2025-12-22'
published: '2025-12-22'
---

<details>
<summary>Peng et al. (2025)</summary>

- **Authors:** Beverly Peng, Thomas Dalhuisen, Aidan Rogers, Violeta Capric, Helen E. Davies, Steven G. Deeks, Christopher L. Dupont, Jesus Estevez, Marcelo Freire, Natalie S. Haddad, Samantha A. Jones, J. Daniel Kelly, Kristin Ladell, F. Eun-Hyung Lee, Jeffrey N. Martin, Kelly L. Miners, Michael J. Peluso, David A. Price, Amy D. Proal, David Putrino, Richard H. Scheuermann, Michael B. VanElzakker, Yun Zhang, Gene S. Tan, Yu Qian 
- **Institutes:** J. Craig Venter Institute; University of California, San Francisco; Icahn School of Medicine at Mount Sinai; Emory University; Cardiff University; Massachusetts General Hospital; National Institutes of Health 
- **Publisher:** medRxiv (Preprint) 
- **Link:** [DOI](https://doi.org/10.1101/2025.11.16.25340350) 

</details>

## Summary

This study demonstrates that low-cost patient questionnaires, when analyzed with advanced machine learning, can objectively categorize the complex "umbrella" of Long COVID into specific biological subtypes (endotypes) and severity levels. By identifying ten global endotypes—including a severe, female-predominant cluster characterized by hormonal and neurological symptoms—the research provides a roadmap for personalizing treatments and clinical trials. The finding that acute phase severity significantly predicts the risk of developing severe Long COVID offers a vital window for early intervention. Furthermore, the correlation between symptom-based severity scores and active immune responses (plasmablast antibodies) validates that patient-reported data reflects underlying biological processes.

## What was researched?

The study aimed to determine if unsupervised machine learning (topic modeling) could identify distinct symptom clusters, biologically meaningful endotypes based on organ systems, and quantitative severity groups from standardized Long COVID patient questionnaires. It also investigated whether these symptom-based groupings correlated with clinical health status (EQ-5D) and molecular biomarkers like SARS-CoV-2-specific antibody responses.

## Why was it researched?

The extreme heterogeneity of Long COVID symptoms across multiple organ systems makes it challenging to design effective clinical trials or understand the condition's underlying mechanisms. While Electronic Health Records (EHRs) are often used for analysis, they suffer from missing data and lack of standardization; thus, the researchers sought to validate whether simpler, more accessible questionnaire data could provide a robust framework for patient stratification and precision medicine.

## How was it researched?

Researchers analyzed de-identified questionnaire data from four independent cohorts (UCSF, $n=669$; ISMMS, $n=615$; Emory, $n=60$; and Cardiff, $n=317$) totaling 1,661 participants. They employed a machine learning pipeline using Poisson Factor Analysis for topic modeling to reduce data dimensionality, followed by unsupervised clustering and hierarchical mapping of symptoms to organ systems. Validation was conducted by comparing symptom-based severity scores against EQ-5D health scores and immunological data, including MENSA (plasmablast) and serum antibody assays.

## What has been found?

The analysis identified ten global endotypes and three distinct severity levels (mild, moderate, and severe) that were consistent across different clinical sites. Key findings include:
* A specific severe cluster was identified that is predominantly female and characterized by neurological, hormonal, and temperature regulation symptoms.
* Three distinct symptom trajectories were discovered: "acute-resolving," "persistent but attenuated," and "progressive" (where symptoms like joint pain and concentration difficulties worsen over time).
* Patients with non-mild symptoms during the acute infection phase had a 2.6-fold higher risk of developing moderate or severe Long COVID.
* Symptom-based severity scores significantly correlated with SARS-CoV-2 S1 IgG antibodies 💊 from plasmablasts (MENSA), indicating an active immune response in more severe cases.

## Discussion

A significant strength of this study is the cross-cohort validation, showing that the machine learning approach is robust even when merging different datasets. The researchers noted that while traditional tools like PCA failed to identify clusters, topic modeling successfully captured the "co-occurrence" of symptoms. However, limitations include the stochastic nature of Poisson factorization, the lack of randomization in cohorts, and imbalanced gender distributions, which required sex-stratified analysis to ensure accuracy.

## Conclusion & Future Work

The authors conclude that machine learning-assisted screening of simple questionnaires can robustly identify Long COVID endotypes and severity, providing a framework for precision medicine trial design. Future work will focus on identifying group-specific biomarkers by linking these clusters to broader experimental data and conducting sex-stratified analyses of daily hormone levels to better understand sex-specific mechanisms of disease severity.
