import { useEffect, useMemo, useRef, useState } from "react";
import {
  ChevronDown,
  CreditCard,
  Landmark,
  LifeBuoy,
  LockKeyhole,
  LogOut,
  MessageSquareText,
  Send,
  ShieldAlert,
  Sparkles,
  TicketCheck,
  UserPlus,
  WalletCards,
  X
} from "lucide-react";
import kamaProfile from "./assets/kama-profile.svg";

const initialMessages = [
  {
    id: createId(),
    role: "assistant",
    text: "Salam. I can help with accounts, cards, balance, transfers, and support requests."
  }
];

const quickActions = [
  { label: "Balance", message: "Check my balance", icon: WalletCards },
  { label: "New account", message: "Create an AZN current account", icon: Landmark },
  { label: "New card", message: "Create a debit card", icon: CreditCard },
  { label: "Block card", message: "Block my card", icon: ShieldAlert },
  { label: "Block account", message: "Block my account", icon: LockKeyhole },
  { label: "New request", message: "Create a support request", icon: LifeBuoy },
  { label: "Requests", message: "Show my support requests", icon: TicketCheck }
];

function createId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

function normalizeToken(payload) {
  return (
    payload?.access_token ||
    payload?.AccessToken ||
    payload?.AuthenticationResult?.AccessToken ||
    ""
  );
}

async function requestJson(url, options = {}) {
  const { headers = {}, ...rest } = options;
  const response = await fetch(url, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...headers
    }
  });

  const text = await response.text();
  let payload = text;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = text;
  }

  if (!response.ok) {
    const detail = payload?.detail || payload || "Request failed";
    const error = new Error(String(detail));
    error.status = response.status;
    throw error;
  }

  return payload;
}

function getErrorMessage(error) {
  const message = error?.message || "Something went wrong";
  if (
    error?.status === 401 ||
    message.includes("Invalid JWT") ||
    message.includes("Invalid JWT token") ||
    message.includes("401")
  ) {
    return "Session expired. Please sign in again.";
  }
  return message;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function InlineText({ text }) {
  return String(text)
    .split("**")
    .map((part, index) =>
      index % 2 === 1 ? <strong key={`${part}-${index}`}>{part}</strong> : part
    );
}

function normalizeAssistantText(text) {
  return String(text || "")
    .replace(/\r\n?/g, "\n")
    .replace(/\s+(Card Categories:|Card Functions:|Account Status:|Card Status:|Accounts:|Cards:)/gi, "\n\n$1\n")
    .replace(/\s+-\s+(?=\S)/g, "\n- ")
    .replace(/\s+(Would you like|Each card type|Premium cards|For detailed|For more)/g, "\n\n$1")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function FormattedText({ text }) {
  const lines = normalizeAssistantText(text).split("\n");
  const nodes = [];
  let bullets = [];

  function flushBullets() {
    if (!bullets.length) return;
    const listItems = bullets;
    bullets = [];
    nodes.push(
      <ul className="message-list" key={`list-${nodes.length}`}>
        {listItems.map((item, index) => (
          <li key={`${item}-${index}`}>
            <InlineText text={item} />
          </li>
        ))}
      </ul>
    );
  }

  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) {
      flushBullets();
      return;
    }

    const bullet = line.match(/^[-•]\s+(.+)$/);
    if (bullet) {
      bullets.push(bullet[1]);
      return;
    }

    flushBullets();
    const isHeading = /^[^.!?]{2,}:$/.test(line);
    nodes.push(
      <p className={isHeading ? "message-heading" : "message-paragraph"} key={`line-${nodes.length}`}>
        <InlineText text={line} />
      </p>
    );
  });

  flushBullets();
  return <div className="message-content">{nodes}</div>;
}

function AuthForm({ mode, setMode, onLogin, onSignup, feedback }) {
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({
    firstname: "",
    surname: "",
    email: "",
    phone_number: "",
    birth_date: "",
    password: ""
  });
  const [loadingAction, setLoadingAction] = useState("");

  async function withLoading(action, callback) {
    setLoadingAction(action);
    try {
      await callback();
    } finally {
      setLoadingAction("");
    }
  }

  return (
    <section className="auth-card" aria-label="Authentication">
      <div className="tabs" role="tablist" aria-label="Authentication">
        <button
          className={`tab ${mode === "login" ? "is-active" : ""}`}
          type="button"
          onClick={() => setMode("login")}
        >
          Sign in
        </button>
        <button
          className={`tab ${mode === "signup" ? "is-active" : ""}`}
          type="button"
          onClick={() => setMode("signup")}
        >
          Register
        </button>
      </div>

      {mode === "login" ? (
        <form
          className="auth-form"
          onSubmit={(event) => {
            event.preventDefault();
            withLoading("login", () => onLogin(loginForm));
          }}
        >
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={loginForm.email}
              onChange={(event) => setLoginForm({ ...loginForm, email: event.target.value })}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={loginForm.password}
              onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
              required
            />
          </label>
          <button className="primary-button" type="submit" disabled={loadingAction === "login"}>
            <LockKeyhole size={17} />
            {loadingAction === "login" ? "Signing in" : "Sign in"}
          </button>
        </form>
      ) : (
        <form
          className="auth-form"
          onSubmit={(event) => {
            event.preventDefault();
            withLoading("signup", () => onSignup(signupForm, setLoginForm));
          }}
        >
          <div className="field-grid">
            <label>
              First name
              <input
                type="text"
                autoComplete="given-name"
                value={signupForm.firstname}
                onChange={(event) => setSignupForm({ ...signupForm, firstname: event.target.value })}
                required
              />
            </label>
            <label>
              Surname
              <input
                type="text"
                autoComplete="family-name"
                value={signupForm.surname}
                onChange={(event) => setSignupForm({ ...signupForm, surname: event.target.value })}
                required
              />
            </label>
          </div>
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={signupForm.email}
              onChange={(event) => setSignupForm({ ...signupForm, email: event.target.value })}
              required
            />
          </label>
          <label>
            Phone
            <input
              type="tel"
              autoComplete="tel"
              value={signupForm.phone_number}
              onChange={(event) => setSignupForm({ ...signupForm, phone_number: event.target.value })}
              required
            />
          </label>
          <label>
            Birth date
            <input
              type="date"
              value={signupForm.birth_date}
              onChange={(event) => setSignupForm({ ...signupForm, birth_date: event.target.value })}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="new-password"
              value={signupForm.password}
              onChange={(event) => setSignupForm({ ...signupForm, password: event.target.value })}
              required
            />
          </label>
          <button className="primary-button" type="submit" disabled={loadingAction === "signup"}>
            <UserPlus size={17} />
            {loadingAction === "signup" ? "Creating" : "Create account"}
          </button>
        </form>
      )}

      {feedback.message ? (
        <p className={`feedback inline ${feedback.isError ? "is-error" : ""}`}>{feedback.message}</p>
      ) : null}
    </section>
  );
}

function AuthMenu({ signedIn, email, mode, setMode, feedback, onLogin, onSignup, onLogout }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (signedIn) setOpen(false);
  }, [signedIn]);

  return (
    <div className="auth-menu">
      <button className="auth-menu-button" type="button" onClick={() => setOpen((value) => !value)}>
        <img src={kamaProfile} alt="" />
        <span>{signedIn ? "Account" : "Login / Register"}</span>
        {open ? <X size={16} /> : <ChevronDown size={16} />}
      </button>

      {open ? (
        <div className="auth-popover">
          {signedIn ? (
            <section className="signed-card">
              <p className="mini-label">Signed in as</p>
              <strong>{email || "Secure session"}</strong>
              <button className="ghost-button" type="button" onClick={onLogout}>
                <LogOut size={17} />
                Log out
              </button>
            </section>
          ) : (
            <AuthForm
              mode={mode}
              setMode={setMode}
              onLogin={onLogin}
              onSignup={onSignup}
              feedback={feedback}
            />
          )}
        </div>
      ) : null}
    </div>
  );
}

function MessageBubble({ message }) {
  return (
    <article className={`message ${message.role}`}>
      {message.role === "assistant" ? (
        <img className="avatar image-avatar" src={kamaProfile} alt="Kama assistant" />
      ) : null}
      <div className="bubble">
        {message.text ? (
          <FormattedText text={message.text} />
        ) : (
          <span className="typing-dots" aria-label="Kama is typing">
            <span />
            <span />
            <span />
          </span>
        )}
      </div>
    </article>
  );
}

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("kama_access_token") || "");
  const [email, setEmail] = useState(localStorage.getItem("kama_email") || "");
  const [mode, setMode] = useState("login");
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState({ message: "", isError: false });
  const messagesEndRef = useRef(null);

  const signedIn = Boolean(token);
  const connectionLabel = sending ? "Thinking" : signedIn ? "Ready" : "Offline";
  const sessionLabel = useMemo(() => (signedIn ? email || "Secure session" : "Guest mode"), [email, signedIn]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;

    async function validateSession() {
      try {
        const profile = await requestJson("/Profile/", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        if (!cancelled && profile?.email) {
          setEmail(profile.email);
          localStorage.setItem("kama_email", profile.email);
        }
      } catch (error) {
        if (cancelled || error?.status !== 401) return;
        clearSession();
        setFeedback({ message: "Session expired. Please sign in again.", isError: true });
      }
    }

    validateSession();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleLogin(form) {
    setFeedback({ message: "", isError: false });
    try {
      const payload = await requestJson("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.email.trim(),
          password: form.password
        })
      });
      const nextToken = normalizeToken(payload);
      if (!nextToken) throw new Error("Login succeeded, but no access token was returned.");

      setToken(nextToken);
      setEmail(form.email.trim());
      localStorage.setItem("kama_access_token", nextToken);
      localStorage.setItem("kama_email", form.email.trim());
      setFeedback({ message: "Signed in.", isError: false });
      setMessages((current) => [
        ...current,
        { id: createId(), role: "assistant", text: "Welcome back. How can I help?" }
      ]);
    } catch (error) {
      setFeedback({ message: getErrorMessage(error), isError: true });
    }
  }

  async function handleSignup(form, setLoginForm) {
    setFeedback({ message: "", isError: false });
    try {
      await requestJson("/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          email: form.email.trim(),
          firstname: form.firstname.trim(),
          surname: form.surname.trim(),
          phone_number: form.phone_number.trim()
        })
      });
      setLoginForm((current) => ({ ...current, email: form.email.trim() }));
      setMode("login");
      setFeedback({ message: "Account created. You can sign in now.", isError: false });
    } catch (error) {
      setFeedback({ message: getErrorMessage(error), isError: true });
    }
  }

  async function sendMessage(message) {
    const cleanMessage = message.trim();
    if (!cleanMessage || sending) return;
    if (!signedIn) {
      setFeedback({ message: "Sign in first.", isError: true });
      return;
    }

    const assistantId = createId();
    setDraft("");
    setFeedback({ message: "", isError: false });
    setSending(true);
    setMessages((current) => [
      ...current,
      { id: createId(), role: "user", text: cleanMessage },
      { id: assistantId, role: "assistant", text: "" }
    ]);

    try {
      const answer = await requestJson("/chat", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: cleanMessage })
      });
      const finalText = typeof answer === "string" ? answer : JSON.stringify(answer, null, 2);
      const typingDelay = finalText.length > 700 ? 5 : 12;
      let visibleText = "";
      for (const char of finalText) {
        visibleText += char;
        setMessages((current) =>
          current.map((item) => (item.id === assistantId ? { ...item, text: visibleText } : item))
        );
        await sleep(typingDelay);
      }
    } catch (error) {
      const authExpired = error?.status === 401;
      if (authExpired) {
        setToken("");
        setEmail("");
        localStorage.removeItem("kama_access_token");
        localStorage.removeItem("kama_email");
      }
      const errorMessage = getErrorMessage(error);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId ? { ...item, text: errorMessage } : item
        )
      );
      setFeedback({ message: errorMessage, isError: true });
    } finally {
      setSending(false);
    }
  }

  function logout() {
    clearSession();
    setFeedback({ message: "Signed out.", isError: false });
  }

  function clearSession() {
    setToken("");
    setEmail("");
    localStorage.removeItem("kama_access_token");
    localStorage.removeItem("kama_email");
  }

  return (
    <main className="app-shell">
      <header className="app-nav">
        <div className="brand-lockup">
          <img src={kamaProfile} alt="Kama assistant profile" />
          <div>
            <strong>Kama</strong>
            <span>Secure banking assistant</span>
          </div>
        </div>

        <div className="nav-actions">
          <div className="session-pill">
            <span className={`status-dot ${signedIn ? "is-online" : ""}`} />
            <span>{sessionLabel}</span>
          </div>
          <AuthMenu
            signedIn={signedIn}
            email={email}
            mode={mode}
            setMode={setMode}
            feedback={feedback}
            onLogin={handleLogin}
            onSignup={handleSignup}
            onLogout={logout}
          />
        </div>
      </header>

      <section className="workspace">
        <aside className="assistant-panel" aria-label="Assistant profile">
          <div className="assistant-portrait-wrap">
            <img className="assistant-portrait" src={kamaProfile} alt="Kama assistant" />
          </div>
          <p className="eyebrow">
            <Sparkles size={14} />
            Your banking companion
          </p>
          <h1>
            Better banking.
            <em> Calmer support.</em>
          </h1>
          <p className="assistant-copy">
            Ask about accounts, cards, balances, transfers, and support requests from one focused workspace.
          </p>
        </aside>

        <section className="chat-panel" aria-label="Chat">
          <header className="chat-header">
            <div>
              <p className="eyebrow">
                <MessageSquareText size={14} />
                Live assistant
              </p>
              <h2>Kama Chat</h2>
            </div>
            <div className="header-meta">
              <MessageSquareText size={16} />
              <span>{connectionLabel}</span>
            </div>
          </header>

          <div className="messages" aria-live="polite">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="quick-actions" aria-label="Quick chat actions">
            {quickActions.map(({ label, message, icon: Icon }) => (
              <button
                key={label}
                type="button"
                disabled={!signedIn || sending}
                onClick={() => sendMessage(message)}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </div>

          <form
            className={`composer ${!signedIn ? "is-disabled" : ""}`}
            onSubmit={(event) => {
              event.preventDefault();
              sendMessage(draft);
            }}
          >
            <textarea
              rows={1}
              placeholder={signedIn ? "Type your message..." : "Sign in from the top right menu..."}
              value={draft}
              disabled={!signedIn}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage(draft);
                }
              }}
            />
            <button className="send-button" type="submit" disabled={!signedIn || sending || !draft.trim()}>
              <Send size={18} />
              {sending ? "Sending" : "Send"}
            </button>
          </form>
        </section>
      </section>
    </main>
  );
}
