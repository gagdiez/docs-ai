---## Yielding a Promise

Let's look at an example that takes a prompt from a user (e.g. "What is 2+2"), and yields the execution until an external service provides a response.

<CodeTabs>
  <Language value="rust" language="rust">
    ```
    pub fn request(&mut self, prompt: String) {
        // internal variable to keep track of the requests
        self.request_id += 1;

        // this will create a unique ID in the YIELD_REGISTER
        let yield_promise = env::promise_yield_create(
            "return_external_response",
            &json!({ "request_id": self.request_id })
                .to_string()
                .into_bytes(),
            Gas::from_tgas(5),
            GasWeight::default(),
            YIELD_REGISTER,
        );

        // load the ID created by the promise_yield_create
        let yield_id: CryptoHash = env::read_register(YIELD_REGISTER)
            .expect("read_register failed")
            .try_into()
            .expect("conversion to CryptoHash failed");

        // store the request, so we can delete it later
        let request = Request { yield_id, prompt };
        self.requests.insert(self.request_id, request);

        // return the yield promise
        env::promise_return(yield_promise);
    }

```
  </Language>
</CodeTabs>

#### Creating a Yielded Promise
In the example above, we are creating a [`Promise`](./crosscontract.md#promises) to call the contract's function `return_external_response`.

Notice that we create the `Promise` using `env::promise_yield_create`, which will create an **identifier** for the yielded promise in the `YIELD_REGISTER`.

#### Retrieving the Yielded Promise ID
We read the `YIELD_REGISTER` to retrieve the `ID` of our yielded promise. We store the `yield_id` and the user's `prompt` so the external service query them (the contract exposes has a function to list all requests).

#### Returning the Promise
Finally, we return the `Promise`, which will **not execute immediately**, but will be **yielded** until the external service provides a response.

<details>

<summary> What is that `self.request_id` in the code? </summary>

The `self.request_id` is an internal unique identifier that we use to keep track of stored requests. This way, we can delete the request once the external service provides a response (or the waiting times out)

Since we only use it to simplify the process of keeping track of the requests, you can remove it if you have a different way of tracking requests (e.g. an indexer)

</details>

---

## Signaling the Resume

The `env::promise_yield_resume` function allows us to signal which yielded promise should execute, as well as which parameters to pass to the resumed function.

<CodeTabs>
  <Language value="rust" language="rust">
    ```
    pub fn respond(&mut self, yield_id: CryptoHash, response: String) {
        // resume computation with the response
        env::promise_yield_resume(&yield_id, &serde_json::to_vec(&response).unwrap());
    }

```
  </Language>
</CodeTabs>

In the example above, the `respond` function would be called by an external service, passing which promise should be resume (`yield_id`), and the response to the prompt. 

:::warning Gatekeeping the Resume

Since the function used to signal the resume is public, developers must make sure to guard it properly to avoid unwanted calls. This can be done by simply checking the caller of the function

:::

---

## The Function that Resumes

The function being resumed will have access to all parameters passed to it, including those passed during the yield creation, or the external service response.

<CodeTabs>
  <Language value="rust" language="rust">
    ```
    #[private]
    pub fn return_external_response(
        &mut self,
        request_id: u32,
        #[callback_result] response: Result<String, PromiseError>,
    ) -> Response {
        self.requests.remove(&request_id);

        match response {
            Ok(answer) => Response::Answer(answer),
            Err(_) => Response::TimeOutError,
        }
    }

```
  </Language>
</CodeTabs>

In the example above, the `return_external_response` receives two parameters:

1. A `request_id` - passed on [creation](#creating-a-yielded-promise) - which is used to remove the request from the state
2. A `response` - passed when [signaling to resume](#signaling-the-resume) - which contains the external response, or a `PromiseError` if the contract timed out while waiting

:::tip There's plenty of time

The contract will be able to wait for 200 blocks - around 4 minutes - before timing out

:::

:::info

Notice that, in this particular example, we choose to return a value both if there is a response or a time out

The reason to not raise an error, is because we are changing the state (removing the request in line `#7`), and raising an error would revert this state change

:::