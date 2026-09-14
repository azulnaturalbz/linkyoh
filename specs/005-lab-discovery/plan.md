# Implementation plan

Spec Kit artifacts are provided here before implementation. This checkout has
no .specify scripts or repo-local Spec Kit skills, so their commands cannot run;
no tooling bootstrap or runtime dependency changes are part of this dispatch.

1. Extract presentation blocks in base.html, preserving its sole metadata renderer.
   Lab pages override only chrome/assets; legacy forms/help stay on their base.
2. Reuse approved CSS/assets, not fixture businesses/images/check records. Add
   shared Django cards, finder, Checked, contact and provider components.
3. Add read-only discovery adapter and batched evidence queries. Validate and pair
   geography before pagination; retain canonical wrappers and existing ordering.
4. Add built-in locale middleware/catalogs and gated WOP context. Preserve native
   GET forms; enhancement must not be required for the primary journey.
5. Run isolated synthetic database tests and browser matrix. No production DB or
   contact calls. Commit app-only source/evidence, update own ledger row and HOLD.

Recovery: revert the UI commit/release image after authorization; no schema or
data backfill exists. Deployment later uses shared-host app-only procedure.
