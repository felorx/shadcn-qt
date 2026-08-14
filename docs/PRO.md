# Core and Pro architecture

## Product boundary

This public repository and the `shadcn-qt` distribution contain Core. Core is a
usable product under GPL-3.0-only or a commercial Core Order Form. It must not
depend on Pro at import time or degrade when Pro is absent.

Install public Core from PyPI with exactly one Qt binding extra, for example:

```bash
python -m pip install "shadcn-qt[pyside6]"
```

Pro is maintained in a private repository and distributed as `shadcn-qt-pro`
with the import name `shadcn_qt_pro`. The public `shadcn_qt.pro` package is a
small compatibility bridge that imports and forwards the private package only
when it is installed.

The repositories must not form a split Python package. A private distribution
must never install files below the public `shadcn_qt/` directory.

## Initial Pro product plan

Pro capabilities should be independently valuable and should not remove or
artificially degrade documented Core behavior. Planned categories are:

1. high-volume DataTable and remote-data adapters;
2. advanced charts and export adapters;
3. advanced Qt Designer tooling and commercial templates;
4. organization theme registries and governed design-token workflows;
5. C++ catalog expansion, LTS compatibility, migration tooling, and enterprise
   support integrations.

Exact availability is defined by release notes and the customer's Order Form;
this roadmap is not a contractual promise.

## Entitlement design

Pro uses signed offline JSON certificates. A certificate contains an immutable
license ID, customer name, edition, developer seats, enabled features, issue
date, update end date, optional runtime expiry, and optional metadata. The
issuer signs a canonical JSON payload with Ed25519.

The signing private key stays outside source control and build artifacts. The
verification public key may ship with Pro. Issuance records, revocations,
payment evidence, and accepted agreement versions belong in a restricted
commercial system of record, not either source repository.

For perpetual covered versions, the package release date is compared with the
certificate's update end date. The current date does not disable that already
covered release. Runtime expiry is reserved for evaluation and explicitly
expiring subscriptions.

## Delivery controls

- private GitHub repository for source and CI;
- private package index or authenticated release downloads for wheels/sdists;
- short-lived download credentials and organization-scoped access;
- signed license certificate delivered separately from package credentials;
- signed releases, hashes, and immutable customer issuance records;
- no production private keys, customer certificates, or package tokens in Git.

## Public release guardrails

`tools/check_core_boundary.py` fails when private package paths, key material,
or customer certificates appear in Core. `tools/check_python_dist.py` also
rejects a public wheel containing `shadcn_qt_pro` implementation files. Both
checks must run before every public release.
