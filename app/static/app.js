const form = document.getElementById("email-form");
const submitBtn = document.getElementById("submit-btn");
const loading = document.getElementById("loading");
const resultBox = document.getElementById("result");
const errorBox = document.getElementById("error-box");
const statusPill = document.getElementById("status-pill");
const copyBtn = document.getElementById("copy-btn");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");
  resultBox.classList.add("hidden");
  loading.classList.remove("hidden");
  submitBtn.disabled = true;
  statusPill.textContent = "Processando";
  statusPill.className = "pill neutral";

  const data = new FormData(form);

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: data,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Falha ao processar email.");
    }

    document.getElementById("category").textContent = payload.category;
    document.getElementById("confidence").textContent =
      `${Math.round(payload.confidence * 100)}%`;
    document.getElementById("summary").textContent = payload.summary;
    document.getElementById("reasoning").textContent = payload.reasoning;
    document.getElementById("reply").textContent = payload.suggested_reply;

    const signals = document.getElementById("signals");
    signals.innerHTML = "";
    const items = payload.detected_signals?.length
      ? payload.detected_signals
      : ["Nenhum sinal específico detectado."];
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      signals.appendChild(li);
    });

    statusPill.textContent = payload.category;
    statusPill.className = `pill ${payload.category === "Produtivo" ? "good" : "bad"}`;

    resultBox.classList.remove("hidden");
  } catch (error) {
    errorBox.textContent = error.message || "Erro inesperado.";
    errorBox.classList.remove("hidden");
    statusPill.textContent = "Erro";
    statusPill.className = "pill bad";
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
  }
});

copyBtn.addEventListener("click", async () => {
  const content = document.getElementById("reply").textContent;
  await navigator.clipboard.writeText(content);
  copyBtn.textContent = "Copiado!";
  setTimeout(() => (copyBtn.textContent = "Copiar resposta"), 1300);
});
