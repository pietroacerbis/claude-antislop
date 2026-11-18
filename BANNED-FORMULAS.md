# The antislop list

<!-- antislop: off: this file lists the patterns it checks -->

61 patterns, printed from `skills/deslop/scripts/patterns.py` by `check.py --list`. Edit the patterns there, then print this file again: `tests/test_check.py` fails when the two differ.

- **fail**: the text does not ship with it.
- **flag**: read in context. One can be fine; more than 2 different ones in one text mean a rewrite.

Code, quotations of four words or more, blockquotes, URLs and link targets are never checked. A file with the line `<!-- antislop: off -->` is skipped.

## Sentence shapes, English

| Id | Pattern | Severity | Catches | Fix |
|---|---|---|---|---|
| R1 | not-x-but-y | fail | This is not a pipeline problem, but a systems problem. | Say the thing directly. Keep a contrast only when the reader really holds the belief you correct. |
| R2 | not-about-x | fail | It's not about the tools, it's about the people. | State the point the second half makes, without the first half. |
| R3 | most-opener | fail | Most founders treat AI as a productivity tool. | Describe what happens, with who and how many, instead of diagnosing a crowd. |
| R4 | its-actually | fail | AI looks like a democratizer. It's actually an amplifier. | Commit to the claim. The reveal adds nothing the claim does not carry. |
| R5 | not-only-but | fail | It not only saves time but also improves accuracy. | Say both things plainly, or keep the stronger one. |
| R6 | staccato-verbs | flag | Build. Test. Scale. | Write a real sentence with what is built, tested and scaled. |
| R7 | triple-beat | flag | The data. The workflows. The results. | Seriousness by structure: name what each item is and what it did. |
| R8 | narrating-participle | fail | We rebuilt their CRM, highlighting the importance of clean data. | Delete the clause that explains the action. Keep the action and its result. |
| R9 | participle-pileup | flag | We audited the CRM, finding gaps, fixing fields, cleaning data. | At most two -ing clauses in a row. Split the sentence. |
| R10 | false-range | flag | We take you from strategy to execution. | The two ends must sit on one scale you could measure. Otherwise name the items. |
| R11 | conjunction-opener | flag | But the data says otherwise. | One per text at most. Fold it into the sentence before. |
| R12 | standalone-because | flag | Because automation without foundations is faster failure. | Fold the reason into the sentence it explains, or show it. |
| R13 | dash | fail | The fix — long overdue — shipped on Monday. | Use a comma, a colon, a period or parentheses. An en dash between two numbers is fine. |
| R14 | ai-vocabulary | fail | We built a robust, holistic framework. | Use the plain word, or the number behind it. |
| R15 | filler-transition | fail | Here's the thing: nobody reads the deck. | Deliver the surprise. Never announce it. |
| R16 | engagement-bait | fail | Agree or disagree? | Earn the reply with something worth answering. Never ask for it. |
| R17 | self-locating-clause | fail | This is the part that runs here. | State the fact and stop. The reader already knows which section is open. |
| R18 | is-not-a-it-is-b | fail | The CRM is not a database, it is a habit. | Say what it is. Drop the half that denies a claim nobody made. |
| R19 | x-without-y-is | fail | A strategy without execution is just a wish. | Name the mechanism: what breaks, after how long, and why. |
| R20 | dies-the-day | fail | A playbook dies the day nobody updates it. | Say what stops working, when, and what keeps it working. |
| R21 | chat-closer | flag | Great question! Let me know if you need anything else. | End when the content ends. |
| H1 | staged-opener | fail | Let's dive in. | Cut the run-up and open on the point. |
| H2 | arguing-with-no-one | flag | Don't get me wrong, tools matter. | Remove the defence against an objection nobody raised. State the claim. |
| H3 | copula-avoidance | flag | The page serves as a hub for the whole team. | Use is, are or has. |
| H4 | named-closer | flag | That is the real win. | Cut the line that names what the paragraph showed, or replace it with a new fact. |
| H5 | fragment-row | flag | No meetings. No slides. Just results. | Merge the fragments into one sentence with a claim. |
| H6 | double-hyphen-dash | flag | The fix -- long overdue -- shipped. | A double hyphen used as a dash: use a comma, a colon or a period. |
| H7 | split-contrast | fail | That's not an incremental update. That's a new way to work. | The not-X-but-Y contrast split across two sentences: keep the second, without the denial. |

## Words and phrases, English

| Id | Pattern | Severity | Catches | Fix |
|---|---|---|---|---|
| P1 | ai-vocabulary-words: showcase, showcases, leverage, leveraging, seemingly, arguably, notably, importantly, ultimately, fundamentally, inherently, undeniably, understandably | fail | Ultimately, this will showcase our values. | Delete the word, or replace it with the fact it stands for. |
| P2 | ai-vocabulary-context: landscape, dynamics, ecosystem, navigate, unpack, harness, vital | flag | We help founders navigate the AI landscape. | Fine in a literal or technical sense. As decoration, name the real thing. |
| P3 | promotional: in the heart of, boasts, stunning, breathtaking, rich tapestry of, bustling, state-of-the-art, best-in-class, world-class, next-level, supercharge, turbocharge, skyrocket, unlock the potential, unlock growth, empower teams | flag | Supercharge your pipeline with world-class tools. | Replace the adjective with the measured change. |
| P4 | puffery: stands as a testament to, serves as a reminder of, a testament to, enduring legacy, indelible mark, deeply rooted, steadfast dedication, plays a vital role, of paramount importance, cannot be overstated, at the end of the day, when all is said and done, make no mistake, the bottom line is, the future looks bright, exciting times ahead, a step in the right direction, setting the stage for | flag | The launch stands as a testament to our team. | Show the importance through its consequence. End on the last concrete fact. |
| P5 | vague-intensity: visceral, primal, bone-deep, groundbreaking, revolutionary, mind-blowing, eye-opening, jaw-dropping | flag | The results were mind-blowing. | Name the specific change. |
| P6 | hollow-process: deep dive, circle back, move the needle, low-hanging fruit, table stakes, double down on, the reality is, let me be honest, stop me if you've heard this one | flag | Let's circle back and move the needle. | State the claim, or the action and its owner. |
| P7 | announced-insight: here's what most people miss, here's what nobody talks about, i'll wait, think about that for a second, but here's where it gets interesting | flag | Here's what nobody talks about: churn. | Deliver the point without the drumroll. |
| P8 | engagement-closers: this might ruffle some feathers, comment below | flag | Comment below with your thoughts. | Ask a specific question, or end on the content. |
| P9 | linkedin-cliche: i'm excited to announce, we're excited to announce, thrilled to, big news, a whole new way to, can't wait to see, humbled and grateful, beyond grateful, it's been a journey, the grind never stops, level up, crushing it, killing it, lessons learned, fail fast, move fast and break things, growth mindset | flag | I'm excited to announce our new product! | Say what happened, with the date and the number. |
| P10 | competence-performance: surgical precision, with practiced ease, seamless, effortless, flawless execution, well-oiled machine, like clockwork, fine-tuned | flag | A seamless onboarding experience. | Show the action, not the label of competence. |
| P11 | stock-metaphor: silver bullet, secret sauce, the missing piece, in today's fast-paced world, in today's digital age, ever-evolving, ever-changing landscape | flag | Data is the secret sauce in today's fast-paced world. | Write the operational instruction instead of the image. |

## Italian

| Id | Pattern | Severity | Catches | Fix |
|---|---|---|---|---|
| I1 | non-e-a-e-b | fail | Il CRM non è un database, è un'abitudine. | Di' cosa è. Togli la metà che nega una tesi che nessuno ha sostenuto. |
| I2 | non-e-a-ma-b | fail | Non è un problema di pipeline ma di sistema. | Di' direttamente la seconda metà. |
| I3 | non-si-tratta-di | fail | Non si tratta di strumenti, ma di persone. | Togli la cornice e lascia il punto. |
| I4 | non-questione-di | fail | Non è una questione di budget. | Di' di cosa è questione. |
| I5 | e-a-non-b | flag | È un processo, non un tool. | Il contrasto rovesciato: tieni solo la parte affermativa. |
| I6 | x-senza-y | fail | Una strategia senza esecuzione è un desiderio. | Scrivi il meccanismo: cosa si rompe, dopo quanto, perché. |
| I7 | muore-il-giorno | fail | Un playbook muore il giorno che nessuno lo aggiorna. | Di' cosa smette di funzionare, quando, e cosa lo tiene in piedi. |
| I8 | nessuno-lo-verbo | flag | Documenti che nessuno legge. | Una valutazione senza causa: di' perché succede e cosa lo rende possibile comunque. |
| I9 | most-opener-it | fail | La maggior parte delle aziende usa l'AI male. | Descrivi cosa succede, con chi e quanti. |
| I10 | in-realta-pivot | flag | Sembra semplice. In realtà è un sistema. | Afferma la tesi senza la rivelazione. |
| I11 | conjunction-opener-it | flag | Ma i dati dicono altro. | Al massimo una per testo. Uniscila alla frase prima. |
| I12 | standalone-perche | flag | Perché l'automazione senza basi è un fallimento più veloce. | Unisci il motivo alla frase che spiega. |
| I13 | non-solo-ma-anche | flag | Non solo fa risparmiare tempo ma anche errori. | Di' le due cose in modo semplice, o tieni la più forte. |
| I14 | narrating-gerund | fail | Abbiamo rifatto il CRM, evidenziando l'importanza dei dati puliti. | Togli il gerundio che commenta. Tieni l'azione e il risultato. |
| I15 | gerund-pileup | flag | Abbiamo lavorato sul CRM, pulendo dati, sistemando campi, creando report. | Al massimo due gerundi di fila. Spezza la frase. |
| I16 | ai-vocabulary-it | fail | Un approccio olistico e trasformativo. | Usa la parola semplice, o il numero dietro. |
| I17 | ai-vocabulary-it-context | flag | È fondamentale navigare il panorama dell'AI. | Va bene in senso letterale. Come decorazione, di' la cosa vera. |
| I18 | filler-it | fail | La verità è che nessuno legge la deck. | Dai la sorpresa, non annunciarla. |
| I19 | self-locating-it | fail | Questa è la parte che gira qui. | Scrivi il fatto e fermati. |
| I20 | filler-it-connective | flag | Detto questo, non a caso il team è cresciuto. | Togli il connettivo, la frase regge da sola. |
| I21 | staged-opener-it | flag | Parliamoci chiaro: il CRM non lo usa nessuno. | Togli la rincorsa e apri sul punto. |
| I22 | split-contrast-it | fail | Non è un aggiornamento. È un nuovo modo di lavorare. | Il contrasto spezzato in due frasi: tieni la seconda, senza la negazione. |
