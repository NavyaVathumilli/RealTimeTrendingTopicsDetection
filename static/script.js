async function analyze() {
  const keyword = document.getElementById("keyword").value;
  const period = document.getElementById("period").value;
  const loading = document.getElementById("loading");
  const output = document.getElementById("output");

  loading.style.display = "block";
  output.innerHTML = "";

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keyword, period }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const data = await res.json();
    loading.style.display = "none";
    output.innerHTML = data.result;
  } catch (err) {
    loading.style.display = "none";
    output.innerHTML = "<b>Request timed out or failed:</b> " + err;
  }
}
