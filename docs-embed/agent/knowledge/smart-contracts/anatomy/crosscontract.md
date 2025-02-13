---## Snippet: Querying Information

While making your contract, it is likely that you will want to query information from another contract. Below, you can see a basic example in which we query the greeting message from our [Hello NEAR](../quickstart.md) example.

<CodeTabs>
<Language value="js" language="ts">
    ```
  hello_account: AccountId = "hello-nearverse.testnet";

  @initialize({})
  init({ hello_account }: { hello_account: AccountId }) {
    this.hello_account = hello_account;
  }

  @call({})
  query_greeting(): NearPromise {
    const promise = NearPromise.new(this.hello_account)
      .functionCall("get_greeting", NO_ARGS, NO_DEPOSIT, THIRTY_TGAS)
      .then(
        NearPromise.new(near.currentAccountId())
          .functionCall(
            "query_greeting_callback",
            NO_ARGS,
            NO_DEPOSIT,
            THIRTY_TGAS,
          ),
      );

    return promise.asReturn();
  }

  @call({ privateFunction: true })
  query_greeting_callback(): String {
    let { result, success } = promiseResult();

    if (success) {
      return result.substring(1, result.length - 1);
    } else {
      near.log("Promise failed...");
      return "";
    }
  }

```

</Language>

<Language value="rust" language="rust">
    ```
// Find all our documentation at https://docs.near.org
use near_sdk::{env, near, AccountId, Gas, NearToken, PanicOnDefault};

pub mod external_contract;
pub use crate::external_contract::*;

pub mod high_level;
pub mod low_level;

const NO_ARGS: Vec<u8> = vec![];
const NO_DEPOSIT: NearToken = NearToken::from_near(0);
const FIVE_TGAS: Gas = Gas::from_tgas(5);
const TEN_TGAS: Gas = Gas::from_tgas(10);

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    pub hello_account: AccountId,
}

#[near]
impl Contract {
    #[init]
    #[private] // Public - but only callable by env::current_account_id()
    pub fn init(hello_account: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        Self { hello_account }
    }
}

```
    ```
use near_sdk::ext_contract;

// Validator interface, for cross-contract calls
#[ext_contract(hello_near)]
trait HelloNear {
    fn get_greeting(&self) -> String;
    fn set_greeting(&self, greeting: String);
}

```
    ```
    // Public - query external greeting
    pub fn hl_query_greeting(&self) -> Promise {
        // Create a promise to call HelloNEAR.get_greeting()
        let promise = hello_near::ext(self.hello_account.clone())
            .with_static_gas(FIVE_TGAS)
            .get_greeting();

        promise.then(
            // Create a promise to callback query_greeting_callback
            Self::ext(env::current_account_id())
                .with_static_gas(FIVE_TGAS)
                .hl_query_greeting_callback(),
        )
    }

    #[private] // Public - but only callable by env::current_account_id()
    pub fn hl_query_greeting_callback(
        &self,
        #[callback_result] call_result: Result<String, PromiseError>,
    ) -> String {
        // Check if the promise succeeded by calling the method outlined in external.rs
        if call_result.is_err() {
            log!("There was an error contacting Hello NEAR");
            return "".to_string();
        }

        // Return the greeting
        let greeting: String = call_result.unwrap();
        greeting
    }

```
    ```
    // Public - query external greeting
    pub fn ll_query_greeting(&self) -> Promise {
        // Create a promise to call HelloNEAR.get_greeting()
        let hello_promise = Promise::new(self.hello_account.clone()).function_call(
            "get_greeting".to_owned(),
            NO_ARGS,
            NO_DEPOSIT,
            TEN_TGAS,
        );

        hello_promise.then(
            // Create a promise to callback query_greeting_callback
            Self::ext(env::current_account_id())
                .with_static_gas(TEN_TGAS)
                .ll_query_greeting_callback(),
        )
    }

    #[private] // Public - but only callable by env::current_account_id()
    pub fn ll_query_greeting_callback(
        &self,
        #[callback_result] call_result: Result<String, PromiseError>,
    ) -> String {
        // Check if the promise succeeded by calling the method outlined in external.rs
        if call_result.is_err() {
            log!("There was an error contacting Hello NEAR");
            return "".to_string();
        }

        // Return the greeting
        let greeting: String = call_result.unwrap();
        greeting
    }

```

</Language>

</CodeTabs>

---

## Snippet: Sending Information
Calling another contract passing information is also a common scenario. Below you can see a function that interacts with the [Hello NEAR](../quickstart.md) example to change its greeting message.

<CodeTabs>
<Language value="js" language="ts">
    ```
  @call({})
  change_greeting({ new_greeting }: { new_greeting: string }): NearPromise {
    const promise = NearPromise.new(this.hello_account)
      .functionCall(
        "set_greeting",
        JSON.stringify({ greeting: new_greeting }),
        NO_DEPOSIT,
        THIRTY_TGAS,
      )
      .then(
        NearPromise.new(near.currentAccountId())
          .functionCall(
            "change_greeting_callback",
            NO_ARGS,
            NO_DEPOSIT,
            THIRTY_TGAS,
          ),
      );

    return promise.asReturn();
  }

  @call({ privateFunction: true })
  change_greeting_callback(): boolean {
    let { success } = promiseResult();

    if (success) {
      near.log(`Success!`);
      return true;
    } else {
      near.log("Promise failed...");
      return false;
    }
  }
}
```

</Language>

<Language value="rust" language="rust">
    ```
// Find all our documentation at https://docs.near.org
use near_sdk::{env, near, AccountId, Gas, NearToken, PanicOnDefault};

pub mod external_contract;
pub use crate::external_contract::*;

pub mod high_level;
pub mod low_level;

const NO_ARGS: Vec<u8> = vec![];
const NO_DEPOSIT: NearToken = NearToken::from_near(0);
const FIVE_TGAS: Gas = Gas::from_tgas(5);
const TEN_TGAS: Gas = Gas::from_tgas(10);

#[near(contract_state)]
#[derive(PanicOnDefault)]
pub struct Contract {
    pub hello_account: AccountId,
}

#[near]
impl Contract {
    #[init]
    #[private] // Public - but only callable by env::current_account_id()
    pub fn init(hello_account: AccountId) -> Self {
        assert!(!env::state_exists(), "Already initialized");
        Self { hello_account }
    }
}

```
    ```
use near_sdk::ext_contract;

// Validator interface, for cross-contract calls
#[ext_contract(hello_near)]
trait HelloNear {
    fn get_greeting(&self) -> String;
    fn set_greeting(&self, greeting: String);
}

```
    ```
    // Public - change external greeting
    pub fn hl_change_greeting(&mut self, new_greeting: String) -> Promise {
        // Create a promise to call HelloNEAR.set_greeting(message:string)
        hello_near::ext(self.hello_account.clone())
            .with_static_gas(FIVE_TGAS)
            .set_greeting(new_greeting)
            .then(
                // Create a callback change_greeting_callback
                Self::ext(env::current_account_id())
                    .with_static_gas(FIVE_TGAS)
                    .hl_change_greeting_callback(),
            )
    }

    #[private]
    pub fn hl_change_greeting_callback(
        &mut self,
        #[callback_result] call_result: Result<(), PromiseError>,
    ) -> bool {
        // Return whether or not the promise succeeded using the method outlined in external.rs
        if call_result.is_err() {
            env::log_str("set_greeting failed...");
            false
        } else {
            env::log_str("set_greeting was successful!");
            true
        }
    }
}
```
    ```
    // Public - change external greeting
    pub fn ll_change_greeting(&mut self, new_greeting: String) -> Promise {
        let args = json!({ "greeting": new_greeting }).to_string().into_bytes();
        let hello_promise = Promise::new(self.hello_account.clone()).function_call(
            "set_greeting".to_owned(),
            args,
            NO_DEPOSIT,
            TEN_TGAS,
        );

        hello_promise.then(
            // Create a promise to callback query_greeting_callback
            Self::ext(env::current_account_id())
                .with_static_gas(TEN_TGAS)
                .ll_change_greeting_callback(),
        )
    }

    #[private]
    pub fn ll_change_greeting_callback(
        &mut self,
        #[callback_result] call_result: Result<(), PromiseError>,
    ) -> bool {
        // Return whether or not the promise succeeded using the method outlined in external.rs
        if call_result.is_err() {
            env::log_str("set_greeting failed...");
            false
        } else {
            env::log_str("set_greeting was successful!");
            true
        }
    }
}
```

</Language>

</CodeTabs>

---

## Promises
Cross-contract calls work by creating two promises in the network:
1. A promise to execute code in the external contract (`Promise.create`)
2. Optional: A promise to call another function with the result (`Promise.then`)

Both promises will contain the following information:

- The address of the contract you want to interact with
- The function that you want to execute
- The (**encoded**) arguments to pass to the function
- The amount of GAS to use (deducted from the **attached Gas**)
- The amount of NEAR to attach (deducted from **your contract’s balance**)

:::tip

The callback can be made to **any** contract. Meaning that the result could potentially be handled by another contract

:::


<hr class="subsection" />

### Creating a Cross Contract Call

To create a cross-contract call with a callback, create two promises and use the `.then` method to link them:


<Tabs>
  <TabItem value="js" label="🌐 JavaScript">

    ```ts
    NearPromise.new("external_address").functionCall("function_name", JSON.stringify(arguments), DEPOSIT, GAS)
    .then(
      // this function is the callback
      NearPromise.new(near.currentAccountId()).functionCall("callback_name", JSON.stringify(arguments), DEPOSIT, GAS)
    );
    ```

  </TabItem>
  <TabItem value="rs" label="🦀 Rust">

    There is a helper macro that allows you to make cross-contract calls with the syntax `#[ext_contract(...)]`. It takes a Rust Trait and converts it to a module with static methods. Each of these static methods takes positional arguments defined by the Trait, then the `receiver_id`, the attached deposit and the amount of gas and returns a new `Promise`. *That's the high-level way to make cross-contract calls.*

    ```rust
    #[ext_contract(external_trait)]
    trait Contract {
        fn function_name(&self, param1: T, param2: T) -> T;
    }

    external_trait::ext("external_address")
    .with_attached_deposit(DEPOSIT)
    .with_static_gas(GAS)
    .function_name(arguments)
    .then(
      // this is the callback
      Self::ext(env::current_account_id())
      .with_attached_deposit(DEPOSIT)
      .with_static_gas(GAS)
      .callback_name(arguments)
    );

    ```

    <hr class="subsection" />

    There is another way to achieve the same result. You can create a new `Promise` without using a helper macro. *It's the low-level way to make cross-contract calls.*

    ```rust
    let arguments = json!({ "foo": "bar" })
        .to_string()
        .into_bytes();

    let promise = Promise::new("external_address").function_call(
        "function_name".to_owned(),
        arguments,
        DEPOSIT,
        GAS
    );

    promise.then(
        // Create a promise to callback query_greeting_callback
        Self::ext(env::current_account_id())
            .with_static_gas(GAS)
            .callback_name(),
    );

    ```

<details>
<summary> Gas </summary>

You can attach an unused GAS weight by specifying the `.with_unused_gas_weight()` method but it is defaulted to 1. The unused GAS will be split amongst all the functions in the current execution depending on their weights. If there is only 1 function, any weight above 1 will result in all the unused GAS being attached to that function. If you specify a weight of 0, however, the unused GAS will **not** be attached to that function. If you have two functions, one with a weight of 3, and one with a weight of 1, the first function will get `3/4` of the unused GAS and the other function will get `1/4` of the unused GAS.

</details>

  </TabItem>
</Tabs>

:::info

If a function returns a promise, then it will delegate the return value and status of transaction execution, but if you return a value or nothing, then the `Promise` result will not influence the transaction status

:::

:::caution

The Promises you are creating will **not execute immediately**. In fact, they will be queued in the network an:
- The cross-contract call will execute 1 or 2 blocks after your function finishes **correctly**.

:::

---

## Callback Function
If your function finishes correctly, then eventually your callback function will execute. This will happen whether the **external contract fails or not**.

In the callback function you will have access to the result, which will contain the status of the external function (if it worked or not), and the values in case of success.

<CodeTabs>
  <Language value="js" language="ts">
    ```
  @call({ privateFunction: true })
  query_greeting_callback(): String {
    let { result, success } = promiseResult();

    if (success) {
      return result.substring(1, result.length - 1);
    } else {
      near.log("Promise failed...");
      return "";
    }
  }

  @call({})
```

</Language>

<Language value="rust" language="rust">

  ```
    #[private] // Public - but only callable by env::current_account_id()
    pub fn hl_query_greeting_callback(
        &self,
        #[callback_result] call_result: Result<String, PromiseError>,
    ) -> String {
        // Check if the promise succeeded by calling the method outlined in external.rs
        if call_result.is_err() {
            log!("There was an error contacting Hello NEAR");
            return "".to_string();
        }

        // Return the greeting
        let greeting: String = call_result.unwrap();
        greeting
    }

```

</Language>

</CodeTabs>

:::info Callback with always execute

We repeat, if your function finishes correctly, then your callback will **always execute**. This will happen no matter if the external function finished correctly or not

:::

:::warning

Always make sure to have enough Gas for your callback function to execute

:::

:::tip

Remember to mark your callback function as private using macros/decorators, so it can only be called by the contract itself

:::

<hr class="subsection" />

### What happens if the function I call fails?
If the external function fails (i.e. it panics), then your callback will be **executed anyway**. Here you need to **manually rollback** any changes made in your
contract during the original call. Particularly:

1. **Refund the predecessor** if needed: If the contract attached NEAR to the call, the funds are now back in **the contract's account**
2. **Revert any state changes**: If the original function made any state changes (i.e. changed or stored data), you need to manually roll them back. **They won't revert automatically**

:::warning
If your original function finishes correctly then the callback executes **even if the external function panics**. Your state will **not** rollback automatically,
and $NEAR will **not** be returned to the signer automatically. Always make sure to check in the callback if the external function failed, and manually rollback any
operation if necessary.
:::

---

## Concatenating Functions and Promises

✅ Promises can be concatenate using the `.and` operator: `P1.and(P2).and(P3).then(P4)`: `P1`, `P2`, and `P3` execute in parallel, after they finish, `P4` will execute and have access to all their results

⛔ You cannot **return** a joint promise without a callback: `return P1.and(P2)` is invalid since it misses the `then`

✅ You can concatenate `then` promises: `P1.then(P2).then(P3)`: `P1` executes, then `P2` executes with the result of `P1`, then `P3` executes with the result of `P2`

⛔ You cannot use an `and` within a `then`: `P1.then(P2.and(P3))` is invalid

⛔ You cannot use a `then` within a `then`: `P1.then(P2.then(P3))` is invalid

<hr class="subsection" />

### Multiple Functions, Same Contract

You can call multiple functions in the same external contract, which is known as a **batch call**.

An important property of batch calls is that they **act as a unit**: they execute in the same [receipt](/concepts/protocol/transaction-execution#receipts--finality), and if **any function fails**, then they **all get reverted**.

<Tabs>
  <TabItem value="js" label="🌐 JavaScript">

  ```
export function batch_actions(accountId: AccountId) {

  const promise = NearPromise.new(accountId)
    .functionCall("set_greeting", JSON.stringify({ greeting: 'hi' }), NO_DEPOSIT, TEN_TGAS)
    .functionCall("get_greeting", NO_ARGS, NO_DEPOSIT, TEN_TGAS)
    .functionCall("set_greeting", JSON.stringify({ greeting: 'bye' }), NO_DEPOSIT, TEN_TGAS)
    .functionCall("get_greeting", NO_ARGS, NO_DEPOSIT, TEN_TGAS)
    .then(
      NearPromise.new(near.currentAccountId())
      .functionCall("batch_actions_callback", NO_ARGS, NO_DEPOSIT, TEN_TGAS)
    )
    return promise.asReturn();
};

```

  </TabItem>
  <TabItem value="rs" label="🦀 Rust">

  ```
    pub fn batch_actions(&mut self) -> Promise {
        let hi = json!({ "greeting": "hi" }).to_string().into_bytes();
        let bye = json!({ "greeting": "bye" }).to_string().into_bytes();

        // You can create one transaction calling multiple methods
        // on a same contract
        Promise::new(self.hello_account.clone())
            .function_call("set_greeting".to_owned(), hi, NO_DEPOSIT, XCC_GAS)
            .function_call("get_greeting".to_owned(), NO_ARGS, NO_DEPOSIT, XCC_GAS)
            .function_call("set_greeting".to_owned(), bye, NO_DEPOSIT, XCC_GAS)
            .function_call("get_greeting".to_owned(), NO_ARGS, NO_DEPOSIT, XCC_GAS)
            .then(Self::ext(env::current_account_id()).batch_actions_callback())
    }

```

  </TabItem>
</Tabs>

:::tip

Callbacks only have access to the result of the **last function** in a batch call

:::

---

### Multiple Functions: Different Contracts

You can also call multiple functions in **different contracts**. These functions will be executed in parallel, and do not impact each other. This means that, if one fails, the others **will execute, and NOT be reverted**.

<Tabs>
  <TabItem value="js" label="🌐 JavaScript">

  ```
export function multiple_contracts(contract: CrossContractCall) {
  const promise1 = NearPromise.new(contract.hello_account)
    .functionCall("get_greeting", NO_ARGS, NO_DEPOSIT, TEN_TGAS)
  const promise2 = NearPromise.new(contract.counter_account)
    .functionCall("get_num", NO_ARGS, NO_DEPOSIT, TEN_TGAS)
  const promise3 = NearPromise.new(contract.guestbook_account)
    .functionCall("get_messages", NO_ARGS, NO_DEPOSIT, TEN_TGAS)

  return promise1
    .and(promise2)
    .and(promise3)
    .then(
      NearPromise.new(near.currentAccountId())
      .functionCall("multiple_contracts_callback", JSON.stringify({ number_promises: 3 }), NO_DEPOSIT, TEN_TGAS)
    )
};

```

  </TabItem>
  <TabItem value="rs" label="🦀 Rust">

  ```
    pub fn multiple_contracts(&mut self) -> Promise {
        // We create a promise that calls the `get_greeting` function on the HELLO_CONTRACT
        let hello_promise = Promise::new(self.hello_account.clone()).function_call(
            "get_greeting".to_owned(),
            NO_ARGS,
            NO_DEPOSIT,
            XCC_GAS,
        );

        // We create a promise that calls the `get_num` function on the COUNTER_CONTRACT
        let counter_promise = Promise::new(self.counter_account.clone()).function_call(
            "get_num".to_owned(),
            NO_ARGS,
            NO_DEPOSIT,
            XCC_GAS,
        );

        // We create a promise that calls the `get_messages` function on the GUESTBOOK_CONTRACT
        let args = json!({ "from_index": "0", "limit": 2 })
            .to_string()
            .into_bytes();

        let guestbook_promise = Promise::new(self.guestbook_account.clone()).function_call(
            "get_messages".to_owned(),
            args,
            NO_DEPOSIT,
            XCC_GAS,
        );

        // We join all promises and chain a callback to collect their results.
        hello_promise
            .and(counter_promise)
            .and(guestbook_promise)
            .then(
                Self::ext(env::current_account_id())
                    .with_static_gas(XCC_GAS)
                    .multiple_contracts_callback(),
            )
    }

```

  </TabItem>
</Tabs>

:::tip

Callbacks have access to the result of **all functions** in a parallel call

:::


---

## Security Concerns

While writing cross-contract calls there is a significant aspect to keep in mind: all the calls are **independent** and **asynchronous**. In other words:

- The function in which you make the call and function for the callback are **independent**.
- There is a **delay between the call and the callback**, in which people can still interact with the contract

This has important implications on how you should handle the callbacks. Particularly:

1. Make sure you don't leave the contract in a exploitable state between the call and the callback.
2. Manually rollback any changes to the state in the callback if the external call failed.

We have a whole [security section](../security/callbacks.md) dedicated to these specific errors, so please go and check it.

:::warning
Not following these basic security guidelines could expose your contract to exploits. Please check the [security section](../security/callbacks.md), and if still in doubt, [join us in Discord](https://near.chat).
:::
