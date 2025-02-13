---## Install

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">
  Include `near-api-js` as a dependency in your package.

  ```bash
  npm i near-api-js
  ```

  :::tip Static HTML
  If you are building a site without using `npm`, you can include the library directly in your HTML file through a CDN.

  ```html
  <script src="https://cdn.jsdelivr.net/npm/near-api-js/dist/near-api-js.min.js"></script>
  ```
  :::

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```bash
  cargo add near-api
  ```
  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```shell
  pip install py-near
  ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Import {#import}

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">
  You can use the API library in the browser, or in Node.js runtime. 

  ```
import * as nearAPI from "near-api-js";
import dotenv from "dotenv";
```

  <details>
    <summary>Using the API in Node.js</summary>

    All these examples are written for the browser, to use these examples in Node.js you should convert the project to an ES module. To do this, add the following to your `package.json`:

  ```
{
  "type": "module",
  "dependencies": {
```

  </details>

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  The methods to interact with the NEAR API are available through the `prelude` module.

  ```
use near_api::prelude::*;
use near_crypto::SecretKey;
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  You can use the NEAR API by importing the `py_near` package, either entirely
  ```python
    ```

  or only the parts you need, for example:
  ```python
  from py_near.account   from py_near.providers   ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Connecting to NEAR {#connect}

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  The object returned from `connect` is your entry-point for all commands in the API.
  To transactions you'll need a [`KeyStore`](#signers).

  ```
const connectionConfig = {
  networkId: "testnet",
  keyStore: myKeyStore,
  nodeUrl: "https://rpc.testnet.near.org",
};
const nearConnection = await connect(connectionConfig);

```

  <details>
    <summary>Mainnet/Localnet connection</summary>

    ```js
    // Mainnet config example
    const connectionConfig = {
      networkId: "mainnet",
      keyStore: myKeyStore,
      nodeUrl: "https://rpc.mainnet.near.org",
    };

    // Localnet config example
    const connectionConfig = {
      networkId: "local",
      nodeUrl: "http://localhost:3030",
    };
    ```
  </details>

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  To interact with the blockchain you'll need to create a `NetworkConfig` object.

  Preset connections `mainnet` and `testnet` are available that come with standard configurations for each network.

  ```
    let network = NetworkConfig::testnet();

```

  You can also create your own custom connection.

  ```
    let network = NetworkConfig {
        network_name: "testnet".to_string(),
        rpc_url: "https://rpc.testnet.near.org".parse().unwrap(),
        rpc_api_key: None,
        linkdrop_account_id: Some("testnet".parse().unwrap()),
        near_social_db_contract_account_id: Some("v1.social08.testnet".parse().unwrap()),
        faucet_url: Some("https://helper.nearprotocol.com/account".parse().unwrap()),
        meta_transaction_relayer_url: Some("http://localhost:3030/relay".parse().unwrap()),
        fastnear_url: None,
        staking_pools_factory_account_id: Some("pool.f863973.m0".parse().unwrap()),
    };

```

  </TabItem>
</Tabs>

<hr class="subsection" />

### Key Handlers: Stores & Signers 

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  To sign transactions you'll need to a `KeyStore` with valid keypairs.

  <Tabs>
  <TabItem value="browser" label="Browser" default>

  `BrowserLocalStorageKeyStore` can only be used in the browser, it uses the browser's local storage to store the keys.

  ```js
  // Creates keyStore using private key in local storage

  const { keyStores } = nearAPI;
  const myKeyStore = new keyStores.BrowserLocalStorageKeyStore();
  ```

  </TabItem>
  <TabItem value="dir" label="Credentials Path">

  `UnencryptedFileSystemKeyStore` can be used is used to load keys from the legacy credentials directory used by the NEAR CLI.

  ```
const credentialsDirectory = ".near-credentials";
const credentialsPath = path.join(homedir(), credentialsDirectory);
const myKeyStore = new keyStores.UnencryptedFileSystemKeyStore(credentialsPath);

```

  </TabItem>
  <TabItem value="file" label="File">

  Keystores can be created by loading a private key from a json file.

  ```
const credentialsPath = "../credentials-file.json"; // Path relative to the working directory
const credentials = JSON.parse(fs.readFileSync(credentialsPath));
// Create a key pair from the private key
const keyPair = KeyPair.fromString(credentials.private_key);
// Create a keystore and add the key pair
const myKeyStore = new keyStores.InMemoryKeyStore();
myKeyStore.setKey("testnet", accountId, keyPair);

```

  </TabItem>
  <TabItem value="key" label="Private Key">

  Keystores can be created by using a private key string.

  Private keys have the format "ed25519:5Fg2...".

  ```
const myKeyStore = new keyStores.InMemoryKeyStore();
const keyPair = KeyPair.fromString(privateKey); // ed25519:5Fg2...
await myKeyStore.setKey("testnet", accountId, keyPair);

```

  </TabItem>
  <TabItem value="seed" label="Seed Phrase">

  Keystores can be created by using a seed phrase. To parse the seed phrase into a private key, the `near-seed-phrase` library is needed.

  ```bash
  npm i near-seed-phrase
  ```

  Seed phrases have the format "shoe three gate ..." and are usually 12 words long.

  ```
const { secretKey } = parseSeedPhrase(seedPhrase); // "royal success river ..."
const myKeyStore = new keyStores.InMemoryKeyStore();
const keyPair = KeyPair.fromString(secretKey); // ed25519::5Fg2...
await myKeyStore.setKey("testnet", accountId, keyPair);

```

  </TabItem>
  </Tabs>
  </TabItem>

  <TabItem value="rust" label="🦀 Rust">

  To sign transactions you'll need to create a `Signer` that holds a valid keypair.

  <Tabs>
  <TabItem value="keystore" label="Keystore" default>

  Signers can be created using the Keystore that is also used as the standard for saving keys with the NEAR CLI.

  ```
    let account_id: AccountId = account_id_string.parse().unwrap();

    // Create a signer from the encrypted keystore
    let signer = KeystoreSigner::search_for_keys(account_id.clone(), &network)
        .await
        .unwrap(); // Search for the correct keys
    let signer = Signer::new(signer).unwrap(); // Create the signer

```

  </TabItem>
  <TabItem value="dir" label="Credentials Path">

  Signers can be created using the credentials directory which is the legacy option for saving keys with the NEAR CLI.

  ```
    let home_dir = std::env::var("HOME").unwrap();
    let credentials_dir = std::path::Path::new(&home_dir).join(".near-credentials");
    let credentials_path = credentials_dir.join(format!("testnet/{}.json", account_id_string)); // Path to the credentials file
    let signer = Signer::new(Signer::access_keyfile(credentials_path).unwrap()).unwrap(); // Create the signer

```

  </TabItem>
  <TabItem value="file" label="File">

  Signers can be created by loading a public and private key from a file.

  ```
    let credentials_path = std::path::PathBuf::from("../credentials-file.json"); // Path relative to the root directory of the project
    let signer = Signer::new(Signer::access_keyfile(credentials_path).unwrap()).unwrap(); // Create the signer

```

  </TabItem>
  <TabItem value="key" label="Private Key">

  Signers can be created by using a private key string.

  Private keys have the format "ed25519:5Fg2...".

  ```
    let private_key = SecretKey::from_str(&private_key_string).unwrap(); // ed25519:5Fg2...
    let signer = Signer::new(Signer::secret_key(private_key)).unwrap(); // Create the signer

```

  </TabItem>
  <TabItem value="seed" label="Seed Phrase">

  Signers can be created by using a seed phrase.

  Seed phrases have the format "shoe three gate ..." and are usually 12 words long.

  ```
    let seed_phrase = Signer::seed_phrase(seed_phrase_string, None).unwrap(); // "royal success river ..."
    let signer = Signer::new(seed_phrase).unwrap(); // Create the signer

```

  </TabItem>
    </Tabs>

  </TabItem>
  <TabItem value="python" label="🐍 Python">
  TODO: not exactly the same in Python, it's more and account + RPC URL, or a JSON RPC provider
  </TabItem>
</Tabs>


  <hr class="subsection" />

  ### RPC Failover

  RPC providers can experience intermittent downtime, connectivity issues, or rate limits that cause client transactions to fail. This can be prevented by using the `FailoverRpcProvider` that supports multiple RPC providers.

  <Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Set up a new FailoverRpcProvider with two JSON RPC providers
const jsonProviders = [
  new providers.JsonRpcProvider(
    { url: "https://test.rpc.fastnear.com" }, // RPC URL
    {
      retries: 3, // Number of retries before giving up on a request
      backoff: 2, // Backoff factor for the retry delay
      wait: 500, // Wait time between retries in milliseconds
    }, // Retry options
  ),
  new providers.JsonRpcProvider({
    url: "https://rpc.testnet.near.org",
  }), // Second RPC URL
];
const provider = new providers.FailoverRpcProvider(jsonProviders); // Create a FailoverRpcProvider

const connectionConfig = {
  networkId: "testnet",
  keyStore: myKeyStore,
  nodeUrl: "https://incorrect-rpc-url.com", // Incorrect RPC URL
  provider: provider,
};
const nearConnection = await connect(connectionConfig);

```

  </TabItem>
  <TabItem value="python" label="🐍 Python">
    You can pass multiple RPC providers to `JsonRpcProvider`

    ```python
    from py_near.providers 
    provider = JsonProvider(["https://test.rpc.fastnear.com", "https://rpc.testnet.pagoda.co"])
    ```
  </TabItem>
</Tabs>

---

## Account

### Instantiate Account {#instantiate-account}

This will return an Account object for you to interact with.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const account = await connection.account("example-account.testnet");

```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let my_account_id: AccountId = "example-account.testnet".parse().unwrap();
    // Create an account object
    let my_account = Account(my_account_id.clone());

```

  </TabItem>
  <TabItem value="python" label="🐍 Python">
    You can instantiate any account with the following code:

    ```python
    from py_near.account 
    account = Account(account_id="example-account.testnet", rpc_addr="https://rpc.testnet.pagoda.co")
    await account.startup()
    ```

    If you want to use it to submit transactions later, you need to also pass the `private_key` param:

    ```python
    account = Account(account_id="example-account.testnet", private_key="ed25519:...", rpc_addr="https://rpc.testnet.pagoda.co")
    ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Get Balance {#get-balance}

Gets the available and staked balance of an account in yoctoNEAR.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const accountBalance = await account.getAccountBalance();
console.log(accountBalance);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let near_balance = Tokens::of(my_account_id.clone())
        .near_balance()
        .fetch_from(&network)
        .await
        .unwrap();
    println!("{:?}", near_balance);

```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

    ```python
    from py_near.account 
    account = Account(account_id="example-account.testnet", rpc_addr="https://rpc.testnet.pagoda.co")
    await account.startup()

    account_balance = account.get_balance()
    ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Get State {#get-state}

Get basic account information, such as its code hash and storage usage.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const accountState = await account.state();
console.log(accountState);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">
  
  ```
    let account_info = my_account.view().fetch_from(&network).await.unwrap();
    println!("{:?}", account_info);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

    ```python
    from py_near.account 
    account = Account(account_id="example-account.testnet", rpc_addr="https://rpc.testnet.pagoda.co")
    await account.startup()

    account_state = account.fetch_state()
    ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Get Details {#get-details}

Returns the authorized apps of an account. This is a list of contracts that the account has function call access keys for.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const accountDetails = await account.getAccountDetails();
console.log(accountDetails);
```

  </TabItem>
</Tabs>

<hr class="subsection" />

### Create an Account {#create-account}

In order to create .near or .testnet accounts, you need to make a function call to the top-level-domain account (i.e. `near` or `testnet`), calling `create_account`. In this example we generate a new public key for the account by generating a random private key.

The deposit determines the initial balance of the account.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Generate a new key pair
const newKeyPair = KeyPair.fromRandom("ed25519");
const newPublicKey = newKeyPair.getPublicKey().toString();
const newPrivateKey = newKeyPair.toString();
console.log("Private key", newPrivateKey);
console.log("Public key", newPublicKey);

const createAccountResult = await account.functionCall({
  contractId: "testnet",
  methodName: "create_account",
  args: {
    new_account_id: newAccountId, // example-account.testnet
    new_public_key: newPublicKey, // ed25519:2ASWc...
  },
  attachedDeposit: utils.format.parseNearAmount("0.1"), // Initial balance for new account in yoctoNEAR
});
console.log(createAccountResult);
```

  <details>
    <summary>Creating an account from a seed phrase</summary>

    You can also create an account with a public key that is derived from a randomly generated seed phrase.

    ```
const { seedPhrase, publicKey, secretKey } = generateSeedPhrase();
console.log("Seed phrase", seedPhrase);
console.log("Private key", secretKey);
console.log("Public key", publicKey);

const createAccountResult = await account.functionCall({
  contractId: "testnet",
  methodName: "create_account",
  args: {
    new_account_id: newAccountId, // example-account.testnet
    new_public_key: publicKey, // ed25519:2ASWc...
  },
  attachedDeposit: utils.format.parseNearAmount("0.1"), // Initial balance for new account in yoctoNEAR
});
console.log(createAccountResult);
```

  </details>

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let (private_key, create_account_tx) = Account::create_account()
        .fund_myself(
            new_account_id.clone(), // example-account.testnet
            account_id.clone(),
            NearToken::from_millinear(100), // Initial balance for new account in yoctoNEAR
        )
        .new_keypair()
        .generate_secret_key()
        .unwrap();

    println!("Private key: {:?}", private_key.to_string());
    println!("Public key: {:?}", private_key.public_key().to_string());

    let create_account_result = create_account_tx
        .with_signer(signer.clone()) // Signer is the account that is creating the new account
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", create_account_result);
```

  <details>
    <summary>Creating an account from a seed phrase</summary>

    You can also create an account via a randomly generated seed phrase.

    ```
    let (seed_phrase, create_account_tx) = Account::create_account()
        .fund_myself(
            new_account_id.clone(), // example-account.testnet
            account_id.clone(),
            NearToken::from_millinear(100), // Initial balance for new account in yoctoNEAR
        )
        .new_keypair()
        .generate_seed_phrase()
        .unwrap();

    println!("Seed phrase: {:?}", seed_phrase);

    let create_account_result = create_account_tx
        .with_signer(signer.clone()) // Signer is the account that is creating the new account
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", create_account_result);
```

  </details>

  </TabItem>
  <TabItem value="python" label="🐍 Python">
  
    ```python
    await account.function_call("testnet", "create_account", {"new_account_id": "example-account.testnet", "new_public_key": "ed25519:..."}, "30000000000000", 1 * NEAR)
    ```

  </TabItem>

</Tabs>

<hr class="subsection" />

### Create a Sub-Account {#create-sub-account}

Accounts can create sub-accounts of themselves, which are useful for creating separate accounts for different purposes. It is important to remark that the parent account has no control over any of its sub-accounts.

The deposit determines the initial balance of the account.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Generate a new key pair
const newSubKeyPair = KeyPair.fromRandom("ed25519");
const newSubPublicKey = newSubKeyPair.getPublicKey().toString();
const newSubPrivateKey = newSubKeyPair.toString();
console.log("Private key", newSubPrivateKey);
console.log("Public key", newSubPublicKey);

const createSubAccountResult = await account.createAccount(
  newSubAccountId, // sub.example-account.testnet
  newSubPublicKey, // ed25519:2ASWc...
  utils.format.parseNearAmount("0.1"), // Initial balance for new account in yoctoNEAR
);
console.log(createSubAccountResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let (private_key, create_sub_account_tx) = Account::create_account()
        .fund_myself(
            sub_account_id.clone(), // sub.example-account.testnet
            account_id.clone(),
            NearToken::from_millinear(100), // Initial balance for sub account in yoctoNEAR
        )
        .new_keypair()
        .generate_secret_key()
        .unwrap();

    println!("Private key: {:?}", private_key.to_string());
    println!("Public key: {:?}", private_key.public_key().to_string());

    let create_sub_account_result = create_sub_account_tx
        .with_signer(signer.clone()) // Signer is the account that is creating the sub account
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", create_sub_account_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

    Create a sub-account and fund it with your main account:

    ```python
    from py_near.account     from py_near.dapps.core 
    account = Account(account_id="example-account.testnet", private_key="ed25519:...", rpc_addr="https://rpc.testnet.pagoda.co")
    await account.startup()

    res = account.create_account(account_id="sub.example-account.testnet", public_key="...", initial_balance=1 * NEAR))
    ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Delete Account {#delete-account}

When deleting an account, you need to specify a beneficiary account id. This is the account that will receive the remaining NEAR balance of the account being deleted. 

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const deleteAccountResult =
  await accountToDelete.deleteAccount(beneficiaryAccountId); // example-beneficiary.testnet
console.log(deleteAccountResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let delete_account_result = account_to_delete
        .delete_account_with_beneficiary(beneficiary_account_id.clone()) // example-beneficiary.testnet
        .with_signer(signer.clone()) // Signer is the account that is being deleted
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", delete_account_result);
```

  </TabItem>
</Tabs>

:::warning

Only NEAR tokens will be transferred to the beneficiary, so you should transfer all your FTs, NFTs, etc. to another account before deleting.

:::

:::danger

If the beneficiary account does not exist, the NEAR tokens will be burned

:::

---

## Transactions

### Send Tokens {#send-tokens}

Transfer NEAR tokens between accounts. 

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const sendTokensResult = await account.sendMoney(
  "receiver-account.testnet", // Receiver account
  utils.format.parseNearAmount("1"), // Amount being sent in yoctoNEAR
);
console.log(sendTokensResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let send_tokens_result = Tokens::of(account_id.clone()) // example-account.testnet
        .send_to("receiver-account.testnet".parse().unwrap())
        .near(NearToken::from_near(1))
        .with_signer(signer.clone())
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", send_tokens_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

    ```python
    from py_near.account     from py_near.dapps.core 
    account = Account(account_id="example-account.testnet", private_key="ed25519:...", rpc_addr="https://rpc.testnet.pagoda.co")
    await account.startup()

    await account.send_money("receiver-account.testnet", 1 * NEAR))
    ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Call Function

A call function changes the contract's state and requires a signer/keypair.


<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const contractCallResult = await account.functionCall({
  contractId: "guestbook.near-examples.testnet", // Contract account ID
  methodName: "add_message", // Method to call
  args: {
    text: "Hello, world!",
  }, // Arguments for the method
  gas: 100000000000000, // Optional: gas limit
  deposit: 0, // Optional: deposit in yoctoNEAR
});
console.log(contractCallResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let contract_id: AccountId = "guestbook.near-examples.testnet".parse().unwrap();
    let contract = Contract(contract_id.clone());

```

  ```
    let args = json!({
        "text": "Hello, world!"
    });

    let function_call_result = contract
        .call_function("add_message", args)
        .unwrap()
        .transaction()
        .deposit(NearToken::from_near(1))
        .with_signer(account_id.clone(), signer.clone()) // Signer is the account that is calling the function
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", function_call_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  await account.function_call("usn.near", "ft_transfer", {"receiver_id": "bob.near", "amount": "1000000000000000000000000"})
  ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Batch Actions

You can send multiple [actions](../1.concepts/protocol/transaction-anatomy.md#actions) in a batch to a single receiver. If one action fails then the entire batch of actions will be reverted.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">
  
  ```
// Prepare the actions
const callAction = transactions.functionCall(
  "increment", // Method name
  [], // Arguments
  "30000000000000", // Gas
  0, // Deposit
);
const transferAction = transactions.transfer(utils.format.parseNearAmount("1"));

// Send the batch of actions
const batchActionsResult = await account.signAndSendTransaction({
  receiverId: "counter.near-examples.testnet",
  actions: [callAction, transferAction],
});
console.log(batchActionsResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    // Prepare the actions
    let call_action = Action::FunctionCall(Box::new(FunctionCallAction {
        method_name: "increment".to_string(),
        args: vec![],
        gas: 30_000_000_000_000,
        deposit: 0,
    }));
    let transfer_action = Action::Transfer(TransferAction {
        deposit: 1_000_000_000_000_000_000_000_000,
    }); // Transfer 1 NEAR

    // Send the batch of actions
    let batch_actions_result = Transaction::construct(
        account_id.clone(),
        "counter.near-examples.testnet".parse().unwrap(),
    )
    .add_actions(vec![call_action, transfer_action])
    .with_signer(signer)
    .send_to(&network)
    .await
    .unwrap();
    println!("{:?}", batch_actions_result);
```

  </TabItem>
</Tabs>

<hr class="subsection" />

### Simultaneous Transactions

Transactions can be sent in parallel to the network, so you don't have to wait for one transaction to complete before sending the next one. Note that these one transaction could be successful and the other one could fail. 

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Prepare the transactions
const args = Buffer.from(JSON.stringify({ text: "Hello, world!" }));
const tx1 = account.signAndSendTransaction({
  receiverId: "guestbook.near-examples.testnet",
  actions: [
    transactions.functionCall(
      "add_message", // Method name
      args, // Arguments
      100000000000000, // Gas
      0, // Deposit
    ),
  ],
});

const tx2 = account.signAndSendTransaction({
  receiverId: "counter.near-examples.testnet",
  actions: [
    transactions.functionCall(
      "increment", // Method name
      [], // Arguments
      100000000000000, // Gas
      0, // Deposit
    ),
  ],
});

// Send the transactions simultaneously
const transactionsResults = await Promise.all([tx1, tx2]);
console.log(transactionsResults);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    // Prepare the transactions
    let args = serde_json::to_vec(&json!({
        "text": "Hello, world!"
    }))
    .unwrap();
    let action1 = Action::FunctionCall(Box::new(FunctionCallAction {
        method_name: "add_message".to_string(),
        args,
        gas: 100_000_000_000_000,
        deposit: 0,
    }));
    let tx1 = Transaction::construct(
        account_id.clone(),
        "guestbook.near-examples.testnet".parse().unwrap(),
    )
    .add_action(action1)
    .with_signer(signer.clone());

    let action2 = Action::FunctionCall(Box::new(FunctionCallAction {
        method_name: "increment".to_string(),
        args: vec![],
        gas: 100_000_000_000_000,
        deposit: 0,
    }));
    let tx2 = Transaction::construct(
        account_id.clone(),
        "counter.near-examples.testnet".parse().unwrap(),
    )
    .add_action(action2)
    .with_signer(signer.clone());

    // Send the transactions simultaneously
    let (tx1_result, tx2_result) = tokio::join!(tx1.send_to(&network), tx2.send_to(&network));
    println!("{:?}", tx1_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
    from py_near.account 
  account = Account(account_id="example-account.testnet", private_key="ed25519:...", rpc_addr="https://rpc.testnet.pagoda.co")
  await account.startup()

  # Prepare the transactions
  tx1 = account.function_call("guestbook.near-examples.testnet", "add_message", { "text": "Hello, world!" })
  tx2 = account.function_call("counter.near-examples.testnet", "increment", {})

  # Send the transactions simultaneously
  const transactionsResults = await asyncio.gather(tx1, tx2)
  ```

  </TabItem>
</Tabs>

<hr class="subsection" />

### Deploy a Contract {#deploy-a-contract}

You can deploy a contract from a compiled WASM file. 

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const deployResult = await account.deployContract(
  fs.readFileSync("../contracts/contract.wasm"), // Path of contract WASM relative to the working directory
);
console.log(deployResult);

```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  Note that the `signer` here needs to be a signer for the same `account_id` as the one used to construct the `Contract` object.

  ```
    let new_contract = Contract(account_id.clone());
    let deploy_result = new_contract
        .deploy(include_bytes!("../../contracts/contract.wasm").to_vec()) // Path of contract WASM relative to this file
        .without_init_call()
        .with_signer(signer) // Signer is the account that is deploying the contract
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", deploy_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
    from py_near.account 
  account = Account(account_id="example-account.testnet", private_key="ed25519:...", rpc_addr="https://rpc.testnet.pagoda.co")
  await account.startup()

  with open("contract.wasm", "rb") as f:
    contract_code = f.read()
  await account.deploy_contract(contract_code)
  ```
  </TabItem>
</Tabs>

---

## View Function

View functions are read-only functions that don't change the state of the contract. We can call these functions without a signer / keypair or any gas.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
async function viewContract({
  contractId,
  methodName,
  args = {},
  finality = "optimistic",
}) {
  // Set up a new provider
  const url = `https://rpc.testnet.near.org`;
  const provider = new providers.JsonRpcProvider({ url });

  // Convert the arguments to base64
  const argsBase64 = args
    ? Buffer.from(JSON.stringify(args)).toString("base64")
    : "";

  // Make the view call
  const viewCallResult = await provider.query({
    request_type: "call_function",
    account_id: contractId,
    method_name: methodName,
    args_base64: argsBase64,
    finality: finality,
  });

  // Parse the result
  return JSON.parse(Buffer.from(viewCallResult.result).toString());
}

// Use the view call function
const viewCallData = await viewContract({
  contractId: "guestbook.near-examples.testnet",
  methodName: "total_messages",
});
console.log(viewCallData);

// If args are required, they can be passed in like this:
// args: {
//   from_index: "0",
//   limit: "10"
// }

```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    // Create contract object
    let contract_id: AccountId = "guestbook.near-examples.testnet".parse().unwrap();
    let contract = Contract(contract_id.clone());

    // Make a view call to a contract
    let view_call_result: Data<u32> = contract
        .call_function("total_messages", ())
        .unwrap()
        .read_only()
        .fetch_from(&network)
        .await
        .unwrap();
    println!("{:?}", view_call_result.data);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  view_call_result = await account.view_function("guestbook.near-examples.testnet", "total_messages", {})
  # If args are required, they can be passed in like this in the 3rd argument:
  # {
  #   "from_index": "0",
  #   "limit": "10"
  # }
  print(view_call_result)
  ```
  </TabItem>
</Tabs>

---

## Keys

### Get All Access Keys {#get-all-access-keys}

List all the access keys for an account.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const accessKeys = await account.getAccessKeys();
console.log(accessKeys);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let keys = account.list_keys().fetch_from(&network).await.unwrap();
    println!("{:?}", keys);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  keys = await account.get_access_key_list()
  ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Add Full Access Key {#add-full-access-key}

Add a new [full access key](../1.concepts/protocol/access-keys.md#full-access-keys) to an account. Here we generate a random keypair, alternatively you can use a keypair from a seed phrase.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Generate a new key pair
const newFullKeyPair = KeyPair.fromRandom("ed25519");
const newFullPublicKey = newFullKeyPair.getPublicKey().toString();
console.log(newFullPublicKey);

const addFullKeyResult = await account.addKey(
  newFullPublicKey, // The new public key ed25519:2ASWc...
);
console.log(addFullKeyResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let keys = account.list_keys().fetch_from(&network).await.unwrap();
    println!("{:?}", keys);

    // Add full access key
    let (new_full_private_key, txn) = account
        .add_key(AccessKeyPermission::FullAccess)
        .new_keypair() // Generate a new keypair
        .generate_secret_key() // Get the private key from the keypair
        .unwrap();

    let new_full_public_key = new_full_private_key.public_key().to_string();
    println!("{:?}", new_full_public_key);

    let add_full_key_result = txn
        .with_signer(signer.clone())
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", add_full_key_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  keys = await account.add_full_access_public_key("5X9WvUbRV3aSd9Py1LK7HAndqoktZtcgYdRjMt86SxMj")
  ```
  </TabItem>
</Tabs>

<hr class="subsection" />

### Add Function Call Key {#add-function-call-key}

Add a new [function call key](../1.concepts/protocol/access-keys.md#function-call-keys) to an account. When adding the key you should specify the contract id the key can call, an array of methods the key is allowed to call, and the allowance in gas for the key.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
// Add function call access key
// Generate a new key pair
const newFunctionKeyPair = KeyPair.fromRandom("ed25519");
const newFunctionPublicKey = newFunctionKeyPair.getPublicKey().toString();
console.log(newFunctionPublicKey);

const addFunctionKeyResult = await account.addKey(
  newFunctionPublicKey, // The new public key ed25519:2ASWc...
  "example-contract.testnet", // Contract this key is allowed to call (optional)
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let new_function_call_key = AccessKeyPermission::FunctionCall(FunctionCallPermission {
        allowance: Some(250_000_000_000_000_000_000_000), // Gas allowance key can use to call methods (optional)
        receiver_id: "example-contract.testnet".to_string(), // Contract this key is allowed to call
        method_names: vec!["example_method".to_string()], // Methods this key is allowed to call
    });

    let (new_function_private_key, txn) = account
        .add_key(new_function_call_key)
        .new_keypair()
        .generate_secret_key()
        .unwrap();

    let new_function_public_key = new_function_private_key.public_key().to_string();
    println!("{:?}", new_function_public_key);

    let add_function_key_result = txn
        .with_signer(signer.clone())
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", add_function_key_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  await account.add_public_key(
    "5X9WvUbRV3aSd9Py1LK7HAndqoktZtcgYdRjMt86SxMj",
    "example-contract.testnet", # Contract this key is allowed to call
    ["example_method"], # Methods this key is allowed to call (optional)
    0.25 * NEAR # Gas allowance key can use to call methods (optional)
  )
  ```
  </TabItem>

</Tabs>

<hr class="subsection" />

### Delete Access Key {#delete-access-key}

When deleting an access key, you need to specify the public key of the key you want to delete.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const deleteFullKeyResult = await account.deleteKey(publicKeyToDelete); // The public key being deleted ed25519:2ASWc...
console.log(deleteFullKeyResult);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let delete_full_key_result = account
        .delete_key(public_key_to_delete.parse().unwrap())
        .with_signer(signer.clone())
        .send_to(&network)
        .await
        .unwrap();
    println!("{:?}", delete_full_key_result);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

  ```python
  await account.delete_public_key("5X9WvUbRV3aSd9Py1LK7HAndqoktZtcgYdRjMt86SxMj")
  ```
  </TabItem>
</Tabs>

---

## Validate Message Signatures

Users can sign messages using the `wallet-selector` `signMessage` method, which returns a signature. This signature can be verified using the following code:

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

    ```
import * as borsh from 'borsh';
import naj from 'near-api-js';
import js_sha256 from 'js-sha256';

class Payload {
    constructor({ message, nonce, recipient, callbackUrl }) {
        this.tag = 2147484061;
        this.message = message;
        this.nonce = nonce;
        this.recipient = recipient;
        if (callbackUrl) { this.callbackUrl = callbackUrl }
    }
}

const payloadSchema = { struct: { tag: 'u32', message: 'string', nonce: { array: { type: 'u8', len: 32 } }, recipient: 'string', callbackUrl: { option: "string" } } }

async function authenticate({ accountId, publicKey, signature, message, recipient, nonce }) {
    // A user is correctly authenticated if:
    // - The key used to sign belongs to the user and is a Full Access Key
    // - The object signed contains the right message and domain
    const full_key_of_user = await verifyFullKeyBelongsToUser({ accountId, publicKey })
    const valid_signature = verifySignature({ publicKey, signature, message, recipient, nonce })
    return valid_signature && full_key_of_user
}

function verifySignature({ publicKey, signature, message, recipient, nonce }) {
    // Reconstruct the expected payload to be signed
    const payload = new Payload({ message, recipient, nonce });
    const serialized = borsh.serialize(payloadSchema, payload);
    const to_sign = Uint8Array.from(js_sha256.sha256.array(serialized))

    // Reconstruct the signature from the parameter given in the URL
    let real_signature = Buffer.from(signature, 'base64')

    // Use the public Key to verify that the private-counterpart signed the message
    const myPK = naj.utils.PublicKey.from(publicKey)
    return myPK.verify(to_sign, real_signature)
}

async function verifyFullKeyBelongsToUser({ publicKey, accountId }) {
    // Call the public RPC asking for all the users' keys
    let data = await fetch_all_user_keys({ accountId })

    // if there are no keys, then the user could not sign it!
    if (!data || !data.result || !data.result.keys) return false

    // check all the keys to see if we find the used_key there
    for (const k in data.result.keys) {
        if (data.result.keys[k].public_key === publicKey) {
            // Ensure the key is full access, meaning the user had to sign
            // the transaction through the wallet
            return data.result.keys[k].access_key.permission == "FullAccess"
        }
    }

    return false // didn't find it
}

// Aux method
async function fetch_all_user_keys({ accountId }) {
    const keys = await fetch(
        "https://rpc.testnet.near.org",
        {
            method: 'post',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: `{"jsonrpc":"2.0", "method":"query", "params":["access_key/${accountId}", ""], "id":1}`
        }).then(data => data.json()).then(result => result)
    return keys
}

export { authenticate }
```

  </TabItem>
</Tabs>

---


## Utilities

### NEAR to yoctoNEAR {#near-to-yoctonear}

Convert an amount in NEAR to an amount in yoctoNEAR.

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  ```
const amountInYoctoNear = utils.format.parseNearAmount("1");
console.log(amountInYoctoNear);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  ```
    let from_near = NearToken::from_near(1);
    println!("{:?}", from_near);
```

  </TabItem>
  <TabItem value="python" label="🐍 Python">

   ```python
   from py_near.dapps.core 
   amount_in_yocto = 1 * NEAR
   ```

  </TabItem>
</Tabs>

<hr class="subsection" />

### Format Amount {#format-amount}

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  Format an amount in yoctoNEAR to an amount in NEAR.

  ```
const amountInNear = utils.format.formatNearAmount("1000000000000000000000000");
console.log(amountInNear);
```

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  Format an amount of NEAR into a string of NEAR or yoctoNEAR depending on the amount.

  ```
    let display_amount = NearToken::exact_amount_display(&ONE_NEAR);
    println!("{:?}", display_amount);
```

  </TabItem>
</Tabs>

---

## Additional resources

<Tabs groupId="api">
  <TabItem value="js" label="🌐 JavaScript">

  - [Documentation](https://near.github.io/near-api-js)
  - [Github](https://github.com/near/near-api-js)
  - [Full Examples](https://github.com/PiVortex/near-api-examples/tree/main/javascript)
  - [Cookbook](https://github.com/near/near-api-js/tree/master/packages/cookbook) which contains examples using the near-js/client package, a wrapper tree shakable package for near-api-js.

  </TabItem>
  <TabItem value="rust" label="🦀 Rust">

  - [Documentation](https://docs.rs/near-api/latest/near_api/)
  - [Github](https://github.com/near/near-api-rs)
  - [Full Examples](https://github.com/PiVortex/near-api-examples/tree/main/rust)

  </TabItem>
  <TabItem value="python" label="🐍 Python">

    - [Phone number transfer](https://py-near.readthedocs.io/en/latest/clients/phone.html)

  </TabItem>
</Tabs>
