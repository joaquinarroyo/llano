# English (en) — full dictionary

Reference list. The agent reads it only in mode `all` or when it reviews a text. The
eval linter also uses it. The most frequent entries are already in `../rules.md`.

Each approved word has one meaning, as in ASD-STE100. When two approved words look
similar, the "Note" column says when to use each one.

## Verbs

| Avoid | Use | Note |
|---|---|---|
| utilize, employ, leverage, make use of | use | |
| perform, carry out, conduct, execute (general) | the real verb, or "do" | "perform an installation" → "install"; "execute" is fine for code |
| proceed to + verb | the verb | "proceed to delete" → "delete" |
| ensure, make sure, confirm, validate (general) | verify | one verb for "check"; "validate" is fine for input validation |
| modify, alter, amend | change | "modify" is fine for a file change in a diff |
| eliminate, purge (data, files) | delete | data, files, records |
| take out, strip (from a list, from code) | remove | "remove" for lists and code, "delete" for data |
| append, incorporate, introduce | add | "append" is fine for a string or a file |
| commence, initiate, kick off | start | general use |
| spin up, fire up, boot up (a service) | start | processes, services, servers |
| terminate, conclude, finalize, wrap up | end, stop | "stop" for processes, "end" for tasks |
| require, necessitate | need | "require" is fine for a formal requirement |
| possess, feature, boast | have | |
| provide, furnish, supply | give | |
| facilitate, enable (general sense), empower | let, help | "enable" is fine for a feature flag |
| augment, boost, ramp up | increase | |
| diminish, decrease, lessen | reduce | |
| demonstrate, illustrate, indicate | show | |
| address, tackle | fix, handle | "address" is fine for a network address |
| obtain, acquire, retrieve (general) | get | "retrieve" is fine for a fetch from storage |
| assist | help | |
| attempt | try | |
| comprehend | understand | |
| determine, ascertain | find, decide | |
| endeavor | try | |
| implement a solution | fix, add, change | "implement an interface/function" is a technical term, keep it |
| figure out | find | |
| look into | examine, investigate | |
| point out | show, say | |
| come up with | find, write, create | |

## Connectors

| Avoid | Use |
|---|---|
| in the event that, in case, provided that | if |
| in order to, so as to, with the aim of | to |
| due to the fact that, owing to, since, as (causal), given that | because |
| however, nevertheless, nonetheless | but |
| therefore, consequently, thus, hence, as a result | so |
| despite the fact that, notwithstanding | although |
| with regard to, in relation to, regarding, in terms of | about |
| by means of, via (non-technical), through (non-spatial) | with |
| prior to, in advance of | before |
| subsequently, following that | after, then |
| at this point in time, currently, at present | now |
| simultaneously, concurrently (general) | at the same time |
| on occasion | sometimes |
| frequently | often |
| in a [adjective] manner | adverb ("in a quick manner" → "quickly") |
| the entirety of, all of the | all |
| a large number of, a great deal of | many, much |
| a number of, a series of | several, some |
| at the level of | in, at |
| on the basis of, based on (as a connector) | from, by, according to |
| that is why, this is the reason why | so |
| additionally, furthermore, moreover, in addition | also |
| in this way, in this manner | so, this way |
| when it comes to, in the context of | for, in |
| ultimately, at the end of the day | finally, in the end |
| the former, the latter | repeat the noun |

## Ambiguous words

| Avoid | Use | Why |
|---|---|---|
| since (causal) | because | "since" also means time |
| as (causal) | because | "as" also means time and comparison |
| while (contrast) | but, although | "while" also means time |
| once (= after) | after, when | "once" also means one time |
| should (= if) | if | "Should it fail" → "If it fails" |
| eventually (= possibly) | maybe, possibly | readers from Romance languages read it as "possibly" |
| actually (= currently) | now | "actually" means "in fact" |
| affect / effect | change, result | readers confuse the two |
| would, could (to soften a fact) | is, can | state the fact |

## Banned filler

Delete these. If the sentence breaks without them, rewrite it.

**Openers:** "Sure!", "Of course!", "Absolutely!", "Perfect!", "Great question!",
"Good question!", "I understand", "Happy to help", "Let me explain", "Let's dive in",
"Here's the thing", "So,".

**Closers:** "I hope this helps", "Hope that helps", "Feel free to ask",
"Let me know if you have any other questions", "Good luck!", "In summary" or
"In conclusion" followed by a repetition.

**Meta-phrases:** "It's worth noting that", "It's important to note that",
"It's important to mention that", "It should be noted that", "Keep in mind that",
"Note that" (when nothing follows that is a warning), "As mentioned earlier",
"As you can see", "What this means is that", "It goes without saying",
"Needless to say", "Arguably", "In today's world", "In a world where".

**Intensifiers:** "basically", "essentially", "really", "truly", "definitely",
"clearly", "obviously", "absolutely", "literally", "simply", "just", "actually",
"very", "quite", "generally speaking".

**Empty adjectives and clichés:** "robust", "powerful", "comprehensive", "holistic",
"seamless", "seamlessly", "frictionless", "cutting-edge", "state-of-the-art",
"best-in-class", "leverage", "delve into", "dive deep", "plays a crucial role",
"plays a key role", "in the current landscape", "navigate the complexities",
"a world of possibilities", "take it to the next level", "game-changer", "unlock".
Also avoid groups of three adjectives that list no real items ("fast, reliable and
scalable").

## Technical terms

Keep these as the ecosystem uses them: commit, branch, merge, rebase, pull request
(PR), deploy, build, endpoint, token, hook, framework, runtime, payload, header, query,
cache, log, bug, test, script, prompt, skill, plugin, pipeline, worker, timeout,
feature flag, log in, set up, roll back, check out.

Pick one form per response and keep it (core rule 7). "Log in" (verb) and "login"
(noun) are different: do not mix them. "Set up" (verb) and "setup" (noun) follow the
same rule.
