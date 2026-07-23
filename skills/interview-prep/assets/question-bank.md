# Question Bank — Behavioral / Cultural-Fit / Soft-Skill

This file is the consolidated question taxonomy synthesized from the corpus. Each family lists representative English and Spanish entries. The `playbook` mode selects from these families based on the JD; the `mock-interview` mode drills from them.

## A. Self-introduction & narrative

The opening family. Establish identity, motivation, and value proposition in 60–90 seconds. Every playbook produces an elevator pitch in this family.

- Tell me about yourself. / Cuéntame un poco sobre ti.
- Why this company? / ¿Por qué quieres trabajar en esta empresa?
- Why this role? / ¿Por qué te gustaría trabajar en X puesto?
- Why should we hire you? / ¿Por qué deberíamos escogerte a ti?
- Why are you changing jobs? / ¿Por qué quieres cambiar de trabajo?
- What's your elevator pitch (30-second professional summary)?
- What are your greatest achievements? / ¿Cuáles han sido tus mayores logros?

**Coaching (from *preguntas y respuestas entrevista.pdf*)**: For "cuéntame un poco sobre ti" — do NOT recite the CV; do NOT start with childhood; do NOT ramble. DO lead with one professional identity sentence, then one relevance-to-the-role sentence, then one why-this-company sentence. Max 90 seconds.

## B. Strengths & weaknesses (trap questions)

High-trap family. Designed to expose negativity, dishonesty, or generic AI-level platitudes.

- What are your strengths / 3 virtues? / ¿Dime tus 3 mayores virtudes?
- What is your greatest weakness? / ¿Cuál es tu mayor debilidad?
- How would you describe yourself in three words? / ¿Cómo te definirías en tres palabras?
- How do you react to criticism? / ¿Cómo reaccionas ante las críticas?
- How do you handle stress? / ¿Cómo reaccionas ante situaciones de estrés?

**Coaching**: For weaknesses — a real weakness paired with a mitigation is strongest (per *Cracking the Coding Interview*). "I'm a perfectionist" is a forbidden answer. For strengths — pick exactly 3, with a one-line specific evidence per strength (no more, no less).

## C. Behavioral / experience (STAR-eliciting)

Routed through STAR + Nugget First. Every answer should lead with a nugget, then walk Situation → Task → Action → Result.

- Tell me about a time you had a tight deadline and how you met it. If you didn't meet it, how did you handle the situation? (Spanish source)
- Describe a situation where you used persuasion to successfully convince someone to see things your way. (*Interviewology*)
- Step by step, using a real-life example, tell me how you delegated responsibilities on a project and how you handled it. (*Interviewology*)
- Walk me through your biggest failure, what you learned, and how you dealt with it. (*Interviewology*)
- Tell me about a challenging project you worked on. (*Frontend Handbook*)
- Tell me about a time you disagreed with a technical decision. (*Frontend Handbook*)
- Tell me about a time you had a challenging interaction with a teammate. (*Cracking* S.A.R. example)
- What kind of disagreements have you had with colleagues/managers and how did you resolve them? (*metainterview*)
- How do you operate in an ambiguous, fast-changing environment? (*metainterview*)
- How do you keep your code clean? (*Frontend Handbook*)

## D. Leadership & teamwork

- Can you lead teams? / ¿Te ves capaz de liderar equipos?
- What role do you take in a team? / ¿Cómo sos a la hora de trabajar en equipo, qué rol tomas?
- How do you demonstrate your impact / are you self-directed in reaching goals? (*metainterview*)
- How do you tailor communications to different audiences / cross-functional partners? (*metainterview*)
- How have you approached improving your skills? (*metainterview*)

## E. Cultural fit & company research

These are most accurate when the `playbook` has additional company context. If the `job-application` skill's `company-research` mode has been run, that output should feed these answers.

- What do you know about us and the role? / ¿Qué sabes de la empresa y el puesto?
- What do you like (and dislike) about your current job? (trap)
- What do you like about our company? / ¿Qué es lo que te gusta de nuestra empresa? (trap)
- How long would you stay with us? / ¿Cuánto tiempo te quedarías con nosotros? (trap)
- What are you looking for? / ¿Qué es lo que estás buscando? (trap)
- Are you in other selection processes? / ¿Estás en algún otro proceso de selección? (trap)
- What makes our company better than others? / ¿Qué crees que hace nuestra empresa mejor que otras?
- What is your background/education? / ¿Háblame de tu formación académica?
- Do you have enough training for this role? / ¿Crees que tienes la suficiente formación para el puesto?

**Gap-handling variants** (when the candidate has a CV gap):
- Why have you been unemployed so long? / ¿Por qué has estado tanto tiempo sin trabajar?
- You don't have enough experience. / No tienes la suficiente experiencia.
- You have too much experience. / Tienes demasiada experiencia.

## F. Questions to ask the interviewer

The `playbook` always produces at least 3 candidate questions. Mix styles: genuine (what brought the interviewer to the company), insightful (why a specific technical/product decision), and passion (opportunities to learn X).

- What brought you to this company, and what's been most challenging? (*Cracking*)
- Why did the product choose protocol X over Y? (insightful, per *Cracking*)
- What opportunities are there to learn about scalability? (passion, per *Cracking*)
- Why are you hiring for this role? / ¿Por qué estáis buscando un candidato? (Spanish)
- What's the ideal candidate profile? / ¿Qué tipo de perfil buscáis? (Spanish)
- What are the promotion possibilities? / ¿Qué posibilidades de ascenso hay? (Spanish)
- What training options exist? / ¿Qué opciones de formación hay? (Spanish)
- What retains employees here? / ¿Qué es lo que retiene a los trabajadores? (Spanish)
- How do you evaluate performance and compensation? / ¿Cómo evaluáis el desempeño y retribución? (Spanish)
- How many years has the company operated? / ¿Cuántos años lleva funcionando? (Spanish)
- What's your competitive advantage? / ¿Qué ventaja competitiva tenéis? (Spanish)

## Selection logic (skill-internal)

| Skill mode | Families pulled |
|---|---|
| `personality-strategy` | A (pitch), B (modulated by archetype) |
| `playbook` | A (elevator pitch), B, C (3–5 selected by JD), D, E (with company context), F (3 generated) |
| `mock-interview` | C and B heavy; A once at session start; E with one trap drill; F one closing round |

When a JD is provided to the `playbook`, scan it for keyword signals and elevate the C-family questions whose domain they imply (leadership signals → "delegated responsibilities", conflict signals → "disagreements with managers", ambiguity signals → "ambiguous environment"). When combination with the `job-application` skill is available, use its company-research output to specialize E-family questions.