# MVP Checklist — CLI Mail Client (SMTP/POP3 implemented from scratch in Java)

> Goal: reach a level that is **good enough to include on a résumé** as a personal project demonstrating application-layer networking knowledge. Avoid over-engineering; Spring, a database, and a frontend are not needed at this stage.

---

## 0. Architecture decisions (read before coding)

- [ ] **Do not** use Spring Boot / Spring Initializr for this MVP (there is no need for dependency injection, a web server, or auto-configuration).
- [ ] **Do not** split into multiple Maven modules at the start—the management cost is greater than the benefit at this scope.
- [ ] **Do** organize the code into clear packages within one Maven/Gradle module:
  ```text
  src/main/java/com/yourname/mailclient/
  ├── protocol/
  │   ├── smtp/SmtpClient.java       # Pure domain logic; no CLI dependency
  │   ├── smtp/SmtpResponse.java
  │   ├── pop3/Pop3Client.java
  │   └── pop3/Pop3Response.java
  ├── cli/
  │   └── Main.java                  # Scanner input, calls protocol/, prints output
  └── model/
      └── EmailMessage.java
  ```
  → Keeping `protocol/` separate from `cli/` is the most important boundary. It makes a future migration to a REST API possible by replacing only `cli/` without touching `protocol/`.

## 1. Environment & setup

- [ ] Confirm which JDK you use (JDK 25 or an available LTS release). This does **not affect** the implementation because `Socket`, `BufferedReader`, and `PrintWriter` are long-stable APIs.
- [ ] Run `test-mail-server-1.0.jar` with **Java 8 separately** (as required by that JAR), and use `telnet` to confirm that the SMTP and POP3 ports are listening correctly.
- [ ] Create a plain Java project (a simple, single-module Maven project), or use `javac`/`java` directly if you want to keep it even more minimal.

## 2. Protocol layer (the core and highest-priority part)

- [ ] `SmtpClient`: open a `Socket` and read the `220` banner.
- [ ] Send the command sequence: `EHLO` → `MAIL FROM` → `RCPT TO` → `DATA` → message content terminated by `\r\n.\r\n` → `QUIT`.
- [ ] Parse response codes (`250`, `354`, `221`, …) and distinguish success/failure by the first digit (2xx/3xx = OK; 4xx/5xx = error).
- [ ] `Pop3Client`: `USER` → `PASS` → `STAT`/`LIST` → `RETR <n>` → `QUIT`.
- [ ] Close the `Socket` correctly (`try-with-resources` or `finally`), including when an error occurs mid-session.
- [ ] Implement a basic timeout (`socket.setSoTimeout(...)`) so the client cannot hang indefinitely when the server does not respond.

## 3. CLI layer

- [ ] Use `Scanner` in `main()` to read the recipient, subject, and body.
- [ ] Call `SmtpClient` to send the message and print each step to the console (reproducing the kind of interaction observed through `telnet`/Wireshark in the original lab).
- [ ] Call `Pop3Client` to retrieve the email just sent and print it for comparison.
- [ ] Handle basic errors: catch `IOException` and print a clear message instead of crashing with an unreadable stack trace.

## 4. Testing

- [ ] Manual test: send an email to yourself, retrieve it, and compare the content with the result previously observed through Thunderbird/`telnet`.
- [ ] Error cases: server not running (connection refused), invalid email format, and empty `DATA`.
- [ ] (Recommended) Write a few JUnit 5 unit tests for the response parser to demonstrate edge cases (multi-line responses such as `250-` versus `250 `).

## 5. Polish for résumé readiness

- [ ] `README.md` includes:
  - [ ] A short description: *“A raw Java `Socket` SMTP/POP3 client implemented from scratch according to RFC 5321/1939, without JavaMail/Jakarta Mail.”*
  - [ ] The directory structure (a diagram like section 0).
  - [ ] Run instructions: how to start the fake mail server and how to run the CLI.
  - [ ] **Why implement it from scratch instead of using a library** (showing engineering reasoning, not just that it works)—for example, understanding the protocol at the byte level and practicing socket programming.
  - [ ] A real screenshot/GIF or console log excerpt (an SMTP/POP3 trace) so a résumé reader can immediately see the app working.
- [ ] Keep a meaningful Git history, split into small steps (not one commit called “done”).
- [ ] Push to a public GitHub repository with a clear name.

> ✅ At this point, the project is sufficient to list on a résumé as a *personal project demonstrating networking-protocol knowledge*. Continuing with the sections below is optional.

---

## 6. Future development (optional; add gradually to strengthen the résumé)

### Level 1 — Add technical depth (without changing the overall architecture)

- [ ] Fully handle dot-stuffing (when a body line starts with `.`, escape it as `..`).
- [ ] Support MIME encoded-words for subjects/bodies containing Vietnamese characters (`=?UTF-8?B?...?=`).
- [ ] Add comprehensive unit tests for `SmtpClient`/`Pop3Client` with mock sockets (`PipedInputStream`/`PipedOutputStream`).

### Level 2 — Turn it into a service (the point where module separation becomes worthwhile)

- [ ] Add a thin REST API (Spring Boot) that calls the existing `protocol/` layer. **This is the point to consider multiple modules**, because natural boundaries appear: `protocol-core` (domain) / `api` (controllers, DTOs) / `infrastructure`.
- [ ] Résumé story at this stage: *“Separated protocol logic from the delivery layer, enabling the same SMTP/POP3 client to be reused by both a CLI and a REST API.”*

### Level 3 — Full web app (if you want a larger project)

- [ ] Add a React frontend and store send/receive history in a database.
- [ ] Consider SQL (PostgreSQL) for accounts/history because the relationships are clear. Avoid choosing NoSQL solely to learn a new technology when it is not actually needed (revisit the earlier SQL-vs-NoSQL analysis).
- [ ] Add a prominent “protocol trace” view to the UI as a differentiator from ordinary mail clients.

### Level 4 — Further expansion (only if you have the time and interest)

- [ ] Support real SSL/TLS (`SSLSocket`) for connecting to a real Gmail SMTP/POP3 server as an “advanced mode.”
- [ ] Use WebSocket to push the trace in real time instead of fetching it after sending completes.

---

**Guiding principle for future development:** split modules or add layers only when a *real* responsibility boundary appears (for example, when adding a caller besides the CLI). Do not split things “just in case”; that would be over-engineering and contrary to the MVP spirit.
