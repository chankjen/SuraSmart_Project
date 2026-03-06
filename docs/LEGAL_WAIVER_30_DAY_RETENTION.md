# Sura Smart - Mobile/Web Biometric Data Retention Waiver

**Under the provisions of the Kenya Data Protection Act (2019) and associated regulations regarding data minimization and evidence retention:**

## 1. Context and Purpose
The Sura Smart platform employs advanced facial recognition and biometric processing to assist law enforcement in locating missing persons. To comply with Data Minimization principles, standard operating procedures dictate that biometric data processed within the system is cryptographically destroyed within **30 days** after a case is formally resolved and closed.

## 2. Retention Tiering 
Sura Smart utilizes a tiered retention policy based on the nature of the case:
- **Standard Cases (Found Safe):** All Personally Identifiable Information (PII) and biometric data (images, facial embeddings, voice prints) are permanently deleted 30 days post-resolution. Only a non-reversible cryptographic hash of the case log is retained on the blockchain for auditing purposes.
- **Criminal Cases (Foul Play Suspected):** Data is retained for **5 years** to support ongoing criminal investigations, prosecutions, and as mandated by standard law enforcement evidence retention schedules.

## 3. Acknowledgment and Consent
By utilizing the Sura Smart platform and contributing biometric data (e.g., uploading photos of a missing person), the reporting party (Family Member/Guardian) and the investigating authority (Police Officer) acknowledge and agree to the following:

1. **Standard Deletion:** Unless explicitly flagged as a "Criminal Case" by the investigating authority, all uploaded images and generated biometric models associated with the case will be irreversibly destroyed 30 days after the case changes to the `CLOSED` status.
2. **Loss of Evidence:** Once cryptographically shredded, this data **cannot** be retrieved by the Sura Smart system, law enforcement, or any other party for any subsequent investigations. 
3. **Waiver of Further Retention:** The reporting party waives any expectation that the submitted biometric data will be retained beyond the 30-day window for standard non-criminal cases.
4. **Blockchain Auditability:** The system will permanently retain a minimal metadata footprint (cryptographic hash) on a private ledger. This hash proves that the case existed and was properly handled, but it cannot be used to reconstruct any PII or imagery.

## 4. Authorization Signatures

**Reporting Party (Family Member/Guardian):**
Name: ______________________
Date: ______________________
Signature: ______________________

**Investigating Authority (Police Officer):**
Name: ______________________
Badge/ID Number: ______________________
Date: ______________________
Signature: ______________________

---
*Document Version: 1.0 (Kenya MVP)*
*Legal Basis: Kenya Data Protection Act (2019) - Section 39 (Retention of personal data)*
