/* Fixed hypothetical cases: no randomization, remote requests, or saved responses. */
(() => {
  "use strict";
  const root = document.getElementById("rd-activity");
  if (!root) return;
  const el = id => document.getElementById(`rd-${id}`);
  const cases = [
    { name: "University A", below: 30, above: 50, payBelow: 42000, payAbove: 45600 },
    { name: "University B", below: 45, above: 55, payBelow: 48000, payAbove: 51600 }
  ];
  const money = n => `$${n.toLocaleString("en-US", {maximumFractionDigits: 2})}`;
  const fields = ["degree", "eligibility", "effect"];
  const radios = Array.from(root.querySelectorAll('input[name="rd-population"]'));
  const claimRadios = Array.from(root.querySelectorAll('input[name="rd-claim-answer"]'));
  const designRadios = Array.from(root.querySelectorAll('input[name="rd-design-answer"]'));
  let caseIndex = 0;
  let attempted = false;
  let solved = false;

  function answers(c) {
    const jump = c.above - c.below;
    const earnings = c.payAbove - c.payBelow;
    return { degree: jump, eligibility: earnings, effect: earnings / (jump / 100) };
  }
  function parseAnswer(value, dollars) {
    let cleaned = value.trim().replace(/,/g, "");
    if (dollars) cleaned = cleaned.replace(/^\$\s*/, "");
    if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(cleaned)) return null;
    const n = Number(cleaned);
    return Number.isFinite(n) ? n : null;
  }
  const close = (value, expected) => value !== null && Math.abs(value - expected) < 0.011;

  function plot(kind, c) {
    const degree = kind === "degree";
    const low = degree ? c.below : c.payBelow;
    const high = degree ? c.above : c.payAbove;
    const min = degree ? 0 : 35000, max = degree ? 100 : 65000;
    const ticks = degree ? [0, 50, 100] : [35000, 50000, 65000];
    const y = value => 182 - (value - min) / (max - min) * 154;
    const label = value => degree ? `${value}%` : money(value);
    let svg = "";
    for (const tick of ticks) {
      svg += `<line class="rd-grid" x1="52" x2="300" y1="${y(tick)}" y2="${y(tick)}"/><text x="44" y="${y(tick) + 4}" text-anchor="end">${degree ? `${tick}%` : `$${tick / 1000}k`}</text>`;
    }
    svg += '<line class="rd-cutoff" x1="176" x2="176" y1="20" y2="186"/>';
    const slope = degree ? 8 : 4000;
    svg += `<path class="rd-line" d="M 52 ${y(low - slope)} L 176 ${y(low)} M 176 ${y(high)} L 300 ${y(high + slope)}"/>`;
    svg += `<circle class="rd-dot" cx="176" cy="${y(low)}" r="4"/><circle class="rd-dot rd-dot-above" cx="176" cy="${y(high)}" r="4"/>`;
    svg += `<text class="rd-value" x="166" y="${y(low) + 19}" text-anchor="end">${label(low)}</text><text class="rd-value" x="186" y="${y(high) - 12}">${label(high)}</text>`;
    svg += '<text x="52" y="206" text-anchor="middle">2.6</text><text x="176" y="206" text-anchor="middle">3.0</text><text x="300" y="206" text-anchor="middle">3.4</text><text x="176" y="230" text-anchor="middle">GPA · cutoff at 3.0</text>';
    el(`${kind}-plot`).innerHTML = svg;
    el(`${kind}-desc`).textContent = `Illustrative relationship at ${c.name}. Immediately below the cutoff: ${label(low)}. Immediately above: ${label(high)}. Compare the limiting values at GPA 3.0, not distant points on the lines.`;
  }

  function clearFeedback() {
    attempted = false;
    solved = false;
    el("status").textContent = "";
    el("solution").hidden = true;
    el("solution-button").hidden = true;
    el("next").hidden = true;
    for (const id of [...fields, "interpretation", "claim", "design"]) {
      el(`${id}-hint`).textContent = "";
      el(`${id}-hint`).removeAttribute("data-correct");
      el(id).removeAttribute("aria-invalid");
    }
  }

  function loadCase() {
    el("form").reset();
    clearFeedback();
    const c = cases[caseIndex];
    el("case").textContent = `Case ${caseIndex + 1} of 2 · ${c.name}`;
    el("context").textContent = caseIndex === 0
      ? "Use the values immediately below and above the cutoff to estimate the effect of eligibility, then the effect of completing the economics degree."
      : "The arithmetic has already been done at University B. Your task is to decide what the estimate means after learning more about the eligibility rule.";
    for (const id of ["calculations", "interpretation"]) {
      el(id).hidden = caseIndex === 1;
      el(id).disabled = caseIndex === 1;
    }
    for (const id of ["claim", "design"]) {
      el(id).hidden = caseIndex === 0;
      el(id).disabled = caseIndex === 0;
    }
    el("assumptions").hidden = caseIndex === 1;
    el("evidence").hidden = caseIndex === 0;
    el("solution-button").textContent = caseIndex === 0 ? "Show worked solution" : "Show explanation";
    el("prob-below").textContent = `${c.below}%`;
    el("prob-above").textContent = `${c.above}%`;
    el("pay-below").textContent = money(c.payBelow);
    el("pay-above").textContent = money(c.payAbove);
    plot("degree", c);
    plot("earnings", c);
  }

  function hint(id, value, c, a) {
    if (id === "degree") {
      if (close(value, a.degree / 100)) return "You entered a probability change. Express it in percentage points for this box.";
      if (close(value, c.above)) return "That is the completion rate above the cutoff. We need the change across the cutoff.";
      return "Subtract the completion rate just below the cutoff from the rate just above. Do not divide by the starting rate.";
    }
    if (id === "eligibility") return "Compare annual earnings just above and just below the cutoff. This box asks for the effect of eligibility, before scaling by degree completion.";
    if (close(value, a.eligibility / (c.above / 100))) return "You divided by the share completing economics above the cutoff. The denominator must measure how much eligibility changes that share.";
    if (close(value, a.eligibility / a.degree)) return "Check units: the denominator in the ratio is a probability change, not a number of percentage points.";
    if (close(value, a.eligibility)) return "That is the earnings effect of eligibility. Not everyone changes their degree choice when they become eligible.";
    return "Scale the earnings jump by the change in the probability of completing economics. Convert percentage points to a probability before dividing.";
  }

  function showSolution() {
    if (!attempted) return;
    const c = cases[caseIndex], a = answers(c);
    el("solution").innerHTML = caseIndex === 1
      ? `<h4>What University B identifies</h4>
      <p><strong>The $3,600 earnings jump is a local effect of crossing the cutoff and gaining access to the policy package.</strong> It combines major eligibility with internship access. Under the stated continuity assumptions, the comparison can identify that combined effect.</p>
      <p>But $3,600 ÷ 0.10 = $36,000 is <strong>not identified as a degree effect</strong>. Eligibility now has another route to earnings, through the internship. This breaks the assumption that eligibility affects earnings only through degree completion, often called the exclusion restriction.</p>
      <p>Smooth SAT scores support comparability of students. They cannot rule out two policies changing at the same cutoff. A narrower window still crosses both rules, and a larger sample only estimates the combined effect more precisely.</p>
      <p><strong>A design that separates the policies:</strong> keep internship access the same on both sides while major eligibility still changes at the cutoff. If the other assumptions from University A hold, the earnings-to-completion ratio can then identify a local degree effect under that version of the policy. The original data do not reveal how much of the $3,600 came from each route.</p>`
      : `<h4>Worked solution · ${c.name}</h4>
      <p class="rd-equation">Completion jump: ${c.above}% − ${c.below}% = <strong>${a.degree} percentage points</strong>, or ${a.degree / 100}.<br>Eligibility effect: ${money(c.payAbove)} − ${money(c.payBelow)} = <strong>${money(a.eligibility)} per year</strong>.<br>Degree effect: ${money(a.eligibility)} ÷ ${a.degree / 100} = <strong>${money(a.effect)} per year</strong>.</p>
      <p>The earnings jump is averaged over students near the threshold, including those whose degree choice is unchanged. Dividing by the change in degree completion isolates the average effect for students near the cutoff whose choice is changed by eligibility, under the stated assumptions. It is not an estimate for every economics graduate, or even every student near the cutoff.</p>`;
    el("solution").hidden = false;
    el("solution-button").hidden = true;
    el("next").hidden = caseIndex !== 0;
    if (!solved) el("status").textContent = caseIndex === 0 ? "Solution revealed. Compare each step with your attempt before trying University B." : "Explanation revealed. Compare it with your assessment of the claim and the proposed designs.";
  }

  function checkIdentification() {
    const claim = claimRadios.find(r => r.checked);
    const design = designRadios.find(r => r.checked);
    if (!claim || !design) {
      if (!claim) el("claim-hint").textContent = "Choose the conclusion supported by this design.";
      if (!design) el("design-hint").textContent = "Choose a design that addresses the problem.";
      el("status").textContent = "Answer both questions before checking your reasoning.";
      (!claim ? claimRadios[0] : designRadios[0]).focus();
      return;
    }
    attempted = true;
    const claimOK = claim.value === "package";
    const designOK = design.value === "separate";
    const claimHints = {
      "degree-ratio": "The division is numerically correct. Does the earnings jump reflect only a change in degree completion?",
      "degree-jump": "Ask what changes at the threshold. Is completing economics the only route from eligibility to earnings?",
      "nothing": "Two policies change together, but students are still comparable at the cutoff under the stated assumptions. Distinguish the effect of the package from its individual components."
    };
    const designHints = {
      "narrower": "Even immediately on either side of 3.0, access to both the major and the internship changes.",
      "larger": "More observations improve precision. Do they separate the two routes from eligibility to earnings?",
      "balance": "Balanced pre-college characteristics address comparability. Do they remove the internship policy that changes at the same cutoff?"
    };
    el("claim-hint").textContent = claimOK ? "Correct: the package effect is identified, but its degree component is not." : claimHints[claim.value];
    el("design-hint").textContent = designOK ? "Correct: this varies major eligibility without simultaneously varying internship access, subject to the other RD assumptions." : designHints[design.value];
    for (const [id, ok] of [["claim", claimOK], ["design", designOK]]) {
      el(`${id}-hint`).setAttribute("data-correct", String(ok));
      el(id).setAttribute("aria-invalid", String(!ok));
    }
    solved = claimOK && designOK;
    el("status").textContent = solved
      ? "Both answers are correct. You distinguished calculating a ratio from identifying a causal effect."
      : `${Number(claimOK) + Number(designOK)} of 2 answers correct. Reconsider the routes from the cutoff to earnings and what each proposed design changes.`;
    el("solution-button").hidden = solved;
    if (solved) showSolution();
    else (!claimOK ? claim : design).focus();
  }

  el("form").addEventListener("submit", event => {
    event.preventDefault();
    clearFeedback();
    if (caseIndex === 1) {
      checkIdentification();
      return;
    }
    const values = Object.fromEntries(fields.map(id => [id, parseAnswer(el(id).value, id !== "degree")]));
    const selected = radios.find(radio => radio.checked);
    const missing = fields.filter(id => values[id] === null);
    if (missing.length || !selected) {
      for (const id of missing) {
        el(`${id}-hint`).textContent = "Enter a number to check this answer.";
        el(id).setAttribute("aria-invalid", "true");
      }
      if (!selected) el("interpretation-hint").textContent = "Choose the population your estimate describes.";
      el("status").textContent = "Complete all three calculations and choose an interpretation before checking. You can use a calculator.";
      (missing.length ? el(missing[0]) : radios[0]).focus();
      return;
    }
    attempted = true;
    const c = cases[caseIndex], a = answers(c);
    let correct = 0;
    let firstIncorrect = null;
    for (const id of fields) {
      const ok = close(values[id], a[id]);
      el(`${id}-hint`).textContent = ok ? "Correct." : hint(id, values[id], c, a);
      el(`${id}-hint`).setAttribute("data-correct", String(ok));
      el(id).setAttribute("aria-invalid", String(!ok));
      if (ok) correct++;
      else if (!firstIncorrect) firstIncorrect = el(id);
    }
    const populationOK = selected.value === "switchers";
    el("interpretation-hint").textContent = populationOK ? "Correct: a local effect for students whose degree choice responds to eligibility."
      : selected.value === "always" ? "Eligibility does not change these students' degree choices. They do not generate the jump in completion."
      : selected.value === "all-nearby" ? "Being near the cutoff makes the comparison local, but some nearby students would choose the same degree on either side."
      : "The comparison is local to the eligibility cutoff. It cannot establish an average degree effect for every economics graduate.";
    el("interpretation-hint").setAttribute("data-correct", String(populationOK));
    if (populationOK) correct++;
    else if (!firstIncorrect) firstIncorrect = selected;
    solved = correct === 4;
    el("status").textContent = solved
      ? "All four answers are correct. Next, assess whether the method is valid at University B."
      : `${correct} of 4 answers correct. Use the hints to revise your answers, or reveal the worked solution.`;
    el("solution-button").hidden = solved;
    if (solved) showSolution();
    else firstIncorrect.focus();
  });
  fields.forEach(id => el(id).addEventListener("input", clearFeedback));
  [...radios, ...claimRadios, ...designRadios].forEach(radio => radio.addEventListener("change", clearFeedback));
  el("solution-button").addEventListener("click", showSolution);
  el("next").addEventListener("click", () => {
    if (el("solution").hidden || caseIndex !== 0) return;
    caseIndex = 1;
    loadCase();
    el("case").setAttribute("tabindex", "-1");
    el("case").focus();
  });
  el("reset").addEventListener("click", () => {
    caseIndex = 0;
    loadCase();
    el("case").setAttribute("tabindex", "-1");
    el("case").focus();
  });
  loadCase();
  el("charts").hidden = false;
  el("actions").hidden = false;
  el("navigation").hidden = false;
})();
