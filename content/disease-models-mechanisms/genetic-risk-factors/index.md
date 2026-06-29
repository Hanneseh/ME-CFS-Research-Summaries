---
title: Genetic Risk Factors
description: A living thread on GWAS, whole-genome sequencing, Mendelian randomization, genetic correlations, rare monogenic variation, combinatorial genetic analysis, and gene-prioritization studies in ME/CFS.
date: 2026-06-11
last_updated: 2026-06-11
thread_status: active
evidence_level: early replication, landmark GWAS published
primary_topics:
  - GWAS & Common Variant Association
  - Whole-Genome Sequencing & Rare Variants
  - Mendelian Randomization
  - Combinatorial Genetic Analysis
  - Gene Prioritization & Network Medicine
  - Genetic Correlation with Comorbidities
cssclasses: [thread-page]
---

## Current Takeaway

Genetic research into ME/CFS has moved from underpowered candidate-gene studies to large-scale, replicable findings. The DecodeME genome-wide association study—the largest ME/CFS genetic study to date, comparing 15,579 cases against 259,909 controls—identified eight genome-wide significant loci pointing to immune response genes (BTN2A2, OLFM4, RABGAP1L) and a neurological pain signal (CA10). Critically, the genetic risk profile did not overlap with depression or anxiety, providing objective biological evidence that distinguishes ME/CFS from psychiatric conditions. Complementary methods including Mendelian randomization, combinatorial analytics, protein quantitative trait loci (pQTL) analysis, and whole-genome sequencing (WGS) have independently converged on immune dysregulation, neurological dysfunction, energy metabolism, and calcium signaling as biologically grounded disease pathways.

The picture emerging across studies is of a polygenic, highly heterogeneous condition in which both common variants with small individual effects and rare variants with large individual effects contribute to risk. Combinatorial analysis of the DecodeME cohort identified over 22,000 reproducible multi-SNP signatures across 2,311 unique genes, and WGS of 31 participants from 25 families found pathogenic or likely pathogenic variants in 39% of affected individuals—predominantly affecting ATP generation and oxidative phosphorylation. A meta-GWAS combining DecodeME and the Million Veteran Program (MVP) found significant enrichment in brain regions (cerebellum, frontal cortex) and glutamatergic synapse gene sets, whereas no peripheral tissue reached significance, pointing toward a central neurobiological dimension of risk. Across all approaches, evidence is early and in many cases limited to European-ancestry cohorts; causal pathways are plausible but not yet clinically actionable, and no diagnostic genetic test or genetically guided treatment has been validated.

## Why This Matters

Establishing the genetic architecture of ME/CFS provides an objective biological anchor for a disease that has been historically contested. Identifying heritable risk loci enables mechanistic hypothesis generation, drug-target discovery, and patient stratification—essential preconditions for designing treatments that address root causes rather than symptoms. The finding of shared genetic risk with Long COVID supports the hypothesis that post-viral illness has a genetically predisposed substrate, opening the possibility that findings in one condition may accelerate research in the other. Mendelian randomization adds causal inference beyond association, identifying higher mitochondrial DNA copy number as protective and increased mean platelet volume as a risk factor—biomarker candidates that could eventually support stratified trial design.

## State of Evidence

- **Established:** ME/CFS has a heritable component. The DecodeME GWAS produced the first genome-wide significant loci with stringent case definitions requiring post-exertional malaise. These loci cluster around immune and neurological function, and the risk profile does not overlap genetically with depression or anxiety.
- **Plausible but early:** Combinatorial multi-SNP signatures (neurological dysregulation, inflammation, calcium signaling, cellular stress) are reproducible across independent patient subgroups within the DecodeME cohort. Rare monogenic variants in energy metabolism and synaptic signaling pathways are found in a substantial minority of affected families in small WGS studies. Mendelian randomization implicates mitochondrial DNA copy number and platelet characteristics as potential causal factors. Genetic variants affecting metabolite levels (HSD11B1, SCGN) suggest a partly heritable metabolic phenotype. Glutamatergic synapse enrichment in a two-dataset meta-GWAS converges with rare WGS variant signals in the same neuronal gene sets.
- **Not established:** Causal genetic mechanisms sufficient to diagnose ME/CFS or predict treatment response. Replication of DecodeME GWAS hits in non-European or less strictly defined cohorts. Whether rare monogenic findings in small WGS cohorts generalise to the broader ME/CFS population. Clinical actionability of any identified genetic risk profile.
- **Key limitations:** Most studies rely on European-ancestry samples, limiting generalisability. UK Biobank cohorts used as controls or case sources depend on self-reported diagnoses, introducing misclassification risk. Small pQTL and WGS cohorts require larger external validation. The DecodeME GWAS was not replicated in looser-phenotype biobanks, which the authors attribute to case-definition differences; this remains unresolved.

## Timeline

### 2025-04-14 - Network medicine framework prioritises 250 candidate genes via protein interaction mapping

A computational study mapped a set of 22 ME/CFS-associated seed genes onto the STRING protein interaction database and applied a Random Walk with Restart algorithm to rank 1,063 interacting proteins by network proximity, selecting the top 250 to define an in silico "ME/CFS disease module." Pathway enrichment of this module revealed significant overlaps with sphingolipid metabolism, energy-related pathways, heme degradation, thermogenesis, and TP53-regulated metabolic genes, and the module showed substantial genetic overlap with known metabolic and neurodegenerative disorders. The result is a prioritised candidate gene list intended to filter exome and genome sequencing data in future patient cohorts rather than a diagnostic framework. Because the analysis is entirely in silico and based on pre-existing literature, the identified module is a theoretical scaffold that requires experimental validation, and reliance on published literature may bias the results toward well-studied pathways.

Sources:

- [Maccallini 2025, medRxiv](https://doi.org/10.1101/2025.04.13.25325733)

### 2025-08-06 - DecodeME GWAS identifies eight genome-wide significant loci, including immune and pain genes

The DecodeME collaboration published the first large-scale, co-produced GWAS for ME/CFS, comparing 15,579 cases of European ancestry (diagnosed with stringent criteria requiring post-exertional malaise) against 259,909 UK Biobank controls. Eight genome-wide significant loci were identified: three near immune-response genes (BTN2A2, OLFM4, RABGAP1L), one near CA10 sharing a signal with multisite chronic pain, and four additional regions. Importantly, the genetic risk profile showed no overlap with depression or anxiety, strengthening the biological distinction of ME/CFS from psychiatric conditions. The findings did not replicate in other large biobanks using less stringent case definitions, which the authors attribute to case-definition heterogeneity rather than false-positive signals; replication in independent strictly-defined cohorts and fine-mapping remain to be completed, and rare variants and non-European ancestries were not analysed.

Sources:

- [DecodeME Collaboration 2025, medRxiv preprint](https://doi.org/10.1101/2025.08.06.25333109)

### 2025-11-28 - Metabolite GWAS links genetic variants in HSD11B1 and SCGN to metabolic perturbations

A metabolite genome-wide association study (mGWAS) compared 875 ME/CFS patients with 36,033 controls from the UK Biobank, testing 135 NMR-measured metabolic biomarkers including lipoproteins, fatty acids, and low-molecular-weight metabolites. The study identified 112 significant genetic-metabolic associations unique to the ME/CFS group, with variants in HSD11B1—a gene encoding an enzyme central to cortisol regeneration in peripheral tissues—associated with changes in VLDL phospholipids, and variants in SCGN affecting total fatty acid levels. Additional immune-related genes (ADAP1, NR1H3, CD40) showed differential genetic effects on metabolic pathways between patients and controls, suggesting combined disruption of lipid metabolism, inflammation, and neurotransmitter transport. The study's primary limitation is its reliance on UK Biobank self-reported diagnoses, which may include misdiagnosed individuals, and the patient group had higher rates of medication use that could confound metabolic readings.

Sources:

- [Huang et al. 2025, iScience](https://doi.org/10.1016/j.isci.2025.114316)

### 2025-12-03 - Combinatorial analytics identifies over 22,000 reproducible multi-SNP signatures across 2,311 genes

Using the PrecisionLife combinatorial analytics platform, researchers analysed genomic data from 14,767 DecodeME participants and compared them to UK Biobank controls, searching for combinations of one to four SNPs significantly over-represented in ME/CFS cases across three independent patient subgroups to ensure reproducibility. The analysis identified 22,411 reproducible genetic signatures involving 2,311 unique genes, with individuals carrying the highest burden of signatures 1.64 times more likely to have ME/CFS than those with the fewest. A core set of 259 genes mapped to four mechanistic domains—neurological dysregulation, inflammation, cellular stress, and calcium signalling—and 76 of 180 genes previously linked to Long COVID were shared with ME/CFS, indicating substantial but partial biological overlap between the two conditions. The study was a preprint at publication and relied on self-reported questionnaire data, though these were validated against clinical criteria; its central implication—that ME/CFS is highly polygenic and unlikely to respond to a single universal treatment—awaits peer review and independent replication.

Sources:

- [Sardell et al. 2025, medRxiv preprint](https://doi.org/10.64898/2025.12.01.25341362)

### 2025-12-19 - pQTL analysis links complement pathway genetic variants to an inflammatory patient subgroup

A pQTL study in 50 ME/CFS patients and 121 non-fatigued controls tested 9,146 SNPs for associations with plasma complement protein levels, identifying 3,192 significant associations including 11 variants previously linked to ME/CFS in other analyses. A distinct patient subgroup was characterised by a "high C3/low Bb" complement protein profile indicating dysregulation of the alternative complement pathway, and six significant pQTLs were independently validated through their association with fatigue-related phenotypes in the UK Biobank. The findings provide a genetic mechanism by which risk alleles may drive inflammatory heterogeneity, and C3 and Factor B emerge as candidate predictive markers. The small cohort size (50 patients) is the primary limitation and necessitates replication in substantially larger cohorts before these pQTL signals can be considered robust.

Sources:

- [Maya et al. 2025, Preprints.org](https://doi.org/10.20944/preprints202512.1773.v1)

### 2025-12-24 - Whole-genome sequencing finds rare pathogenic variants in 39% of affected individuals

A precision genomics study applied clinical-grade whole-genome sequencing to 31 participants from 25 families and RNA sequencing to 16 of those patients, using machine-learning triage to identify rare, large-effect monogenic variants. Pathogenic or likely pathogenic variants were identified in 39% of affected individuals, predominantly involving pathways of ATP generation, oxidative phosphorylation, and synaptic signalling. Despite high genetic diversity between patients, the individual mutations converged on shared core problems—impaired energy production and reduced cellular stress resilience—supporting a model in which ME/CFS may represent a collection of distinct rare molecular disorders that share a physiological endpoint. The cohort of 31 participants is too small to estimate population-level prevalence of monogenic contributors, and larger prospective family-based and population-based WGS studies are required to determine how commonly rare variants drive ME/CFS independently of common polygenic risk.

Sources:

- [Birch et al. 2025, Journal of Translational Medicine](https://doi.org/10.1186/s12967-025-07586-w)

### 2026-04-21 - Mendelian randomization with DecodeME data implicates mitochondrial DNA copy number and platelet volume as causal factors

Researchers applied genetic correlation, pleiotropic heritability analysis, and Mendelian randomization to DecodeME summary statistics (15,579 cases, 259,909 controls), evaluating 22 trait domains spanning cellular energetics, neurovascular regulation, and barrier-microbiome function. Strong genetic overlap was found between ME/CFS and migraine, irritable bowel syndrome, and cellular energetics domains. Mendelian randomization identified three potential causal factors: higher mitochondrial DNA copy number was protective against ME/CFS, while increased glycoprotein acetyls and higher mean platelet volume increased risk, pointing toward energy metabolism and platelet-associated inflammatory signalling as mechanistically upstream features of susceptibility. The analysis relied on GWAS summary statistics rather than individual-level data, limiting the ability to capture patient subgroup heterogeneity, and the identified causal factors require replication and experimental follow-up before they can inform clinical decisions.

Sources:

- [Wielscher et al. 2026, Research Square preprint](https://doi.org/10.21203/rs.3.rs-9363637/v2)

### 2026-05-15 - Meta-GWAS of DecodeME and MVP (19,470 cases) finds CNS enrichment and glutamatergic synapse signals replicated in WGS data

A meta-analysis combined the DecodeME GWAS with the Million Veteran Program (MVP) dataset, totalling 19,470 cases and 699,111 controls of European ancestry, and ran post-GWAS enrichment analyses across tissues, cell types, and canonical pathways. The analysis found significant genetic enrichment in multiple brain regions—including the cerebellum and frontal cortex—and the pituitary gland, while no peripheral tissue (muscle, immune) reached statistical significance; the most specific replicated pathway was glutamatergic synapses, the brain's primary excitatory signalling system. These CNS enrichment signals were then validated against an independent set of 115 ME/CFS risk genes previously identified via machine learning on WGS data from a separate European-ancestry cohort, providing multi-level convergence. The study is a preprint, relies on European-ancestry public datasets, uses self-reported clinician diagnoses in some cohorts, and physical-proximity gene mapping may misattribute some signals; how these neuronal enrichment signals mechanistically produce the peripheral and systemic features of ME/CFS is not yet explained.

Sources:

- [Maccallini 2026, Research Square preprint](https://doi.org/10.21203/rs.3.rs-9702020/v1)

### 2026-06-11 - Solve M.E. webinar highlights launch and genetic rationale of Sequence ME & Long Covid project

Solve M.E. hosted an educational webinar featuring the DecodeME management team—including Prof. Chris Ponting, Sonya Chowdhury, and Andy Devereux-Cooke—to discuss the launch of the "Sequence ME & Long Covid" study. Moving beyond the GWAS design of DecodeME (which identified 8 risk loci across 15,500 genomes), the new project will use Oxford Nanopore long-read whole-genome sequencing to read all 3 billion base pairs of participants. This allows detection of rare genetic and structural variations (deletions, inversions) invisible to standard GWAS. The project has secured £4.75 million in UK government and donor funding for Phase 1 to sequence 6,000 ME/CFS patient samples from DecodeME, with ultimate goals of sequencing 9,000 ME/CFS and 9,000 Long Covid patients. The team argued that whole-genome sequencing is a necessary starting point to build a biological blueprint for defining disease subtypes and discovering drug targets. As a project launch and funding announcement, this presentation outlines the study rationale and does not report clinical efficacy or diagnostic outcome data.

Sources:

- [Ponting et al. 2026, Solve M.E. Webinar](https://youtu.be/v6VQ2593m-8?si=-OnvQ_DFYRITTicN)

## Open Questions

- Do the eight DecodeME GWAS loci replicate in strictly-defined ME/CFS cohorts outside European-ancestry UK populations?
- What proportion of ME/CFS cases carry rare monogenic variants with large individual effects, as opposed to polygenic common-variant burden alone?
- Do the convergent neuronal and glutamatergic enrichment signals in meta-GWAS reflect primary CNS pathology, or downstream gene-expression consequences of peripheral immune and metabolic dysfunction?
- Can the 76 genes shared between ME/CFS and Long COVID genetic profiles identify patient subgroups who are most likely to benefit from common therapeutic strategies?
- How do heritable metabolic perturbations (HSD11B1, cortisol regeneration, lipid profiles) interact with environmental post-viral triggers in determining who develops ME/CFS after infection?

## Related Threads

- [Mitochondrial & Metabolic Dysfunction](../mitochondrial-metabolic-dysfunction/)
- [Immune Dysregulation & Inflammation](../immune-dysregulation-inflammation/)
- [Neuroinflammation & Brain Changes](../neuroinflammation-brain-changes/)
