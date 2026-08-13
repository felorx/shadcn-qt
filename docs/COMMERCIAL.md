# Commercial licensing

shadcn-qt follows the established “GPL or commercial” library model. The public
package is useful and complete; organizations that cannot comply with GPLv3 can
purchase permission to use the same shadcn-qt code in proprietary applications.
Commercial licensing is offered by [Felorx](https://felorx.com), the current
publisher and copyright holder identified by the project metadata.

## What a standard commercial license includes

- use in closed-source internal and distributed Applications;
- source access and internal modifications without a shadcn-qt source-disclosure
  obligation;
- unlimited Applications and end-user copies;
- no runtime, device, or revenue royalty;
- a defined number of active developer seats;
- continued use of versions received during the paid update period, unless the
  Order Form explicitly uses an expiring subscription;
- updates and support only for the period and service level on the Order Form.

CI runners and unattended build agents do not consume seats. Every employee or
contractor who accesses the shadcn-qt source or uses it to design, develop, test,
maintain, or build an Application does consume a seat.

## How entitlement works

The PyPI artifact contains both the GPL text and the standard commercial terms.
It does not contain DRM and does not call an activation server. A commercial
customer's proof of entitlement is the accepted Order Form, invoice, checkout
receipt, or license certificate that identifies the customer, licensor, seats,
covered edition/version, and term.

Downloading or installing `shadcn-qt` from PyPI does not by itself create a
commercial license. Without a valid Order Form, the current package is offered
under GPL-3.0-only.

## Core commercial rights and Pro access

The public `shadcn-qt` package is Core. Buying commercial rights for Core
changes the legal terms for proprietary applications; it does not unlock or
include `shadcn-qt-pro`.

Pro is a separately ordered private distribution. A Pro Order Form and signed
license certificate identify the customer, licensed seats, enabled features,
covered release range, update period, and any evaluation or subscription end
date. The certificate is entitlement evidence and supports offline validation;
it is not a substitute for the accepted Order Form and payment record.

For perpetual covered versions, enforcement belongs at the download and update
boundary: ending maintenance must not disable a version the customer already
has a continuing right to use. Evaluation or explicitly expiring subscriptions
may stop at the date stated in their Order Form.

## Suggested offer structure

| Offer | Scope | Typical sales motion |
| --- | --- | --- |
| Individual | 1 developer | Self-service checkout |
| Team | Named seat count, one organization | Self-service or invoice |
| Enterprise | Negotiated seats/site, SLA and procurement terms | Signed Order Form |
| Evaluation | Fixed non-production period | Zero-cost evaluation Order Form |

Set currency, price, taxes, refund policy, support channel, update duration, and
regional consumer terms in the storefront and Order Form. Do not encode them in
the Python package, where they would be difficult to change correctly.

## Before the first sale

1. The public publisher is currently identified as Felorx. Before issuing an
   Order Form, replace the publisher name with the full legal person/entity name
   if Felorx is only a brand, and include the licensor's address and notice
   email on every Order Form.
2. Have qualified counsel review the commercial agreement, ownership chain,
   governing law, tax handling, privacy terms, and refund/consumer rules.
3. Use [ORDER_FORM_TEMPLATE.md](ORDER_FORM_TEMPLATE.md) as the operational
   checklist, not as a substitute for legal review.
4. Record CLA acceptance before merging third-party copyrighted contributions.
5. Give each customer a durable invoice/order ID and retain the exact agreement
   version that applied to the sale.
6. Never claim that a shadcn-qt purchase includes Qt or PyQt commercial rights.
7. Keep Pro signing private keys outside source control and retain immutable
   license-certificate issuance and revocation records.

The standard terms are in
[`LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt`](../LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt).
This project documentation is not legal advice.
