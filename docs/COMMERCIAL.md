# Commercial licensing

shadcn-qt follows the established “GPL or commercial” library model. The public
package is useful and complete; organizations that cannot comply with GPLv3 can
purchase permission to use the same shadcn-qt code in proprietary applications.

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

1. Replace the generic copyright-holder description with the legal owner where
   appropriate and put the licensor's legal name, address, and notice email on
   every Order Form.
   Also replace the generic LICENSE copyright-holder text and Python package
   author, then configure real source, documentation, and sales URLs; the
   release workflow blocks until this is done.
2. Have qualified counsel review the commercial agreement, ownership chain,
   governing law, tax handling, privacy terms, and refund/consumer rules.
3. Use [ORDER_FORM_TEMPLATE.md](ORDER_FORM_TEMPLATE.md) as the operational
   checklist, not as a substitute for legal review.
4. Record CLA acceptance before merging third-party copyrighted contributions.
5. Give each customer a durable invoice/order ID and retain the exact agreement
   version that applied to the sale.
6. Never claim that a shadcn-qt purchase includes Qt or PyQt commercial rights.

The standard terms are in
[`LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt`](../LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt).
This project documentation is not legal advice.
