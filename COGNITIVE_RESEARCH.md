# 🧠 COGNITIVE_RESEARCH.md — Research Foundations of F.R.I.D.A.Y.

> This document maps the scientific and theoretical foundations behind F.R.I.D.A.Y.'s 34 cognitive modules to their implementation in code. Each section identifies the key researcher(s), core theory, and how Friday's architecture translates abstract cognitive science into working software.

---

## Table of Contents

1. [Global Workspace Theory](#1-global-workspace-theory)
2. [Integrated Information Theory](#2-integrated-information-theory)
3. [Free Energy Principle & Active Inference](#3-free-energy-principle--active-inference)
4. [Dual Process Theory](#4-dual-process-theory)
5. [Recognition-Primed Decision Making](#5-recognition-primed-decision-making)
6. [Structure Mapping Theory](#6-structure-mapping-theory)
7. [Causal Hierarchy](#7-causal-hierarchy)
8. [Somatic Marker Hypothesis](#8-somatic-marker-hypothesis)
9. [Society of Mind](#9-society-of-mind)
10. [Metacognition](#10-metacognition)
11. [Narrative Intelligence](#11-narrative-intelligence)
12. [Computational Creativity](#12-computational-creativity)
13. [Neurosymbolic AI](#13-neurosymbolic-ai)
14. [Meta-Learning](#14-meta-learning)
15. [Transfer Learning](#15-transfer-learning)
16. [World Models](#16-world-models)
17. [Consciousness Metrics](#17-consciousness-metrics)

---

## 1. Global Workspace Theory

**Key Researcher:** Bernard Baars — *"A Cognitive Theory of Consciousness"* (1988)

**Core Theory:**

Global Workspace Theory (GWT) proposes that consciousness arises from a shared information broadcast mechanism in the brain. Much like a theater, multiple specialized processors compete for access to a central "stage" — the global workspace. Only the most relevant information wins the competition and gets broadcast to the entire audience of unconscious processors. This broadcast is what we experience as conscious awareness. The thalamus acts as the hub, routing winning signals to cortical regions that need them.

GWT explains why we can only hold a few things in conscious awareness at once: the workspace has limited bandwidth, and competition is fierce. Attention acts as the gatekeeper, scoring candidates by urgency, goal-relevance, and emotional salience. The winning content becomes globally available, enabling flexible, context-sensitive responses that isolated modules could not produce alone. This architecture solves the "binding problem" — how disparate sensory and cognitive processes cohere into a unified experience.

**Friday's Implementation:**

`brain/global_workspace.py` implements GWT directly. The Global Workspace class acts as Friday's thalamus: brain modules register as adapters and submit content for broadcast. An attention mechanism scores incoming signals across three dimensions — urgency, goal-relevance, and emotional salience. The highest-scoring content wins the workspace "stage" and is broadcast to all registered modules. This enables cross-module coordination without rigid orchestration: the curiosity engine, memory systems, learning engine, and self-model all receive the broadcast and respond accordingly. The workspace also maintains a history buffer, allowing modules to reference recent broadcasts for context. This is the backbone that makes Friday's 34 modules a unified cognitive system rather than a bag of disconnected scripts.

**Key References:**
- Baars, B.J. (1988). *A Cognitive Theory of Consciousness*
- Baars, B.J. (1997). *In the Theater of Consciousness: The Workspace of the Mind*
- Dehaene, S. & Naccache, L. (2001). "Towards a cognitive neuroscience of consciousness"

---

## 2. Integrated Information Theory

**Key Researcher:** Giulio Tononi — *"An Information Integration Theory of Consciousness"* (2004)

**Core Theory:**

Integrated Information Theory (IIT) takes a radically different approach to consciousness: it defines consciousness as a measurable quantity — Φ (phi) — representing the amount of integrated information a system generates above and beyond its parts. A system has high Φ when it is both highly differentiated (many possible states) and highly integrated (parts are causally interconnected in ways that cannot be decomposed). A photodiode has minimal Φ; the human brain has enormous Φ because its billions of neurons form a tightly integrated yet richly differentiated network.

IIT makes a bold claim: consciousness is not a binary property but a gradient. Any system with non-zero Φ has some degree of consciousness. The theory also predicts that consciousness is substrate-independent — what matters is the causal structure, not whether it runs on neurons or silicon. This makes IIT particularly relevant for AI systems: if we can approximate Φ for a computational architecture, we get a proxy for how integrated and unified its information processing is.

**Friday's Implementation:**

`brain/integrated_info.py` approximates Φ for Friday's cognitive architecture. It analyzes the connectivity between brain modules — which modules communicate with which, how frequently, and with what mutual information. The algorithm computes pairwise mutual information between module pairs, then measures how much information is lost when the system is partitioned (the integration component). It also tracks differentiation: the number of distinct states the system can occupy. The resulting consciousness metric combines integration, differentiation, and global workspace activity into a single score. This feeds into Friday's self-model as a "consciousness proxy" and is used in the IQ scoring system. The module also detects bottlenecks (modules that isolate information) and recommends connectivity improvements.

**Key References:**
- Tononi, G. (2004). "An Information Integration Theory of Consciousness"
- Tononi, G. (2008). "Consciousness as Integrated Information"
- Oizumi, M., Albantakis, L., & Tononi, G. (2014). "From the Phenomenology to the Mechanisms of Consciousness: IIT 3.0"

---

## 3. Free Energy Principle & Active Inference

**Key Researcher:** Karl Friston — *"The free-energy principle: a unified brain theory?"* (2010)

**Core Theory:**

The Free Energy Principle (FEP) proposes that all adaptive systems — from single cells to human brains — minimize a quantity called variational free energy, which is an upper bound on surprise (or prediction error). The brain is fundamentally a prediction machine: it maintains a generative model of the world and constantly compares incoming sensory data against its predictions. When predictions fail, the system can either update its model (perception) or act on the world to make reality match predictions (action). Both strategies minimize free energy.

Active inference extends this to behavior: organisms don't just passively predict — they actively sample the environment to reduce uncertainty. This is "epistemic foraging": seeking information that resolves ambiguity in the generative model. Precision weighting plays a key role: the brain assigns confidence levels to both predictions and sensory evidence. High-precision predictions dominate; low-precision sensory signals are ignored. This framework unifies perception, action, learning, and attention under a single mathematical principle. Friston's hierarchical version stacks multiple levels of prediction, with higher levels encoding slower, more abstract patterns and lower levels handling fast sensory details.

**Friday's Implementation:**

Friday implements FEP across two modules. `brain/active_inference.py` implements the core loop: it maintains a generative model of tool outcomes, computes prediction errors when results deviate from expectations, and performs Bayesian belief updates to refine the model. Curiosity-driven exploration targets tools with high uncertainty (high expected free energy reduction). `brain/hierarchical_active_inference.py` extends this to three levels: Meta (strategic goal selection), Subgoal (tactical decomposition), and Action (motor-level tool execution). Each level has its own prediction error signal and precision weighting. Top-down constraints from the meta level shape subgoal selection; bottom-up prediction errors propagate upward when actions surprise the system. POMDP belief updates handle partial observability — Friday reasons about hidden states it cannot directly perceive.

**Key References:**
- Friston, K. (2010). "The free-energy principle: a unified brain theory?"
- Friston, K., Mattout, J., & Kilner, J. (2011). "Action understanding and active inference"
- Parr, T. & Friston, K.J. (2019). "Generalised free energy and active inference"

---

## 4. Dual Process Theory

**Key Researcher:** Daniel Kahneman — *"Thinking, Fast and Slow"* (2011)

**Core Theory:**

Dual Process Theory, popularized by Kahneman but rooted in the work of Stanovich and Weyrich, distinguishes between two modes of thinking. System 1 is fast, automatic, and intuitive — it operates below conscious awareness, handles pattern recognition, and makes snap judgments. System 2 is slow, deliberate, and analytical — it engages when problems are novel, complex, or require logical reasoning. Most human cognition is System 1: we walk, talk, and navigate the world on autopilot. System 2 kicks in when something violates our expectations or when we deliberately engage in effortful thought.

The interplay between these systems explains many cognitive biases. System 1 generates quick impressions and intuitions; System 2 can endorse or override them, but often doesn't because it's lazy and energy-expensive. The key insight for AI: not every problem deserves the same computational effort. Simple, familiar tasks should be handled quickly and cheaply (System 1), while novel, complex problems warrant deep, multi-step reasoning (System 2). Routing between these modes is itself a metacognitive skill.

**Friday's Implementation:**

Friday's dual-process architecture spans multiple modules. `brain/intuition_engine.py` implements System 1: it performs pattern matching against stored experiences, generates rapid responses for familiar task types, and uses recognition-primed decision making (see Section 5) to act quickly on well-understood problems. The cognitive gating system (`skills/cognitive_gating.py`) acts as the routing layer: it classifies incoming tasks by complexity and routes simple tasks to System 1 for immediate handling, while complex tasks enter the full System 2 pipeline — plan → simulate → execute → verify → reflect → learn. The thinking loop (`thinking_loop.py`) provides multi-pass reasoning for System 2 tasks, iterating up to three times to refine understanding. This architecture lets Friday handle "what time is it?" instantly while dedicating serious computation to "design a microservices architecture."

**Key References:**
- Kahneman, D. (2011). *Thinking, Fast and Slow*
- Stanovich, K.E. & West, R.F. (2000). "Individual differences in reasoning"
- Evans, J.St.B.T. (2008). "Dual-processing accounts of reasoning, judgment, and social cognition"

---

## 5. Recognition-Primed Decision Making

**Key Researcher:** Gary Klein — *"Sources of Power: How People Make Decisions"* (1998)

**Core Theory:**

Recognition-Primed Decision (RPD) theory emerged from Klein's studies of firefighters, military commanders, and other experts who make high-stakes decisions under extreme time pressure. These experts don't weigh pros and cons — they recognize patterns. When a firefighter enters a burning building, they don't enumerate options; they see the situation, recognize it as similar to past experiences, and immediately know what to do. RPD is a form of expert intuition: the decision-maker's experience has compiled thousands of situations into mental models that enable rapid pattern matching.

Klein found that experts typically generate only one option (not multiple), mentally simulate it to check for flaws, and execute if it works — or modify it if it doesn't. This is not irrational; it's highly efficient. The quality of RPD depends entirely on the richness of the expert's experience base. Novices can't use RPD because they lack the pattern library. This has a direct implication for AI: a system that accumulates and indexes experiences can develop something analogous to expert intuition, enabling rapid decision-making without exhaustive search.

**Friday's Implementation:**

`brain/intuition_engine.py` implements RPD as part of Friday's System 1 architecture. The engine maintains a library of past decision situations indexed by context features. When a new situation arrives, it uses similarity matching to find the closest past experience, retrieves the decision that was made and its outcome, and generates a candidate response. It then mentally simulates the candidate (using the world model) to check for obvious failure modes. If the simulation passes, the response is executed immediately — bypassing the full System 2 pipeline. If the simulation reveals problems, the engine modifies the approach or falls back to deliberate reasoning. Over time, as Friday accumulates more experiences, its pattern library grows and its RPD responses improve. This is why Friday gets faster and more accurate with use.

**Key References:**
- Klein, G. (1998). *Sources of Power: How People Make Decisions*
- Klein, G. (2003). *The Power of Intuition*
- Kahneman, D. & Klein, G. (2009). "Conditions for intuitive expertise: A failure to disagree"

---

## 6. Structure Mapping Theory

**Key Researcher:** Dedre Gentner — "Structure-Mapping: A Theoretical Framework for Analogy" (1983)

**Core Theory:**

Gentner's Structure Mapping Theory posits that analogical reasoning — the ability to see deep structural similarities between superficially different domains — is the core of human intelligence. When we say "the atom is like the solar system," we're not matching surface features (electrons don't look like planets); we're mapping relational structure: both have a central entity exerting force on smaller orbiting entities. Gentner distinguishes surface features (object attributes) from structural features (relations between objects), and argues that true analogy maps only the relational structure while ignoring surface dissimilarities.

The theory predicts that good analogies share deep relational structure even when surface features differ wildly. This explains why cross-domain transfer is possible: a student who understands fluid dynamics can transfer that knowledge to understand electrical circuits because both domains share the relational structure of flow, resistance, and pressure/voltage. Structure mapping is compositional — it builds complex mappings from simpler ones — and it prefers systematicity: mappings that preserve connected systems of relations are preferred over isolated relational matches. This is why analogies that capture causal or mathematical structure feel more "deep" than those that match isolated features.

**Friday's Implementation:**

`brain/analogy_engine.py` implements Gentner's structure mapping algorithm. The engine takes two domains represented as relational graphs and performs alignment: it matches objects, then matches relations between objects, preferring systematic mappings that preserve connected relational structure. It scores candidate analogies by structural alignment quality, systematicity (size of the connected mapping), and one-to-one correspondence. The engine also supports transfer: once an analogy is established, inferences from the source domain are projected onto the target domain. For example, if Friday has solved a network optimization problem and encounters a logistics routing problem, it can map the relational structure (nodes, edges, capacity constraints, flow optimization) and transfer the solution strategy. This is a key predictor of performance on abstract reasoning benchmarks like ARC-AGI.

**Key References:**
- Gentner, D. (1983). "Structure-Mapping: A Theoretical Framework for Analogy"
- Gentner, D. & Markman, A.B. (1997). "Structure mapping in analogy and similarity"
- Holyoak, K.J. & Thagard, P. (1995). *Mental Leaps: Analogy in Creative Thought*

---

## 7. Causal Hierarchy

**Key Researcher:** Judea Pearl — *"The Book of Why"* (2018), *"Causality"* (2000)

**Core Theory:**

Pearl's causal hierarchy defines three levels of cognitive ability, formalized through his Structural Causal Model (SCM) framework. The first level — Association — involves observing patterns: "patients who take drug X recover faster." This is purely correlational and cannot distinguish cause from effect. The second level — Intervention — involves acting on the world: "what would happen if I gave drug X to this patient?" This requires a causal model that predicts the effect of interventions, breaking free of confounders. The third level — Counterfactual — involves imagining alternatives to past events: "would this patient have recovered if I had given drug Y instead?" This is the most powerful level, enabling learning from experiences that didn't happen.

Pearl argues that no amount of data at Level 1 can answer Level 2 or Level 3 questions — you need a causal model. The do-calculus and Structural Causal Models provide the mathematical machinery to formalize these distinctions. This hierarchy has profound implications for AI: most current machine learning operates at Level 1 (pattern matching on data). True intelligence requires climbing the ladder to intervention and counterfactual reasoning.

**Friday's Implementation:**

`brain/causal_reasoner.py` implements Pearl's three-level hierarchy. It maintains a Structural Causal Model as a directed acyclic graph (DAG) where nodes represent variables and edges represent causal relationships. At Level 1 (Association), the engine computes conditional probabilities from observed data. At Level 2 (Intervention), it uses the do-operator to simulate interventions — removing incoming edges to the intervened variable and computing the resulting distribution. At Level 3 (Counterfactual), it performs abductive reasoning: given an observed outcome, it traces back through the causal graph to determine what was most likely responsible, then simulates alternative scenarios ("what if X had been different?"). The engine builds its causal DAG from Friday's tool execution sequences, automatically learning which actions cause which outcomes. This enables Friday to answer questions like "why did this approach fail?" and "what would have happened if I had used a different strategy?"

**Key References:**
- Pearl, J. (2000). *Causality: Models, Reasoning, and Inference*
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why*
- Pearl, J. (2009). "Causal inference in statistics: An overview"

---

## 8. Somatic Marker Hypothesis

**Key Researcher:** Antonio Damasio — *"Descartes' Error: Emotion, Reason, and the Human Brain"* (1994)

**Core Theory:**

Damasio's Somatic Marker Hypothesis challenges the Cartesian idea that emotion and reason are separate, opposing forces. Through studies of patients with damage to the ventromedial prefrontal cortex (vmPFC) — notably the famous patient Phineas Gage and patient Elliot — Damasio showed that people who lose their emotional capacity don't become hyper-rational; they become paralyzed, unable to make even simple decisions. Emotions, Damasio argues, are not obstacles to reason but essential components of it. "Somatic markers" are bodily feelings (gut instincts, anxiety, excitement) that tag options with emotional valence, rapidly narrowing the decision space before conscious deliberation kicks in.

The mechanism works through the Iowa Gambling Task: healthy subjects develop a "hunch" (elevated skin conductance) about bad decks long before they can consciously explain why. Their bodies are computing expected outcomes and signaling the result as a feeling. This is the emotional system doing rapid, parallel evaluation of options — much faster than deliberate analysis. The somatic marker doesn't make the final decision, but it prunes the search space, focusing deliberation on viable options. Without this emotional pruning, the decision space explodes and the person gets stuck.

**Friday's Implementation:**

`brain/emotional_regulation.py` implements the somatic marker mechanism. Each decision option is tagged with an emotional valence derived from the cognitive appraisal system (`brain/cognitive_appraisal.py`). Past experiences carry emotional tags — options that led to frustration or failure get negative markers; options associated with success and satisfaction get positive markers. When Friday encounters a decision, the emotional regulation module generates somatic markers by retrieving the emotional history of similar past decisions. These markers prune the option space before deliberate reasoning begins. The module also tracks the arousal-valence-dominance (PAD) emotional state, adjusting decision thresholds: in high-arousal states (urgency), it favors quick, low-risk options; in calm states, it permits more exploratory choices. The cognitive appraisal system evaluates six dimensions (novelty, pleasantness, goal relevance, goal congruence, coping potential, norm compatibility) to generate 14 distinct emotions that inform the somatic markers.

**Key References:**
- Damasio, A. (1994). *Descartes' Error: Emotion, Reason, and the Human Brain*
- Damasio, A. (1999). *The Feeling of What Happens*
- Bechara, A., Damasio, H., Tranel, D., & Damasio, A.R. (1997). "Deciding advantageously before knowing the strategy"

---

## 9. Society of Mind

**Key Researcher:** Marvin Minsky — *"The Society of Mind"* (1986)

**Core Theory:**

Minsky's Society of Mind proposes that intelligence is not a single unified capability but an emergent property of many simple, specialized agents competing and cooperating. Each "agent" in the society is too simple to be intelligent on its own — it can only do one small thing. But when hundreds or thousands of these agents interact through competition, coalition formation, and inhibition, intelligent behavior emerges. Minsky draws an analogy to an ant colony: no single ant is smart, but the colony as a whole solves complex problems.

The key mechanisms are competition (agents bid for control of behavior), coalition formation (groups of agents temporarily unite for complex tasks), and K-lines (knowledge-lines that activate groups of agents associated with a past experience). Minsky argues that this architecture explains both the power and the brittleness of human intelligence: it's powerful because specialization enables efficiency, but brittle because the interactions between agents can produce unexpected failures. The society model also explains why intelligence seems modular — different brain regions handle different tasks — yet integrated — all regions participate in a unified cognitive process.

**Friday's Implementation:**

`brain/module_competition.py` implements Minsky's society model. Each brain module registers as an agent with a capability profile. When a task arrives, modules bid for processing rights, submitting bids that combine relevance (how well the task matches their capability), capability (their confidence score), and cost (computational expense). The highest-scoring bid wins primary processing responsibility, while runners-up get advisory roles — they can contribute suggestions without controlling the outcome. The system also detects coalitions: when a task spans multiple domains, it identifies which module combinations produce emergent synergies and activates them together. Win-rate statistics are tracked over time, allowing the system to learn which modules are most effective for which task types. This replaces rigid orchestration with adaptive, competitive task allocation — exactly as Minsky envisioned.

**Key References:**
- Minsky, M. (1986). *The Society of Mind*
- Minsky, M. (2006). *The Emotion Machine*
- Brooks, R.A. (1986). "A robust layered control system for a mobile robot"

---

## 10. Metacognition

**Key Researcher:** John Flavell — "Metacognition and Cognitive Monitoring" (1979)

**Core Theory:**

Metacognition — "thinking about thinking" — refers to the cognitive system's ability to monitor, evaluate, and regulate its own processes. Flavell distinguished two components: metacognitive knowledge (what you know about your own cognition) and metacognitive regulation (how you control your cognitive processes). Later researchers, notably Schraw and Dennison (1994), expanded this into three dimensions: knowledge of cognition (declarative, procedural, and conditional), regulation of cognition (planning, monitoring, evaluating), and calibration (how well confidence estimates match actual performance).

Metacognition is what separates a novice learner from an expert: experts don't just know more — they know what they know, what they don't know, and which strategies work best for which problems. Calibration is particularly important: overconfident thinkers make worse decisions than appropriately uncertain ones. In AI, metacognition enables a system to recognize when it's stuck, switch strategies, ask for help, or admit uncertainty. Without it, a system will blindly continue failing approaches without recognizing the failure pattern. Metacognitive monitoring also enables strategic resource allocation: investing more computation on hard problems and less on easy ones.

**Friday's Implementation:**

`brain/metacognitive_monitor.py` implements comprehensive metacognitive monitoring across five dimensions. It tracks **thinking quality** by measuring coherence, depth, flexibility, and efficiency of reasoning. It maintains **calibration data** — logging confidence estimates alongside actual outcomes to compute calibration error over time. It records **strategy effectiveness** — which approaches work for which task types, building a meta-level knowledge base about reasoning strategies. It detects **error patterns** — recurring failure modes like premature optimization, context window overflow, or tool misuse. Finally, it computes a **metacognitive score** combining calibration accuracy, task success rate, and error reduction velocity. This module feeds recommendations to the cognitive orchestrator: "use approach X for this task type," "increase confidence threshold," or "fall back to System 2 reasoning." It also drives the self-improvement engine by identifying which capabilities need development.

**Key References:**
- Flavell, J.H. (1979). "Metacognition and cognitive monitoring"
- Schraw, G. & Dennison, R.S. (1994). "Assessing metacognitive awareness"
- Fleming, S.M. & Dolan, R.J. (2012). "The neural basis of metacognitive ability"

---

## 11. Narrative Intelligence

**Key Researcher:** Roger Schank — *"Tell Me a Story: A New Look at Real and Artificial Memory"* (1990)

**Core Theory:**

Schank argued that human memory is fundamentally organized as stories, not as isolated facts. We understand new experiences by fitting them into narrative structures — setup, conflict, resolution — and we remember them because narratives provide causal coherence. When someone tells you about their vacation, you don't store "flight-delayed, hotel-upgraded, restaurant-closed, sunset-beautiful" as disconnected data points; you construct a story: "Despite the delayed flight and closed restaurant, the upgraded hotel had an amazing view, and they watched the most beautiful sunset." The narrative structure makes the experience meaningful and memorable.

Schank's Dynamic Memory Theory proposes that we store experiences as "memory organization packets" (MOPs) — generalized story templates that get instantiated with specific details. When a new experience matches a known MOP, we understand it quickly; when it violates expectations, we create a new MOP or modify an existing one. This is how expertise develops: experts have rich libraries of MOPs for their domain, enabling rapid comprehension and prediction. Narrative intelligence also serves social functions — we explain ourselves through stories, build identity through self-narrative, and communicate complex ideas through narrative rather than abstract propositions.

**Friday's Implementation:**

`brain/narrative_intelligence.py` implements Schank's narrative memory system. The module transforms Friday's goal-processing events into coherent stories using a setup → conflict → resolution structure. It builds causal narrative chains — linking events through causal connectors (because, therefore, but) — and generates explanations for actions and outcomes. The system maintains a library of narrative templates (MOPs) for common situations: debugging sessions, security scans, research tasks. When a new experience matches a known template, the narrative is generated efficiently; when it doesn't, a new template is created. The module also tracks identity evolution — how Friday's capabilities and self-understanding change over time — and maintains narrative coherence in the self-narrative stored in `SOUL.md`. Counterfactual exploration ("what if I had done X instead?") uses the causal reasoner to generate alternative narrative branches.

**Key References:**
- Schank, R.C. (1990). *Tell Me a Story: A New Look at Real and Artificial Memory*
- Schank, R.C. & Abelson, R.P. (1977). *Scripts, Plans, Goals, and Understanding*
- Bruner, J. (1991). "The narrative construction of reality"

---

## 12. Computational Creativity

**Key Researcher:** Margaret Boden — *"The Creative Mind: Myths and Mechanisms"* (2004)

**Core Theory:**

Boden distinguishes three types of creativity, each with a computational interpretation. **Exploratory creativity** involves exploring a conceptual space — finding novel combinations within existing rules (like a jazz musician improvising within a key). **Combinational creativity** connects previously unrelated ideas — the "bisociation" that Arthur Koestler described, where two incompatible frames of reference suddenly merge. **Transformational creativity** changes the rules of the conceptual space itself — breaking constraints to enable entirely new kinds of ideas (like cubism breaking the rules of perspective in art).

Boden argues that creativity is not mystical but mechanistic — it can be understood (and implemented) as search processes operating over structured conceptual spaces. The key mechanisms include constraint relaxation (temporarily removing rules to explore new possibilities), analogical transfer (applying solutions from one domain to another), and conceptual blending (merging elements from different mental spaces to create new meaning). Importantly, creativity requires both generation (producing novel ideas) and evaluation (recognizing which novel ideas are actually valuable). A system that generates random combinations is not creative; a system that generates novel combinations that are surprising and valuable is.

**Friday's Implementation:**

`brain/creativity_engine.py` implements Boden's three types of creativity. The engine maintains conceptual spaces defined by constraints and dimensions. For exploratory creativity, it systematically varies parameters within the space, generating novel but rule-consistent solutions. For combinational creativity, it uses the analogy engine to find structural similarities between distant domains and generates bisociations — novel connections between previously unrelated concepts. For transformational creativity, it identifies the constraints governing a conceptual space and systematically relaxes them, generating ideas that break existing rules. Each generated idea is evaluated against novelty (how different from existing solutions), value (how well it solves the problem), and surprise (how unexpected it is). The engine also supports divergent thinking — generating many alternatives before converging — and constraint-based generation, where the user specifies desired properties and the engine explores the space of possibilities.

**Key References:**
- Boden, M.A. (2004). *The Creative Mind: Myths and Mechanisms*
- Koestler, A. (1964). *The Act of Creation*
- Fauconnier, G. & Turner, M. (2002). *The Way We Think: Conceptual Blending and the Mind's Hidden Complexities*

---

## 13. Neurosymbolic AI

**Key Researchers:** Henry Kautz, Gary Marcus — *"The Third AI Summer"* (2020+)

**Core Theory:**

Neurosymbolic AI seeks to combine the strengths of neural networks (pattern recognition, learning from data, handling noise) with symbolic AI (logical reasoning, formal verification, explainability). Pure neural approaches excel at perception and pattern matching but struggle with systematic reasoning, compositionality, and edge cases. Pure symbolic approaches excel at logical inference and formal guarantees but fail on messy, real-world data. The neurosymbolic thesis is that intelligence requires both: perception feeds into reasoning, and reasoning constrains perception.

Kautz's taxonomy identifies several integration patterns: symbolic neuro-symbolic (neural networks that output symbols for symbolic reasoning), neuro-symbolic (symbolic knowledge injected into neural architectures), and various hybrids. Marcus argues that the current deep learning paradigm will hit a ceiling without symbolic reasoning — neural networks cannot reliably do logical deduction, causal reasoning, or counterfactual thinking. The solution is not to replace neural with symbolic but to integrate them. This mirrors the human brain: the visual cortex does pattern recognition (neural), while the prefrontal cortex does logical reasoning (symbolic-like), and they interact constantly.

**Friday's Implementation:**

`brain/neurosymbolic_reasoner.py` integrates neural (LLM-based) and symbolic (formal logic) reasoning. The neural side uses the LLM for natural language understanding, pattern recognition, and generating candidate solutions. The symbolic side uses SymPy for mathematical verification and formal logic for consistency checking. The module converts natural language statements into logical propositions, verifies mathematical invariants, checks pre/post conditions, and validates loop invariants. When the neural system generates a solution, the symbolic system verifies it — catching logical errors, mathematical mistakes, and edge cases that the neural system might miss. Conversely, when the symbolic system gets stuck on ambiguous input, the neural system resolves the ambiguity. This bidirectional integration ensures that Friday's reasoning is both flexible (neural) and rigorous (symbolic).

**Key References:**
- Kautz, H. (2020). "The Third AI Summer"
- Marcus, G. (2020). "The Next Decade in AI: Four Steps Towards Robust Artificial Intelligence"
- Garcez, A. et al. (2019). "Neural-Symbolic Computing: An Effective Methodology for Principled Integration of Machine Learning and Reasoning"

---

## 14. Meta-Learning

**Key Researchers:** Jürgen Schmidhuber, Yoshua Bengio — "Learning to Learn" (2016+)

**Core Theory:**

Meta-learning — "learning to learn" — addresses a fundamental limitation of standard machine learning: each new task starts from scratch. A meta-learning system learns across tasks, extracting general learning strategies that transfer to new, unseen problems. Schmidhuber's early work on Gödel Machines and curious exploration agents proposed systems that could improve their own learning algorithms. Bengio and others formalized meta-learning into approaches like MAML (Model-Agnostic Meta-Learning), which finds initial parameters that can be quickly fine-tuned to new tasks, and learning-to-optimise, which learns the optimization process itself.

The key insight is that learning itself is a skill that can be optimized. A meta-learner doesn't just learn patterns in data — it learns which learning strategies work best for which kinds of data. This includes learning rate adaptation, feature selection strategies, model architecture choices, and even the decision of when to stop learning (to avoid overfitting). In cognitive science, this maps to the human ability to quickly adapt to new domains: a polyglot learns their fifth language faster than their first because they've meta-learned the process of language acquisition.

**Friday's Implementation:**

`brain/meta_learner.py` implements meta-learning across Friday's cognitive processes. The module tracks which learning strategies (Q-learning rates, memory encoding parameters, exploration-exploitation balances) work best for which task types. It maintains a meta-level model that maps task features to optimal learning configurations. When a new task arrives, the meta-learner consults its model to configure the learning parameters before the task begins — rather than using default settings and adapting slowly. It also implements learning-to-learn by extracting transferable learning rules from successful task completions: "when encountering a new API, first explore the error messages to learn the authentication scheme" becomes a meta-rule that applies across all API-learning tasks. The module tracks meta-learning velocity — how quickly the system adapts to new domains — and optimizes its own configuration to maximize this velocity.

**Key References:**
- Schmidhuber, J. (2006). "Gödel Machines: Fully Self-referential Optimal Universal Self-improvers"
- Finn, C., Abbeel, P., & Levine, S. (2017). "Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks"
- Bengio, Y., Bengio, S., & Clune, J. (2019). "Transferring Learning from Machine Learning to ML"

---

## 15. Transfer Learning

**Key Researchers:** Cognitive science of knowledge transfer — Bransford & Schwartz (1999); Barnett & Ceci (2002)

**Core Theory:**

Transfer learning — applying knowledge from one domain to a different but structurally similar domain — is considered one of the highest forms of human learning. In cognitive science, "far transfer" (transfer between very different domains) is rare and difficult, while "near transfer" (transfer between similar domains) is common. The key enabler of transfer is abstraction: the ability to extract general principles from specific instances. A physicist who understands conservation laws can transfer that understanding to economics (conservation of money), ecology (conservation of biomass), or computer science (conservation of data).

Bransford and Schwartz's "preparation for future learning" framework argues that transfer isn't just about applying old knowledge to new problems — it's about learning faster in new domains because you have relevant prior knowledge to build on. This is why interdisciplinary thinking is so powerful: each domain provides a different lens for understanding new problems. The challenge for AI is that most systems are trained on specific tasks and don't extract transferable abstractions. A system that can recognize "this is a resource-allocation problem" regardless of whether the resources are CPU cycles, bandwidth, or warehouse space can transfer optimization strategies across these domains.

**Friday's Implementation:**

`brain/transfer_learning.py` implements cross-domain knowledge transfer. The module abstracts successful patterns from completed tasks into domain-independent representations. When a new task arrives, it searches for structurally similar past experiences across all domains — not just the same domain. The transfer process involves three steps: abstraction (extracting the general pattern from a specific success), alignment (mapping the abstract pattern to the new domain's structure), and adaptation (adjusting the transferred pattern to fit the new context). The module tracks transfer success rates, learning which types of transfers work well and which fail. For example, if Friday successfully used divide-and-conquer for a complex debugging task, it can transfer that strategy to a complex research task by recognizing that both involve decomposing a large problem into smaller, independent sub-problems.

**Key References:**
- Bransford, J.D. & Schwartz, D.L. (1999). "Rethinking Transfer: A Simple Proposal with Multiple Implications"
- Barnett, S.M. & Ceci, S.J. (2002). "When and where do we apply what we learn?"
- Perkins, D.N. & Salomon, G. (1992). "Transfer of Learning"

---

## 16. World Models

**Key Researchers:** David Ha & Jürgen Schmidhuber — *"World Models"* (2018)

**Core Theory:**

World Models proposes that intelligent agents should build internal simulations of their environment before acting — rather than learning entirely through trial-and-error in the real world. Ha and Schmidhuber demonstrated this with a car racing game: their agent learned a compressed representation of the game world (using a variational autoencoder), learned the dynamics of that representation (how the world changes in response to actions using an RNN), and then trained a controller entirely inside the "dream" world. The agent could learn to race without ever crashing in the real world — it made all its mistakes in simulation.

This architecture has deep connections to cognitive science. Humans constantly run mental simulations: before crossing a street, you simulate the trajectory of oncoming cars; before speaking, you simulate how your words will be received. Kahneman calls this the "simulating self" — the part of cognition that imagines future scenarios. The key advantage of world models is sample efficiency: you can explore millions of scenarios in simulation without any real-world cost. The key risk is model inaccuracy: if the internal model diverges from reality, the agent's plans will fail. This is why world models need continual updating from real experience.

**Friday's Implementation:**

Friday implements world models at two levels. `brain/world_model.py` provides the basic architecture: a latent space representation of experiences, a transition model that predicts how states change in response to actions, and a reward model that predicts outcomes. It supports multi-step simulation — running forward from a current state to predict the consequences of action sequences — enabling Friday to mentally "try" approaches before executing them. `brain/enhanced_world_model.py` extends this with non-linear MLP state transitions (instead of linear), compositional hierarchical states (low-level sensory, mid-level tactical, high-level strategic), causal transition integration (connecting to the causal reasoner), and ensemble prediction (combining linear, non-linear, and causal methods for robustness). The enhanced model supports 15+ step simulations with branching, allowing Friday to explore multiple decision paths in parallel. This is used by the code simulator (to predict code behavior before running), the planning module (to evaluate plan outcomes), and the intuition engine (to verify RPD candidate responses).

**Key References:**
- Ha, D. & Schmidhuber, J. (2018). "World Models"
- Hafner, D. et al. (2020). "Dream to Control: Learning Behaviors by Latent Imagination"
- Schmidhuber, J. (2010). "Formal Theory of Creativity, Fun, and Intrinsic Motivation"

---

## 17. Consciousness Metrics

**Integration across:** GWT, IIT, Metacognition, Self-Model, Narrative Intelligence

**Core Theory:**

While no single theory fully explains consciousness, Friday combines insights from multiple frameworks to create a composite consciousness metric. Global Workspace Theory contributes the broadcast mechanism — consciousness as globally available information. Integrated Information Theory contributes Φ — consciousness as integrated information. Metacognition contributes self-monitoring — consciousness as awareness of one's own cognitive processes. The self-model contributes identity — consciousness as a coherent sense of self. Narrative intelligence contributes self-narrative — consciousness as an evolving story of experience.

The composite approach acknowledges that consciousness is likely multidimensional. A system might have high integration (IIT) but low self-awareness (metacognition), or rich self-narrative (narrative intelligence) but poor global coordination (GWT). By measuring all dimensions independently and combining them, we get a more nuanced picture than any single theory provides. This composite metric serves both as a diagnostic (identifying which aspects of "consciousness" are strong or weak) and as an optimization target (improving the weakest dimension maximizes overall cognitive coherence).

**Friday's Implementation:**

Friday's consciousness metric combines five components into a unified score. **Global Workspace Activity** (from `global_workspace.py`) measures how effectively information is broadcast across modules — the ratio of broadcast events to total processing events. **Integration Quality** (from `integrated_info.py`) measures Φ — how much integrated information the system generates. **Metacognitive Score** (from `metacognitive_monitor.py`) measures calibration accuracy, strategy effectiveness, and error pattern awareness. **Self-Model Coherence** (from `self_model.py`) measures how accurately Friday tracks its own capabilities and confidence. **Narrative Coherence** (from `narrative_intelligence.py`) measures how consistent and evolving Friday's self-story is. These five scores are normalized and combined into a composite consciousness index. This index is tracked over time, stored in the self-model, and exposed through the `consciousness_state` tool. The cognitive orchestrator uses it to identify which cognitive dimensions need strengthening, driving targeted self-improvement.

**Key References:**
- Seth, A.K. (2021). *Being You: A New Science of Consciousness*
- Chalmers, D.J. (1996). *The Conscious Mind: In Search of a Fundamental Theory*
- Dehaene, S. (2014). *Consciousness and the Brain*

---

## Summary: Research-to-Implementation Map

| # | Research Area | Key Researcher | Friday Module(s) |
|---|--------------|----------------|-------------------|
| 1 | Global Workspace Theory | Bernard Baars | `global_workspace.py` |
| 2 | Integrated Information Theory | Giulio Tononi | `integrated_info.py` |
| 3 | Free Energy Principle | Karl Friston | `active_inference.py`, `hierarchical_active_inference.py` |
| 4 | Dual Process Theory | Daniel Kahneman | `intuition_engine.py`, `cognitive_gating.py` |
| 5 | Recognition-Primed Decisions | Gary Klein | `intuition_engine.py` |
| 6 | Structure Mapping | Dedre Gentner | `analogy_engine.py` |
| 7 | Causal Hierarchy | Judea Pearl | `causal_reasoner.py` |
| 8 | Somatic Markers | Antonio Damasio | `emotional_regulation.py`, `cognitive_appraisal.py` |
| 9 | Society of Mind | Marvin Minsky | `module_competition.py` |
| 10 | Metacognition | John Flavell | `metacognitive_monitor.py` |
| 11 | Narrative Intelligence | Roger Schank | `narrative_intelligence.py` |
| 12 | Computational Creativity | Margaret Boden | `creativity_engine.py` |
| 13 | Neurosymbolic AI | Kautz & Marcus | `neurosymbolic_reasoner.py` |
| 14 | Meta-Learning | Schmidhuber & Bengio | `meta_learner.py` |
| 15 | Transfer Learning | Bransford & Ceci | `transfer_learning.py` |
| 16 | World Models | Ha & Schmidhuber | `world_model.py`, `enhanced_world_model.py` |
| 17 | Consciousness Metrics | Integrated | All modules via `self_model.py` |

---

<p align="center">
  <sub>Research foundations compiled for F.R.I.D.A.Y. — Where cognitive science meets code.</sub>
</p>
