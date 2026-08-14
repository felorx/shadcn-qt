# Core and Pro

shadcn-qt Core remains public and complete for its documented component set.
Customers choose GPL-3.0-only or buy commercial Core rights for proprietary
applications.

shadcn-qt Pro is distributed separately through a private package channel. Its
distribution name is `shadcn-qt-pro` and its Python import name is
`shadcn_qt_pro`. The public `shadcn_qt.pro` namespace is only a bridge and never
contains private implementation code.

Core commercial rights do not include Pro. A Pro Order Form and signed license
certificate define:

- customer and license ID;
- active developer seats;
- enabled feature identifiers;
- covered Pro releases and update end date;
- perpetual, subscription, or evaluation term;
- support and SLA, if any.

Perpetual covered releases continue to work after maintenance ends. Renewal
controls access to later releases and support. Only evaluation or explicitly
expiring subscription entitlements should stop at a runtime expiry date.

Private signing keys, customer certificates, and entitlement records are never
stored in the public repository.
