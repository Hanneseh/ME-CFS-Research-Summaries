#!/usr/bin/env python
"""Fetch grounding content (abstracts) for new_source clusters.

For each new_source work item, resolve the best PMID/DOI/URL from its cluster
members and fetch a PubMed abstract via NCBI eutils where a PMID exists.
Writes agent-cli/state/source_grounding.json keyed by cluster_id. Clusters
without a PMID get abstract=null and are listed for manual/page resolution.
"""
from __future__ import annotations

import json
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
STATE = BASE / "agent-cli" / "state"
OUT = STATE / "source_grounding.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def main() -> None:
    clusters = {c["cluster_id"]: c for c in json.loads((STATE / "candidate_clusters.json").read_text())}
    work = json.loads((STATE / "work_items.json").read_text())["work_items"]
    ns = [w for w in work if w["decision"] == "new_source"]

    grounding = {}
    pmid_to_cluster = {}
    for w in ns:
        cid = w["cluster_id"]
        cl = clusters.get(cid, {})
        pmid = doi = url = title = None
        for m in cl.get("members", []):
            title = title or m.get("title")
            url = url or m.get("canonical_url") or m.get("link")
            if not pmid and m.get("pmid"):
                pmid = m["pmid"]
            if not doi and m.get("doi"):
                doi = m["doi"]
        grounding[cid] = {
            "cluster_id": cid,
            "primary_thread": w.get("primary_thread"),
            "secondary_threads": w.get("secondary_threads") or [],
            "title": title,
            "url": url,
            "pmid": pmid,
            "doi": doi,
            "abstract": None,
        }
        if pmid:
            pmid_to_cluster.setdefault(pmid, []).append(cid)

    pmids = list(pmid_to_cluster.keys())
    if pmids:
        params = f"?db=pubmed&id={','.join(pmids)}&retmode=xml"
        req = urllib.request.Request(EUTILS + params, headers={"User-Agent": "ME-CFS-curation/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            xml = r.read().decode("utf-8", errors="replace")
        root = ET.fromstring(xml)
        for art in root.findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            title = art.findtext(".//ArticleTitle") or ""
            abst_parts = []
            for ab in art.findall(".//Abstract/AbstractText"):
                label = ab.get("Label")
                txt = "".join(ab.itertext())
                abst_parts.append(f"{label}: {txt}" if label else txt)
            journal = art.findtext(".//Journal/Title") or ""
            year = art.findtext(".//PubDate/Year") or art.findtext(".//ArticleDate/Year") or ""
            abstract = "\n".join(abst_parts).strip()
            for cid in pmid_to_cluster.get(pmid, []):
                grounding[cid]["abstract"] = abstract or None
                grounding[cid]["resolved_title"] = title
                grounding[cid]["journal"] = journal
                grounding[cid]["year"] = year

    OUT.write_text(json.dumps(grounding, indent=2), encoding="utf-8")
    with_abs = sum(1 for g in grounding.values() if g["abstract"])
    print(f"new_source clusters: {len(ns)}")
    print(f"PMIDs queried: {len(pmids)} | clusters with abstract: {with_abs}")
    print("Clusters WITHOUT abstract (need page/DOI resolution):")
    for cid, g in grounding.items():
        if not g["abstract"]:
            print(f"  {cid} | {g['primary_thread']} | pmid={g['pmid']} doi={g['doi']} | {(g['title'] or '')[:50]} | {g['url']}")


if __name__ == "__main__":
    main()
