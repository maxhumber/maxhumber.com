---
title: Code Philosophy
date: 2024-11-15
tags: code
slug: codephilosophy
---

John Ousterhout's [A Philosophy of Software Design](https://www.amazon.com/Philosophy-Software-Design-John-Ousterhout/dp/1732102201) is a masterpiece of software engineering wisdom. Here are some of the most impactful quotes from the book, organized by theme.

#### Complexity

Complexity is the heart of most software engineering challenges.

- **Understanding Complexity**: "If a software system is hard to understand and modify, then it is complicated; if it is easy to understand and modify, then it is simple."
- **Change Amplification**: "The first symptom of complexity is that a seemingly simple change requires code modifications in many different places."
- **Cognitive Load**: "The second symptom of complexity is cognitive load, which refers to how much a developer needs to know in order to complete a task."
- **Incremental Complexity**: "Complexity is incremental: you have to sweat the small stuff."
- **Accumulating Complexity**: "Over time, complexity accumulates, and it becomes harder and harder for programmers to keep all of the relevant factors in their minds as they modify the system."

#### Code Design

Good design is all about making the right tradeoffs and choosing the appropriate abstractions.

- **Simplicity**: "It’s more important for a module to have a simple interface than a simple implementation."
- **Write Twice; Commit Once**: "Designing software is hard, so it’s unlikely that your first thoughts about how to structure a module or system will produce the best design."
- **Abstractions**: "When designing methods, the most important goal is to provide clean and simple abstractions."
- **Deep Modules**: "The best modules are deep: they have a lot of functionality hidden behind a simple interface."
- **Information Hiding**: "Information hiding makes it easier to evolve the system."
- **Avoiding Config Parameters**: "You should avoid configuration parameters as much as possible."

#### DX (Developer Experience)

The humans in the software development loop are just as important as the "loops" themselves.

- **Optimize for Legibility**: "Software should be designed for ease of reading, not ease of writing."
- **Reduce Suffering**: "Most modules have more users than developers, so it is better for the developers to suffer than the users."
- **Comments and Clarity**: "The guiding principle for comments is that comments should describe things that aren’t obvious from the code."
- **Obviousness in Code**: "If someone reading your code says it’s not obvious, then it’s not obvious, no matter how clear it may seem to you."
- **Choosing Good Names**: "Choosing a mediocre name for a particular variable... will have a significant impact on complexity and manageability."

Taken together all of these quotes stress that software is as much about managing complexity as it is about writing code.