---## Unlocking the wallet ecosystem

Wallet Selector makes it easy for users to interact with dApps by providing an abstraction over various wallets and wallet types within the NEAR ecosystem.

:::info

You can check the current list of supported wallets in the [README.md](https://github.com/near/wallet-selector/blob/main/README.md) file of near/wallet-selector repository.

:::

---

## Install

The easiest way to use NEAR Wallet Selector is to install the core package from the NPM registry, some packages may require near-api-js v0.44.2 or above check them at packages.

```bash
npm install near-api-js
```

```bash
npm install @near-wallet-selector/core
```

Next, you'll need to install the wallets you want to support:

```bash
npm install \
  @near-wallet-selector/near-wallet \
  @near-wallet-selector/my-near-wallet \
  @near-wallet-selector/sender \
  @near-wallet-selector/nearfi \
  @near-wallet-selector/here-wallet \
  @near-wallet-selector/math-wallet \
  @near-wallet-selector/nightly \
  @near-wallet-selector/meteor-wallet \
  @near-wallet-selector/ledger \
  @near-wallet-selector/wallet-connect \
  @near-wallet-selector/nightly-connect \
  @near-wallet-selector/default-wallets \
  @near-wallet-selector/coin98-wallet
```

---

## Setup Wallet Selector

Optionally, you can install our [`modal-ui`](https://www.npmjs.com/package/@near-wallet-selector/modal-ui) or [`modal-ui-js`](https://www.npmjs.com/package/@near-wallet-selector/modal-ui-js) package for a pre-built interface that wraps the `core` API and presents the supported wallets:

```bash
npm install @near-wallet-selector/modal-ui
```

Then use it in your dApp:

```ts

const selector = await setupWalletSelector({
  network: "testnet",
  modules: [setupNearWallet()],
});

const modal = setupModal(selector, {
  contractId: "test.testnet",
});

modal.show();
```

:::info Required CSS

To integrate the Wallet Selector, you also need to include the required CSS:

```
```

:::

---

## Reference

The API reference of the selector can be found [`here`](https://github.com/near/wallet-selector/blob/main/packages/core/docs/api/selector.md)

### Sign in

```ts
// NEAR Wallet.
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  const accounts = await wallet.signIn({ contractId: "test.testnet" });
})();
```

### Sign out

```ts
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  await wallet.signOut();
})();
```

### Get accounts

```ts
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  const accounts = await wallet.getAccounts();
  console.log(accounts); // [{ accountId: "test.testnet" }]
})();
```

### Verify Owner

```ts
// MyNearWallet
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  await wallet.verifyOwner({
    message: "Test message",
  });
})();
```

### Sign and send transaction

```ts
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  await wallet.signAndSendTransaction({
    actions: [
      {
        type: "FunctionCall",
        params: {
          methodName: "addMessage",
          args: { text: "Hello World!" },
          gas: "30000000000000",
          deposit: "10000000000000000000000",
        },
      },
    ],
  });
})();
```

### Sign and send transactions

```ts
(async () => {
  const wallet = await selector.wallet("my-near-wallet");
  await wallet.signAndSendTransactions({
    transactions: [
      {
        receiverId: "guest-book.testnet",
        actions: [
          {
            type: "FunctionCall",
            params: {
              methodName: "addMessage",
              args: { text: "Hello World!" },
              gas: "30000000000000",
              deposit: "10000000000000000000000",
            },
          },
        ],
      },
    ],
  });
})();
```
