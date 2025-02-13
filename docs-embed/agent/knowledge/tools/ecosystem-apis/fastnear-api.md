---## Endpoints

The [FastNEAR Server](https://github.com/fastnear/fastnear-api-server-rs) provides a low-latency endpoint for wallets and explorers.

- Mainnet: `https://api.fastnear.com`
- Testnet: `https://test.api.fastnear.com`

---

## Examples

### [Query last block produced](https://github.com/fastnear/neardata-server/)

```bash
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

<hr className="subsection"/>

### [Query User's Balance](https://github.com/fastnear/fastnear-api-server-rs)

```bash
# Query user's FTs
curl https://api.fastnear.com/v1/account/root.near/ft
```

<details>
  <summary> Response </summary>

```json
{"account_id":"root.near","tokens":[{"balance":"199462092","contract_id":"pixeltoken.near","last_update_block_height":null},...
```

</details>

<hr className="subsection"/>

```sh
# Query user's NFTs
curl https://api.fastnear.com/v1/account/root.near/nft
```

<details>
  <summary> Response </summary>

```json
{"account_id":"root.near","tokens":[{"contract_id":"nft.goodfortunefelines.near","last_update_block_height":null},...
```

</details>

<hr className="subsection"/>

```sh
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
