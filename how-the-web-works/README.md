# 🌐 How the Web Works?

> 📅 Last updated: 2026-01-11 17:01 UTC
> 🔗 [View in Notion](https://www.notion.so/How-the-Web-Works-2e56249cbbe2801db43bc62655307bd9)

---

<details>
<summary>How the Web Works?</summary>

- When we browse a website, our browser (the client) sends a request to a server. The server processes the request and returns a response.
- This communication happens using HTTP (HyperText Transfer Protocol), which defines how data is exchanged over the web.
</details>
<details>
<summary>Key Parts of an HTTP Request</summary>

- Method – Specifies what action we want to perform (GET, POST, PUT, DELETE).
- URL – The address of the resource being requested.
- Headers – Extra information (e.g., content type, authentication tokens).
- Body (Optional) – Contains data for the server (e.g., form submissions).
</details>
<details>
<summary>Key Parts of an HTTP Response</summary>

- Status Code – Indicates if the request was successful (200 OK, 404 Not Found).
- Headers – Metadata about the response.
- Body – The actual content returned by the server. It can contain
  - HTML markup (used in traditional web applications)
  - Data in JSON format (used in APIs)
</details>
<details>
<summary>How Web Pages Are Generated</summary>

- Web pages are built using HTML (HyperText Markup Language). In web applications, HTML can be generated in two ways:
  - On the Server – The server generates the full HTML page and sends it to the client. This technique is referred to as Server-Side Rendering (SSR).
  - On the Client – The server sends only raw data (JSON), and the client dynamically generates web page using JavaScript. This technique is referred to as Client-Side Rendering (CSR).
</details>
<details>
<summary>What is JSON?</summary>

- JSON (JavaScript Object Notation) is a lightweight format used to structure data.
- It is commonly used in APIs because it is easy to read and process for both humans and computers.
</details>
<details>
<summary>What is an API?</summary>

- An API (Application Programming Interface) is a way for applications to communicate with each other.
- In web development, an API allows a client (browser, mobile app, or another system) to send/request data to/from a server.
</details>
