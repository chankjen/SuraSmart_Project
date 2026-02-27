# Sura Smart: Regulatory Compliance Framework

**Version:** 1.0 | **Date:** 2026-02-27 | **Classification:** Internal Engineering Reference

This document maps each regulatory requirement to the concrete technical implementation in the Sura Smart codebase. It must be reviewed annually and updated whenever the data model, jurisdiction, or data flows change.

---

## 1. Biometric Information Privacy Act (BIPA) — Illinois / US

| Requirement | Implementation |
|---|---|
| Written consent before collecting biometric data | `SearchSession.consent_given = True` required (enforced by frontend consent modal). Field is stored and immutable after creation. |
| Retain consent records | `SearchSession` records are never deleted; only uploaded images are purged (see GDPR below). |
| Inform subjects of purpose and retention | Required to be displayed in the app's consent modal (frontend obligation). |
| No sale of biometric data | No third-party data sharing integrations exist. Any future sharing requires legal review. |

**Code references:**
- Model field: [`SearchSession.consent_given`](file:///d:/SuraSmart_Project/backend/facial_recognition/models.py)
- API enforcement: [`search_facial_recognition`](file:///d:/SuraSmart_Project/backend/facial_recognition/views.py) receives and stores `consent_given` from frontend.

---

## 2. GDPR (EU) & CCPA (California)

### 2.1 Right to Erasure (Article 17 — GDPR)

Biometric image files and face embeddings are purged for resolved cases after 90 days.

```bash
# Run manually or schedule via Celery beat
python manage.py purge_closed_cases --days 90

# Preview deletions without executing
python manage.py purge_closed_cases --days 90 --dry-run
```

**What is purged:**
- Physical image files (`media/facial_recognition/...`)
- `face_embedding` JSON field (set to `null`)
- Search session uploaded images (`media/search_sessions/...`)

**What is retained (for audit trail):**
- `FacialRecognitionImage` DB row (with `status = 'purged'`)
- `SearchSession` row (with image field cleared)
- `FacialMatch` records and `blockchain_hash` values

### 2.2 Data Minimization (Article 5(1)(c) — GDPR)

- Only biometric data strictly necessary for identification is stored.
- No raw video data is retained; only extracted embeddings per search.
- `FacialRecognitionImage` embeddings are stored once and reused (no duplicate processing).

### 2.3 Data Subject Rights

| Right | Implementation |
|---|---|
| Access | `GET /api/missing-persons/` filtered by `reported_by` returns all a family user's data. |
| Erasure | `purge_closed_cases` command + manual admin deletion. |
| Portability | All data is serializable via DRF serializers. Export script is planned (Phase 2). |

---

## 3. Cross-Border Data Transfer (Schrems II)

| Requirement | Implementation |
|---|---|
| EU data must stay in EU | Deploy `sura_smart_backend` to AWS `eu-central-1` (Frankfurt) for EU users. |
| Data residency controls | `DATABASE_URL` and `MEDIA_ROOT` are environment-variable configured per region. |
| Standard Contractual Clauses | Required for any AWS/Azure sub-processor. Legal team must sign SCCs before production EU launch. |

**Docker Compose override for EU deployment:**
```yaml
# docker-compose.eu.yml
services:
  backend:
    environment:
      - AWS_REGION=eu-central-1
      - DATABASE_URL=${EU_DATABASE_URL}
```

---

## 4. Law Enforcement Chain of Custody (TRD Section 1.1.4)

All searches and matches are audit-logged:

| Event | Audit Record |
|---|---|
| Facial search performed | `SearchSession` row with user, timestamp, `consent_given`, and session ID |
| Match created | `FacialMatch` row with `algorithm_version`, `model_name`, `match_confidence` |
| Match verified / rejected | `verified_by`, `verified_at`, `verification_notes` on `FacialMatch` |
| Blockchain notarization | `FacialMatch.blockchain_hash` (SHA-256 of match payload, to be anchored to chain in Phase 2) |

---

## 5. Human-in-the-Loop (HITL) Protocol — TRD Section 4.2.3

Any AI match where `90% ≤ confidence < 98%` is flagged `requires_human_review = True`.

**Enforcement:**
- Frontend displays a warning banner for borderline matches.
- `finalize` action is disabled in the UI until an authorized officer verifies or rejects the match via `POST /api/facial-recognition/facial-matches/{id}/verify/`.
- Only users with `can_verify_matches = True` (Police / Government roles) can clear the flag.

---

## 6. Audit Schedule (TRD Section 10.5)

| Frequency | Activity | Command / Owner |
|---|---|---|
| Weekly | Automated drift detection | Celery beat task (planned) |
| Quarterly | Full demographic bias audit | `python manage.py run_bias_audit --output-dir reports/` |
| Annually | Third-party algorithmic audit | External auditor (e.g., O'Neil Risk Consulting) |

---

## 7. Licensing Compliance

| Dataset / Library | License | Usage |
|---|---|---|
| DeepFace | MIT | ✅ Unrestricted commercial use |
| NumPy | BSD | ✅ Unrestricted |
| LFW (Labeled Faces in the Wild) | Unrestricted academic | ⚠️ MVP/Testing only |
| UTKFace | CC-BY | ✅ Attribution required in publications |
| VGGFace2 | Academic Use Only | ❌ **Requires commercial license before production training** |
| CelebA | Non-commercial | ❌ **Do NOT use for production model training** |

> [!CAUTION]
> Training the production Facenet512 model on VGGFace2 or CelebA without a commercial license is a **legal violation**. Use synthetic data (StyleGAN3) or negotiate licensing before production deployment.

---

## 8. Recommended Next Steps

1. **Immediate:** Obtain legal sign-off on `consent_given` modal copy (BIPA requirement).
2. **Short-term:** Schedule `purge_closed_cases` as a Celery beat task (90-day cadence).
3. **Short-term:** Anchor `blockchain_hash` to a public or permissioned blockchain for immutable audit trail.
4. **Pre-launch:** Sign SCCs with AWS for EU data residency.
5. **Pre-launch:** Commission external algorithmic bias audit (O'Neil Risk Consulting or equivalent).
