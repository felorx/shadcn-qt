# License and product tiers

The public shadcn-qt codebase has one feature set and two alternative license
paths. Paying for a commercial license changes the legal rights for proprietary
use; it does not unlock the public widgets with a runtime key.

| Path | Cost | May ship a closed-source application? | Main obligations |
| --- | --- | --- | --- |
| GPL-3.0-only | Free | No, unless the complete combined work is distributed compatibly with GPLv3 | Preserve notices, provide corresponding source, license the covered combined work under GPLv3 |
| Commercial | Paid by active developer seat | Yes | Retain a valid Order Form, stay within the seat count, do not redistribute shadcn-qt as a standalone/competing library |
| Evaluation | Time-limited when issued | No production distribution | Internal evaluation only for the period on the Order Form |

## Standard commercial packaging

- **Individual**: one Authorized Developer.
- **Team**: a stated number of Authorized Developers under one organization and
  Order Form.
- **Enterprise**: negotiated seat or site scope, procurement terms, support,
  and optional SLA.

The standard commercial agreement permits unlimited Applications and unlimited
end-user copies, with no runtime royalty. Unless an Order Form says the license
itself expires, customers keep the right to use versions obtained during the
paid update period; renewal is needed for later versions and continued support.
Prices, currency, tax, support, governing law, and the legal licensor identity
belong in the Order Form rather than source code.

## Public package and future add-ons

The public `shadcn-qt` distribution contains the complete current 65-class
catalog, native-widget compatibility, themes, and Qt Designer integration. The
same artifact can be used under GPL or a commercial Order Form.

`shadcn_qt.pro` remains reserved for possible separately ordered enterprise
extensions such as specialized remote-data adapters, advanced Designer
tooling, private theme registries, or SLA integrations. A commercial license
for the public package does not automatically include a future Pro artifact.

See [COMMERCIAL.md](COMMERCIAL.md), [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md),
and the repository [LICENSE](../LICENSE).
