---## [NearBlocks API](https://api.nearblocks.io/api-docs/)

The NearBlocks API provides a simple way to query actions that happened on a NEAR account, such as function calls, token transfers, etc

```bash
# All the times **anyone** called "create_drop" on Keypom
https://api.nearblocks.io/v1/account/v2.keypom.near/txns?method=create_drop

# All the times that gagdiez.near called "create_drop" on Keypom
https://api.nearblocks.io/v1/account/v2.keypom.near/txns?method=create_drop&from=gagdiez.near
```


<details>
  <summary> Response </summary>

```json
{
  "txns": [
    {
      "predecessor_account_id": "gagdiez.near",
      "receiver_account_id": "v2.keypom.near",
      "receipt_kind": "ACTION",
      "receipt_outcome": {
        "status": true,
        ...
      },
      ...
    }
  ]
}
```

</details>

:::info More info

Find more information about the NearBlocks API in their [api page](https://api.nearblocks.io/api-docs/)

:::

---

## [FastNear API](https://fastnear.com/)

FastNear exposes low-latency APIs for wallets and explorers. Their API allows you to easily query the NEAR blockchain to get an account's assets, map keys into account IDs, explore a block's transactions, etc.

#### [Blockchain Data](https://github.com/fastnear/neardata-server/)

```bash
# Query last block produced
curl https://mainnet.neardata.xyz/v0/last_block/final
```

<details>
  <summary> Response </summary>

```json
  {
    "block": {
      "author": "aurora.pool.near",
      "header": {
        "height": 129311487,
        "prev_height": 129311486,
        ...
      }
    }
  }
```

</details>

#### [User Queries](https://github.com/fastnear/fastnear-api-server-rs)

```bash
# Query user's FTs
curl https://api.fastnear.com/v1/account/root.near/ft

# Query user's NFTs
curl https://api.fastnear.com/v1/account/root.near/ft

# Query all user's assets
curl https://api.fastnear.com/v1/account/root.near/full
```

<details>
  <summary> Response </summary>

```json
  {
    "account_id": "root.near",
    "tokens": [
      { "balance": "199462092", "contract_id": "the-token.near" },
      ...
    ]
  }
```

</details>

:::info More info

Find more information about the FastNear API in their [services page](https://fastnear.com/services)

:::