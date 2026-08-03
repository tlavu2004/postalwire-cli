# PostalWire

PostalWire is a small command-line mail client implemented from scratch in Java. It communicates directly with an SMTP server to send mail and a POP3 server to retrieve it, using raw `Socket` connections rather than JavaMail/Jakarta Mail.

The project is intentionally an MVP: its purpose is to demonstrate application-layer protocol knowledge, text-based network communication, and careful resource/error handling without prematurely adding Spring, a database, or a frontend.

## What it demonstrates

- SMTP flow: `EHLO` → `MAIL FROM` → `RCPT TO` → `DATA` → `QUIT`
- POP3 flow: `USER` → `PASS` → `STAT`/`LIST` → `RETR` → `QUIT`
- Response-code parsing, multi-line responses, socket timeouts, and clean shutdown
- A clear separation between protocol logic, the CLI, and the message model

## Architecture

```text
src/main/java/com/yourname/mailclient/
├── protocol/
│   ├── smtp/SmtpClient.java
│   ├── smtp/SmtpResponse.java
│   ├── pop3/Pop3Client.java
│   └── pop3/Pop3Response.java
├── cli/Main.java
└── model/EmailMessage.java
```

`protocol/` contains transport and protocol logic and must not depend on the CLI. This boundary keeps a future REST adapter or other delivery mechanism from requiring changes to the protocol layer.

## Requirements

- JDK 25 or another supported LTS JDK for the client
- Java 8 to run the supplied `test-mail-server-1.0.jar`
- Maven (if the project uses Maven) or a JDK with `javac`/`java`
- `telnet` for a quick manual port/connectivity check

## Local mail server

Start the fake mail server with Java 8, using the JAR supplied with the exercise:

```bash
java8 -jar test-mail-server-1.0.jar
```

Use the SMTP and POP3 ports printed by the server. Confirm that each port accepts a connection before starting the client:

```text
telnet localhost <smtp-port>
telnet localhost <pop3-port>
```

Do not commit the server JAR or local mail data to this repository.

## Build and run

The implementation is still being built from the MVP checklist. Once the Maven build is present:

```bash
mvn test
mvn package
java -cp target/classes com.yourname.mailclient.cli.Main
```

The CLI should ask for the recipient, subject, and body, print the SMTP exchange, retrieve the message through POP3, and print the retrieved content for comparison. Configure the server host, SMTP/POP3 ports, and test credentials through the project’s chosen configuration mechanism; never hard-code real credentials.

## Testing checklist

- Send a message to a test mailbox and retrieve it through POP3.
- Verify the content against Thunderbird or a direct `telnet` session.
- Verify connection-refused, malformed-address, timeout, and empty-`DATA` cases.
- Add JUnit 5 tests for response parsing, especially `250-` versus `250 ` multi-line responses.

## Why raw sockets?

Using a mail library would make sending mail easier, but would hide the protocol exchange this project is intended to study. Implementing the client directly makes the SMTP/POP3 command sequence, response codes, line termination, and socket lifecycle explicit. It is an educational and portfolio project, not a replacement for a production mail library.

## Scope and roadmap

The full checklist is in [`docs/blueprint/postalwire-mvp-blueprint.md`](docs/blueprint/postalwire-mvp-blueprint.md). Optional follow-up work includes complete dot-stuffing, MIME encoded-words, mock-socket tests, a REST adapter, a web UI, TLS, and real-time protocol tracing.

## License

No license has been selected yet. Add one before publishing the repository for reuse by others.
