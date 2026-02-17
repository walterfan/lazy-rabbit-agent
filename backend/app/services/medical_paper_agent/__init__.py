"""
Medical Paper Writing Assistant — Multi-Agent System.

Implements a Supervisor + SubAgent architecture for medical paper writing:
  - LiteratureAgent: PubMed/ClinicalTrials.gov literature search
  - StatsAgent: Statistical analysis (t-test, Cox regression, etc.)
  - WriterAgent: IMRAD structure paper writing
  - ComplianceAgent: CONSORT/STROBE compliance checking
"""
